# Synthesized Features: GRR deck, content pack

Source of truth for moving the deck into the bank template. It covers 27 slides, in order: every word, number and speaker note as it stands in v83 (2026-11-12). Copy the text exactly. Change layout and styling only, never wording or numbers.

## Visual conventions

Map these to the nearest colours in the template; keep the meaning consistent across slides.

| Meaning | Original colour | Use for |
|---|---|---|
| Primary / dark | navy `#072447` | headings, dark panels, the "In-house" tier |
| Accent | blue `#2765FF` | section labels, highlight numbers, UC1 (always with a **dashed** outline: "joining, not yet in") |
| High (good) | green `#2E8B57` | High band, best cell |
| Moderate | amber `#E0A526` | Moderate band, "In progress" tag |
| Low (bad) | red `#C0392B` | Low band, worst cell |
| Unknown | grey dashed outline `#9295A0` | Unknown state (never a filled colour) |
| Panels | light grey `#F3F3F1` | cards, table cells, stat boxes |

Recurring elements:
- **Section label**: small upper-case blue text above the headline.
- **Headline**: one sentence, the slide's message.
- **Stat box**: a large blue number on the left and one sentence on the right. Two stat boxes sit side by side at the bottom of the axis slides.
- **Footer**: small grey source line at the bottom-left.
- **Step tracker** (axis slides 8–11, top-right): ① How they got here · ② Can we talk to them · ③ What we can offer. The current step is filled navy; the others are grey outlines.
- **Page number**: in a navy wedge at the top-right of every slide except the cover and the three dividers (numbering follows the deck order, so the cover counts as 1). Side margins are 0.5 in, as in the template.
- **Speaker notes**: go into the PowerPoint notes pane, not on the slide.

---

## 1 · Cover

Layout: title slide.

- Title: **Synthesized Features**
- Subtitle: A persona framework for collections allocation
- Byline: Group Retail Risk · Group AI, Data & Analytics · November 2026

Notes:
> Opening: where we are on the synthesized features use case. The framework is agreed; today is about what the combined results show, whether a risk score is still needed, how the transcript work (UC1) joins, and how we pilot and measure it. Data: August 2026 month end, unless marked otherwise.

## 2 · Summary

Layout: two columns over a bottom timeline. The left column holds two stacked cards; the right column holds a grey card with three stat boxes; a four-step timeline runs full width underneath.

- Section label: Summary
- Headline: **Synthesized features give allocation a view of the customer, built from data we already hold**

Left column:
- Card 1, "Today": No model beyond 60 DPD. Cases are allocated by bucket and product, and late buckets hold little behaviour to model.
- Card 2, "UC2 · Synthesized features": Signals from every data domain, condensed each month into four answers per account. A numbered list follows:
  1. How did they get here?
  2. Can we reach them?
  3. Will they pay?
  4. Can they pay?

Right column, "What it shows" (three stat boxes):

| Number | Text |
|---|---|
| 54% | of card collections came from just a fifth of the accounts, picked out in advance by the framework. |
| 8× | Within the same DPD bucket (91–120), some loan customers pay 8 times as often as others. |
| 12% | of 180+ accounts show a positive signal; one in five of them pays, against under 3% of the rest. |

Timeline, "Next":

| When | What |
|---|---|
| By 20 Nov | UC2 synthesized features signed off; one may follow later |
| 20 Nov – 11 Dec | UC1 transcript signals and UC2 combined, with action support |
| 11 – 20 Dec | Pilot selection |
| From 4 Jan | Pilot |

Notes:
> Three messages. One: beyond 60 DPD there is no model; cases are allocated by bucket and product, and the late buckets are where data runs dry. Two: the UC2 synthesized features take signals from every data domain and condense them each month into four answers per account: how did they get here, can we reach them, will they pay, and can they pay. Three: what it shows. If we had told collectors at the start of the month which fifth of card accounts to focus on, that fifth would have brought in 54 percent of everything collected over the next three months. Each account was scored by what customers with the same four answers had paid before, on months and accounts the test had not seen. Within the same DPD bucket, 91 to 120, groups of loan customers pay anywhere from 9 to 76 percent of the time within three months, depending on their answers: about eight times apart. At 180+, 12 percent of accounts show a positive signal, and about one in five of them pays, against under 3 percent of the rest. Next: by 20 November the UC2 synthesized features are signed off; one, ability, may follow later, pending bureau data and the framework. From 20 November to 11 December, the UC1 transcript signals and UC2 are combined, with action support. Pilot selection from 11 to 20 December, and the pilot from 4 January.

## 3 · Where we start

Layout: three equal cards side by side.

- Section label: Where we start
- Headline: **Allocation follows the bucket, not the customer**

| Card label | Card title | Text |
|---|---|---|
| Who works the case | In-house or agency | Rule-based: **DPD level and product** decide which team gets the case, not whether the customer can pay or has kept their word. |
| What we offer | Settlement, plan or push back | Pre-approved settlement programmes (PLUS, CARES) with waivers fixed **by product and DPD stage**, not by the customer's capacity or track record. |
| Where 180+ effort goes | 374k accounts at 180+ | Worked as one pool, though a small share still shows signs they could pay. Finding them is the 180+ goal. |

Notes:
> Where we start. Beyond 60 DPD there is no model. Allocation is rule-based and run by BI: the DPD level and the product decide whether a case goes to an in-house team or an agency. Offers come from the pre-approved settlement programmes, PLUS and CARES, whose waivers are fixed by product and DPD stage. The bucket tells us how late someone is, not whether we can reach them, whether they can pay, or whether they have kept their word. At 180+ the book is large, about 374 thousand accounts, and a small share of it still shows signs of being able to pay: that is the group we want to find.

