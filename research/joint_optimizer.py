"""Joint ICR-OPT: four-operator routing, contract activation and coalition settlement.

Synthetic research benchmark. Requires numpy and scipy. Monetary values and
traffic volumes are illustrative, not measured tariffs or operational forecasts.
"""
import argparse
import json
from itertools import combinations
from pathlib import Path
import numpy as np
from scipy.optimize import milp, linprog, Bounds, LinearConstraint
from scipy.sparse import lil_matrix

N=4
Z=5
T=2
TIERS=3
NAMES=['T1','T2','T3','T4']

def instance(seed):
    rng=np.random.default_rng(seed)
    coverage=rng.random((Z,N))<rng.uniform(.28,.78,N)
    if not coverage.any(): coverage[0,0]=True
    demand=rng.uniform(24,125,(Z,N,T))*rng.uniform(.55,1.5,N)[None,:,None]
    demand*=np.array([.55,1.45])[None,None,:]
    capacity=rng.uniform(25,115,(Z,N,T))*np.array([1.1,.68])[None,None,:]
    capacity*=coverage[:,:,None]
    return dict(seed=seed,coverage=coverage,demand=demand,capacity=capacity,
                benefit=rng.uniform(4.7,10,N),host_cost=rng.uniform(.9,4.5,N),
                peak_extra=rng.uniform(.6,2.5,N),gamma=rng.uniform(.4,3,N),
                fixed=np.where(np.eye(N,dtype=bool),0,rng.uniform(35,360,(N,N))))

def optimize(data,coalition=tuple(range(N))):
    present=set(coalition)
    coverage,demand,capacity=(data[k] for k in ('coverage','demand','capacity'))
    flow=[];edges=set()
    for z in range(Z):
      for t in range(T):
       for i in sorted(present):
        if coverage[z,i]:continue
        for j in sorted(present):
         if i==j or not coverage[z,j] or capacity[z,j,t]<1e-10:continue
         edges.add((i,j))
         for level in range(TIERS):
          cost=data['host_cost'][j]+(data['peak_extra'][j] if t else 0)+data['gamma'][j]*(level+.5)/TIERS
          flow.append((z,t,i,j,level,cost))
    pairs=sorted(edges);F=len(flow);P=len(pairs)
    empty=dict(welfare=0.,volumes=np.zeros((N,N,T)),pair_host_cost=np.zeros((N,N)),
               base_gains=np.zeros(N),guest_values=np.zeros(N),host_costs=np.zeros(N),
               fixed=np.zeros((N,N)),active=[])
    if not F:return empty
    pair_index={pair:F+k for k,pair in enumerate(pairs)}
    margin=np.array([data['benefit'][i]-cost for z,t,i,j,level,cost in flow])
    objective=np.r_[-margin,np.array([data['fixed'][i,j] for i,j in pairs])]
    variables=F+P
    bounds=Bounds(np.zeros(variables),np.r_[np.full(F,np.inf),np.ones(P)])
    integer=np.r_[np.zeros(F),np.ones(P)]
    rows=[];rhs=[]
    def add(items,limit):
     row={}
     for var,weight in items:row[var]=row.get(var,0.)+weight
     rows.append(row);rhs.append(float(limit))
    home={};segments={};agreements={}
    for k,(z,t,i,j,level,cost) in enumerate(flow):
     home.setdefault((z,t,i),[]).append(k)
     segments.setdefault((z,t,j,level),[]).append(k)
     agreements.setdefault((i,j),[]).append(k)
    for (z,t,i),idx in home.items():add(((k,1) for k in idx),demand[z,i,t])
    for (z,t,j,level),idx in segments.items():add(((k,1) for k in idx),capacity[z,j,t]/TIERS)
    for (i,j),idx in agreements.items():
     max_flow=sum(demand[z,i,t] for z in range(Z) for t in range(T)
                  if not coverage[z,i] and coverage[z,j])
     add([(k,1) for k in idx]+[(pair_index[i,j],-max_flow)],0)
    A=lil_matrix((len(rows),variables))
    for row_idx,row in enumerate(rows):
     for var,val in row.items():A[row_idx,var]=val
    sol=milp(objective,integrality=integer,bounds=bounds,
             constraints=LinearConstraint(A.tocsr(),-np.inf,np.array(rhs)),
             options={'time_limit':25,'mip_rel_gap':1e-9})
    if sol.status!=0 or sol.x is None:
     raise RuntimeError('MILP not certified optimal: '+str(sol.message))
    volume=np.zeros((N,N,T));pair_cost=np.zeros((N,N))
    guest=np.zeros(N);host=np.zeros(N)
    for qty,(z,t,i,j,level,cost) in zip(sol.x[:F],flow):
     if qty<1e-8:continue
     volume[i,j,t]+=qty
     guest[i]+=qty*data['benefit'][i]
     host[j]+=qty*cost
     pair_cost[i,j]+=qty*cost
    fixed=np.zeros((N,N));active=[]
    for i,j in pairs:
     if volume[i,j,:].sum()>1e-7:
      fixed[i,j]=data['fixed'][i,j];active.append((i,j))
    baseline=guest-host-.4*fixed.sum(axis=1)-.6*fixed.sum(axis=0)
    W=float(baseline.sum())
    if abs(W+sol.fun)>1e-4:raise AssertionError('Objective mismatch')
    return dict(welfare=W,volumes=volume,pair_host_cost=pair_cost,base_gains=baseline,
                guest_values=guest,host_costs=host,fixed=fixed,active=active)

