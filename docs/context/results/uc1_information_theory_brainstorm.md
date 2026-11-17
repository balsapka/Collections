# UC1 signals and information theory: brainstorm

Brainstorm, 2026-11-17. Ideas only: nothing here is decided, built or measured. Question: how could
information theory help with UC1 signals (any number of transcripts per customer, a time series of
them, signals extracted from each), and with their integration beside the persona axes?

Fixed context: A1–A4 are not touched; UC1 outputs are taken as they are (the UC1 team owns
extraction and time aggregation, so ideas for their side are discussion points, not asks); the
stated block (A5 stated ability, A6 stated intent, dispute / relief flags) sits beside the axes
(`uc1_integration_proposal.md`); no clustering as an axis, no synthetic data, no combined score.
Numbers marked *(sample)* come from the 8% sample. KB = `docs/context/reference/uc1_data_kb.md`.

**Practical point.** Every measure below can be computed from contingency counts (signal level ×
outcome × axis state). A PROD snippet can export those counts, aggregates only with small cells
masked, and the bits are worked out outside PROD, so the approach fits the governance rules. Small
cells bias mutual information (MI) upward: compare against a shuffled baseline. Masking cells below
10 adds a little bias too.

## The basic picture

A call is a **noisy channel**: the customer's hidden state H (real capacity, real intent) goes in;
the detected level X, or "NA", comes out. The channel is shaped by what the agent asked, the script,
the LLM and its confidence. The time series is many readings of a state that drifts.

## 1. Entropy and surprise

- **Entropy of each signal.** Intent is lopsided: `payback_full` 45% of intent detections,
  `no_payment` 2% *(sample, KB §4.3)*. A `no_payment` carries about 5.6 bits of surprise, a
  `payback_full` about 1.2. Surprise is not relevance to payment, but it shows where one statement
  moves the picture most. Needs: level counts (in the KB).
- **Entropy of "NA".** "Not yet asked" is NA for intent (KB §4.1), so the detected / NA pattern
  carries information about the conversation as well as the customer: a measure of agenda.
- **Entropy of one customer's sequence.** Changing statements = high entropy. The UC1 team's Phase
  3.3 "diverse captures → LOW confidence" (KB §6) is this in informal form; a formal version is a
  discussion point for them.

## 2. How much a new call adds

- **Conditional entropy between calls,** H(X_t | X_{t−1}), by the gap between calls. Consecutive
  capacity statements agree 61.5%, improve 19.4%, worsen 19.1% *(sample, KB §5)*. Expect near 0 bits
  at a few days, rising to the overall entropy at long gaps. Where the curve flattens defines a
  "contact episode" and when to stop counting repeated calls. Needs: consecutive level pairs by gap
  bucket.
- **Effective number of independent calls.** Calls are skewed (p99 50 per customer, 26
  signal-bearing; KB §5); redundancy gives an effective count, so `transcript_count` overstates
  support.
- **How much remarks add.** I(remark level; transcript level) on the same day; 52% of remark days
  have a same-day transcript *(sample, KB §2)*. High MI = remarks add little where a transcript
  exists.

## 3. Agent and script effects

- **I(X; agent | DPD bucket, product):** the share of a signal's information that is about who called
  (about 183 agents, KB §2; needs bias correction or a permutation baseline). Large = it measures the
  script (KB §5, §10.2).
- **Whether the agent asks:** the same on detected / NA.
- **I(level changed; agent changed)** over consecutive calls tests the UC1 team's warning that
  movement is partly the agent (KB §5).
- **I(X; month)** at fixed strata picks up script changes; selection by month is strong (July 22% of
  calls extracted, March–May about 3%).

## 4. Information about payment, net of the axes

- **I(signal; later payment)** per signal and per candidate coding. Payments end 2026-08-31.
- **I(A5; Y | A1), I(A6; Y | A3)**, or conditioned on all four axes: what UC1 adds beyond the axes, in
  bits.
- **Partial information decomposition:** Y's information about A5 and A1 together splits into unique
  to A5, unique to A1, redundant, and synergistic (only the pair says it). Synergy is the
  side-by-side reading ("says able, money shows nothing"). Needs: one A5 × A1 × Y count table per
  model_id.
- **The circular check:** the UC1 team's F2 corroboration reads our A1 (KB §7), so I(stated capacity;
  A1) may be partly inflated. Their F7 finding (40.5% vs 41.4%) is near-zero MI.
- **Asymmetric orthogonality:** uncertainty coefficients U(A1 | A5) and U(A5 | A1) show direction,
  which Cramér's V (used for the axes today) hides.

## 5. Information bottleneck and rate–distortion for condensing

- Compress X (8 signals, 22 levels, multi-hot) into k states T, keeping as much of I(T; Y) as
  possible while minimising I(X; T). The curve of I(T; Y) against k shows how many states are worth
  having. The deterministic version gives hard, rule-like partitions.
- Clustering as an axis is rejected, so use it as a **yardstick for the hand-built mapping**: what
  fraction of the achievable I(·; Y) do A5 / A6 keep?
