# Synthesized Features: speaker script

This is what to say on each slide, start to finish, for deck version 83 (27 slides). Slides 1–18 are the talk, about 25 minutes. Slides 19–27 are backup: use them only when a question calls for them.

---

## Part 0 · Opening

### Slide 1 · Synthesized Features

Good morning, and thank you for the time. We're from Group AI, Data and Analytics, presenting with Group Retail Risk.

Today is about where we are on the synthesized features use case. The framework itself is agreed. What we want to walk you through is what the results show, how the transcript work from UC1 joins it, and how we would pilot and measure it.

Unless a slide says otherwise, every number comes from the August 2026 month end.

### Slide 2 · Summary

Three messages.

First, where we are today. Beyond 60 days past due there is no model. Cases are allocated by bucket and product, and the late buckets are exactly where the behavioural data runs dry.

Second, what we built. The UC2 synthesized features take signals from every data domain we hold and condense them, every month, into four answers per account: how did they get here, can we reach them, will they pay, and can they pay.

Third, what it shows. Three numbers:
- If we had told collectors at the start of the month which fifth of card accounts to focus on, that fifth would have brought in 54 percent of everything collected over the next three months. That was tested on months and accounts the method had never seen.
- Within the same DPD bucket, 91 to 120, some groups of loan customers pay 9 percent of the time and others 76 percent. That's about eight times apart, inside a single bucket.
- At 180+, 12 percent of accounts show a positive signal. About one in five of them pays, against under 3 percent of the rest.

On next steps: each synthesized feature has its own model specification document, with the full logic and comprehensive back-test results. Two of the four, deterioration and locatability, have been signed off by Architha and Nayeema. By 20 November we plan to close the other two, credibility and ability, pending the final results and your feedback today. Ability may follow slightly later, depending on the bureau data.

From 20 November to 11 December, we combine the UC1 transcript signals with these features, with support on actions. Pilot selection runs from 11 to 20 December, and the pilot starts on 4 January.

### Slide 3 · Allocation follows the bucket, not the customer

Let's start with how things work today.

Who works the case is rule-based: the DPD level and the product decide whether it goes to an in-house team or to an agency.

What we offer comes from the pre-approved settlement programmes, PLUS and CARES. Their waivers are fixed by product and DPD stage.

At 180+ the book is large, about 374 thousand accounts, and it's worked as one pool.

The common thread: the bucket tells us how late someone is. It doesn't tell us whether we can reach them, whether they can pay, or whether they've kept their word. And at 180+, a small share still shows signs of being able to pay. Finding them is the 180+ goal.

### Slide 4 · Everything we know about a customer, condensed into a few states

This is what "synthesized features" means.

On the left are ten data domains: card billing and transactions, CASA transactions, salary, loan instalments, bureau, digital logins, collector activity and customer records. The call transcripts are joining.

From these we build more than fifty signals, questions like: is salary regular, do our calls connect, are promises kept, was the customer last seen abroad, are they paying while late.

The signals are then condensed into four persona states per account, every month: deterioration, locatability, payment credibility and ability. The conversations from UC1 will join the same picture.

There are two goals. At 61 to 180, personas that drive allocation. At 180+, finding the customers with any positive payment signal.

### Slide 5 · Three questions before a case reaches a collector

Here's the framework in one picture, in the order a case meets it.

First: how did they get here? The DPD path tells us whether the customer is curing now, has cured or paid before, paid for a while and then stopped suddenly, or never paid at all. That gives context, and a flag for which cases to prioritise.

Second: can we talk to them? This is the gate. Only reachable customers go on. For those who don't answer, or who look abroad, the decision is the route: tracing or an agency.

Third, for the reachable: what can we offer? This is the nuance: will they pay, which is credibility; can they pay, which is ability and still in progress; and soon what customers tell us on calls, from the transcript work.

Together these decide the offer and who should work the case. The final personas come out of a workshop with GRR.

### Slide 6 · Built to be explained and trusted

Four design choices, each made with adoption in mind.

- **Rules you can trace.** Rules, not a black-box model, so every state can be traced back to the rule that assigned it.
- **Unknown is a state.** Unknown is a state of its own, always with the reason. Counted up, those reasons show us where data is missing; for ability, they point to the bureau salary feed.
- **Point in time.** Each month end uses only what was known that day, so every test is fair.
- **Customer-level evidence.** Salary, CASA, bounces and logins are read across all of a customer's accounts, not just the delinquent one.