def coalition_values(data):
    v={0:0.}
    for mask in range(1,16):
     members=[i for i in range(N) if mask&(1<<i)]
     v[mask]=optimize(data,members)['welfare']
    return v

def payoffs(base,payments):
    gains=base['base_gains'].copy()
    for (i,j),amount in payments.items():
     gains[i]-=amount;gains[j]+=amount
    return gains

def bilateral_payments(base,host_surplus_share=.5):
    prices={}
    for i,j in base['active']:
     q=base['volumes'][i,j,:].sum()
     minimum=base['pair_host_cost'][i,j]+.6*base['fixed'][i,j]
     maximum=base['guest_values'][i]*q/max(1e-10,base['volumes'][i,:,:].sum())-.4*base['fixed'][i,j]
     prices[(i,j)]=minimum+host_surplus_share*(maximum-minimum)
    return prices

def core_violation(payoff,v):
    blocked=[]
    for mask in range(1,15):
     members=[i for i in range(N) if mask&(1<<i)]
     gap=float(v[mask]-payoff[members].sum())
     if gap>1e-6:blocked.append(dict(mask=mask,coalition=[NAMES[i] for i in members],gap=gap))
    return sorted(blocked,key=lambda x:-x['gap'])

def unconstrained_core(v):
    """Idealized core with transferable payoffs between every operator."""
    grand=v[15]
    A=[];y=[]
    for mask in range(1,15):
     A.append([-int(bool(mask&(1<<i))) for i in range(N)])
     y.append(-v[mask])
    lp=linprog(np.zeros(N),A_ub=A,b_ub=y,A_eq=[np.ones(N)],b_eq=[grand],
               bounds=[(0,None)]*N,method='highs')
    if lp.success:return dict(feasible=True,gains=lp.x,least_core_epsilon=0.)
    relaxed=linprog(np.r_[np.zeros(N),1.],
       A_ub=[row+[-1] for row in A],b_ub=y,A_eq=[np.r_[np.ones(N),0]],
       b_eq=[grand],bounds=[(0,None)]*(N+1),method='highs')
    if not relaxed.success:raise RuntimeError('Idealized least-core failed')
    return dict(feasible=False,gains=relaxed.x[:N],least_core_epsilon=float(relaxed.x[-1]))

