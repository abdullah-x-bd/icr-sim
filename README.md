# ICR-OPT

**A geospatial and techno-economic simulator for intra-circle roaming in border and underserved regions.**

This repository develops a framework for examining whether permanent, capacity-aware intra-circle roaming (ICR) can improve mobile connectivity without compromising host-network performance or making participating telecom service providers worse off.

Our starting point is a practical coverage problem. A district can have four mobile operators with different network footprints, yet subscribers still lose service wherever their home network is absent. Rather than treating each network independently, we study how their existing infrastructure can be coordinated, when roaming should be admitted, and which commercial arrangements could make cooperation sustainable.

## Joint agreement optimization and coalition-stable settlements

Our [joint optimization research model](./research/joint_optimizer.py) simultaneously selects directed ICR agreements and allocates traffic using a mixed-integer program. It then recomputes the optimal sharing surplus for every possible subgroup of four operators and tests whether a proposed division of gains would motivate any subgroup to exit.

The [coalition-stability laboratory](./joint-settlements.html) lets us explore 24 solved synthetic network games in a browser, compare equal division with bilateral bargaining and core-constrained settlement, and adjust operator gains to test stability. The precomputed, core-constrained invoices include attributable fixed enablement fees and cost-reflective peak/off-peak usage rates. Browser changes to gains are diagnostics, not fresh network optimizations.

A 200-case synthetic benchmark found **12/200** equal divisions stable, **105/200** bilateral 50/50 allocations stable and **200/200** core-constrained allocations feasible under the model's explicit bilateral cost-floor and value-ceiling bounds. This **does not** establish a universal existence theorem or measured operator benefits. The complete equations, experiment assumptions, sensitivity results and limitations are in the [joint optimization research note](./docs/joint-optimization.md).

## ICR charging and multilateral settlement research

The [charging and settlement design study](./docs/settlement-design.md) separates cost accounting, contract charging basis and inter-operator clearing. It develops incremental-cost bounds, two-part and capacity-based contract options, bilateral bargaining, reciprocal netting and coalition-stable multilateral payoffs.

The methodology includes a synthetic four-operator mixed-integer simulation of 420 network instances, coalition-value recomputation in 24 cases, and 100,000 one-pair stochastic contract stresses. These experiments are **illustrative**, not estimates of actual ICR tariff outcomes. A companion [fixed-flow four-operator settlement model](./models/settlement.js) implements transparent accounting, price corridors and coalition checks, with [tests](./tests/settlement.cjs).

The primary economic policy question is whether an incremental-cost-based charge with transparent fixed costs, measured resource usage and justified peak capacity compensation can give all operators a positive incremental gain, while leaving no subgroup with a stronger standalone alternative.

## Research questions

- Where does one operator cover the gaps in another operator's network?
- How much new area is physically reachable under bilateral or multilateral ICR?
- How much previously unserved traffic can actually be carried once peak load and protected capacity are accounted for?
- Which guest-to-host assignments maximize incremental private value or wider public benefit?
- What wholesale charges, transfers, or targeted support make an arrangement acceptable to the participating operators?
- Which blackspots remain unserved even after every feasible sharing arrangement?

The focus is on border and remote regions where persistent connectivity gaps merit analysis beyond disaster-only roaming.

## Priority case study: Sikkim–China border, Nathu La highway

We have made the **Deorali Bazar–Nathu La Pass (NH 310)** corridor our first evidence-grounded border case, using TRAI's May 2026 independent drive test. The published poor-signal sample fractions are **35.02% Airtel, 41.14% BSNL, 19.44% Jio and 47.56% Vi** on the highway test, each with its own sample count. These are not operator-specific no-coverage measurements, and they do not reveal aligned cross-operator coverage overlap.

Our new **[Sikkim economic workbench](./sikkim.html)** combines these observed marginal signal data with the official FY 2025–26 national average of 25.51 GB per wireless data subscriber per month. It leaves subscriber exposure, cross-operator overlap, ability to attach, host capacity, roaming costs and incremental guest value as **explicitly assumed, editable quantities**.

The Sikkim pilot performs a small exact economic search among no ICR, Airtel, Jio and Vi as potential BSNL host networks for peak and off-peak periods. It can decline uneconomic agreements and calculate bilateral cost-recovery and guest-acceptable rate ranges. Because aligned multi-TSP signal observations are absent, it limits each time period to **at most one host**. No quoted rate is presented as an actual Indian wholesale roaming tariff.

