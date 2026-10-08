# ICR-OPT 1.2: Evidence Acquisition and Economic Optimization Plan

## Sikkim-first implementation completed (8 October 2026)

The initial empirically anchored study is now the **Deorali Bazar–Nathu La Pass highway on the Sikkim–China border**. We have loaded TRAI's May 2026 operator-specific signal-quality measurements and official FY 2025–26 national subscriber-usage benchmark. The pilot uses observed marginal data together with explicitly labelled scenarios for cross-operator overlap, daily subscriber exposure, actual recovery of weak-signal traffic, available spare host capacity and commercial economics.

The [standalone workbench](../sikkim.html), [case methodology](./sikkim-pilot.md), [data acquisition specification](./sikkim-data-acquisition.md) and [Sikkim validation tests](../tests/sikkim.cjs) are available. The pilot has an exact small-scale contract selection model for BSNL as guest with one host per daypart. It is deliberately **not** presented as the final general four-operator MILP described later in this plan.

Before making empirical tariff claims, the outstanding requirements are aligned multi-operator coverage observations, actual candidate roaming GB, safely usable host capacity, incremental host cost and guest economic values. The next calibration decision is whether these can be obtained from TRAI, DBN or participating TSPs as aggregated statistics.



**Prepared 8 October 2026**

## Objective

Build a calibrated economic model of permanent intra-circle roaming in border regions. Retain the present coverage and capacity approximation for now. Replace arbitrary demand and cost assumptions with sourced values or defensible bounds, then allow those economic inputs to determine whether roaming agreements should be activated and where traffic should be routed.

Version 1.1 prices a technically allocated set of traffic after optimization. It does not recompute allocation when integration costs, capacity scarcity or guest alternatives make a roaming agreement uneconomic. Correcting that limitation is the mathematical priority.

## Evidence we can access now