## 4 · Synthesized features

Layout: a three-column flow, left → middle → right, with arrows between the columns and a bottom band.

- Section label: Synthesized features
- Headline: **Everything we know about a customer, condensed into a few states**

| Data domains | → | Signals | → | Persona states |
|---|---|---|---|---|
| Card billing · Card transactions · CASA transactions · Salary · Loan instalments · Bureau · Digital logins · Collector activity · Customer records · *Transcripts · joining* (dashed) | | Is salary regular? · Do calls connect? · Are promises kept? · Last seen abroad? · Paying while late? · and 45+ more | | A1 · Deterioration: How did they get here? · A2 · Locatability: Can we talk to them? · A3 · Payment credibility: Will they pay? · A4 · Ability: Can they pay? · *UC1 conversations · joining* (dashed) |

Bottom band:
- 10 data domains · 50+ signals · 4 states per account, every month
- 61–180 DPD: personas that drive allocation
- 180+ DPD: find the customers with a positive signal

Notes:
> What synthesized features means. Every data domain we hold, from card billing and transactions, financial transactions and salary to loans, bureau, logins and collector activity, is turned into more than fifty signals, and the signals into four persona states per account each month. The call transcripts from UC1 will join the same picture. Two goals: at 61 to 180, personas that drive allocation, with a risk score only inside a segment where it still needs ranking; at 180+, finding the customers with any positive payment signal.

## 5 · The idea

Layout: three numbered columns joined by arrows. Each column ends in a "Decides / Informs" box.

- Section label: The idea
- Headline: **Three questions before a case reaches a collector**

Column 1, **How did they get here?** (A1 · Deterioration). Four families, each with its states:
- Curing now: stabilized
- Cured or paid before: slow roller · repeat delinquent
- Paid, then stopped suddenly: seasoned · early-life straight roller
- Never paid: early payment default

Bottom box: *Informs:* Context and priority

Column 2, **Can we talk to them?** (A2 · Locatability)
- "Two checks": where they were last seen · whether calls connect
- Reachable: calls connect (highlighted)
- Non-Reachable · calls fail
- Skip · last seen abroad

Bottom box: *Informs:* How we can reach them

Column 3, **What can we offer?** The nuance, for every customer
- A3 · Credibility · Will they pay?: High · Moderate · Low · Unknown
- A4 · Ability · Can they pay? *(In progress tag)*: High · Moderate · Low · Unknown
- UC1 · Conversations · joining (dashed): intent and ability to pay, from call transcripts

Bottom box: *Decides:* Offer and agent

No footer.

Notes:
> The framework in one picture, in the order a case meets it. First, how did they get here: the deterioration journey tells us whether the customer is curing now, has cured or paid before, paid for a while and then stopped suddenly, or never paid at all. That gives context, and a flag for which cases to prioritise. Second, can we talk to them: where we last saw them, and whether our calls connect. This does not filter anyone out, and it does not decide the route on its own. It tells us how a case can be worked: by phone, or with tracing for those who look abroad. Third, the nuance: will they pay, can they pay, which is still in progress, and soon what they told us in conversations, from the transcript work. Together these decide the offer and who should work the case. The final personas will come out of workshops with GRR in the coming few weeks.

## 6 · How it is built

Layout: a 2 × 2 grid of short cards.

- Section label: How it is built
- Headline: **Built to be explained and trusted**

| Title | Text |
|---|---|
| Rules you can trace | Every state comes from a written rule, and the record says which rule assigned it and why. |
| Unknown is a state | When evidence is missing we say so, with the reason, instead of guessing. |
| Point in time | Each month end uses only what was known that day: the view a strategy would have had. |
| Customer-level evidence | Salary, CASA, bounces and logins are read across all of a customer's accounts, not only the delinquent one. |

Notes:
> Four design choices, each made for adoption. Rules rather than a model, so every state can be traced to the rule that assigned it. Unknown is a state of its own, always with the reason; counted up, those reasons show us where data is missing, and for ability they point to the bureau salary feed. Point-in-time month ends, so any back-test is fair. And customer-level evidence across all accounts.

## 7 · Part 1 divider

Layout: section divider.

- Label: Part 1
- Title: **The four axes**
- Subtitle: Deterioration · Locatability · Payment credibility · Ability

Notes:
> Four pages, in the order a case meets them: how they got here, whether we can talk to them, whether they will pay, and whether they can pay, which is still in progress.

## 8 · A1 · Deterioration

Layout: an axis slide. The step tracker sits top-right with step 1 active. Below the headline, the left side holds the decision path and the right side the August mix. Two stat boxes run across the bottom.

- Section label: A1 · Deterioration
- Tag: States · decided by rules
- Headline: **Customers curing now pay far more often than any other group**

Left, "How a customer gets a label": Read from the DPD history alone, so it covers every account. Asked in order; the first "yes" decides.

| # | Question | → State | Gloss |
|---|---|---|---|
| 1 | Nothing paid since the first months? | Early payment default | bad from the start |
| 2 | Holding at one level for months? | Stabilized | stopped falling |
| 3 | Back within a year of curing? | Repeat delinquent | been here before |
| 4 | Fell to 61+ fast, after a year of good history? | Seasoned straight roller | sudden stop |
| 5 | Fell to 61+ fast, in the first year? | Early-life straight roller | fell fast, early |
| 6 | Otherwise | Slow roller | fell slowly, paying on the way |

Right, "August mix · share of accounts" (two stacked 100% bars, or a small table):

