# Findings from the initial ICR-OPT experiments

**Baseline: 8 October 2026.** All results below come from the simulator's reproducible synthetic presets. They are scenario outputs, not measured telecom outcomes, published tariffs, or forecasts for a particular Indian operator.

## 1. Reachability and carried traffic are different outcomes

The experiments distinguish:

- **Native area coverage:** the share of equal-sized grid cells where the home TSP has coverage.
- **T1 ICR-reachable area:** T1's own cells plus otherwise uncovered cells served by at least one *eligible* host footprint, before considering traffic capacity.
- **Aggregate traffic recovery:** the fraction of all four operators' originally uncovered traffic that can actually be admitted over six representative four-hour windows.

The second measure is a *potential coverage footprint*. It does not mean every subscriber can attach or obtain the requested quality of service.

| Preset | Cells | T1 native | T1 potentially reachable | Aggregate unmet traffic carried | Grid cells with no TSP |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sparse border | 384 | 40.1% | 96.1% | 47.6% | 15 |
| Exact 95/90/2 | 2,000 | 95.0% | 99.6% | 61.0% | 8 |
| Peak congestion | 450 | 48.0% | 96.9% | 11.5% | 14 |
| Complementary footprints | 416 | 38.0% | 79.1% | 36.5% | 87 |
| Remote blackspots | 400 | 24.0% | 68.8% | 25.4% | 125 |

In the sparse-border preset, approximately 90.3% of initial demand occurs in cells with at least one eligible host footprint, yet the model carries 47.6% of initial demand. This gap reveals the contribution of capacity and economic admission limits after physical coverage is accounted for.

## 2. The 95/90/2 case illustrates the correct coverage arithmetic

This preset is constructed with exact cell counts.

- There are 2,000 cells.
- T1 covers 1,900 and lacks coverage in 100.
- T2 covers 90 of T1's missing 100 cells.
- T3 covers two *different* cells in that missing set.
- T4 covers none of T1's missing cells.
- The union recovers 92 missing cells, leaving eight outside every network.

T1's potential area coverage increases from 95.0% to 99.6%. This is a **4.6 percentage-point** increase in area coverage, not a 92-percentage-point increase. The directional complementarity values of 90%, 2%, and 0% are percentages **of T1's uncovered area**, not the full geography.

In a general case, one cannot add pairwise complementarity values because the host footprints can overlap. The simulator uses the underlying cell incidence matrix to calculate each union.

## 3. Capacity protection materially changes the result

Holding the sparse-border geography and other assumptions fixed:

| Assumption | Share of aggregate unmet traffic carried |
| --- | ---: |
| Default reserve of 12% | 47.6% |
| Increase host capacity reserve to 30% | 26.2% |
| Increase host capacity reserve to 50% | 7.6% |
| Increase peak load pressure to 170% | 12.4% |
| Restrict roaming eligibility to the model's border strip | 20.4% |
| No ICR | 0.0% |

The geographic coverage itself does not change when capacity reserve rises. An unchanged coverage matrix can therefore produce radically different actual service results.

In the default sparse-border run, approximate recovery of aggregate unmet traffic is 89.3% in the 02:00 window but only 9.2% in the 18:00 window. For the peak-congestion preset, those values are 66.8% and 0.0%, respectively. These are different load assumptions over representative windows, not observations from real daily traffic.

The *no ICR* allocation yields zero recovered traffic. Even in that counterfactual, the coverage map can still report the host footprints that would become potentially reachable **if** sharing were enabled. That is a geographical diagnostic, not an assertion that service is active.

## 4. Operator incentives require separate accounting

The model values newly recovered traffic privately and subtracts the extra host operating and congestion cost. Wholesale payments then move money among operators but do **not** change the total private surplus from a fixed allocation.

Under the default sparse-border assumptions:

| Operator | Incremental posted-tariff gain, illustrative INR per representative day |
| --- | ---: |
| T1 | 216,345 |
| T2 | 77,438 |
| T3 | 72,217 |
| T4 | 34,405 |
| **Total** | **400,405** |

The values are rounded and use hypothetical traffic units, valuations and charges. They establish internal accounting consistency, not profitability claims about real TSPs.