See the [Sikkim pilot evidence and methodology](./docs/sikkim-pilot.md) and [TRAI corridor measurements](./data/sikkim_nathula_idt_2026.csv). The underlying model is [sikkim-model.js](./sikkim-model.js), with a self-contained interactive HTML version.

**Research distinction:** Sikkim's administratively counted village mobile coverage is substantial, but this does not establish continuous quality or connectivity along particular mountain roads. We are testing economic conditions for improving route continuity, not asserting that every border village has no service.

## Run the simulator

Open **[ICR-OPT](./index.html)** in a modern browser. The application runs entirely client-side and works offline, without installation, external services, or API keys.

Select a preset, change the assumptions, and run the model. The app provides an editable directed coverage-complementarity matrix, grid-level coverage visualization, six representative four-hour traffic windows, operator capacity settings, bilateral roaming permissions, indicative wholesale tariff analysis, and settlement accounts. Current experiments can be exported as CSV or JSON.

The interface supports four allocation modes: no roaming, maximum private efficiency, public-interest efficiency, and posted-price admission.

## Economic calibration and tariff pricing (Version 1.1)

The **Economics & settlements** tab includes an editable pricing calculator for every active directed guest-host link.

We calculate separately for peak and off-peak periods:

- The host's minimum economically viable rate, including operating cost, scarcity/opportunity cost and attributable fixed integration cost.
- The guest's maximum viable rate, after accounting for the value of its next-best available alternative and attributable fixed costs.
- An illustrative negotiated rate within the feasible interval, using an adjustable host share of bilateral surplus.
- Adjusted daily gains for each operator, whether every bilateral quote is feasible, and the feasibility of pooled multilateral transfers.

The sensitivity buttons provide four **synthetic** calibration starting points: baseline assumptions, peak scarcity, fixed-cost pressure and strong alternatives. You can edit the assumptions for each operator and adjust the assumed GB equivalent represented by one simulator traffic unit.

The current calculator evaluates the **already assigned traffic** from the original optimization engine. Changing its new economic parameters changes the rate evaluation, not the radio allocation or traffic quantities. This intentionally separates initial tariff discovery from the next stage of jointly optimizing routing, contract choices and prices.

For formulas, scope and calibrated input requirements, read [Economic calibration and tariff design](./docs/tariff-model.md).

## Preset cases

| Case | Starting question |
| --- | --- |
| Sparse border | What if T1 has around 40% native coverage but can use other networks? |
| Exact 95/90/2 | How should we interpret directed gap coverage without double-counting? |
| Peak congestion | What happens when hosts have little spare capacity at busy hours? |
| Complementary footprints | How valuable is reciprocity when coverage areas differ? |
| Remote blackspots | Which places require new infrastructure because no existing network serves them? |

## Initial findings

These are outputs of **synthetic, illustrative scenarios**, not field measurements or estimates of actual BSNL, Airtel, Jio, or other operator performance.

| Preset | T1 native area coverage | T1 area reachable with eligible ICR | Share of all operators' previously unserved traffic carried |
| --- | ---: | ---: | ---: |
| Sparse border | 40.1% | 96.1% | 47.6% |
| Exact 95/90/2 | 95.0% | 99.6% | 61.0% |
| Peak congestion | 48.0% | 96.9% | 11.5% |
| Complementary footprints | 38.0% | 79.1% | 36.5% |
| Remote blackspots | 24.0% | 68.8% | 25.4% |

The coverage columns are **area metrics for T1**. The traffic column concerns **aggregate unmet demand across all four operators over a representative day**. They have different denominators and must not be treated as directly equivalent.

Three conclusions emerge:

1. Coverage complementarity is valuable but does not guarantee service. In the sparse-border preset, the other networks make much of T1's uncovered area reachable, yet capacity and economics limit the traffic actually carried.
2. Busy-hour spare capacity can be a stronger constraint than geographic reach. In the peak-congestion preset, only 11.5% of aggregate unmet traffic is carried over the day, despite 96.9% physical reachability for T1.
3. No form of roaming can cover a cell where every participating network is absent. The remaining blackspots need a separate infrastructure, upgrade, or subsidy decision.

In the exact 95/90/2 experiment, T1 covers 1,900 of 2,000 equal-area cells. Within its 100 missing cells, T2 covers 90, T3 covers two distinct cells, T4 covers none, and eight remain unreachable. This is a controlled geometrical case, not an empirical observation.

The simulator also separates the *total private surplus created by sharing* from the *posted-tariff gains of individual operators*. It calculates a cooperative settlement benchmark and a theoretical private-surplus subsidy requirement when applicable. The nominal rupee figures are scenario parameters and must not be interpreted as measured costs, regulated tariffs, or commercially recommended prices.