| Family | Loans 61–180 | Cards 61–180 |
|---|---|---|
| Curing now | 10% | 7% |
| Cured or paid before | 33% | 25% |
| Paid, then stopped suddenly | 51% | 60% |
| Never paid | 6% | 8% |

Stat boxes:
- **60%**: of card accounts curing now paid within 3 months; of those who only cured before, 22% did.
- **Half**: of loans (six in ten cards) paid for a while, then stopped all at once: an event, not a habit.

Footer: 31 August 2026, 61–180 DPD · paid: meaningful payment within 3 months

Notes:
> Deterioration reads only the DPD history, so it covers every account. Six questions asked in order; the first yes decides. The states fall into four families. Stabilized customers are curing now: they have stopped falling. Slow rollers and repeat delinquents have cured or paid before, but are falling now. Straight rollers, seasoned or early in life, paid for a while and then stopped all at once, which points to an event rather than a habit: half of loans and six in ten card accounts. Early payment defaults never paid at all. Which family a customer falls into matters: 60 percent of card accounts curing now made a meaningful payment within three months, against 22 percent of those who only cured before. This holds within every DPD bucket: inside the same bucket, how likely a customer is to pay varies widely depending on which deterioration family they are in. Loans show the same pattern. Whatever the path, the next question is whether we can talk to them.

## 9 · A2 · Locatability

Layout: an axis slide with step 2 active. The left side holds two rule cards and the route line; the right side a 3 × 3 matrix. Two stat boxes run across the bottom.

- Section label: A2 · Locatability
- Tag: States · decided by rules
- Headline: **Only one in five card customers at 61–180 can be reached**

Left, "How a customer gets a label":
- **Location: Where were they last seen?** Logins and in-person card use show where they are; a travel purchase or collector note signals they have left. The latest evidence wins. Chips: In Country · Skip · Unknown (dashed)
- **Reachability: Do our calls connect?** Recent call days all failed, no contact since → Non-Reachable. A recent contact → Reachable. Chips: Reachable · Non-Reachable · Unknown (dashed)
- **Informs how we work a case:** by phone, or with tracing.

Right, "August mix": Location × reachability, 61–180. % of card accounts, with loans shown under each card figure.

| Location \ Reach | Reachable | Non-Reachable | Unknown |
|---|---|---|---|
| In Country | **8.5%** (loans 10.2%), green cell | 13.6% (loans 14.2%) | 1.9% (loans 2.7%) |
| Skip | 6.2% (loans 8.1%) | **31.7%** (loans 28.5%), red cell | 6.1% (loans 6.8%) |
| Unknown | 6.3% (loans 7.9%) | 22.3% (loans 14.9%) | 3.4% (loans 6.8%) |

Stat boxes:
- **1 in 3**: look abroad and do not answer, the largest group on cards and loans alike: candidates for tracing or an agency.
- **3.7%**: of 180+ card accounts are reachable (loans 4.8%), a positive signal for finding those still worth working.

No footer.

Notes:
> Locatability tells us how a case can be worked. Two rules: where did we last see the customer, from logins and in-person card use, with travel purchases and collector notes as signs of departure, latest evidence wins; and do our calls connect. The matrix shows how they combine. Only about one in five card customers and one in four loan customers at 61 to 180 are reachable. The largest group, about a third, look abroad and do not answer: these are candidates for tracing or an agency rather than in-house calls. At 180+ we look only for positives, and being reachable counts as one: 3.7 percent of card accounts and 4.8 percent of loans. Reachability carries real information: customers who look credible or able but cannot be reached pay about a third as often as reachable customers with the same profile, although they get as many call days. It is not a filter, though: in the tier test about one in five in-house card accounts and two in five loan accounts are not reachable, and the tiers barely change if we define reachability differently, for example six failed call days instead of three.

## 10 · A3 · Payment credibility

Layout: an axis slide with step 3 active. The left side holds the points table and a band bar; the right side the August mix. Two stat boxes run across the bottom.

- Section label: A3 · Payment credibility
- Tag: Score · points → band
- Headline: **Within the same bucket, credible customers roll far less**

Left, "How a customer gets a label": Three sources earn points; we add them up.

| Source | Detail | Points |
|---|---|---|
| Promises kept | last 12 months | Kept +2 · Partly +1 · Broken −1 |
| Paying while delinquent | regular = the monthly due paid in 2 of the last 3 months | Regular +2 · Some +1 |
| Record before | clean = paid as billed before falling behind | Clean +1 |

Band bar: **High** 4+ points (green) · **Moderate** 2–3 points (amber) · **Low** 0–1 points (red)

Below it: An explicit refusal to pay → **one band down**

Right, "August mix":

| | High | Moderate | Low |
|---|---|---|---|
| Cards 61–180 | 2.5% | 19.4% | 78.0% |
| Loans 61–180 | 4.9% | 27.9% | 67.2% |
| Cards 180+ | 0.1% | 2.7% | 97.2% |
| Loans 180+ | 0.3% | 4.3% | 95.4% |

Stat boxes:
- **42% vs 90%**: of card customers at 91–120 DPD rolled further: High vs Low credibility.
- **59%**: of card customers made no promise to pay in the last 12 months: their credibility rests on payments alone.

Footer: Roll rates: back-test, 3-month outcomes compared within each DPD band

Notes:
> Credibility is about this customer on this debt. Three sources earn points: promises kept in the last twelve months; paying while delinquent, two points for paying the monthly due in two of the last three months, one for any smaller payment; and the record before delinquency. Four points or more is High, two or three Moderate, below two Low. An explicit refusal moves one band down. Because points build up as customers pay, and paying keeps the bucket low, we compare outcomes within the same DPD band: at 91 to 120 days, how often High and Low credibility customers roll further: 42 percent against 90 percent for cards. At 180+ almost everyone is Low: 97 percent of cards and 95 percent of loans. 59 percent of card customers made no promise to pay in the last twelve months, so their credibility rests on payments alone: this is where the transcript signals will add the most.