---

## Part 1 · The four axes

### Slide 7 · The four axes

The next four slides take one axis each, in the order a case meets them: how they got here, whether we can talk to them, whether they will pay, and whether they can pay.

### Slide 8 · A1 Deterioration: customers curing now pay far more often than any other group

Deterioration reads only the DPD history, so it covers every account.

Six questions, asked in order; the first "yes" decides. The states fall into four families:
- **Curing now:** stabilized customers. They've stopped falling.
- **Cured or paid before:** slow rollers and repeat delinquents. They've paid before, but they're falling now.
- **Paid, then stopped suddenly:** straight rollers, seasoned or early in life. They paid for a while and then stopped all at once.
- **Never paid:** early payment defaults.

On the right is the August mix, the share of accounts in each family. The big one: half of loans and six in ten card accounts paid for a while and then stopped all at once. That points to an event, not a habit.

The split matters. 60 percent of card accounts curing now made a meaningful payment within three months; of those who cured before, 22 percent did. And within every DPD bucket from 61 to 180 the gap is 26 to 49 percentage points, so it's not just that curing customers sit in earlier buckets. For loans it's 74 against 38 percent.

This axis is closed and signed off. Whatever the path, the next question is whether we can talk to them.

### Slide 9 · A2 Locatability: only one in five card customers at 61–180 can be reached

Locatability is the gate. Two questions.

Where did we last see the customer? We look at logins and in-person card use. A travel purchase or a collector note is a sign they've left. The latest evidence wins.

Do our calls connect? If the recent call days all failed with no contact since, the customer is Non-Reachable; a recent contact makes them Reachable.

The matrix shows how the two combine. Only about one in five card customers, and one in four loan customers, at 61 to 180 are reachable, and only they go on to the nuance step.

The largest single group, about a third, look abroad and don't answer. They're candidates for tracing or an agency rather than in-house calls.

At 180+ we only look for positives, and being reachable counts as one: 3.7 percent of card accounts and 4.8 percent of loans.

This axis is also closed and signed off.

### Slide 10 · A3 Payment credibility: within the same bucket, credible customers roll far less

Credibility is about this customer, on this debt.

Three sources earn points:
- promises kept in the last twelve months;
- paying while delinquent: two points for paying the monthly due in two of the last three months, one for any smaller payment;
- the record before delinquency.

Four points or more is High, two or three is Moderate, below that is Low. An explicit refusal to pay moves the customer one band down.

Points build up as customers pay, and paying keeps the bucket low, so the fair comparison is within the same DPD band. At 91 to 120 days, 42 percent of High-credibility card customers rolled further, against 90 percent of Low.

Two more things. At 180+ almost everyone is Low: 97 percent of cards and 95 percent of loans. And 59 percent of card customers made no promise to pay in the last twelve months, so their credibility rests on payments alone. That's where the transcript signals will add the most.

We plan to close this axis by 20 November.

### Slide 11 · A4 Ability: ability tells us what a customer can realistically be offered

Ability is still in progress.

We look at four families of evidence:
- income, meaning regular salary, ours or bureau;
- other money arriving or held;
- the customer's own spending;
- activity on their other products with us.

We count how many are strong. Two or more is High, one is Moderate, some evidence but nothing strong is Low, and no evidence at all is Unknown. A bounced cheque or a returned direct debit moves the customer one band down.

This axis depends on one thing we don't control. About a third of customers have no current or savings account with us, and half never had a salary credit here. Without a regular bureau salary feed many of them stay Unknown: today that's 58 percent of card customers at 61 to 180.

Where we do see the money, ability separates customers clearly. 31 percent of High-ability card customers were back below 61 DPD three months later, against 8 percent of those with no evidence; and 59 against 20 percent made a payment. At 180+, Moderate or High ability counts as a positive signal, for 6.5 percent of card accounts.

We aim to close ability by 20 November too, but it may follow slightly later.

---

## Part 2 · From states to a strategy

### Slide 12 · From states to a strategy

Part 2 is a first look, not a plan; none of it has been agreed with GRR yet.

Combined, the states give far more personas than anyone could act on. So we narrow the question to the cases kept in-house, where a strategy is actually needed, and end with a short list for the strategy workshop.

