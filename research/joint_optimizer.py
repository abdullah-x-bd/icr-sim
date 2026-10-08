"""ICR-OPT joint routing, agreements and coalition-constrained settlements.

Fully synthetic and for economic mechanism testing, not operational roaming tariffs.
Requires numpy and scipy. All monetary units are hypothetical and internally
consistent with traffic units. An exact MILP solve is required before certification.
"""
import argparse
import json
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.optimize import milp, linprog, Bounds, LinearConstraint
from scipy.sparse import lil_matrix

N = 4
Z = 5
T = 2
TIERS = 3
NAMES = ['T1', 'T2', 'T3', 'T4']


def instance(seed):
    rng = np.random.default_rng(seed)
    coverage = rng.random((Z, N)) < rng.uniform(.28, .78, N)
    if not coverage.any():
        coverage[0, 0] = True
    demand = rng.uniform(24, 125, (Z, N, T)) * rng.uniform(.55, 1.5, N)[None, :, None]
    demand *= np.array([.55, 1.45])[None, None, :]
    capacity = rng.uniform(25, 115, (Z, N, T)) * np.array([1.1, .68])[None, None, :]
    capacity *= coverage[:, :, None]
    return dict(seed=seed, coverage=coverage, demand=demand, capacity=capacity,
                benefit=rng.uniform(4.7, 10, N), host_cost=rng.uniform(.9, 4.5, N),
                peak_extra=rng.uniform(.6, 2.5, N), gamma=rng.uniform(.4, 3.0, N),
                fixed=np.where(np.eye(N, dtype=bool), 0, rng.uniform(35, 360, (N, N))))


def optimize(data, coalition=tuple(range(N))):
    present = set(coalition)
    coverage, demand, capacity = (data[k] for k in ('coverage', 'demand', 'capacity'))
    flow = []
    edges = set()
    for z in range(Z):
        for t in range(T):
            for i in sorted(present):
                if coverage[z, i]:
                    continue
                for j in sorted(present):
                    if i == j or not coverage[z, j] or capacity[z, j, t] < 1e-10:
                        continue
                    edges.add((i, j))
                    for level in range(TIERS):
                        price = (data['host_cost'][j] + (data['peak_extra'][j] if t else 0)
                                 + data['gamma'][j] * (level + .5) / TIERS)
                        flow.append((z, t, i, j, level, price))
    pair_list = sorted(edges)
    F, P = len(flow), len(pair_list)
    empty = dict(welfare=0., volumes=np.zeros((N, N, T)), pair_host_cost=np.zeros((N, N)),
                 period_host_cost=np.zeros((N, N, T)), base_gains=np.zeros(N), guest_values=np.zeros(N),
                 host_costs=np.zeros(N), fixed=np.zeros((N, N)), active=[])
    if not F:
        return empty
    pair_index = {pair: F + k for k, pair in enumerate(pair_list)}
    marginal = np.array([data['benefit'][i] - price for z,t,i,j,l,price in flow])
    objective = np.r_[-marginal, np.array([data['fixed'][i,j] for i,j in pair_list])]
    variables = F + P
    bounds = Bounds(np.zeros(variables), np.r_[np.full(F, np.inf), np.ones(P)])
    integer = np.r_[np.zeros(F), np.ones(P)]
    rows, rhs = [], []
    def add(pairs, limit):
        row = {}
        for key, weight in pairs:
            row[key] = row.get(key, 0.) + weight
        rows.append(row); rhs.append(float(limit))
    home = {}; segments = {}; agreements = {}
    for idx, (z,t,i,j,l,unit_cost) in enumerate(flow):
        home.setdefault((z,t,i), []).append(idx)
        segments.setdefault((z,t,j,l), []).append(idx)
        agreements.setdefault((i,j), []).append(idx)
    for (z,t,i), indices in home.items():
        add(((idx, 1) for idx in indices), demand[z,i,t])
    for (z,t,j,l), indices in segments.items():
        add(((idx, 1) for idx in indices), capacity[z,j,t]/TIERS)
    for (i,j), indices in agreements.items():
        max_flow = sum(demand[z,i,t] for z in range(Z) for t in range(T)
                       if not coverage[z,i] and coverage[z,j])
        add([(idx, 1) for idx in indices] + [(pair_index[i,j], -max_flow)], 0)
    matrix = lil_matrix((len(rows), variables))
    for k,row in enumerate(rows):
        for var,weight in row.items():
            matrix[k,var] = weight
    solution = milp(objective, integrality=integer, bounds=bounds,
                    constraints=LinearConstraint(matrix.tocsr(), -np.inf, np.array(rhs)),
                    options=dict(time_limit=25, mip_rel_gap=1e-9))
    if solution.status != 0 or solution.x is None:
        raise RuntimeError(f'MILP not certified optimal: status={solution.status}: {solution.message}')
    volumes=np.zeros((N,N,T)); pair_cost=np.zeros((N,N));period_cost=np.zeros((N,N,T))
    guest=np.zeros(N); host=np.zeros(N)
    for qty, (z,t,i,j,l,cost) in zip(solution.x[:F],flow):
        if qty < 1e-8:
            continue
        volumes[i,j,t] += qty
        guest[i] += qty * data['benefit'][i]
        host[j] += qty * cost
        pair_cost[i,j] += qty * cost
        period_cost[i,j,t] += qty * cost
    fixed = np.zeros((N,N)); active=[]
    for i,j in pair_list:
        if volumes[i,j,:].sum()>1e-7:
            active.append((i,j)); fixed[i,j]=data['fixed'][i,j]
    # Agreement cost borne 40% by guest and 60% by host.
    baseline=guest-host-.4*fixed.sum(axis=1)-.6*fixed.sum(axis=0)
    welfare=float(baseline.sum())
    if abs(welfare+solution.fun)>1e-4:
        raise AssertionError('Internal objective/accounting mismatch')
    return dict(welfare=welfare, volumes=volumes, pair_host_cost=pair_cost, period_host_cost=period_cost,
                base_gains=baseline, guest_values=guest, host_costs=host,
                fixed=fixed, active=active)