## 11 · A4 · Ability

Layout: an axis slide with step 3 active. The left side holds four evidence cards in a 2 × 2 grid and a band bar; the right side the August mix and an amber "Needs" box. Two stat boxes run across the bottom.

- Section label: A4 · Ability
- Tag: **In progress** (amber)
- Headline: **Ability tells us what a customer can realistically be offered**

Left, "How a customer gets a label": Four evidence families; we count how many are strong*

| Family | Text |
|---|---|
| Income | Regular salary, ours or bureau |
| Money in | Money arriving or held, not salary |
| Spending | The customer's own spending |
| Other products | Activity on their other products |

Band bar: **High** 2+ strong · **Moderate** 1 strong · **Low** some evidence, none strong · **Unknown** no evidence (dashed, set apart)

Below it: A cheque bounce or returned direct debit → **one band down**

Right, "August mix":

| | High | Moderate | Low | Unknown |
|---|---|---|---|---|
| Cards 61–180 | 1.6% | 13.9% | 27.3% | 57.2% |
| Loans 61–180 | 1.2% | 8.8% | 49.3% | 40.7% |
| Cards 180+ | 0.3% | 6.0% | 8.6% | 85.1% |
| Loans 180+ | 0.1% | 3.5% | 11.0% | 85.4% |

Amber box, **Needs: GRR's bureau salary feed**: About a third of customers have no CASA with us, and half never had a salary credit here. Without a regular bureau salary feed they stay Unknown; with it, income becomes visible across the book. Today the bureau’s bulk salary pull reaches about 1% of customers.

Stat boxes:
- **57%**: of card customers at 61–180 show no evidence of their money yet.
- **4×**: High-ability card customers are back below 61 DPD three months later four times as often as those with no evidence.

Footer: * Strong = regular and above the floor in at least 2 of the last 3 months (floor: AED 3,000 or twice the amount due); at 180+: 3 of the last 6 months

Notes:
> Ability is work in progress. The approach: four families of evidence, income, other money arriving or held (a balance that survives the sweep counts), the customer's own spending, and activity on their other products. We count how many are strong: two or more is High, one is Moderate, some evidence but nothing strong is Low, and no evidence at all is Unknown. A bounced cheque or returned direct debit moves the customer one band down. The axis depends on one thing we do not control: about a third of customers have no current or savings account with us and half never had a salary credit here, so without GRR's bureau salary feed many stay Unknown; today the bureau's bulk salary pull reaches only about 1 percent of customers. 57 percent of card customers at 61 to 180 show no evidence of their money yet. Where we do see it, ability separates customers clearly: 31 percent of High-ability card customers were back below 61 DPD three months later, against 8 percent of those with no evidence, and 59 against 20 percent made a payment. At 180+, Moderate or High ability counts as a positive signal: 6.3 percent of card accounts.

## 12 · Part 2 divider

Layout: section divider.

- Label: Part 2
- Title: **From states to a strategy**
- Subtitle: Too many personas · only in-house needs a strategy · a first look

Notes:
> Part 2 is a first look, not a plan. Combined, the states give far more personas than anyone could act on, so we narrow the question to the cases kept in-house, where a strategy is actually needed. It ends with a short list for the strategy workshop, where UC1 adds its signals, and a note on the risk score. None of it has been agreed with GRR.

## 13 · Combining the states

Layout: a row of tiles forming an equation across the slide, with three items underneath.

- Section label: Combining the states
- Headline: **Combined, the states give hundreds of personas: far too many to give each a strategy**

Equation tiles:

**6** deterioration states (A1) × **9** locatability cells (A2) × **3** credibility bands (A3) × **4** ability bands (A4) = **648** possible personas, today (dark tile) × **UC1** transcript signals: intent · hardship · dispute (blue dashed tile)

Underneath:
- **393**: occur among card accounts in August
- **222**: have enough accounts (10+) to judge
- Box: A **persona** is one combination of states. Each UC1 signal multiplies the count again, and many personas hold only a handful of accounts.

Footer: Cards 61–180 · August 2026 · credibility High / Moderate / Low; ability includes Unknown

Notes:
> Part 2 starts by putting the axes together. A persona is one combination of states: one of six deterioration states, one of nine locatability cells, one of three credibility bands and one of four ability bands. That is 648 possible personas before anything from UC1. The transcript signals, such as stated intent, a hardship reason or a dispute, come on top, and each one multiplies the count again. Many of these combinations do occur: 393 among card accounts in August, of which 222 have ten or more accounts; on loans 323 occur and only 111 have ten or more. Many hold just a handful of accounts. Nobody can write and run a separate strategy for hundreds of personas, so we need a way to decide where a strategy is actually needed.

## 14 · The simplification

Layout: a box on the left ("Every case") with an arrow that splits into three lanes on the right. A "From → To" band runs underneath.

- Section label: The simplification
- Headline: **Only the cases we keep in-house need a strategy of their own**

Left box: **Every case**, 61–180 DPD, allocated first, then worked →

| Lane | Tag | Text |
|---|---|---|
| In-house (dark, emphasised) | Strategy per persona | Offer, agent and channel chosen for who the customer is |
| Agency | Policy terms | Worked by the agency, paid on cash collected |
| Non-workable pool | Policy terms | Least probable to pay, referred out under the policy |

Band, "The question changes":
- From: ~~A strategy for every persona~~ (struck through)
- To: **Which personas earn in-house effort, and what we do with them**