def implementable_settlement(base,v,permit_reverse=False,pairwise_bounds=False):
    """Find stable payments on selected directed contracts, if feasible.

    Stage 1 minimizes maximal coalition deficit. Stage 2 finds the closest
    equal-payoff solution at that optimal stability deficit. Pairwise bounds
    forbid invoices below attributed host cost or above guest value.
    """
    edges=sorted(base['active']);n=len(edges)
    baseline=base['base_gains'];total=base['welfare']
    D=np.zeros((N,n))
    for k,(i,j) in enumerate(edges):
     D[i,k]=-1;D[j,k]=1
    A=[];y=[]
    for mask in range(1,15):
     members=[i for i in range(N) if mask&(1<<i)]
     row=np.r_[-D[members,:].sum(axis=0),-1.]
     A.append(row);y.append(float(baseline[members].sum()-v[mask]))
    if pairwise_bounds:
     limits=[]
     for i,j in edges:
      qty=base['volumes'][i,j,:].sum()
      minimum=base['pair_host_cost'][i,j]+.6*base['fixed'][i,j]
      maximum=base['guest_values'][i]*qty/max(1e-10,base['volumes'][i,:,:].sum())-.4*base['fixed'][i,j]
      limits.append((float(minimum),float(maximum)))
     if any(lo>hi+1e-7 for lo,hi in limits):
      return dict(core_stable=False,epsilon=None,payments={},gains=None,
                  violating_coalitions=[],largest_violation=None,reason='Empty bilateral corridor')
     bounds=limits+[(0,None)]
    else:
     bounds=([(None,None)] if permit_reverse else [(0,None)])*n+[(0,None)]
    primary=linprog(np.r_[np.zeros(n),1.],A_ub=np.array(A).reshape((14,n+1)),
                    b_ub=np.array(y),bounds=bounds,method='highs')
    if not primary.success:raise RuntimeError('Settlement feasibility LP failed: '+primary.message)
    epsilon=max(0.,float(primary.x[-1]))
    # Secondary objective: fair distribution among allocations with the same deficit.
    target=np.full(N,total/N)
    fair_A=[];fair_y=[]
    for mask in range(1,15):
     members=[i for i in range(N) if mask&(1<<i)]
     fair_A.append(np.r_[-D[members,:].sum(axis=0),np.zeros(N)])
     fair_y.append(float(baseline[members].sum()-v[mask]+epsilon+1e-7))
    for i in range(N):
     row=np.r_[D[i,:],np.zeros(N)];row[n+i]=-1
     fair_A.append(row);fair_y.append(target[i]-baseline[i])
     row=np.r_[-D[i,:],np.zeros(N)];row[n+i]=-1
     fair_A.append(row);fair_y.append(baseline[i]-target[i])
    fair=linprog(np.r_[np.zeros(n),np.ones(N)],
                 A_ub=np.array(fair_A),b_ub=np.array(fair_y),
                 bounds=bounds[:-1]+[(0,None)]*N,method='highs')
    if not fair.success:raise RuntimeError('Settlement fairness LP failed: '+fair.message)
    payments={edge:float(fair.x[k]) for k,edge in enumerate(edges)}
    gains=payoffs(base,payments)
    if abs(gains.sum()-total)>1e-5:raise AssertionError('Transfer accounting mismatch')
    blocked=core_violation(gains,v)
    return dict(core_stable=len(blocked)==0,epsilon=epsilon,payments=payments,
                gains=gains,violating_coalitions=blocked,
                largest_violation=max([x['gap'] for x in blocked],default=0.))

def run_game(seed):
    data=instance(seed);base=optimize(data)
    v=coalition_values(data)
    equal=np.full(N,base['welfare']/N)
    bilateral=payoffs(base,bilateral_payments(base))
    ideal=unconstrained_core(v)
    direct=implementable_settlement(base,v)
    signed=implementable_settlement(base,v,permit_reverse=True)
    capped=implementable_settlement(base,v,pairwise_bounds=True)
    return dict(seed=seed,grand_value=base['welfare'],active_agreements=base['active'],
                total_traffic=float(base['volumes'].sum()),coalition_values=v,
                base_gains=base['base_gains'],equal_gains=equal,
                equal_blocked=core_violation(equal,v),
                bilateral_gains=bilateral,bilateral_blocked=core_violation(bilateral,v),
                ideal_core=ideal,directional=direct,signed_credit=signed,
                capped_bilateral=capped,pair_volumes=base['volumes'],
                pair_costs=base['pair_host_cost'],contract_fixed=base['fixed'])

def json_clean(obj):
    if isinstance(obj,np.ndarray):return obj.tolist()
    if isinstance(obj,(np.integer,np.floating)):return obj.item()
    if isinstance(obj,dict):
     return {(':'.join(NAMES[i] for i in k) if isinstance(k,tuple) else str(k)):json_clean(v)
             for k,v in obj.items()}
    if isinstance(obj,(list,tuple)):return [json_clean(v) for v in obj]
    return obj

def main():
    p=argparse.ArgumentParser(description='ICR joint MILP and core-constrained settlements')
    p.add_argument('--seeds',type=int,default=24)
    p.add_argument('--start',type=int,default=20000)
    p.add_argument('--output',type=Path,default=Path('research/joint_results.json'))
    args=p.parse_args();cases=[run_game(seed) for seed in range(args.start,args.start+args.seeds)]
    summary=dict(cases=len(cases),positive=sum(r['grand_value']>1e-8 for r in cases),
       equal_stable=sum(not r['equal_blocked'] for r in cases),
       bilateral_stable=sum(not r['bilateral_blocked'] for r in cases),
       ideal_core_feasible=sum(r['ideal_core']['feasible'] for r in cases),
       nonnegative_directional_tariffs_stable=sum(r['directional']['core_stable'] for r in cases),
       signed_agreement_credits_stable=sum(r['signed_credit']['core_stable'] for r in cases),
       individually_capped_bilateral_stable=sum(r['capped_bilateral']['core_stable'] for r in cases),
       mean_directional_deficit=float(np.mean([r['directional']['epsilon'] for r in cases])),
       max_directional_deficit=float(max(r['directional']['epsilon'] for r in cases)))
    output=dict(model='ICR joint MILP/coalition pricing benchmark',synthetic=True,
       settings=dict(seed_start=args.start,seeds=args.seeds,operators=N,areas=Z,periods=T,cost_tiers=TIERS),
       summary=summary,cases=cases)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(json_clean(output),indent=2))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