A fuller interpretation is in [Findings](./docs/findings.md).

## Mathematical approach

The model combines:

1. Binary grid-level operator coverage and a directional, conditional gap-complementarity matrix.
2. Time-dependent roaming demand and residual host capacity after native traffic and QoS headroom.
3. A minimum-cost-flow allocation with four marginal congestion-cost segments.
4. Separate inter-operator payments, hosting costs, and private service benefits.
5. Cooperative bargaining and individual-rationality constraints.

The technical definitions, equations, assumptions, source literature, validation criteria, and extension plan are documented in [Mathematical model and methodology](./docs/mathematical-model.md).

## Next development milestone: ICR-OPT 1.2

The next milestone is **data-calibrated, economically aware agreement selection**. We will retain the existing coverage simulator while improving the units and provenance of demand, host costs and guest benefits. The optimizer will then decide which directed roaming agreements and traffic flows remain privately viable once integration costs, peak-hour opportunity costs and realistic outside options are included.

The [Version 1.2 execution plan](./docs/implementation-plan-v1.2.md) specifies verified Indian public sources, the confidential-data request, parameter schema, mathematical changes and testable acceptance criteria. The [initial Indian telecom benchmark CSV](./data/india_public_benchmarks_2025_26.csv) preserves FY 2025-26 observed usage and revenue benchmarks with their limitations.

## Validation

With Node.js installed, run `node tests/smoke.cjs`, `node tests/pricing.cjs`, `node tests/sikkim.cjs`, `node tests/settlement.cjs`, and `python -m unittest discover -s tests -p 'test_*.py' -v` from the repository root. These checks cover the exact 95/90/2 geometry, demand and host-capacity limits, absence of self-roaming, wholesale accounting identities, price sensitivity, no-ICR routing and cooperative clearing balances.

## Scope

Version 1.1 is a **research and policy-planning prototype**. All coverage grids, traffic loads, unit valuations, operator shares, and wholesale tariffs are synthetic and editable. The model uses independent capacity pools per grid cell. A deployment model will need real site- and sector-level constraints, interference and signal data, common backhaul limitations, service-specific QoS, and actual operator traffic measurements.

Our immediate development priority is economic data calibration: incremental host traffic costs, busy-hour opportunity costs, realistic roaming volumes, fixed agreement costs and defensible guest benefits. After these are grounded, we can jointly re-optimize traffic allocations and contract pricing. Sector-level network engineering and infrastructure investment comparison are subsequent extensions.

## Repository

- [`index.html`](./index.html) contains the original four-TSP grid simulator.
- [`sikkim.html`](./sikkim.html) contains the self-contained Sikkim-China border economic calibration workbench.
- [`sikkim-model.js`](./sikkim-model.js) contains its source economic optimization engine.
- [`docs/sikkim-pilot.md`](./docs/sikkim-pilot.md) records the official Sikkim measurements, assumptions, equations, and next evidence request.
- [`docs/mathematical-model.md`](./docs/mathematical-model.md) presents the detailed formulation and bibliography.
- [`docs/findings.md`](./docs/findings.md) records baseline results and their interpretation.
- [`docs/tariff-model.md`](./docs/tariff-model.md) explains the Version 1.1 pricing mathematics, assumptions and sensitivity cases.
- [`docs/settlement-design.md`](./docs/settlement-design.md) develops bilateral, reciprocal and multilateral charging and settlement criteria.
- [`models/settlement.js`](./models/settlement.js) implements a fixed-flow four-operator settlement comparator.
- [`joint-settlements.html`](./joint-settlements.html) is an interactive core-stability laboratory.
- [`research/joint_optimizer.py`](./research/joint_optimizer.py) jointly optimizes agreements, traffic and implementable coalition settlements.
- [`docs/joint-optimization.md`](./docs/joint-optimization.md) documents methods, results and limitations.
- [`docs/implementation-plan-v1.2.md`](./docs/implementation-plan-v1.2.md) specifies the economic data acquisition and next optimization milestone.
- [`data/india_public_benchmarks_2025_26.csv`](./data/india_public_benchmarks_2025_26.csv) records sourced FY 2025-26 public market benchmarks.
- [`tests/smoke.cjs`](./tests/smoke.cjs) provides reproducible checks of the original model invariants.
- [`tests/pricing.cjs`](./tests/pricing.cjs) checks rate bounds, accounting, alternative values, economic sensitivity and cooperative clearing.

**Research direction:** ICR as a standing, capacity-aware connectivity mechanism for selected Indian border and underserved regions.