Footer: Agency and non-workable handling as in the collections policy (FR Policy on Operations, July 2025)

Notes:
> The way out of the explosion is the first decision every case meets: allocation. Once a case goes to an agency, the agency works it on the policy's terms and is paid commission on the cash it collects. The non-workable pool, the customers least probable to pay, is referred out under the policy as well. In neither case do we need a persona-level strategy. Only the cases we keep in-house need one: which offer, which agent, which channel. So the question changes from finding a strategy for every persona to deciding which personas earn in-house effort, and what we do with those.

## 15 · How an account gets a tier

Layout: three numbered steps side by side.

- Section label: A first look
- Headline: **How an account gets a tier: by what its persona actually paid**

Step 1, **Describe each account**: One state on each of the four axes. Together they form its **persona**. Example chips: Stopped suddenly · Skip · Non-Reachable · Low credibility · Unknown ability

Step 2, **Measure what it paid**: For each persona: every account in May 2026, everything it paid in June–August, averaged per account.
- **Example:** 400 accounts paid AED 70,000 in total → **AED 175 per account**. 10% of them paid, AED 1,750 each on average.
- Observed, not modelled: the average combines how often and how much.

Step 3, **Rank and cut**: The personas with at least 10 accounts (97% of cards), ranked by AED per account:

| Tier | Cut |
|---|---|
| In-house | AED 1,250 and above |
| Agency | between |
| Non-workable | under AED 175 |

Below it: Illustrative cut-offs from the data; GRR would set them from the commission rate card and in-house cost.

Footer: Cards 61–180 · back-test May → Jun–Aug 2026; tiers hold on unseen months · personas under 10 accounts unassigned (3%)

Notes:
> How the tiers on the next slide are built, in three steps. First, every account has one state on each of the four axes: its deterioration family, its locatability cell, its credibility band and its ability band. Together these form its persona; for the tiers, deterioration is read at family level. Second, for each persona we take every account in May and add up everything it paid in June to August, then divide by the number of accounts. That gives the amount collected per account, an observed average that combines how often accounts paid and how much they paid; for example, 400 accounts paying 70,000 dirhams is 175 dirhams per account. Third, we rank the personas large enough to judge, 97 percent of card accounts, and cut the list: 1,250 dirhams and above in-house, under 175 the non-workable pool, agency in between. The cut-offs are illustrations from the data; GRR would set them from the agency commission rate card and the in-house cost. Every account then takes the tier of its persona. Testing added two refinements. A list built from a single month moves too much, so the table is pooled over several months, and a persona enters in-house only clearly above the cut and leaves only clearly below it, a band of about ten percent either side. And the cut matters far more than anything else: moving it twenty percent either way takes the card in-house list from 70 personas to 44, while changing how we define reachability swaps only a handful.

## 16 · Tiers, a first look

Layout: a table on the left (or a bar of the money share above the table); two descriptive lines and one stat box on the right.

- Section label: A first look
- Headline: **In-house would take a sixth of card accounts and half the money collected**

"Share of money collected":

| Tier | Accounts | Money collected | Recovery, 3 m | Call days |
|---|---|---|---|---|
| **In-house** | 17% | 48% | 10.0% | 11.7 |
| **Agency** | 54% | 46% | 2.7% | 11.8 |
| **Non-workable** | 29% | 6% | 0.56% | 10.9 |

- **In-house:** mostly customers curing now or cured before, who are credible or able.
- **Non-workable:** mostly stopped suddenly or never paid, and not reachable.
- Stat box, **10.9**: call days per account in 3 months still go to the non-workable pool, almost as many as in-house.

Footer: Cards 61–180 · table out-of-sample (5 folds, Jan–May 2026); call days: August · cuts AED 1,250 / 175 · loans: same order, thresholds less stable

Notes:
> A first look; nothing here has been discussed with GRR. With the illustrative cut-offs, in-house would take about a sixth of card accounts and half the money collected. In-house is mostly customers curing now or cured before who are credible or able; the non-workable pool is mostly those who stopped suddenly or never paid and cannot be reached, which also gives the policy's non-workable pool a definition. Tested on unseen months and accounts, the top fifth of card accounts by persona hold 54 percent of the money collected. The illustrative cut-offs give three groups: in-house, 17 percent of accounts and 48 percent of the money, recovering about 10 percent of principal in three months; agency, 54 percent and 46 percent; and the non-workable pool, 29 percent of accounts, about 6 percent of the money, recovering just over half a percent, yet still taking nearly 11 call days per account. The groups keep their order on every unseen month. We also checked how stable the tiers are. Rebuilt from one month alone, the card list keeps about half its personas from one month to the next; pooled over months with the band, about 80 percent, and only about one card account in twenty changes tier while its persona stays the same, down from one in eight, with no loss in money collected. On loans the order holds too, but the book is smaller and the list thinner: even pooled, about one loan account in seven changes tier with the same persona, so the loan tiers are provisional. The cut-offs are illustrations; the commission rate card and the in-house cost would set them properly.

## 17 · UC1

Layout: a horizontal bar chart in a grey panel on the left; chips and a quote line on the right.

- Section label: UC1
- Headline: **In-house is where we talk to customers, so that is where UC1 adds its signals**

Left, "Right-party contact in the last 3 months · cards" (horizontal bars):

| Group | Value | Colour |
|---|---|---|
| In-house | 89% | navy |
| Agency | 45% | blue |
| Non-workable | 16% | grey |

Under the bars: All card accounts 41% · loans 52%

Right, "What transcripts add" (blue dashed chips): Stated intent to pay · Change in income or job · Hardship reason · Dispute · Promise made on the call

