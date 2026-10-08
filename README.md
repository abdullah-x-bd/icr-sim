# ICR-OPT

**A geospatial and techno-economic simulator for intra-circle roaming in border and underserved regions.**

This repository develops a framework for examining whether permanent, capacity-aware intra-circle roaming (ICR) can improve mobile connectivity without compromising host-network performance or making participating telecom service providers worse off.

Our starting point is a practical coverage problem. A district can have four mobile operators with different network footprints, yet subscribers still lose service wherever their home network is absent. Rather than treating each network independently, we study how their existing infrastructure can be coordinated, when roaming should be admitted, and which commercial arrangements could make cooperation sustainable.

## Research questions

- Where does one operator cover the gaps in another operator's network?
- How much new area is physically reachable under bilateral or multilateral ICR?
- How much previously unserved traffic can actually be carried once peak load and protected capacity are accounted for?
- Which guest-to-host assignments maximize incremental private value or wider public benefit?
- What wholesale charges, transfers, or targeted support make an arrangement acceptable to the participating operators?
- Which blackspots remain unserved even after every feasible sharing arrangement?

The focus is on border and remote regions where persistent connectivity gaps merit analysis beyond disaster-only roaming.

## Run the simulator

Open **[ICR-OPT](./index.html)** in a modern browser. The application runs entirely client-side and works offline, without installation, external services, or API keys.

Select a preset, change the assumptions, and run the model. The app provides an editable directed coverage-complementarity matrix, grid-level coverage visualization, six representative four-hour traffic windows, operator capacity settings, bilateral roaming permissions, indicative wholesale tariff analysis, and settlement accounts. Current experiments can be exported as CSV or JSON.

The interface supports four allocation modes: no roaming, maximum private efficiency, public-interest efficiency, and posted-price admission.

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

## Validation

With Node.js installed, run `node tests/smoke.cjs` from the repository root. These checks cover the exact 95/90/2 geometry, demand and host-capacity limits, absence of self-roaming, wholesale accounting identities, price sensitivity, no-ICR routing and cooperative clearing balances.

## Scope

Version 1 is a **research and policy-planning prototype**. All coverage grids, traffic loads, unit valuations, operator shares, and wholesale tariffs are synthetic and editable. The model uses independent capacity pools per grid cell. A deployment model will need real site- and sector-level constraints, interference and signal data, common backhaul limitations, service-specific QoS, and actual operator traffic measurements.

The next development priority is replacing the per-cell capacity approximation with a sector-level network resource model, then comparing commercial ICR against targeted new towers and upgrades under a multi-year cost framework.

## Repository

- [`index.html`](./index.html) contains the self-contained interactive simulator.
- [`docs/mathematical-model.md`](./docs/mathematical-model.md) presents the detailed formulation and bibliography.
- [`docs/findings.md`](./docs/findings.md) records baseline results and their interpretation.

**Research direction:** ICR as a standing, capacity-aware connectivity mechanism for selected Indian border and underserved regions.