### Slide 13 · Combined, the states give hundreds of personas: far too many to give each a strategy

A persona is one combination of states: one of six deterioration states, one of nine locatability cells, one of three credibility bands and one of four ability bands. That's 648 possible personas, before anything from UC1.

The transcript signals, like stated intent, a hardship reason or a dispute, come on top, and each one multiplies the count again.

Many of these combinations really occur. On cards in August, 393 do, and 222 of them have ten or more accounts. On loans, 323 occur, and only 111 have ten or more. Many hold just a handful of accounts.

Nobody can write and run a separate strategy for hundreds of personas. So we need a way to decide where a strategy is actually needed.

### Slide 14 · Only the cases we keep in-house need a strategy of their own

The way out is the first decision every case meets: allocation.

Once a case goes to an agency, the agency works it on the policy's terms and is paid commission on the cash it collects. The non-workable pool, the customers least likely to pay, is referred out under the policy as well. In neither case do we need a persona-level strategy.

Only the cases we keep in-house need one: which offer, which agent, which channel.

So the question changes. It's no longer "a strategy for every persona". It's "which personas earn in-house effort, and what do we do with them".

### Slide 15 · How an account gets a tier: by what its persona actually paid

Here's how we'd sort personas into tiers, in three steps.

1. **Describe each account:** one state on each of the four axes, which together form its persona.
2. **Measure what it paid:** for each persona, take every account in May and add up everything it paid from June to August, divided by the number of accounts. That's an observed average, not a model, and it combines how often and how much. For example, 400 accounts paying 70,000 dirhams is 175 dirhams per account.
3. **Rank and cut:** rank the personas large enough to judge, which covers 97 percent of card accounts, and cut the list. 1,250 dirhams and above goes in-house, under 175 goes to the non-workable pool, and agency is in between.

These cut-offs are only illustrations from the data. GRR would set the real ones from the agency commission rate card and the in-house cost.

### Slide 16 · In-house would take a sixth of card accounts and half the money collected

With those illustrative cut-offs, and tested on unseen months:
- **In-house** would take 17 percent of card accounts and 48 percent of the money collected, recovering about 10 percent of principal in three months.
- **Agency** takes 54 percent of accounts and 46 percent of the money.
- **Non-workable** is 29 percent of accounts but only about 6 percent of the money, recovering just over half a percent.

In-house is mostly customers curing now or cured before, who are credible or able. The non-workable pool is mostly those who stopped suddenly or never paid, and can't be reached.

Look at the call days: the non-workable pool still takes nearly 11 call days per account in three months, almost as many as in-house. That's collector time that could go elsewhere.

On loans the order holds as well, but the exact thresholds move more, because the loan book is smaller.

### Slide 17 · In-house is where we talk to customers, so that is where UC1 adds its signals

The transcript work, UC1, only has something to say where a conversation took place, and that differs sharply across the groups. In the last three months, 89 percent of in-house card accounts had a right-party contact, against 45 percent of the agency group and 16 percent of the non-workable pool.

The transcript signals are what customers tell us: their intent to pay, a change in income or job, a hardship reason, a dispute, a promise made on the call. These come from what customers say on calls, so most of them will come from the in-house cases. That's exactly where a strategy is needed, and where the extra detail is worth the most.

### Slide 18 · The in-house personas become a short list for GRR to give each a strategy

This is where it leads. Most personas fall to the agency or the non-workable pool and need nothing more from us. The in-house tier is a much shorter list: 51 personas on cards, and just 26 of them cover 80 percent of in-house accounts. On loans it's 11 of 16.

Here are the five largest on cards. All five are reachable, while credibility and ability vary, from low credibility with unknown ability to moderate credibility with low ability.

This list is a first cut from one month's data. Before the workshop we'll confirm it holds from month to month.

The way we'd use it: the data proposes the list, UC1 refines it with what customers tell us, and GRR decides the offer, agent and channel for each persona in the strategy workshop. The simplification comes from GRR, not from us merging states.

That's the end of the main story. Thank you. Happy to take questions; the appendix has the detail.

---

## Appendix · use only when asked

### Slide 19 · Signals, rules and governance

The backup slides: where each signal comes from, the exact rules, and the status of each axis.

### Slide 20 · What each group could mean, for discussion