Line with a blue left border: These come from what customers say on calls, so most of them will come from the in-house cases.

Footer: Cards 61–180 · August 2026 · groups at the illustrative cut-offs

Notes:
> The transcript work, UC1, only has something to say where a conversation took place, and that differs sharply across the groups: 89 percent of in-house card accounts had a right-party contact in the last three months, 45 percent of the agency group and 16 percent of the non-workable pool. So the UC1 signals, what customers say about their intent, income, hardship, disputes and promises, land mostly on the in-house cases. That is exactly where a strategy is needed, and where the extra detail is worth having.

## 18 · Towards the strategy workshop

Layout: a table on the left with a dark summary bar under it; three vertical numbered steps on the right.

- Section label: Towards the strategy workshop
- Headline: **The in-house personas become a short list for GRR to give each a strategy**

Left, "The five largest in-house personas · cards":

| Path | Where · reach | Credibility | Ability | Share |
|---|---|---|---|---|
| Stopped suddenly | In country · **reachable** | Low | Unknown | 8.0% |
| Cured before | In country · **reachable** | Low | Low | 6.4% |
| Curing now | Unknown · **reachable** | Moderate | Unknown | 5.0% |
| Stopped suddenly | In country · **reachable** | Moderate | Low | 4.9% |
| Cured before | In country · **reachable** | Moderate | Low | 4.7% |

Dark bar: **26** of 51: in-house personas cover 80% of in-house accounts

Right, steps:
1. **The data proposes**: In-house personas, ranked by size and what they pay. All reachable; credibility and ability vary
2. **UC1 refines** (dashed blue circle): Transcript signals on top, where we talk to customers
3. **GRR decides**: Offer, agent and channel for each persona on the list, in the strategy workshop

Footer: Cards 61–180 · August 2026 · share of in-house accounts · in-house at the illustrative cut-off of AED 1,250 per account in 3 months · loans: 11 of 16 cover 80%

Notes:
> Where this leads. Most personas fall to the agency or the non-workable pool and need nothing more from us. The in-house tier is a much shorter list: 51 personas on cards, and 26 of them cover 80 percent of in-house accounts; on loans 11 of 16. Look at the five largest: every one is reachable, while credibility and ability vary, from low credibility with unknown ability to moderate credibility with low ability. Reachability helps, but it does not decide who lands in-house: about one in five in-house card accounts, and two in five on loans, are not reachable. A core of the list is steady: on cards, the personas that are in-house in every month cover over a third of in-house accounts, and about half with those in-house four months out of five. For the workshop we would build the list from several pooled months, not one; on loans it is still thin and moves, so we would treat it as provisional. That short list is what we would take to GRR: the data proposes it, UC1 refines it with what customers tell us, and GRR decides the offer, agent and channel for each persona in the strategy workshop. The simplification comes from GRR, not from us merging states.

## 19 · Appendix divider

Layout: section divider.

- Label: Appendix
- Title: **Signals, rules and governance**
- Subtitle: For the detailed discussion: where each signal comes from, the exact rules, and how the framework is controlled.

Notes:
> Backup slides for questions on logic and data.

## 20 · What each group could mean

Layout: three columns (one per tier) with a full-width 180+ band underneath.

- Section label: Appendix · A first look
- Headline: **What each group could mean, for discussion**

| | In-house | Agency | Non-workable |
|---|---|---|---|
| Who | Curing now or cured before, reachable, credible or able | Stopped suddenly or cured before, not reachable | Stopped suddenly or never paid, not reachable |
| Treatment (bold) | Convert through skilled collectors: settlement, restructure or deferral | Place with agencies at 61–180, skip tracing where they look abroad | Free collector time: refer to agencies or stop calling |
| Policy | Policy tools: CARES settlements, loan restructure, deferral | Policy: referral by product, DPD stage, contactability and strategy | Policy: non-workable pool to agencies (HOD approval), or no calling with dunning as for Dead Beat accounts |
| Size | 11% of cards · AED 40m | 54% of cards · AED 213m | 32% of cards · AED 138m |
| Outcome | 50% paid in 3 months | 17% paid in 3 months | 4% paid in 3 months |

Band, **180+**: The 12% with a positive signal: lift out of the pool for an in-house attempt. About one in five pays, against under 3% of the rest.

Footer: For discussion in the strategy workshop; not agreed with GRR · cards 61–180; AED = outstanding principal; paid = meaningful payment

Notes:
> For discussion only, not agreed with GRR. Each illustrative group is paired with a treatment the policy already provides; nothing here is a new process. In-house customers are curing now or have cured before, can be reached and are credible or able: half of them pay within three months, so skilled collectors should convert them with the existing tools, the CARES settlements, a restructure or a deferral. The agency tier is mostly customers who stopped suddenly or cured before and cannot be reached: place them with agencies at 61 to 180, with skip tracing where they appear to be abroad. The non-workable pool is customers who stopped suddenly or never paid, and cannot be reached: the policy allows either referral to agencies with HOD approval, or no calling with dunning only, as it does for Dead Beat accounts. At 180+, the 12 percent with a positive signal are lifted out of the pool for an in-house attempt.

## 21 · How a pilot could test it

Layout: three columns of short lists.

- Section label: Appendix · A first look
- Headline: **How a pilot could test it, if the strategy workshop takes it forward**

| Test in each tier | Measure | Size and guardrails |
|---|---|---|
| **In-house:** skilled collectors and settlements vs business as usual | Meaningful payment and roll rate | Cards: agency and non-workable fill both arms in one month |
| **Agency:** placement at 61–180 vs in-house calling | Amount collected per account | In-house needs a 10-pt target; loans need 10 pts and pooling |
| **Non-workable:** agency referral or dunning only vs business as usual (hold-out) | Recovery of outstanding principal | Same policy and compliance rules |
| Random split within each tier, 3 months | Call days and cost per AED collected | Monthly readout and a stop rule |
| | 180+: the flagged group vs the rest | |

