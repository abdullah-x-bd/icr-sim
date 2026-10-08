# ICR-OPT 1.1: Economic Calibration and Wholesale Tariff Design

This extension prices an **already allocated**, capacity-feasible set of directed roaming flows. It adds opportunity costs, economic alternatives and attributable fixed costs to the Version 1 network calculation. Every result remains illustrative until source data are independently calibrated.

## Economic problem

For every active guest-home operator i, visited host j, and period h (peak or off-peak), we calculate the minimum host recovery tariff, the maximum tariff the guest can afford relative to its next-best alternative, a negotiated example within that interval, and the resulting operator-level gains.

A profitable four-party system does not necessarily support a viable bilateral tariff for every active direction. The model therefore reports both pairwise and cooperative-network feasibility.

## Inputs

- Q_ijh: traffic allocated to guest i on host j in period h, in **normalized simulator units per representative day**
- b_i: guest's original private benefit per unit from the coverage simulation
- a_i: guest's next-best-alternative value per unit; the relevant incremental value is b_i minus a_i
- C_ijh: incremental host operating and congestion cost attributed to the directed flow, using cell-level proportional cost allocation
- o_j: off-peak capacity opportunity cost per unit at host j
- m: additional peak premium on the opportunity cost, as a fraction
- FH_j and FG_i: daily fixed host and guest costs **per active directed pair**
- k: assumed GB represented by one normalized traffic unit; default k = 1
- alpha: fraction of positive bilateral surplus allocated to the host, default 0.5

Peak windows start at 10:00, 14:00 and 18:00. Other four-hour windows are off-peak. These labels are modelling assumptions rather than observed busy-hour classifications.

## Cost assignment

If Y_gjt is the total roaming flow hosted in cell g at time t and Phi_gjt(Y_gjt) is its incremental host cost, attribute that cost to each guest proportionally:

C_ijh = sum_over_g,t_in_h [w_t * Phi_gjt(Y_gjt) * x_gijt / Y_gjt], for Y_gjt > 0.

The scarcity cost O_ijh equals o_j * Q_ijh off-peak and o_j * (1 + m) * Q_ijh at peak.

When a pair is active in more than one period, daily fixed costs are allocated to each period in proportion to its share of the pair's total traffic. Thus each active pair incurs the fixed costs only once per representative day.

## Pricing formulas

With Q_ij = sum_h Q_ijh, the **host minimum tariff per normalized unit** is

Pmin_ijh = [C_ijh + O_ijh + FH_j * Q_ijh / Q_ij] / Q_ijh.

The **guest maximum tariff** is

Pmax_ijh = b_i - a_i - FG_i / Q_ij.

A bilateral corridor exists if Pmin_ijh <= Pmax_ijh. Under a positive corridor, the example negotiated tariff is

Pstar_ijh = Pmin_ijh + alpha * (Pmax_ijh - Pmin_ijh).

Divide Pmin, Pmax and Pstar by k to display rupees per **assumed** GB. Changing k alone cannot change private surplus. It simply changes the quotation units.

The quote transfers money between guest and host. It does not create collective private surplus.

## Operator payoffs

For an active directed pair, define its incremental private surplus:

S_ij = Q_ij * (b_i - a_i) - C_ij - O_ij - FH_j - FG_i.

The model sums pair surplus across all active directions to determine system private surplus.

With posted wholesale payments, the model deducts the opportunity, fixed and alternative costs when calculating each operator's adjusted gains.

With negotiated tariffs, the model calculates every operator's combined gain from paying as a guest and receiving payment as a host. It reports a complete negotiated outcome **only if all active peak and off-peak bilateral corridors are feasible**.

For each connected network-sharing coalition C, a pooled arrangement with freely transferable side payments can provide nonnegative incremental payoffs to every operator if its total private surplus S_C is nonnegative.

Where S_C is negative, the theoretical minimum external support for that component is max(0, -S_C). A weighted Nash division of the nonnegative pool is a settlement benchmark, not an automatically enforceable commercial agreement.

## Sensitivity presets

All four presets retain the same underlying *Sparse border* traffic allocation.

| Economic configuration | Daily private surplus | Feasible period-specific quotes | Minimum collective support |
| --- | ---: | ---: | ---: |
| Baseline assumptions | INR 400,405 | 24 / 24 | INR 0 |
| Peak scarcity | INR 125,340 | 18 / 24 | INR 0 |
| Fixed-cost pressure | INR 145,405 | 13 / 24 | INR 0 |
| Strong alternatives | INR -198,014 | 0 / 24 | INR 198,014 |

These are synthetic test values. They are not actual operator tariffs or measured costs.

A useful example occurs for T1 roaming on T2.

Under baseline assumptions, the off-peak host minimum is INR 2.11/assumed GB, guest maximum INR 4.50 and midpoint INR 3.31. The peak values are INR 2.35, INR 4.50 and INR 3.42.

Under peak-scarcity assumptions, the off-peak values become INR 3.22, INR 4.35 and INR 3.78. The peak host minimum rises to INR 5.10 while the guest maximum is INR 4.35, so that period has **no mutually feasible bilateral rate** for the fixed traffic allocation.

## Interpretation and methodological boundaries

1. The new economic parameters do **not yet feed back into the routing optimizer**. A pair that becomes uneconomic remains in the initially chosen fixed routing plan; it is flagged rather than automatically removed. Joint re-optimization of traffic assignment, fixed contract activation and tariffs is the next mathematical extension.
2. A next-best-alternative value is a per-operator assumed counterfactual. In real calibration it may vary by guest, host, period and geography.
3. Scarcity premiums approximate marginal capacity opportunity costs; they require measured utilization and capacity-upgrade evidence for realism.
4. Fixed integration costs are attributed once per active pair **per representative day**. Longer contracts should annualize or amortize costs in a consistent period.
5. Per-GB rates are meaningful only when normalized traffic is calibrated to actual GB and costs/benefits refer to that same traffic unit.
6. A positive aggregate private surplus does not by itself guarantee that every directed pair has a feasible wholesale rate. Component-level pooled transfers may provide an alternative if legally and commercially viable.
7. Uncertainty in costs, forecast roaming volumes and outside options should ultimately generate **ranges** and confidence assessments, not a falsely precise single price.

## Immediate data priorities

We will first obtain defensible ranges for incremental host data-handling costs, time-of-day spare capacity and its opportunity cost, expected roaming GB by directed operator pair, amortized integration charges, and guest incremental retention or contribution value.

For every empirical parameter, the next iteration should record the source, unit, observed period and uncertainty. This is the highest-value input improvement before expanding the physical network simulator.

The [full spatial and optimization methodology](./mathematical-model.md) documents the original Version 1 allocation engine. The [regression tests](../tests/pricing.cjs) verify pricing and settlement identities.