For discussion only, not agreed with GRR. Each group is paired with a treatment the policy already provides; nothing here is a new process.
- **In-house:** customers curing now or cured before, reachable, credible or able. Half of them pay within three months, so skilled collectors convert them with the existing tools: CARES settlements, a restructure or a deferral.
- **Agency:** mostly customers who stopped suddenly or cured before and can't be reached. Place them with agencies at 61 to 180, with skip tracing where they appear to be abroad.
- **Non-workable:** customers who stopped suddenly or never paid and can't be reached. The policy allows either referral to agencies with HOD approval, or no calling with dunning only, as for Dead Beat accounts.
- **At 180+:** the 12 percent with a positive signal are lifted out of the pool for an in-house attempt.

### Slide 21 · How a pilot could test it

If the workshop takes this forward, a pilot would test each group against business as usual, with a random split inside each tier for three months:
- **In-house:** skilled collectors with the settlement tools against the current process.
- **Agency:** placement at 61 to 180 against in-house calling.
- **Non-workable:** agency referral or dunning only against business as usual. That hold-out shows exactly what, if anything, is lost by taking collector time away.

We'd measure meaningful payments and roll rates, the amount collected per account, recovery of principal, and call days and cost per dirham collected; at 180+, the flagged group against the rest.

On sizing: for cards, the agency and non-workable tiers fill both arms in a single month for a five-point lift. In-house needs a ten-point target, and loans need ten points and pooling over months. The same policy and compliance rules apply to every arm, with a monthly readout and a stop rule.

### Slide 22 · Risk score

Is a risk score still worth building? We tested it on accounts and months the method had not seen.

Ranking power is measured as the area under the curve, where 0.5 is chance and 1 is perfect:
- the DPD bucket alone reaches 0.65 on cards and 0.62 on loans;
- the personas reach 0.83 and 0.77, better in every test;
- adding the bucket to the personas adds almost nothing;
- a simple model on the same inputs adds about two points.

So a model adds a little, consistently. Risk score modelling is planned for Phase 2, where a fuller model, using bureau and other domains the axes don't use yet, can be tested against the personas.

### Slide 23 · Appendix A: Signals and their sources

Every source is an existing dataset we already run; no new data feed is needed. Customer signals such as salary, CASA, bounces and logins are read across all of the customer's accounts, because the delinquent account is usually not where the salary lands. Windows are short and end at the month end: three months at 61 to 180, six at 180+.

### Slide 24 · Appendix B: The scoring rules at a glance

The exact rules, for detailed questions:
- **Deterioration** is a decision tree on the DPD history.
- **Locatability** combines location and reachability, with a Deceased override.
- **Credibility** adds up points: High from four, Moderate from two, and a refusal lowers one band.
- **Ability** counts strong evidence families.

Every threshold is in that axis's model specification document.

### Slide 25 · Appendix C: How a journey state is assigned

Deterioration is a short ordered tree. First a guard: if the history starts already delinquent, we can't see how the customer fell in, so the state is Unknown unless the account is stabilized. Then come early payment default, stabilized, repeat delinquent, straight roller split by tenure, and everything else is a slow roller. One-month glitches and billing-cycle jumps are repaired before the tree runs, and every repair is counted.

### Slide 26 · Appendix: New ability rule vs the old

This is how the new ability rule compares with the old one, which rested on income plus the CASA balance.

The old High needed a CASA balance above a floor. The bank sweeps balances against the overdue amount, so High almost never fired. The new rule counts four evidence families instead.

- **Share of accounts:** High grows four to eight times in every book. Low rises for loans and at 180+, mostly customers who keep another product current with us. Cards at 61 to 180 move slightly into Unknown, on purpose: those customers' only account activity was fees or payments on their own loan, which says nothing about ability.
- **Outcomes over the next three months:** cure here means below 61 DPD at month 3, pay means any payment, roll means a worse bucket. Every state orders all three in the right direction. For cards every step is significant, also within the same DPD bucket. For loans, High and Moderate can't be separated yet, because High is still small.

Remember: Unknown means we can't see the customer's money, not that they have none.

### Slide 27 · Appendix D: Status and sign-off

Where each axis stands:
- **Deterioration and locatability:** closed and signed off by GRR.
- **Credibility:** due for sign-off by 20 November.
- **Ability:** may be signed off by then too, or follow later.
- **UC1 transcript signals:** join between 20 November and 11 December.