Footer: Sample per arm (cards, 5-pt lift): agency 970, non-workable 375; in-house 388 at a 10-pt lift · two-sided α 0.05, 80% power

Notes:
> For discussion only. If the strategy workshop takes the allocation view forward, a pilot could test each group against business as usual, with a random split inside each tier for three months. In the in-house tier, skilled collectors with the settlement tools against the current process. In the agency tier, placement with agencies at 61 to 180 against in-house calling. In the non-workable pool, the two treatments the policy allows, agency referral or dunning only, against business as usual: a hold-out that shows exactly what is lost, if anything, by taking collector time away. We measure meaningful payments and roll rates, the amount collected per account, recovery of outstanding principal, and the call days and cost per dirham collected; at 180+, the flagged group against the rest. On cards, the agency and non-workable tiers fill both arms in a single month for a five point lift; the in-house tier needs a ten point target, and loans need a ten point target and pooling over months. The same policy and compliance rules apply to every arm, with a monthly readout and a stop rule.

## 22 · Risk score

Layout: a table on the left; three short findings on the right.

- Section label: Appendix · Risk score
- Headline: **Personas rank payers far better than the bucket; a model adds a little on top**

"How well each view ranks who pays (AUC) · 61–180":

| Ranking customers by | Cards | Loans |
|---|---|---|
| DPD bucket only (today) | 0.65 | 0.62 |
| **Personas** | **0.83** | **0.77** |
| Personas × DPD bucket | 0.84 | 0.77 |
| Simple model (axis states + bucket) | 0.84 | 0.78 |

Under the table: Out-of-sample: 5 folds by account, January–May 2026 cohorts. 0.5 = chance, 1.0 = perfect.

Findings:
- **Personas beat the bucket in every test**: +0.17 on cards, +0.14 on loans. The top 20% of card accounts by persona hold 54% of the money collected (bucket: 30%).
- **The bucket adds almost nothing within personas**: +0.01 on cards, +0.00 on loans.
- A model on the same inputs adds about **+0.02** over the personas. Risk score modelling is planned for **Phase 2**.