def coalition_values(data):
    values={0:0.}
    for mask in range(1,1<<N):
        members=[i for i in range(N) if mask & (1<<i)]
        values[mask]=optimize(data, members)['welfare']
    return values


def payoffs(base, payments):
    gain=base['base_gains'].copy()
    for (i,j),amount in payments.items():
        gain[i]-=amount;gain[j]+=amount
    return gain


def bilateral_payments(base, host_surplus_share=.5):
    prices={}
    for i,j in base['active']:
        qty=base['volumes'][i,j,:].sum()
        lower=base['pair_host_cost'][i,j]+.6*base['fixed'][i,j]
        upper=qty*base['guest_values'][i]/max(1e-10,base['volumes'][i,:,:].sum())-.4*base['fixed'][i,j]
        prices[(i,j)]=lower+host_surplus_share*(upper-lower)
    return prices


def core_violation(payoff, values):
    violations=[]
    for mask in range(1,(1<<N)-1):
        members=[i for i in range(N) if mask & (1<<i)]
        gap=float(values[mask]-payoff[members].sum())
        if gap>1e-6:
            violations.append(dict(coalition=[NAMES[i] for i in members],gap=gap,mask=mask))
    return sorted(violations,key=lambda z:-z['gap'])


def unconstrained_core(values):
    """Idealized core allocation allowing transfers between any operators."""
    grand=values[15]
    M=[]; right=[]
    for mask in range(1,15):
        M.append([-int(bool(mask&(1<<i))) for i in range(N)])
        right.append(-values[mask])
    # x_i may not be negative. Singleton coalitions are zero in this model.
    bounds=[(0,None)]*N
    lp=linprog(np.zeros(N),A_ub=M,b_ub=right,
               A_eq=[np.ones(N)],b_eq=[grand],bounds=bounds,method='highs')
    if lp.success:
        return dict(feasible=True, gains=lp.x, least_core_epsilon=0.)
    rows=[row+[-1] for row in M]
    approx=linprog(np.r_[np.zeros(N),1.],A_ub=rows,b_ub=right,
                   A_eq=[np.r_[np.ones(N),0]],b_eq=[grand],
                   bounds=bounds+[(0,None)],method='highs')
    if not approx.success:
        raise RuntimeError('Idealized least-core solve failed')
    return dict(feasible=False,gains=approx.x[:N],least_core_epsilon=float(approx.x[-1]))


