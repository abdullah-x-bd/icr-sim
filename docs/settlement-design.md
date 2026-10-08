# ICR-OPT: Economic Criteria for Roaming Charges and Settlement

**Research note | 8 October 2026**

## 1. The three separate design choices

1. **Cost standard:** What extra economic cost does the visited TSP incur to host another TSP's service, measured against an explicit no-sharing counterfactual?
2. **Charge basis:** Do parties pay by data volume, voice minute, successful subscriber attachment, reserved busy-hour capacity, fixed integration commitment, or a hybrid?
3. **Clearing and bargaining:** Are the terms settled pair by pair, by reciprocal bilateral netting, or through a multilateral bargaining and clearing arrangement?

These are not interchangeable. Charging per GB is a way to meter a service; it does not determine a fair markup or whether a multilateral agreement is stable.

## 2. Cost standard

For each host j, accounting period t and new ICR traffic volume q, define

C_incremental_jt(q) = C_jt(existing load + q) - C_jt(existing load).

The economic cost can include incremental transport and processing, relevant energy, expected network upgrades triggered by guest traffic, and the opportunity cost of scarce host capacity. When a reserve is physically set aside in advance, capacity reservation has a cost even if the guest does not fully use it.

One-time integration, testing, billing, authentication and contract-administration costs are separately recorded and amortized over an agreed horizon. Do not count sunk network costs as new incremental expense merely because the network is used by another operator. Avoid double-counting the same peak scarcity in both a reservation fee and per-GB surcharge.

For transparent regulated comparisons, distinguish:

- **Pure LRIC:** the forward-looking cost avoided when the incremental service is removed.
- **LRIC+:** incremental cost plus justified allocation of common costs.
- **Fully allocated costing:** all common and joint costs distributed by accounting rules.

These standards have distinct meanings. The 2025 ITU-D report provides a recent comparative description: https://www.itu.int/pub/D-STG-SG01.04_REV_ED-2025.

## 3. Bilateral economically feasible payment corridor

For fixed guest i, host j, a chosen service and time period, define:

- B_ij: incremental guest private value, **net of its next-best alternative**;
- F^G_ij: incremental guest integration and administration cost;
- C^H_ij: actual host incremental variable and scarcity cost;
- F^H_ij: attributable host integration and reserved-capacity cost, with reservation charges kept separate if applicable.

Then for the complete agreement the lower and upper total-payment bounds are

L_ij = C^H_ij + F^H_ij,

U_ij = B_ij - F^G_ij.

An individually rational bilateral charge T_ij requires **L_ij <= T_ij <= U_ij**. The available operating surplus is S_ij=U_ij-L_ij.

If S_ij>=0, a bargaining benchmark with host surplus weight α_ij∈[0,1] is

T*_ij=L_ij + α_ij S_ij.

This is a **total settlement over the contracting horizon**. A per-GB headline number is only T*_ij/Q if volume Q is fixed and there is no separate fixed fee. When demand varies, two-part and contingent contracts need different interpretation.

The cost calculation determines a lower bound. The guest's outside option determines the upper bound. Neither alone specifies a unique fair rate.

## 4. Compare charging forms

| Mechanism | Settlement form | Suitable when | Principal weakness |
| --- | --- | --- | --- |
| Pure pay-as-you-go | p_ij × actual GB | Traffic is variable and spare capacity is genuinely idle | Can fail to recover agreement setup or reserved-capacity expense at low volume |
| Fixed fee only | F_ij per month | Stable reservation or integration commitment | Poor incentive to moderate usage if capacity is congested |
| Two-part | F_ij + p_ij × GB | Fixed enablement expense plus variable network usage | Allocates volume risk unevenly |
| Peak/off-peak | F_ij + p_off Q_off + p_peak Q_peak | Scarce busy-hour capacity has greater opportunity cost | Peak demand may change in response to price; prospective peak classification required |
| Capacity reservation plus overage | F_ij + a_ij × committed busy-hour capacity + p × metered overage | The host must protect scarce capacity in advance | Can be expensive for guest if reserved capacity is unused |
| Volume tiers | Piecewise p(Q), possibly minimum commitment | Long-term predictable and high traffic | Can create distortions at tier thresholds |
| Reciprocal credits/net billing | Signed bilateral debt offset, settle residual net cash | Both parties host one another | Simple 1:1 GB barter ignores unequal host costs and quality |
| Multilateral clearing | Bilateral metered charges plus separate clearing transfers | Three or more operators create joint gains requiring redistribution | Requires transparent governance, auditability and a defensible participation agreement |