- Relevance variable: payment, or GRR's `collection_action` once its value sets exist (due Dec 11; KB
  §6), which would keep exactly what is needed to choose an action.
- Agglomerative merging gives a merge tree of levels: is `with_delay` = `partial` cheap to merge (KB
  §6 ranks them equal)? Is "concrete or not" or "full or partial" the better A6 cut? Does dispute type
  matter, or only its presence?

## 6. Minimum description length (MDL)

- **Two-part code length** to compare structures: A6 cuts, A7 as an axis vs two flags, A5 and A6
  separate vs merged. Extra states pay for themselves only if they compress; no hand-set thresholds.
  Computable from counts.
- **Predictive MDL for summarising a sequence:** code each customer's next call with latest / mode /
  most conservative / time-weighted summaries of earlier calls. The best predictor is the best
  summary. A neutral yardstick for the UC1 team's Phase 3 options, to offer without proposing ours.

## 7. Time

- **Information half-life per signal:** I(X_t; X_{t+Δ}) against Δ (capacity expected slow, intent
  fast), and I(X_t; Y_{t+Δ}) for how long a statement stays useful. Input for the recency workshop
  (KB §6); gaps run from a median of 4 days to p95 50 *(sample)*.
- **Change-point detection by information** (MDL or Bayesian online): a new segment only when it
  saves more bits than the break costs; with an agent covariate it separates real change from agent
  variation. Few points per customer, so it needs pooling.
- **Hidden-state channel:** monthly hidden H, calls read through p(X | H, agent, confidence); channel
  capacity bounds what one call reveals. The confusion matrix would come from the UC1 validation plan
  (stronger-LLM reference on ~2,000 extractions, 50–150 human labels, KB §6); their HMM work is design
  only (KB §10.8), so a discussion point.
- **Entropy rate:** noise around a stable state (summaries suffice) or real dynamics (trajectories
  matter).

## 8. Confidence and formats as noisy channels

- **Does low confidence carry information?** I(level; Y | low) vs I(level; Y | high); capacity is 43%
  low, 51% for `partial` *(sample)*.
- **Bits per detection against a reference** (UC1's reference labels): which levels deserve a state.
- **KL divergence** between legacy and current level distributions in the same strata (KB §4.2), and
  on new `model_version` values as they appear (KB §10.4): a drift alarm.

## 9. Selection and the unreached

- For the unreached the observation is the constant "no call": I(H; X | not reached) = 0.
- Book-level ceiling: P(reached) × information per reached customer; reach is 1.4% of spine rows at
  90 days *(sample, KB §8)*.
- Chain rule: I(S′; Y) = I(R; Y) + P(R = 1) · I(S; Y | R = 1) splits UC1's apparent value into being
  called / answered (overlapping A2: 42% of reached rows are A2 Non-Reachable) and what was said.
- "Not extracted" is a different symbol from "nothing detected"; KL between the extracted sample and
  all calls over the selection strata (KB §8) measures how far sample estimates are from the full run.

## 10. Uses on the persona side

- **Where a call would tell most:** the A1 Unknown cell (about half of CC 61–180) has maximum
  entropy. Strategy belongs to GRR; this only shows where stated signals could add the most bits.
- **Bits added to the persona:** joint entropy with and without the stated block; most of it lands
  in a few percent of rows.

## Most promising, with the cheapest measurement

| # | Idea | Cheapest measurement | Needs the timelines tables? |
|---|---|---|---|
| 1 | Information half-life per signal | Consecutive level pairs by gap bucket, per signal | No |
| 2 | Agent share of information | Level × agent × DPD bucket counts + permutation baseline | No |
| 3 | Reach vs content decomposition | `uc1_evidence` × payment; level × payment among the reached | Either |
| 4 | Net-of-axes MI, redundancy / synergy | A5 × A1 × Y and A6 × A3 × Y counts per model_id | Yes, plus outcomes |
| 5 | Does low confidence carry information? | Level × confidence × Y counts | No |
| 6 | Bottleneck / MDL check of the hand-built mapping | Full-detail × Y vs condensed × Y: share of MI kept | Yes |
| 7 | Predictive MDL yardstick for the UC1 team's time summaries | Next-call level vs latest / mode / most conservative | No (to offer them) |

All give method-test numbers only until the full extraction exists.

## Assessment for the integration phase (2026-11-17)

Worth doing, folded into the stated block's checks (proposal §7, C3 / C4) rather than as a project
of its own: 3 (reach vs content), 4 (net-of-axes MI, first as conditional MI and interaction
information; a full decomposition only if those show something), 6 (how much of the achievable
information the mapping keeps, and which cut). They use the same count tables the checks already
plan, and each answers an integration question with one number and a shuffled baseline.

Not now: 1, 2, 5, 7 are about how UC1 builds its outputs (time, agents, confidence); doing them
ourselves edges into the UC1 team's work. Keep as discussion points. Skipped: the hidden-state
channel, change-point models and the value-of-information view (no labels, too few points per
customer, strategy belongs to GRR).
