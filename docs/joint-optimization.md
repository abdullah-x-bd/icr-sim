# ICR-OPT 1.3: Joint Agreements, Traffic and Coalition-Stable Roaming Charges

**Research status: synthetic, computationally implemented and regression-tested.**  
**8 October 2026 | Geographic scope: general four-TSP networks, not a border-specific estimate.**

## Research question

Given multiple operators with nonidentical coverage, different peak/off-peak network capacity, incremental service costs, guest benefits and fixed agreement activation expenses, can we:

1. Select the set of directed host–guest contracts that maximizes aggregate incremental private economic surplus?
2. Route only technically eligible traffic within protected host capacity?
3. Charge hosts' attributable incremental costs and allocate the remaining private gains so that **all operators** prefer participating?
4. Find payments that also prevent **any subgroup** from earning more by negotiating independently?
5. Express the resulting permitted directional invoices as auditable fixed-enable­ment plus peak and off-peak usage charges?

Version 1.3 answers these **within a synthetic, transferable-utility, complete-information four-operator model**. It does not establish actual Indian tariff levels.

## 1. Joint traffic and agreement activation

Our [reproducible SciPy model](../research/joint_optimizer.py) uses:

- I = 4 operators, G = 5 independent geographical demand areas, T = 2 representative load periods;
- c_gj in {0,1}, indicating a visited operator's synthetic service presence;
- d_git, incremental unmet home demand when its own network is absent;
- K_gjt, assumed protected safe spare host traffic capacity;
- b_i, home operator's incremental private economic benefit per recovered traffic unit;
- m_jtl, host marginal incremental resource cost in each period t and cost tier l;
- F_ij, incremental fixed setup cost for a directed agreement.

Variables:

- x_gijtl >= 0: carried guest demand, by geographical area, host, time and one of three marginal cost tiers;
- y_ij in {0,1}: whether the agreement allowing guest i on host j is activated.

The joint model maximizes

    sum_gijtl (b_i - m_jtl) x_gijtl - sum_ij F_ij y_ij.

Constraints require:

- x = 0 where guest i has native coverage, visited host j has no eligible service, or i = j;
- sum_jl x_gijtl <= d_git for every guest, geographical area and period;
- sum_i x_gijtl <= K_gjt/3 per host, geography, time and tier;
- sum_gtl x_gijtl <= M_ij y_ij to prohibit carrying traffic without an activated agreement;
- x >= 0 and y binary.

The formulation is a **mixed-integer linear program** solved with SciPy/HiGHS. Increasing marginal tier costs approximate scarcity and congestion. The code checks the solver's optimal status and the resulting accounting identity.

The current capacity model remains independent across geographical areas. Real radio sectors may share spectrum and backhaul; this benchmark does not yet establish engineering service guarantees.

## 2. Incremental operator payoffs

The fixed directed agreement cost F_ij is allocated 40% to its guest and 60% to its host in this illustrative benchmark. This split is not a pricing principle; it is an explicit, replaceable accounting assumption.

Before wholesale settlement, operator i has a gain a_i equal to:

    incremental private benefit of its newly served demand
    minus incremental cost of hosting guest demand
    minus the operator's allocated integration costs.

For a payment p_ij from guest i to visited host j,

    gain_i = a_i - sum_j p_ij + sum_k p_ki.

Across all operators, directional wholesale payments cancel, so total gains equal the privately optimal network-sharing surplus. Merely increasing per-GB charges does not increase that total surplus for an unchanged allocation.

Every operator's disagreement baseline is zero **incremental** payoff in the chosen coalition-free counterfactual. In practice, no-ICR, existing roaming and alternative infrastructure choices need explicit empirical valuation.

## 3. Coalition values and core feasibility

For each nonempty subset S of the four operators, the model resolves **the same MILP restricted to S**. Write its independently achievable optimum as v(S). There are 15 nonempty coalitions; 14 are proper nonempty subgroups of the grand coalition.

A proposed incremental gain vector pi is **coalition-stable** if

    sum_i pi_i = v(N)
    sum_{i in S} pi_i >= v(S)  for every nonempty proper subset S.

Singleton conditions imply individual rationality when v({i}) = 0.

We compare:

1. Equal division of v(N) among four operators, without respect to coalition claims.
2. Bilateral equal-surplus bargaining separately on each directed agreement.
3. An idealized **unrestricted-transfer core** that redistributes private surplus however necessary.
4. **Directed nonnegative invoice** settlement using only activated guest-to-host relationships.
5. **Bilateral-capped settlement** where each active directed payment is restricted to the pair's attributed host recovery floor and guest willingness-to-pay ceiling.
6. A separately labelled signed-credit benchmark that permits net credits along active directed pairs.

The primary settlement calculation is a two-stage LP:

- Minimize epsilon >= 0, the maximum deficit of any proper coalition relative to its independently achievable payoff.
- Holding the minimum epsilon fixed, minimize total absolute deviation from equal operator payoffs, subject to the same coalition claims and contract-payment constraints.

If epsilon is effectively zero and operator gains meet all coalition constraints, the chosen agreement and settlement are reported as stable. Otherwise report a **least-core shortfall**, not a win-win claim. The least-core epsilon is not automatically the subsidy required to implement an agreement.

### Bilateral invoice feasibility

For every selected directional flow i to j with quantity Q_ij, let C_ij be its allocated incremental host cost and F_ij the fixed activation expense. In this illustrative cost split:

    L_ij = C_ij + 0.6 F_ij
    U_ij = b_i Q_ij - 0.4 F_ij

The constrained settlement requires **L_ij <= p_ij <= U_ij** for every active pair. This is stronger than allowing arbitrary cross-operator money transfers, and preserves a plausible economic meaning for each total bilateral invoice.