def implementable_settlement(base, values, permit_reverse=False, pairwise_bounds=False):
    """Least-core then closest-to-equal settlement using active agreements.

    Payment on each selected directed agreement is p >= 0, unless the
    explicitly labelled signed-credit experiment is enabled.
    """
    edges=sorted(base['active']); n=len(edges)
    baseline=base['base_gains']; total=base['welfare']
    D=np.zeros((N,n))
    for k,(i,j) in enumerate(edges):
        D[i,k]=-1;D[j,k]=1
    def inequalities(extra=0):
        A=[]; y=[]
        for mask in range(1,15):
            members=[i for i in range(N) if mask&(1<<i)]
            row=np.zeros(n+extra)
            row[:n]=-D[members,:].sum(axis=0)
            if extra:row[n]=-1
            A.append(row); y.append(float(baseline[members].sum()-values[mask]))
        return np.array(A).reshape((14,n+extra)),np.array(y)
    # LP 1 minimizes the maximum coalition deficit. epsilon is not a subsidy.
    A,y=inequalities(extra=1)
    if pairwise_bounds:
        terms=[]
        for i,j in edges:
            qty=base['volumes'][i,j,:].sum()
            lower=base['pair_host_cost'][i,j]+.6*base['fixed'][i,j]
            upper=base['guest_values'][i]*qty/max(base['volumes'][i,:,:].sum(),1e-10)-.4*base['fixed'][i,j]
            terms.append((float(lower),float(upper)))
        if any(lo>hi+1e-7 for lo,hi in terms):
            return dict(core_stable=False,epsilon=None,payments={},gains=None,
                        violating_coalitions=[],largest_violation=None,
                        reason='One or more fixed-flow bilateral corridors are empty')
        bounds=terms+[(0,None)]
    else:
        bounds=([(None,None)] if permit_reverse else [(0,None)])*n+[(0,None)]
    primary=linprog(np.r_[np.zeros(n),1.],A_ub=A,b_ub=y,bounds=bounds,method='highs')
    if not primary.success:
        raise RuntimeError('Constrained least-core LP failed: '+primary.message)
    epsilon=max(0.,float(primary.x[-1]))
    # LP 2: minimize sum of absolute deviations from equal operator payoffs,
    # keeping the minimum attainable coalition deficit unchanged.
    target=np.full(N,total/N)
    stageA=[];stageB=[]
    for mask in range(1,15):
        members=[i for i in range(N) if mask&(1<<i)]
        row=np.r_[-D[members,:].sum(axis=0),np.zeros(N)]
        stageA.append(row);stageB.append(float(baseline[members].sum()-values[mask]+epsilon+1e-7))
    for i in range(N):
        row=np.r_[D[i,:],np.zeros(N)];row[n+i]=-1
        stageA.append(row);stageB.append(target[i]-baseline[i])
        row=np.r_[-D[i,:],np.zeros(N)];row[n+i]=-1
        stageA.append(row);stageB.append(baseline[i]-target[i])
    fair=linprog(np.r_[np.zeros(n),np.ones(N)],A_ub=np.array(stageA),b_ub=np.array(stageB),
                 bounds=bounds[:-1]+[(0,None)]*N,method='highs')
    if not fair.success:
        raise RuntimeError('Constrained fairness LP failed: '+fair.message)
    transfers={edge:float(fair.x[k]) for k,edge in enumerate(edges)}
    payoff=payoffs(base,transfers)
    if abs(payoff.sum()-total)>1e-5:
        raise AssertionError('Transfers do not preserve private surplus')
    gaps=core_violation(payoff,values)
    return dict(core_stable=len(gaps)==0, epsilon=epsilon, payments=transfers,
                gains=payoff, violating_coalitions=gaps,
                largest_violation=max([x['gap'] for x in gaps],default=0.))


