# ICR-OPT Sikkim–China Border Pilot

**Version 1.2 | 8 October 2026 | Pilot corridor: NH 310, Deorali Bazar to Nathu La Pass**

## Research objective

Evaluate where a capacity-aware, permanent intra-circle roaming arrangement might improve service on high-altitude Sikkim border transport corridors, while being commercially attractive to both the home and visited operators.

Our first demonstration tests **BSNL as guest** and compares Airtel, Jio and Vodafone Idea as potential hosts. This is a modelling choice rather than a claim that BSNL is uniquely deficient or that each host has spare capacity. The methodology is intended to generalize to all directed guest-host pairs once paired measurements and commercial information become available.

The case is **not** a measured coverage map of North Sikkim or the entire India–China border. Nathu La is a concrete location on the Sikkim–China boundary with a recent public TRAI drive test. Mangan, Lachen and Lachung are potential subsequent study areas but are outside this tested highway dataset.

## 1. Observed evidence

TRAI conducted drive testing on 8–9 May 2026 and published the results on 3 July 2026. The highway portion was 66.5 km on NH 310, extending from Deorali Bazar towards Nathu La Pass. Reported automatic-selection voice-test signal samples were:

| Operator | Total observed samples | Samples below relevant signal threshold | Poor-signal sample rate | Average highway downlink, Mbps |
| --- | ---: | ---: | ---: | ---: |
| Airtel | 13,089 | 4,584 | 35.02% | 41.60 |
| BSNL | 14,797 | 6,087 | 41.14% | 6.68 |
| Jio | 8,802 | 1,711 | 19.44% | 60.26 |
| Vi | 7,563 | 3,597 | 47.56% | 13.79 |