Footer: Paid = meaningful payment within 3 months (the risk score's target) · strict and rolling time splits give the same picture

Notes:
> Is a risk score still worth building? We tested out-of-sample: the payment rates of each view were learned on some accounts and months and scored on others, January to May 2026, in five folds, and confirmed with time splits. Ranking power is the area under the curve, where 0.5 is chance and 1 is perfect. The DPD bucket alone reaches 0.65 on cards and 0.62 on loans. The personas reach 0.83 and 0.77: far better, in every test, and the top fifth of card accounts by persona hold 54 percent of the money collected, against 30 percent by bucket. Adding the bucket to the personas adds almost nothing. A simple model on the axis states and the bucket adds about two points of AUC over the personas. So a model on the same inputs adds a little, consistently. The risk score modelling is planned for Phase 2, where a full Retail 360 model, using bureau and other domains the axes do not use yet, can be tested against the personas.

## 23 · Appendix A: Signals and their sources

Layout: a full-width table.

- Section label: Appendix A
- Headline: **Signals and their sources**

| Axis | Signals | Sources |
|---|---|---|
| A1 Deterioration | Monthly DPD bucket path, restructures linked to their original loans | Way4 billing history, loan master |
| A2 Locatability | UAE vs foreign logins, in-person card use (POS, ATM) by country, departure notes, travel purchases, call outcomes, deceased flags | Digital login, Way4 card transactions, CASA card transactions, DCORE follow-ups, customer records |
| A3 Credibility | Promises and plans with their outcome, payments vs dues per cycle, record before delinquency, refusals, disputes | DCORE plans and follow-ups, card statements and payments, loan monthly dues and cash |
| A4 Ability | Salary per month (larger of ours and bureau), CASA balance and activity, external card payments, cheque / direct-debit returns, bureau bounces | Wealth-management salary and CASA features, AECB salary and bounce data, loan master (instalment) |

Under the table: Customer-level signals are read across every account of the customer (CIF). Windows end at the observation month end: 3 months at 61–180 DPD, 6 at 180+.

Footer: All sources are existing bank datasets; no new data feed is needed to run the framework

Notes:
> Where the evidence comes from. Every source is an existing bank dataset read through the pipeline catalog. Customer signals such as salary, CASA, bounces and logins are read across all accounts of the customer, because the delinquent account is usually not where the salary lands. Windows are short and end at the month end, so the state reflects the customer now.

## 24 · Appendix B: The scoring rules at a glance

Layout: a full-width table.

- Section label: Appendix B
- Headline: **The scoring rules at a glance**

| Axis | Evidence and points | State |
|---|---|---|
| A1 Deterioration | DPD history only, from January 2024 (reliable window) | First "yes" of six ordered questions (Appendix C) |
| A2 Locatability | Latest location evidence: foreign → Skip; UAE within 3 months (6 at 180+) → In Country; travel rule. Last 3 call days failed (6 at 180+) → Non-Reachable | Location × reachability (9 cells) + Deceased override |
| A3 Credibility | Promises: Kept ≥ 80% +2, Partly +1, Broken < 40% or last 3 broken −1. Payments: monthly due paid in 2 of the last 3 months +2, any payment +1. Record before: 80% paid as billed +1 | High ≥ 4 · Moderate ≥ 2 · else Low; refusal −1 rung; no delinquency history → Unknown |
| A4 Ability | Four evidence families: income (salary, ours or bureau), money arriving or held, own spending, other products. In progress | High: 2+ strong · Moderate: 1 strong · Low: evidence, none strong; distress −1 band; no evidence → Unknown |

Footer: Full specification and reference workbook per axis

Notes:
> The exact rules, for the detailed questions. Deterioration is a decision tree on the DPD history. Locatability combines location and reachability. Credibility adds up points, High from four and Moderate from two, with a refusal lowering one band. Ability, still in progress, counts strong evidence families. Every threshold is in the axis specification and its reference workbook.

## 25 · Appendix C: How a journey state is assigned

Layout: a full-width table.

- Section label: Appendix C
- Headline: **How a journey state is assigned**

| # | Question | Yes when | State |
|---|---|---|---|
| 0 | Start of journey seen? | Oldest month already delinquent and not stabilized | Unknown |
| 1 | Early payment default? | ≤ 3 months of history, rolled in, never paid since | EPD |
| 2 | Stabilized? | Pays about one month's due in 5 of the last 6 months (61–180 only) | Stabilized |
| 3 | Repeat delinquent? | Cured an earlier spell that reached 31–60 DPD, back within 12 months | Repeat delinquent |
| 4 | Straight roller? | Current to 61+ DPD in ≤ 3 months, no payment on the way | Seasoned (12+ months on book) or early-life |
| 5 | Otherwise | Paid something on the way down, kept rolling | Slow roller |

Footer: Billing artefacts repaired first and counted · retail loans on the same tree, buckets shifted by one

Notes:
> Deterioration is a short ordered tree. A guard first: if the history starts already delinquent, we cannot see how they fell in, so the state is Unknown unless the account is stabilized. Then early payment default, stabilized, repeat delinquent, straight roller split by tenure, and everything else is a slow roller. One-month glitches and billing-cycle jumps are repaired before the tree runs, and every repair is counted.

## 26 · Appendix: New ability rule vs the old

Layout: two tables side by side, with three short cards across the bottom.

- Section label: Appendix · Ability
- Headline: **New ability rule vs the old income + CASA rule**

Left, "Share of accounts in each state, August". Each cell shows the new value in large type and "was …" in small grey type under it.

| | High | Moderate | Low | Unknown |
|---|---|---|---|---|
| Cards 61–180 | 1.62% (was 0.23%) | 13.9% (was 14.4%) | 27.3% (was 28.9%) | 57.2% (was 56.6%) |
| Loans 61–180 | 1.18% (was 0.28%) | 8.8% (was 8.9%) | 49.3% (was 44.7%) | 40.7% (was 46.1%) |
| Cards 180+ | 0.27% (was 0.03%) | 6.0% (was 6.2%) | 8.6% (was 6.4%) | 85.1% (was 87.4%) |
| Loans 180+ | 0.12% (was 0.03%) | 3.5% (was 3.5%) | 11.0% (was 6.9%) | 85.4% (was 89.5%) |

Right, "Next 3 months, 61–180*":

| State | Cards: Cure | Cards: Pay | Cards: Roll | Loans: Cure | Loans: Pay | Loans: Roll |
|---|---|---|---|---|---|---|
| High | 31% | 59% | 53% | 28% | 75% | 59% |
| Moderate | 16% | 41% | 73% | 15% | 65% | 69% |
| Low | 11% | 29% | 82% | 10% | 45% | 82% |
| Unknown | 8% | 20% | 88% | 9% | 36% | 85% |

Bottom cards:
- **High is reachable:** 2 of 4 strong families, not a CASA balance the bank sweeps.
- **Other products with us** give evidence for customers with no CASA activity.
- **Only proven transactions count;** bounces and reversals cancel out.

Footer: * Cure: below 61 DPD at month 3 · Pay: any payment, even partial · Roll: moves to a worse bucket

Notes:
> How the new ability rule compares with the old one, which rested on income plus the CASA balance. The old High needed a CASA balance above the floor, and the bank sweeps balances against the overdue amount, so High almost never fired. The new rule counts four evidence families: income, money arriving or held, the customer's own spending, and other products with us. Two strong families make High, one makes Moderate, some evidence makes Low, none is Unknown; a bounced cheque or returned direct debit moves the customer one band down. Share of accounts: High grows four to nine times in every book. Low rises for loans and at 180+, mostly customers with another product kept current with us. Cards at 61 to 180 move slightly into Unknown on purpose: those customers' only account activity was fees or payments on their own loan, which says nothing about ability. Outcomes are rates within each state over the next three months: cure means below 61 DPD at month 3, pay means any payment, roll means a worse bucket. Every state orders all three in the right direction. For cards every step is significant, also within the same DPD bucket; for loans High and Moderate are not yet separable, because High is still small. The old rule's High was too small to read at all. Unknown means we cannot see the customer's money, not that they have none.

## 27 · Appendix D: Status and sign-off

Layout: a simple two-column table.

- Section label: Appendix D
- Headline: **Status and sign-off**

| Axis | Status |
|---|---|
| A1 Deterioration | **Closed** · signed off by GRR |
| A2 Locatability | **Closed** · signed off by GRR |
| A3 Credibility | Sign-off by 20 Nov |
| A4 Ability | Sign-off by 20 Nov, or later |
| UC1 transcripts | Joining, 20 Nov – 11 Dec |

Footer: Status as of 11 Nov 2026

Notes:
> Where each axis stands. Deterioration and locatability are closed and signed off by GRR. Credibility is due for sign-off by 20 November; ability may be signed off by then too, or follow later. The UC1 transcript signals join between 20 November and 11 December.