BEREC's 2016 roaming market report documents fixed unit rates, balanced/unbalanced traffic pricing, committed traffic and financial minimums. Its June 2026 EU wholesale guidance recognises flat, committed and capacity-based arrangements for negotiating parties in that legal regime. These are examples of contract structure, not automatically applicable Indian price rules.

Sources:
- https://www.berec.europa.eu/en/document-categories/berec/reports/berec-report-on-the-wholesale-roaming-market
- https://www.berec.europa.eu/en/all-documents/berec/regulatory-best-practices/guidelines/berec-guidelines-on-the-application-of-article-3-of-regulation-eu-2022612-of-6-april-2022-on-roaming-on-public-communications-networks-wholesale-roaming-guidelines
- https://www.itu.int/rec/T-REC-D.264/en

## 5. Four-operator win-win optimization

The model should optimize *traffic first* against full incremental economic resource costs:

**maximize aggregate guest incremental value - incremental host service cost - agreement activation/investment costs**,

subject to signal and service eligibility, safe capacity and minimum QoS reserves. Wholesale charges are transfers and therefore cancel out of the aggregate objective. A charge is not a substitute for available radio resources.

Once an efficient feasible allocation is chosen, each operator i has incremental gain

ΔΠ_i = own recovered-service value - hosting incremental cost - own agreement costs
        + wholesale received - wholesale paid + eligible clearing received.

Minimum condition: **ΔΠ_i >= 0** for all participants relative to their explicit outside options. For realistic risk, the contract may specify a minimum target margin or a probabilistic loss bound, with ex-post balancing clauses.

A fully multilateral settlement can be feasible under unrestricted transferable utility when a connected participating group creates sufficient total private surplus. But **positive grand-total surplus alone is not sufficient** if transfers are restricted to particular trading directions, are prohibited, or a subgroup has a better outside arrangement.

### Cooperative stability

For every candidate coalition S of operators, calculate v(S), its maximum feasible private surplus if it cooperates independently of other operators. A proposed payoff vector π is **in the core** if

sum_i π_i = v(N), π_i >= 0, and
sum_(i∈S) π_i >= v(S) for every S⊂N.

Nash bargaining, Shapley value or proportional cost-sharing schemes may be evaluated against these constraints. No single named bargaining solution guarantees coalition stability for every game. When the core is empty, report the least-core relaxation, redesign the operating allocation or identify a transparent compensating subsidy and its funding source.

Research precedents:
- https://www.sciencedirect.com/science/article/abs/pii/S1389128615001127
- https://pubsonline.informs.org/doi/abs/10.1287/mnsc.1050.0455
- https://digital.library.adelaide.edu.au/items/50d2a430-c9a8-42e7-8144-5303453d6ea6

## 6. Simulation experiment and results

We tested **420 seeded synthetic network cases** with four TSPs, five geographical areas, two demand periods, three marginal host capacity/cost tiers and a fixed cost for activating each guest-host direction. The mixed-integer optimizer selected economically efficient traffic and contract activation. In 419 cases some profitable sharing was selected.

Different settlement methods were evaluated on the **same optimized traffic**. The results illustrate the effects of payment design, not real-world rates.

| Charging rule | Cases with every participating TSP nonnegative | Percent of 419 active cases |
| --- | ---: | ---: |
| One pre-chosen common rate of 3.25 synthetic currency units/GB | 44 | 10.5% |
| Host cost recovery plus 20% | 376 | 89.7% |
| Exact incremental host cost recovery | 419 | 100% |
| Bilateral equal division of each pair's positive surplus | 419 | 100% |
| Zero-priced reciprocal offset plus fixed settlement of imbalance | 44 | 10.5% |

**A common rate selected optimally for each case** could make all four nonnegative in 354 of the 419 cases, or 84.5%. So the weakness of the single fixed rate does not mean a uniform rate is always impossible.

The cost-recovery and bilateral 50/50 results reached 100% **by construction under this model**. The optimizer can drop negative pairwise agreements, and these accounting rules are designed to make the retained pairs nonnegative. This is neither evidence that all real operators will sign such contracts nor a meaningful out-of-sample prediction of success.

Equal-price reciprocal netting led to exactly the same net operator gains as equivalent full gross invoicing. Netting cancels offsetting monetary obligations, **not** network costs, quality differences or capacity constraints.

### Stability tests

We recomputed the full characteristic-function values of 24 independent four-operator coalition games, solving the constrained network sharing problem for every subgroup. An economically feasible core distribution existed in all 24 sampled games.