def two_part_terms(base, settlement):
    """Represent total invoices using an enablement fee and two usage rates.

    A fixed enablement fee recovers 60% of the host's agreement setup cost.
    Each period rate covers its host incremental cost and a constant per-GB
    allocation of the remaining jointly negotiated margin.
    """
    result=[]
    for (i,j),payment in settlement['payments'].items():
        volumes=base['volumes'][i,j,:]
        costs=base['period_host_cost'][i,j,:]
        total=float(volumes.sum())
        if total<=1e-10:continue
        enablement=float(.6*base['fixed'][i,j])
        margin=float(payment-costs.sum()-enablement)
        rates=[(float(cost/q+margin/total) if q>1e-10 else None)
               for q,cost in zip(volumes,costs)]
        reconstructed=enablement+sum(q*r for q,r in zip(volumes,rates) if r is not None)
        if abs(reconstructed-payment)>1e-5:raise AssertionError('Tariff breakdown mismatch')
        result.append(dict(guest=NAMES[i],host=NAMES[j],
            activation_fee=enablement,offpeak_rate=rates[0],peak_rate=rates[1],
            offpeak_volume=float(volumes[0]),peak_volume=float(volumes[1]),
            full_payment=float(payment),margin_over_host_cost=margin))
    return result


def run_game(seed):
    data=instance(seed)
    base=optimize(data)
    values=coalition_values(data)
    equal=np.full(N,base['welfare']/N)
    bilateral=payoffs(base,bilateral_payments(base))
    ideal=unconstrained_core(values)
    contracted=implementable_settlement(base,values,False)
    credit=implementable_settlement(base,values,True)
    capped=implementable_settlement(base,values,False,True)
    return dict(seed=seed, grand_value=base['welfare'], active_agreements=base['active'],
      total_traffic=float(base['volumes'].sum()), coalition_values=values,
      base_gains=base['base_gains'], equal_gains=equal,
      equal_blocked=core_violation(equal,values), bilateral_gains=bilateral,
      bilateral_blocked=core_violation(bilateral,values), ideal_core=ideal,
      directional=contracted, signed_credit=credit, capped_bilateral=capped,
      two_part_tariffs=two_part_terms(base,capped) if capped['core_stable'] else [],
      pair_volumes=base['volumes'], pair_costs=base['pair_host_cost'],
      pair_period_costs=base['period_host_cost'],
      contract_fixed=base['fixed'])


def json_clean(obj):
    if isinstance(obj,np.ndarray):return obj.tolist()
    if isinstance(obj,(np.integer,np.floating)):return obj.item()
    if isinstance(obj,dict):
        return {(':'.join(NAMES[i] for i in k) if isinstance(k,tuple) else str(k)):json_clean(v) for k,v in obj.items()}
    if isinstance(obj,list):return [json_clean(v) for v in obj]
    if isinstance(obj,tuple):return [json_clean(v) for v in obj]
    return obj


def main():
    parser=argparse.ArgumentParser(description='Joint ICR agreements, traffic routing and coalition settlements')
    parser.add_argument('--seeds',type=int,default=24)
    parser.add_argument('--start',type=int,default=20000)
    parser.add_argument('--output',type=Path,default=Path('research/joint_results.json'))
    args=parser.parse_args()
    rows=[]
    for seed in range(args.start,args.start+args.seeds):
        rows.append(run_game(seed))
    summary=dict(cases=len(rows),positive=sum(r['grand_value']>1e-8 for r in rows),
                 equal_stable=sum(not r['equal_blocked'] for r in rows),
                 bilateral_stable=sum(not r['bilateral_blocked'] for r in rows),
                 ideal_core_feasible=sum(r['ideal_core']['feasible'] for r in rows),
                 nonnegative_directional_tariffs_stable=sum(r['directional']['core_stable'] for r in rows),
                 signed_agreement_credits_stable=sum(r['signed_credit']['core_stable'] for r in rows),
                 individually_capped_bilateral_stable=sum(r['capped_bilateral']['core_stable'] for r in rows),
                 mean_directional_deficit=float(np.mean([r['directional']['epsilon'] for r in rows])),
                 max_directional_deficit=float(max(r['directional']['epsilon'] for r in rows)))
    payload=dict(model='ICR-OPT joint MILP/coalition pricing benchmark',synthetic=True,
                 settings=dict(seed_start=args.start,seeds=args.seeds,operators=N,areas=Z,periods=T,cost_tiers=TIERS),
                 summary=summary,cases=rows)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(json_clean(payload),indent=2))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()