| Parameter | Source and acquisition | Modelling application | Limitation |
| --- | --- | --- | --- |
| Average data usage, India | [TRAI FY 2025-26 performance](https://www.trai.gov.in/release-publication/reports/performance-indicators-reports) and [PIB summary](https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=2319321&lang=1&reg=3) | Starting scale for monthly demand: 25.51 GB per data subscriber | National mean; not observed uncovered-area demand |
| Revenue realization | Same TRAI/PIB report, INR 8.02 per GB | Retail revenue context and crosscheck | **Not** marginal host cost, wholesale tariff, or guest incremental benefit |
| Monthly wireless ARPU | Same TRAI/PIB report, INR 180.73 | Revenue and user-value sensitivity context | Not recovered-service contribution margin |
| Operator usage comparisons | [RIL FY26 Digital Services](https://www.ril.com/ar2025-26/digital-services.html), [Airtel annual reports](https://www.airtel.in/about-bharti/equity/results/annual-results) | Operator heterogeneity | Operator metric denominators may differ from national TRAI measures; Jio reports 42.3 GB per capita in Q4 FY26 |
| Operator service-area shares | [TRAI monthly subscriptions](https://www.trai.gov.in/release-publication/reports/telecom-subscriptions-reports), through August 2026 | Distribution of simulated subscribers across TSPs in selected circle | Circle data cannot identify district or specific uncovered-grid subscriber shares |
| GR, AGR and statutory charges | [TRAI quarterly financial statements](https://www.trai.gov.in/release-publication/reports/financial-reports), through June 2026 | Aggregate financial crosschecks | GR/AGR do not reveal incremental per-GB host cost |
| Border-area measurement | [TRAI independent drive-test archive](https://www.trai.gov.in/release-publication/qos-reports/idt-reports), Fazilka August 2026 report released 8 October | Later external validation of coverage and QoS observations | Sampled city and route, not whole district and not peak spare capacity |
| Existing ICR programme | [DBN FAQs](https://dbn.gov.in/en/faq) | Investigate operational ICR benchmark and request aggregated data | Public material does not disclose all host/guest wholesale charges |
| Operator coverage | [TRAI coverage portal](https://trai.gov.in/consumer-info/mobile-coverage-map/service-providers) | Future calibration of directed coverage matrix | Consumer display, machine-readable bulk export availability unverified |

Public source records are frozen in [data/india_public_benchmarks_2025_26.csv](../data/india_public_benchmarks_2025_26.csv) with units, reference URLs and restrictions on interpretation.

## Information still needed from operators or DBN

No currently verified public dataset supplies all five inputs at specific border-region, guest-host and time-window resolution.

1. **Carried or recoverable roaming GB:** Total eligible roaming subscribers and aggregate GB for each guest-host pair by daypart and service.
2. **Incremental host cost:** Operating and backhaul cost per additional GB, excluding costs that do not change with roaming; include scarcity or upgrade thresholds.
3. **Host spare capacity:** Aggregated peak and off-peak residual capacity bands in the actual areas where another TSP has gaps.
4. **Guest economic value:** Avoided churn or incremental contribution margin from restored service, compared against its best feasible alternative.
5. **Agreement fixed costs:** Integration, testing, routing, authentication, administration and settlement costs; expected duration and amortisation.

### How to request them

A neutral, institutional research request should first seek a **single anonymised border-region case, 30 days of aggregated observations, and no subscriber-level records**. Ask for parameters as ranges where exact commercial numbers cannot be disclosed. Prefer anonymised roaming count and traffic by direction, peak and off-peak utilization bands, and the wholesale settlement *structure*, with exact tariff rates requested only where voluntarily shareable.

The DBN FAQ lists **connect-usof-dot@gov.in** as contact. The 5 October 2026 TRAI/PIB annual performance release lists **advfea1@trai.gov.in** for Financial & Economic Analysis. These are routes for seeking guidance and public or shareable aggregate statistics; actual incremental network costs and contractual prices would most naturally come from participating operators. Do not assume the authority can disclose confidential partner data.

If there is no access to confidential inputs, the model will publish sensitivity bounds and a tariff *feasibility frontier*, not a specific real-world recommended rate.

## Demand-model correction

Grid **area** coverage is not uncovered subscriber population or lost traffic. We must infer eligible roaming demand from a consistent traffic-volume unit.

For each home operator i, grid g and time category h, estimate

**D(g,i,h) = N(g,i) × u(i,h) × e(g,i,h) × r(g,i,h)**

where:

- N(g,i) is estimated home-subscriber count or subscriber equivalents within geographic cell g;
- u(i,h) is baseline expected GB per subscriber during the particular duration of time category h;
- e(g,i,h) is the fraction of that period where own service is genuinely unavailable;
- r(g,i,h) is the recoverable fraction of otherwise unserved traffic if a partner becomes available.

The period usage u must already account for duration; do not multiply the period weight again. Make every estimate auditable with source, unit, date and uncertainty range. National 25.51 GB/month provides only an initial sanity anchor, not the actual local usage value.

The **guest incremental value** is NOT automatically the average ₹8.02 retail realization per GB or monthly ARPU divided by data volume. Estimate benefit from retained contribution margin, truly incremental usage where monetized, avoided loss of customers and net value relative to switching networks or new deployment. Model any competitive cannibalisation separately.

## Core mathematical upgrade

Let x(g,i,j,h) be carried calibrated GB, and y(i,j) a binary decision activating a contract for guest i on host j.

Maximize total *incremental private* value:

**sum of (guest value minus alternative value) × x
minus actual host variable/congestion and opportunity costs
minus amortised guest and host agreement costs × y.**

Constraints must include physical/contractual coverage eligibility, aggregate demand limits, protected host spare capacity, and **x <= M × y** so that no flow can use a contract that was not activated.

Use a mixed-integer linear model with piecewise-linear host costs and explicit fixed contract costs, comparing its output with Version 1.1. Traffic should disappear or switch to other eligible hosts if a pair has a cost disadvantage, subject to feasible alternatives.

After selection, price the *chosen* flows separately:

**host minimum ₹/GB = (incremental hosting cost + opportunity cost + allocated fixed host cost) / carried GB.**

**guest maximum ₹/GB = (guest incremental value over next-best alternative minus allocated guest fixed cost) / carried GB.**

Every candidate pair/time window must be checked for a nonempty price corridor. For overlapping pair agreements, independently feasible corridors do not suffice: require each operator's total net gain to be nonnegative after **all** directional receipts and payments. Analyze separate cases for strict bilateral tariffs, multilateral pooled settlement and public support.

The chosen bargaining rule determines a proposed division of surplus **within feasible bounds**. This is an optimization or negotiation benchmark, not automatically an observed or regulated wholesale price.

## Reproducible data schema

An input row should minimally contain:

- region_id; scenario_id; period_name; hours_represented; guest_tsp; host_tsp;
- own_coverage_absent; host_coverage_present; subscribers_exposed;
- recoverable_GB_low/base/high; safe_spare_GB_low/base/high;
- host_incremental_cost_INR_per_GB_low/base/high;
- host_opportunity_cost_INR_per_GB_low/base/high;
- guest_incremental_benefit_INR_per_GB_low/base/high;
- host_fixed_cost_INR; guest_fixed_cost_INR; contract_duration_days;
- source_url_or_reference; source_date; geographic_resolution; parameter_status; confidence.

Permitted parameter_status labels: OBSERVED, PUBLIC_PROXY, PARTNER_ESTIMATE and SCENARIO_ASSUMPTION.

Reject mixed units, invalid probability ranges, duplicate rows, negative volumes and entries lacking source status. Keep published raw data separate from inferred model inputs.

## Implementation sequence

| Stage | Estimated development time | Action | Acceptance criterion |
| --- | --- | --- | --- |
| A. Evidence registry | Day 1 | Store selected FY26 sources and definitions; identify unavailable operator data | All benchmark numbers trace to source and include correct units and denominators |
| B. Demand calibration | Days 2–3 | Replace arbitrary per-cell traffic equivalents with explicit candidate GB volumes and low/base/high scenarios | No unexplained conversion from simulated unit to GB; coverage and population are distinct |
| C. Economic routing | Days 4–6 | Add contract activation, fixed costs, opportunity costs and economically-aware traffic rerouting | Raising host costs can switch traffic or deactivate a pair |
| D. Pricing and participation | Days 7–8 | Calculate peak/off-peak rate corridors and per-operator gain constraints | No “win-win” label unless every relevant participation constraint is satisfied |
| E. Validation/report | Days 9–10 | Compare v1.1 with v1.2, backtest synthetic known cases, report source quality and sensitivity | Output reproducible tariff intervals, not unqualified national real rates |

These are development time estimates; actual operator data access depends on cooperation and may take substantially longer.

## Questions the new model must answer

- What is the minimum viable roaming volume for each bilateral agreement?
- How much does a peak-time opportunity cost raise the host tariff floor?
- Can the guest choose a cheaper alternative host without harming total QoS?
- How much incremental traffic is refused because the economically feasible tariff corridor is empty?
- Can a multilateral settlement make all participants whole when individual bilateral price corridors fail?
- How wide are tariff uncertainty bands with only public benchmark inputs, and which additional operator datum would reduce uncertainty the most?

## Scope discipline

Do not add real tower locations, propagation modelling, individual subscriber data, inter-PLMN protocol simulation or tower build decisions during this milestone. Those are subsequent engineering and policy stages after economic feasibility is calibrated.
