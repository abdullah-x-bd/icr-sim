# Data Acquisition Specification: Sikkim–China Border ICR Study

**First corridor: Deorali Bazar–Nathu La Pass (NH 310).**
**Objective: measure spatial complementarity and calibrate commercially viable peak/off-peak wholesale roaming rates.**

## 1. Who holds the required information

| Institution | Primary relevant information | Public source/contact |
| --- | --- | --- |
| TRAI Regional Office, Kolkata | Alignment or aggregation of the existing May 2026 four-operator drive test observations | Official TRAI/PIB release of 3 July 2026; adv.kolkata@trai.gov.in |
| Digital Bharat Nidhi / relevant DoT programme unit | Aggregated, deidentified figures from current funded ICR projects, available settlement structure, site-level scheme constraints | https://dbn.gov.in/en/faq; connect-usof-dot@gov.in |
| Operators carrying or considering roaming traffic | Actual spare capacity, incremental per-GB cost, integration charges and anonymized prospective demand | Operator network, finance and roaming-interconnection teams |
| Sikkim telecom coordination / district administration | Non-sensitive public visitor and route usage aggregates for calibrating corridor-level exposed subscriber-days | Official state or district published statistics; availability to be determined |

The requests should concern **Indian-network communications and aggregate research statistics**. Coordinates, sensitive tower inventories, defence operational details, subscriber identities and call-detail records are unnecessary for this economic model.

## 2. Priority 1: the missing 16-pattern cross-operator coverage table

Our existing observed TRAI data supply four marginal weak-signal sample percentages but not their simultaneous overlap. The requested output is a table of counts over aligned route sampling windows, with each operator represented by binary adequate signal (1) or poor signal (0) according to a clearly specified technology-appropriate threshold.

For four networks there are at most 2^4 = 16 patterns. A sufficient **aggregated** dataset would look like:

| Airtel adequate | BSNL adequate | Jio adequate | Vi adequate | Number of aligned observations |
| --- | --- | --- | --- | --- |
| 0 | 0 | 0 | 0 | requested |
| 0 | 0 | 0 | 1 | requested |
| ... | ... | ... | ... | ... |
| 1 | 1 | 1 | 1 | requested |

Keep the 16 rows aggregated for the entire permitted study corridor, or at most by coarse approved route segment/daypart. **Do not fabricate count values** if aligned data are unavailable.

Provide the sampling window, common denominator, phone/technology configuration, definition of service adequacy and missing-data handling. If the originally published operators were not synchronously measured, a newly aligned independent multi-SIM survey or approved aggregate follow-up is necessary. Matching aggregate marginal percentages after the fact is not a substitute.

This single table would let us compute directed coverage complementarity and all host-union possibilities **without statistical dependence assumptions**, given correctly aligned measurements.

## 3. Priority 2: aggregated roaming demand and capacity

Minimum desirable period is **30 days** with separate busy-hour and other traffic windows.

- Anonymized daily traffic requests potentially recoverable when the guest home network is unusable, expressed in actual **GB** and optionally eligible subscriber counts.
- By home TSP and participating host, the traffic carried or safely supportable under test conditions.
- Host spare-capacity ranges or percent utilisation bands, with definition of the service and relevant band/time.
- Observed attach success or service-availability rate where a technically eligible visited PLMN exists.
- Separate voice, SMS and packet data where technology and inter-PLMN compatibility differ.

The initial simulator needs only aggregate period totals and ranges. It does not require cell IDs, individual subscriber positions or raw signalling events.

## 4. Priority 3: wholesale economic parameters

Request either values or low/mid/high bounds for:

- Additional host network/bearer handling expenditure in **INR per incremental GB**.
- Peak capacity opportunity cost or a justified scenario for incremental upgrades needed under ICR.
- One-off integration, authentication, testing and settlement setup expenses, with contract duration for amortisation.
- Ongoing agreement administration and clearing costs.
- How actual or prospective settlement would be structured: per GB, reserved capacity, fixed fee, or hybrid.
- Guest incremental economics of avoided churn, retaining service availability or other benefits **net of next-best alternative**.

National ARPU or data revenue per GB cannot replace an operator's incremental cost or incremental private benefit. Do not present confidential costs as measured if only generic public filings are available.

## 5. Basic extraction format

Every fact must include **value, unit, date, geographic scope, operator or network pair, published source or custodian, status**, and aggregation method.

Use four status tags:
- OBSERVED: measured as defined at the relevant corridor/date.
- PUBLIC_PROXY: official national or service-area aggregate used with an explicit extrapolation.
- PARTNER_ESTIMATE: stakeholder-provided range with reported method and permission.
- SCENARIO_ASSUMPTION: editable placeholder without independent empirical verification.

Unknown values remain missing, rather than being filled with unjustified zeros.

## 6. Decision gate

The first commercially meaningful statement of a specific **INR/GB** ICR price requires, at minimum:

1. Recoverable traffic volume in GB for the guest and time period;
2. Eligible host presence where guest service is deficient;
3. Available host service capacity to carry that traffic;
4. Credible host incremental and opportunity costs;
5. Credible guest incremental economic benefit and fallback alternative;
6. Fixed contract cost and agreement duration.

Without those six classes of evidence, the appropriate output is a **conditional break-even rate frontier** and an explicitly stated range of possible economic outcomes.

## 7. Practical order of requests

First seek TRAI's aligned cross-operator signal adequacy counts from the existing NH 310 measurement work. If they are not available, request an appropriate aggregated follow-up data product.

In parallel, request DBN guidance on deidentified existing ICR traffic and settlement evidence and contact interested TSP interconnection/economic teams for low/central/high cost and spare-capacity bands.

Finally, seek non-sensitive corridor footfall and usage aggregates to reduce uncertainty in exposed subscriber-days; avoid claiming district subscriptions or national average traffic correspond directly to the highway sample.

The next corridor should be a separate North Sikkim / Mangan–Chungthang–Lachen/Lachung study, **only after a verified independent route dataset becomes available**. Do not extrapolate NH 310 signal statistics to all Sikkim borders.