Primary sources: [TRAI/PIB release](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2280639&lang=1&reg=3), [detailed annexure](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2026/jul/doc202673910301.pdf), [TRAI report directory](https://www.trai.gov.in/node/18240).

The counted **poor-signal** samples reflect technology-dependent thresholds in automatic-selection mode, not zero signal or guaranteed inability to carry service. These are operator-specific *marginal samples*, with **different sample denominators**. This means they cannot directly provide P(Jio good | BSNL poor), a four-way coverage union, or an observed ICR coverage-gain percentage. Neither the total highway length nor the sample counts define the population exposed to poor service throughout the year.

The CSV [data/sikkim_nathula_idt_2026.csv](../data/sikkim_nathula_idt_2026.csv) records original counts and source metadata. Counts, not rounded sample percentages, are used in the calibration engine.

## 2. Village-coverage context

The 2024 Lok Sabha reply reported 66 of 68 identified Sikkim border villages with mobile and 4G service as of May 2024. A July 2025 parliamentary response was reported as covering all 68 identified Sikkim border villages with mobile service. Separately, an August 2025 official release reported that, of 461 Sikkim villages in its RGI denominator, 453 had mobile connectivity and 442 had 4G connectivity as of June 2025.

Sources: [DoT parliamentary reply 2024](https://sansad.in/getFile/loksabhaquestions/annex/182/AS38_fSPeQO.pdf?source=pqals), [regional report of July 2025 parliamentary reply](https://www.sikkimexpress.com/news-details/all-68-identified-border-villages-of-sikkim-under-mobile-coverage), [PIB NER village coverage statement](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2158463&lang=1&reg=3). The source counts are stored in [data/sikkim_village_coverage_context.csv](../data/sikkim_village_coverage_context.csv).

Different denominators and dates must not be combined. Official village-level mobile coverage does not demonstrate continuous network availability along roads, valleys, or routes where people travel. It also does not identify which TSP serves each village.

**Hypothesis:** permanent capacity-aware ICR may improve operator-specific route continuity, but its magnitude is not yet observable from these public aggregate datasets.

## 3. Additional published market benchmark

The latest TRAI FY 2025-26 annual performance summary gives a national mean of **25.51 GB per wireless data subscriber per month**. This enters the pilot as an editable starting benchmark, **not** as a measured Nathu La user-demand quantity. It must not be equated with actual roaming demand.

The same report's ₹8.02 average realization per GB is a **retail revenue** statistic, not a host marginal cost, fair wholesale roaming rate, or guest incremental profit. We do not use it as the default tariff floor or ceiling.

Data source: [FY26 TRAI indicators](https://www.trai.gov.in/release-publication/reports/performance-indicators-reports); original record in [national market benchmark CSV](../data/india_public_benchmarks_2025_26.csv).

## 4. Geographical correlation problem

Let p_B equal BSNL's poor-signal sample fraction, and p_H a potential host's poor-signal fraction.

If both came from a **hypothetical common sampling distribution**, the share of BSNL-poor locations with good host signal would be bounded by

**lower = max(0, p_B - p_H) / p_B**

**upper = min(p_B, 1 - p_H) / p_B**.

An independence scenario has

**central = 1 - p_H**.

These are mathematical Fréchet-type dependence scenarios, not statistically calibrated confidence intervals. The actual TRAI data do not use verified paired route-time samples. The simulator therefore labels lower/independence/upper as **unobserved overlap assumptions** and never claims them as measured conditional coverage.

We further multiply potential host-acceptable locations by an explicitly assumed roaming-attach success factor; this is not inferred from download-speed averages.

## 5. Demand estimator

Our BSNL demonstration works with a user-set estimate of daily **subscriber-days present on the corridor**, not district subscriptions.

Define:

- N: BSNL-equivalent subscriber-days travelling or being present on the studied corridor per representative day, **assumed**;
- U: GB per active wireless data subscriber per month, national published benchmark unless locally measured;
- f: fraction of the user's daily usage attempted on the corridor, **assumed**;
- p_B: observed *marginal* poor-signal sample fraction from the highway test;
- q: fraction of usage associated with the weak-signal condition that is actually recoverable if a host becomes available, **assumed**.

Estimated candidate roaming volume per day is

**D = N × (U / 30) × f × p_B × q**.

This formula assumes representative monthly usage is spread uniformly across 30 days and treats sample-time frequency as a provisional proxy for traffic exposure. That is a **strong uncertainty**, so D must be displayed as scenario-estimated demand, never measured GB lost.

Split D into peak and off-peak assumed fractions. For host j, impose:

**x_jh ≤ D_h × conditional_coverage_j × attach_success**

**x_jh ≤ safe_spare_capacity_jh**.

For this version, select **at most one host per daypart**. Multiple simultaneous hosts in one daypart cannot be reliably assigned from operator marginal coverage alone because their geographical overlap has not been observed.

## 6. Endogenous agreement and tariff optimization

Enumerate four host choices per daypart: no host, Airtel, Jio or Vi. There are **16 combinations** of peak and off-peak choices, including no ICR. A host used across both periods pays its attributable agreement setup cost once per representative day.

For an active host and daypart, the incremental system margin per carried GB is

**guest_incremental_value - guest_alternative_value - host_variable_cost - host_capacity_opportunity_cost**.

Subtract the activated host and guest agreement fixed costs. The optimizer selects the highest-surplus candidate that admits a feasible nonnegative gain for both counterparties under its price-corridor rule. A no-agreement outcome always remains available, so the model never forces an economically negative bilateral agreement.

For pair j carrying total daily Q_j, the period h tariff bounds are

**Pmin_jh = variable_host_cost_jh + opportunity_cost_jh + host_fixed_cost_j / Q_j**

**Pmax_jh = incremental_guest_value - outside_option_value - guest_fixed_cost_j / Q_j**.

When Pmin ≤ Pmax, the illustrative price is

**Pstar = Pmin + host_bargaining_share × (Pmax - Pmin)**.

The reported guest gain and each host's incremental gain are positive or zero in selected scenarios, and the gains sum to total private surplus (within floating-point tolerance).

**Limits:** this is exact enumeration for a small two-daypart, single-guest, one-host-per-period economic decision problem, *not* a full mixed-integer, four-guest geospatial optimizer. Fixed agreement costs are daily-equivalent scenario inputs, not observed one-time contract invoices. Scarcity charges are assumed per GB. The economic test does not establish real spectrum-sharing eligibility, technical roaming arrangements or operational QoS performance.

## 7. Reproducible scenario results

Using only the **published marginal signal fractions and national average usage**, together with **hypothetical economic and passenger-exposure parameters**:

| Scenario | Estimated candidate roaming GB/day | Optimal off-peak host | Optimal peak host | Selected carried GB/day | Private surplus INR/day |
| --- | ---: | --- | --- | ---: | ---: |
| Conservative | ~71 | None | None | 0 | 0 |
| Central | ~354 | Airtel | Airtel | ~196 | ~162 |
| Optimistic | ~921 | Jio | Jio | ~470 | ~1,877 |

For the central scenario, under the specified assumptions, the illustrative Airtel wholesale quote is approximately **₹3.76 per GB off-peak** and **₹4.11 per GB peak**. These values are *not* observed, regulated or recommended tariff levels. Altering subscriber-days, cost assumptions, overlap dependence or guest economic benefits may change the host selection or eliminate the commercial case entirely.

A transparent **zero-surplus** result can be the correct recommendation when the model lacks private economic incentives.

## 8. What exact information would improve this study next?

### Priority A: paired spatial observations

Request an aligned, anonymized table of **route segment/time by network** reporting acceptable signal / attach availability for all participating Indian PLMNs, using synchronized or aligned measurements. If raw route data cannot be shared, a 16-cell four-operator **joint binary coverage-count table** is enough to calculate the four-way complementarity without disclosing individual handset histories.

Suggested columns: sampling window, anonymized route segment, BSNL acceptable (0/1), Airtel acceptable, Jio acceptable, Vi acceptable, number_of_aligned_observations, primary radio technology, threshold definition.

Public point of contact in the official TRAI press statement: **adv.kolkata@trai.gov.in**. Ask for a published or non-sensitive aggregated cross-operator overlap table and technology-specific counts, not restricted raw tower information.

### Priority B: observed demand volume

Obtain anonymized guest subscribers and projected roaming GB per peak/off-peak period for this corridor or a similar high-altitude Sikkim corridor. If sharing commercial data is difficult, publish low/central/high passenger exposures and explicit volume sensitivity instead.

### Priority C: incremental wholesale economics

Seek host cost ranges per GB, spare-capacity bands, attributable agreement integration costs, and guest incremental benefit relative to other alternatives. Any confidential values could be disclosed as rounded ranges, indexed relative costs, or anonymized partner distributions.

### Priority D: additional North Sikkim corridor

Once a separate data source exists for Mangan–Chungthang–Lachen/Lachung, add it as a distinct pilot rather than treating NH 310 as a measurement of that region. The border-region programme can then compare two distinct mountain corridors.

## 9. Files and reproduction

- [Sikkim interactive economic workbench](../sikkim.html) is a self-contained downloadable HTML application.
- [Source model](../sikkim-model.js) exposes the observed data, scenarios, conditional overlap assumptions and exact economic enumeration.
- [Original corridor measurement dataset](../data/sikkim_nathula_idt_2026.csv) contains untouched measured sample counts, average throughput and source metadata.
- [Village context evidence](../data/sikkim_village_coverage_context.csv) documents date-specific administrative statistics.
- [Sikkim regression test](../tests/sikkim.cjs) checks optimization, financial accounting, tariff feasibility, capacity and counterfactuals.
- [Original 1.1 tariff model](./tariff-model.md) remains available for the four-TSP synthetic grid simulation.

Run **node tests/sikkim.cjs** from the repository root with Node.js. No Python packages or external APIs are required for this pilot.

## 10. Follow-on development decision

Do **not** replace the missing overlap matrix with a false precise estimate. After collecting aligned coverage counts and actual guest traffic/host cost evidence, the next phase is four-operator **joint** coverage-and-economics optimization with a shared spatial demand grid, multiple hosts per period and explicit sector resource constraints.

The immediate publishable result of this version is a **conditional economic feasibility frontier**, not a claim of a measured coverage gain or actual market-clearing roaming price.