But a simple equal four-way split had at least one profitable deviating subgroup in **22/24**, and bilateral equal-surplus bargaining had a profitable deviating subgroup in **14/24**. Thus individually rational transfers alone do not establish coalition stability. These frequencies are contingent on a synthetic network generator, not estimates of real industry behaviour.

### Stochastic contract test

A separate **100,000-trial synthetic one-pair contract-risk** experiment set expected off-peak traffic to 300 GB and peak traffic to 120 GB. Forecast variable hosting costs were 2.3 and 4.2 per GB, guest value 5.9 per GB, host fixed cost 60, and guest fixed cost 30 (all monetary units synthetic). Four contracts split the same *forecast* economic surplus equally, while realized volume and host cost varied randomly.

| Contract | Both parties nonnegative after realized traffic/cost shock | Host-loss cases | Guest-loss cases |
| --- | ---: | ---: | ---: |
| One blended unit rate | 97.96% | 2.05% | 0% |
| Separate fixed off-peak/peak unit rates | 99.63% | 0.37% | 0% |
| Up-front enablement fee plus period-specific usage rates | 99.66% | 0.33% | 0.01% |
| Fixed enablement fee plus ex-post cost-indexed usage rates | 97.81% | 0% | 2.19% |

The indexed contract reduced host downside but transferred more downside risk to the guest. The stress distribution, forecast parameters and assumption of **unchanged traffic decisions after tariffs** are artificial. These statistics must not be interpreted as rankings for actual telecom operators.

## 7. Recommended default rule to test in ICR-OPT

Do not impose one nationwide or circle-wide flat rate by default. Use a **capacity-aware two-part contract as the primary benchmark**, with other forms retained as testable alternatives:

1. **Fixed charge:** reimburse only attributable contract-enablement cost or explicitly contracted capacity reservation. Specify amortization horizon and refund rules.
2. **Off-peak usage:** measured GB (or separate voice/SMS units) priced against incremental forward-looking service cost.
3. **Peak capacity/usage:** an auditable marginal scarcity component or reserved-capacity fee where native-service QoS and spare headroom justify it, with no double counting.
4. **Bargaining division:** split the *remaining incremental surplus*, subject to every operator's participation and contract feasibility constraints. Do not present equal splitting as a unique or mandatory rule.
5. **Bilateral invoices, optional multilateral clearing:** itemize every guest-host direction, net the payable balances, and only then add any separately justified coalition-stability transfers. Merely zeroing reciprocal GB is not economic compensation.
6. **Risk and auditing:** define safe host admission, metering, quality remedies, monthly financial reconciliation, periodic cost rebenchmarking and permitted adjustment clauses.

The appropriate charging form can differ by pair. When traffic is low and truly idle capacity exists, pay-as-you-go may dominate a reservation contract. When a host must hold busy-hour capacity or make a costly investment, a capacity commitment and two-part fee can be more appropriate.

**Core test for policy:** If every participating operator is no worse off but a subset could leave and do substantially better, the arrangement may be unstable. ICR-OPT should compare pairwise bargaining with a *core-constrained multilateral settlement* before recommending an industry-wide arrangement.

## 8. Data required for a real tariff determination

- Guest-to-host realized or forecast traffic by service (GB, minute, SMS), geography and time-of-day.
- Safe residual host radio/backhaul capacity and incremental congestion/upgrading cost.
- Long-run incremental costs (and explicit treatment of common costs when justified) on the same service/time basis.
- Guest incremental benefit relative to independently estimated alternative hosts or network build-out.
- Integration costs, reserved-capacity terms, contract length and settlement administration.
- Acceptable cost of financial risk, technical reliability and verifiable QoS obligations.

Costs and demand must be independently audited or supplied as confidential ranges when public disclosure is impracticable. Cooperation should remain limited to justified wholesale cost and access data, with appropriate competition-law review and no exchange of unnecessary future retail-pricing strategy.

## Research files and reproducibility

A downloadable Python research package accompanies the present analysis. It contains the exact SciPy mixed-integer program, fixed seeds, generated case results, coalition feasibility tests and independent stochastic contract experiment. The repository's [settlement model](../models/settlement.js) provides a smaller, dependency-free four-operator fixed-flow calculator. The two programs cover related but **not identical** mathematical experiments.

The model is an exploratory decision-support framework. Empirical calibration and a competition/operational review are prerequisites for applying any proposed wholesale rate to a real agreement.