We do not assume the bounds remain valid when volume and congestion costs respond strategically to the tariff. Dynamic demand, asymmetric information and retail competition are outside this benchmark.

## 4. From an aggregate payment to an actual charging basis

The core LP determines the **total amount p_ij paid across the simulated dayparts**. To express this as a two-part tariff without changing that payment:

    fixed enablement fee = 0.6 F_ij.

For each period t where Q_ijt > 0:

    unit_rate_ijt = (C_ijt / Q_ijt) + (p_ij - sum_t C_ijt - 0.6F_ij) / Q_ij,

where Q_ij = sum_t Q_ijt.

This attributes the host's different per-period incremental resource costs to the corresponding off-peak or peak volume. The negotiated margin is distributed evenly per carried unit.

The identity

    p_ij = fixed enablement fee + sum_t unit_rate_ijt * Q_ijt

is regression tested for every active agreement in the selected games. This is an **accounting decomposition**, not an empirical identification of peak price elasticity or a unique commercially negotiated price. It may be replaced by capacity reservation fees, service-specific charging or an explicitly defined risk-adjustment clause if warranted.

## 5. Results from 200 synthetic joint network games

Deterministic seeds **20000–20199**. For each independent network game, the optimizer first selects which contracts to activate and routes traffic to maximize private surplus. We then calculate all 15 coalition values and evaluate the competing settlement rules.

| Metric | Results |
| --- | ---: |
| Network cases tested | 200 |
| Games with positive optimal sharing | 199 |
| Equal division satisfying every coalition | 12 / 200 |
| Bilateral 50/50 split satisfying every coalition | 105 / 200 |
| Unrestricted-transfer core feasible | 200 / 200 |
| Nonnegative directed-payments core feasible | 200 / 200 |
| Strict bilateral cost-floor / benefit-ceiling core feasible | 200 / 200 |

**These are conditional frequencies from one synthetic instance generator, not statistical predictions of what real TSPs will accept.** Core feasibility is not guaranteed in arbitrary cooperative games, and the tests explicitly include an empty-core counterexample. The 200-case result supports computational consistency under the particular instance distribution, nothing more.

Unlike a static settlement comparison, this experiment **jointly optimizes the directed agreement activations and traffic volumes before calculating the settlement**. Costs therefore influence whether a contract is selected.

### Economic sensitivity on the same 200 seeds

| Model assumption | Mean private surplus (synthetic money units) | Mean active directed contracts | Mean carried traffic units |
| --- | ---: | ---: | ---: |
| Baseline | 1,442.80 | 3.73 | 520.87 |
| Directed setup costs doubled | 992.23 | 2.52 | 417.43 |
| Host incremental cost +1/unit | 956.01 | 3.08 | 443.12 |
| Safe roaming capacity reduced by half | 779.69 | 3.04 | 305.82 |
| Peak incremental scarcity surcharge doubled | 1,082.33 | 3.37 | 442.95 |

These differences demonstrate why an efficient routing and agreement selection engine should *respond* to economics, not merely apply a post-hoc tariff to a fixed allocation.

## 6. Reproduction

From the repository root, install Python 3.11+ with NumPy and SciPy.

    python -m pip install -r research/requirements.txt
    python -m unittest discover -s tests -p 'test_*.py' -v
    python research/joint_optimizer.py --seeds 200 --start 20000 --output research/joint_results.json

The last command generates a complete machine-readable record for all cases, including agreement activation, accepted traffic, the complete coalition-value function, payoff allocations, actual aggregate invoices and fixed/period-rate decompositions. The JSON is generated locally by the research program rather than checking a megabyte of synthetic intermediate results into GitHub.

Explore 24 solved instances without installing Python using the standalone [coalition stability laboratory](../joint-settlements.html). The browser demonstration tests user-entered payoff vectors against precomputed coalition values. **Editing the payout allocation in the browser does not rerun the underlying MILP, and it does not guarantee that a custom allocation can be invoiced using the active contracts.** Only the precomputed core-invoice option has been tested for payment implementability.

An independent [four-operator fixed-flow settlement model](../models/settlement.js) remains in the repo for simpler charging comparisons.

## 7. Scope and limitations

- Monetary figures and traffic quantities are **synthetic**, not Indian operator tariffs, subscriber measurements or field-ready cost estimates.
- The model has only five abstract service areas and two time periods. The regulatory, spectrum, physical site, radio-sector, backhaul and technology compatibility requirements of real roaming are not established here.
- The game's characteristic-function values assume that when a coalition forms independently, its behaviour does not change the payoffs of outsiders beyond removal of access to their infrastructure; actual strategic competitive externalities require a different model.
- Coalition information and true economic benefits are assumed commonly known, though operators may have private cost information and strategic incentives not to disclose it.
- The model's host-cost tiers are piecewise linear and can represent resource scarcity, but they do not establish busy-hour QoS performance. All cost shares and tariff bounds must be independently calibrated.
- A stable coalition payoff alone cannot authorize a regulated telecom arrangement; legal, competition, privacy and operational review remain necessary.
- Robustness to variable future demand, actual asset reservation and performance-based adjustment clauses must be tested before an operational settlement recommendation.

## 8. Immediate empirical upgrade

The next version should use actual anonymous home-to-host traffic demand, host spare capacity, incremental per-GB economic cost and attributable integration costs. It should estimate an operator's recovered-service economic benefit relative to credible alternatives and use the same unit and contract period throughout.

Only after those costs and benefits are observed or defensibly bounded should the solver report a candidate wholesale INR/GB range for real operator negotiation.