At the same allocation, increasing the posted host tariff multiplier to 250% leaves the total private surplus essentially unchanged but redistributes the gains. Under *posted-price admission*, the same high tariff can instead lead to zero admitted ICR traffic because the configured wholesale prices exceed the guest's private benefit.

This suggests a substantive policy distinction:

1. A wholesale tariff can be **too high for guest operators**, despite there being spare technical capacity.
2. A tariff can be **too low for hosts**, even when the guest receives a positive benefit.
3. A cooperative financial settlement can redistribute a positive total surplus to support participation, although settlement feasibility, contracts and competition rules still require separate consideration.

The model offers indicative cost-recovery and bargaining corridors for active guest-host pairs. These are not empirically identified fair market prices.

## 5. A positive public value does not create private cash flow

To illustrate the role of public support, we reduced all operator private values per service unit to 0.2 and applied a public value of 12 in social-efficiency mode, while retaining the sparse-border capacity and cost assumptions.

The model admitted the same 47.6% of initial traffic because the social value outweighed hosting cost, but calculated **negative private surplus of approximately INR 332,915 per representative day**. The cooperative-settlement module consequently reported an equal theoretical external support requirement to keep participating operators whole.

Under the private-efficiency rule with the same low private values, the optimizer admitted no traffic, so there was no private loss requiring compensation.

This experiment demonstrates why the socially preferred ICR policy, the privately sustainable ICR policy, and a negotiated wholesale price need not coincide. The support figure is an internal planning benchmark, not a subsidy recommendation.

## 6. Physical blackspots remain after every commercial bargain

In the remote-blackspots preset, 125 of 400 cells have **no network presence from any of the four operators**. ICR among these operators cannot restore coverage there.

The economic question for these cells is not how to share existing capacity. It is whether an additional tower, small cell, site upgrade, backhaul investment or another connectivity mechanism is worth funding. A future version should optimize this infrastructure alternative jointly with ICR.

## 7. Implications for a permanent border-area ICR framework

The initial results support further examination of:

- **Standing eligibility with dynamic admission:** a roaming right can exist continuously while actual traffic depends on safe host spare capacity.
- **Directed and potentially asymmetric arrangements:** T1 using T2 does not imply T2 needs equal access to T1. Traffic and payments should remain directional.
- **QoS-protected sharing:** native load and safeguarded headroom must be explicit model inputs.
- **Separate network and contract decisions:** the service-maximizing routing rule and privately acceptable settlements should be evaluated separately.
- **Blackspot-aware investment:** persistent gaps with no host footprint need infrastructure planning rather than roaming tariffs.
- **Evidence-based tariffs:** host incremental cost, guest value, capacity scarcity, service mix and actual volumes must be calibrated before setting prices.

## 8. Limits and next research step

The key limitation is the independent grid-cell capacity assumption. Real towers serve multiple cells and share radio sectors, spectrum, backhaul and site resources. A grid cell is an accounting location, not necessarily a distinct capacity pool. The prototype also does not model individual voice/SMS/data QoS, signalling, mobility, inter-PLMN implementation, or the regulatory and security requirements of permanent roaming in border districts.

We will prioritize a **shared-site/sector capacity model**, measured busy-hour traffic, realistic attachment eligibility, and costed build-versus-roam counterfactuals. Only then can the tool support quantitative recommendations for identified border districts or actual operator agreements.

See [the model specification](./mathematical-model.md) for definitions, constraints and the literature foundation.

## Version 1.1 tariff sensitivity findings

The economic extension preserves the same synthetic geographical and traffic allocation while changing only the assumptions used to price it. In the sparse-border base case, daily private surplus is approximately INR 400,405 and all 24 active directed-pair period quotations have nonempty break-even intervals. Under peak scarcity, the same allocation yields roughly INR 125,340 of private surplus but six of 24 bilateral period quotations become infeasible. Higher fixed costs produce roughly INR 145,405 with 11 infeasible quotes. Strong guest alternatives produce a private shortfall of approximately INR 198,014 and no feasible bilateral period quote.

These results demonstrate that **positive total gains need not imply a commercially viable per-unit rate for each direction**. The detailed equations, price bounds and sensitivities appear in [the Version 1.1 tariff model](./tariff-model.md). All monetary figures remain synthetic.
