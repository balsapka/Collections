# Synthesized Features: speaker script

This is what to say on each slide, start to finish, for deck version 100 (33 slides). Slides 1–15 are the main talk, about 22 minutes. Slides 16–22 are Part 3, for discussion: use them if there is time and GRR wants to go into allocation, about 8 minutes. Slides 23–32 are backup: use them only when a question calls for them.

Slide numbers follow the artifact and the content pack, where the alternative credibility slide is 10b. In the PDF and PowerPoint that slide is number 11, so every later slide is one number higher there.

---

## Part 0 · Opening

### Slide 1 · Synthesized Features

Good afternoon. Today is about where we are on UC2, the synthesized features use case. The framework itself has been workshopped with GRR over the past two months. What I want to walk you through is what the framework is, what each synthesized feature is, what the results show, how the UC1 transcript signals will join it, and how we would pilot and measure it.

Unless a slide says otherwise, every number comes from the August 2026 month end.

### Slide 2 · Summary

Before going into detail, here is the whole story on one page, in three messages: where we are today, what we built, and what it shows.

First, where we are today. Beyond 60 days past due there is no model. Cases are allocated by bucket and product, and the late buckets are exactly where the behavioural data runs dry.

Second, what we built. The UC2 synthesized features take signals from every data domain we hold and condense them, every month, into four answers per account. The four answers revolve around four high-level questions: How did they get here? Can we reach them? Will they pay? And can they pay?

Third, what it shows. Three numbers:

- If we had told collectors at the start of the month which fifth of card accounts to focus on, that fifth would have brought in 54 percent of everything collected over the next three months. That was tested on months and accounts the method had never seen.
- Within the same DPD bucket, 91 to 120, some groups of loan customers pay 9 percent of the time and others 76 percent. That's about eight times apart, inside a single bucket.
- At 180+, 12 percent of accounts show a positive signal. About one in five of them pays, against under 3 percent of the rest.

On next steps: each synthesized feature has its own model specification document, with the full logic and comprehensive back-test results. Two of the four have been signed off by Architha and Nayeema. By 20 November we plan to close the other two, pending the final results and your feedback today. One of them may follow slightly later, as it depends on a data input we are still waiting for.

From 20 November to 11 December, we combine the UC1 transcript signals with these features, with support on actions. Pilot selection runs from 11 to 20 December, and the pilot starts on 4 January.

### Slide 3 · Allocation follows the bucket, not the customer

I'll start with how things work today.

Who works the case is rule-based: the DPD level and the product decide whether it goes to an in-house team or to an agency.

What we offer comes from the pre-approved settlement programmes, PLUS and CARES. Their waivers are fixed by product and DPD stage.

At 180+ the book is large, about 374 thousand accounts, and it's worked as one pool.

The common thread: the bucket tells us how late someone is. It doesn't tell us whether we can reach them, whether they can pay, or whether they've kept their word. And at 180+, a small share still shows signs of being able to pay. Finding them is the 180+ goal.

### Slide 4 · Everything we know about a customer, condensed into a few states

So this is what "synthesized features" means.

On the left you can see all the different data domains we hold internally: card billing and transactions, CASA transactions, salary, loan instalments, bureau, digital logins, collector activity and customer records. The call transcripts are joining.

We synthesize them into signals. From all these data domains we build more than fifty signals, questions like: is salary regular, do our calls connect, are promises kept, was the customer last seen abroad, are they paying while late.

That is where the value lies. Late in delinquency, most of these sources look dry on their own: the card is blocked, transactions thin out, calls go unanswered. But each one still holds some signal. Synthesizing means drawing out every piece of it, from every domain, and putting the pieces together. Combined, they tell us far more than any single source can.

The signals are then condensed into four persona traits, or states, per account, every month. These are deterioration, which answers how did they get here; locatability, which answers can we talk to them; payment credibility, which answers will they pay; and finally ability: can they pay? The conversations from UC1 will join the same picture.

There are two goals. At 61 to 180, personas drive allocation across the board. At 180+, we're trying to find the customers with any positive signal to pay.

### Slide 5 · Three questions before a case reaches a collector

Here's the framework in one picture, in the order a case meets it.

First: how did they get here? The deterioration journey tells us whether the customer is curing now, has cured or paid before, paid for a while and then stopped suddenly, or never paid at all. That gives context, and a flag for which cases to prioritise.

Second: can we talk to them? Where we last saw them, and whether our calls connect. This doesn't filter anyone out, and it doesn't decide the route on its own. It tells us how a case can be worked: by phone, or with tracing for those who look abroad.

Third: what can we offer? This is the nuance: will they pay, which is credibility; can they pay, which is ability and still in progress; and soon what customers tell us on calls, from the transcript work.

Together these decide the offer and who should work the case. The final personas will come out of workshops with GRR in the coming few weeks.

### Slide 6 · Built to be explained and trusted

A few design choices behind the framework.

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

On the left is the waterfall: six questions about the deterioration journey, asked in order, and the first "yes" decides the state. Has nothing been paid since the first months? That's an early payment default. Has the account held at one level for months? Stabilized. Is it back within a year of curing? Repeat delinquent. Did it fall to 61+ fast after a year of good history? Seasoned straight roller; if that happened in the first year, early-life straight roller. Everything else is a slow roller: it fell slowly, paying on the way.

These six states fall into four families:

- **Curing now:** stabilized customers. They've stopped falling.
- **Cured or paid before:** slow rollers and repeat delinquents. They've paid before, but they're falling now.
- **Paid, then stopped suddenly:** straight rollers, seasoned or early in life. They paid for a while and then stopped all at once.
- **Never paid:** early payment defaults.

On the right is the August mix, the share of accounts in each family. The big one: half of loans and six in ten card accounts paid for a while and then stopped all at once. That points to an event, not a habit.

Which family a customer falls into matters. 60 percent of card accounts curing now made a meaningful payment within three months; of those who only cured before, 22 percent did. And this holds within every DPD bucket: inside the same bucket, how likely a customer is to pay varies widely depending on which deterioration family they're in. Loans show the same pattern.

This axis is closed and signed off. Whatever the path, the next question is whether we can talk to them.

### Slide 9 · A2 Locatability: only one in five card customers at 61–180 can be reached

Locatability tells us how a case can be worked. Two questions.

Where did we last see the customer? We look at logins and in-person card use. A travel purchase or a collector note is a sign they've left. The latest evidence wins.

Do our calls connect? If the recent call days all failed with no contact since, the customer is Non-Reachable; a recent contact makes them Reachable.

The matrix shows how the two combine. Only about one in five card customers, and one in four loan customers, at 61 to 180 are reachable.

The largest single group, about a third, look abroad and don't answer. For them, tracing matters most.

At 180+ we only look for positives, and being reachable counts as one: 3.7 percent of card accounts and 4.8 percent of loans.

Reachability carries real information. Customers who look credible or able but can't be reached pay about a third as often as reachable customers with the same profile, even though they get as many call days.

But it isn't a filter: it informs how we work a case, by phone or with tracing.

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

### Slide 10b · Alternative: every promise earns credit, keeping it earns more

*Optional: show it right after slide 10 if the discussion turns to how promises score.*

This is an alternative to the scoring on the previous slide, for discussion. Only the promise points change: any promise in the last twelve months earns a point, even one that was broken or is still open, and keeping it earns more: three for kept, two for partly kept. No promise stays at zero. Paying while delinquent, the record before, the bands and the refusal rule are unchanged.

Penalising a broken promise sounds logical: if customers break their word, we should believe them less. The data say otherwise, for three reasons.

First, the warning sign is silence, not a missed promise. Card customers who broke a promise paid six points more often than comparable customers who never made one: same bucket, same payment record, same reachability.

Second, most broken promises are not a walk-away. Close to half of broken card promises still had money behind them, paid in part or late, and those customers pay like partly kept.

Third, a strict deadline marks late payers as broken, yet customers who pay a promise a few weeks late go on to pay like those who paid on time.

Reliability still counts: kept stays above partly kept, and partly kept above broken. We are not rewarding a broken promise; we stop treating it as worse than never engaging at all.

Because every promise gains a point and the bands stay the same, customers only move up. At 61 to 180, High or Moderate grows from 26 to 45 percent of card customers, and those moving up to High pay their due 51 percent of the time, against 27 percent for those who stay Moderate. The ranking improves in every month and every DPD band. And with this scoring the choice of deadline barely matters: the month-end deadline costs almost nothing against 30 days.

### Slide 11 · A4 Ability: ability tells us what a customer can realistically be offered

Ability is still in progress.

We look at four families of evidence:

- income, meaning regular salary, ours or bureau;
- other money arriving or held;
- the customer's own spending;
- activity on their other products with us.

We count how many are strong. Two or more is High, one is Moderate, some evidence but nothing strong is Low, and no evidence at all is Unknown. A bounced cheque or a returned direct debit moves the customer one band down.

This axis depends on one thing we don't control. About a third of customers have no current or savings account with us, and half never had a salary credit here. Without a regular bureau salary feed many of them stay Unknown: today that's 57 percent of card customers at 61 to 180. The bureau's bulk salary pull reaches only about 1 percent of customers.

Where we do see the money, ability separates customers clearly. 31 percent of High-ability card customers were back below 61 DPD three months later, against 8 percent of those with no evidence; and 59 against 20 percent made a payment. At 180+, Moderate or High ability counts as a positive signal, for 6.3 percent of card accounts.

We aim to close ability by 20 November too, but it may follow slightly later.

---

## Part 2 · From states to personas

### Slide 12 · From states to personas

Part 2 puts the four states together into personas. Combined, they give far more personas than anyone could act on, so I'll show where the value actually sits, and finish with what we hand over: every account's persona, every month.

### Slide 13 · Combined, the states give hundreds of personas: far too many to give each a strategy

A persona is one combination of states: one of six deterioration states, one of nine locatability cells, one of three credibility bands and one of four ability bands. That's 648 possible personas, before anything from UC1.

The transcript signals, like stated intent, a hardship reason or a dispute, come on top, and each one multiplies the count again.

Many of these combinations really occur. On cards in August, 393 do, and 171 of them hold fewer than ten accounts each. On loans, 323 occur, and 212 hold fewer than ten.

Nobody can write and run a separate strategy for hundreds of personas. The good news is on the next slide: size and value sit in different personas.

### Slide 14 · 46 personas hold 11% of the card balance and bring in 37% of the money collected

This slide shows that we don't need to treat every persona alike.

The top strip is the card balance, the bottom strip is the money collected over the next three months, and the colours are the same groups in both. By money collected I mean everything paid over those three months, added up.

Look at the dark block first. The ten largest personas hold 40 percent of the balance, but bring in only 10 percent of the money. All of them have low credibility, and most can't be reached.

Now the blue block: 46 personas, customers we can reach who have High or Moderate credibility. They hold 11 percent of the balance and bring in 37 percent of the money. Over three months they pay back about 10.6 percent of everything they owe, against 3.1 percent for the card book as a whole. And it isn't just customers who are already curing: about a third of that money comes from customers who are not curing now.

Everything else, in grey, pays about in line with its size.

These are payments under today's handling. And it is not a one-month result: I checked May on its own against January to April, and nearly nine in ten personas paid above or below the average in both.

### Slide 15 · What we hand over: every account's persona, every month

This is the deliverable. A persona is the combination of all four states, plus whatever we distil from the UC1 call transcripts. Every month, every account gets its persona.

With it come the model specification documents, one per feature, with the final logic and results. Whether we also hand over the supporting signals behind each state depends on whether GRR wants to see them in DCORE; that is still to agree.

The UC1 signals start joining the personas between 20 November and 11 December, so they are in before pilot selection, from 11 to 20 December, and the pilot from 4 January. What to do with each persona stays GRR's decision.

That's the end of the main story. Thank you. If there's time, Part 3 takes it one step further, for discussion; otherwise, happy to take questions.

---

## Part 3 · For discussion · use if there is time

### Slide 16 · A data-driven view of allocation

This part is for discussion and has not been agreed with GRR. It looks at allocation through the data: which cases need a strategy of their own, how personas could be sorted into tiers from what they have actually paid, how stable those tiers are from month to month, and where the UC1 signals add most. The decisions stay with GRR.

### Slide 17 · Only the cases we keep in-house need a strategy of their own

If we take it further, the way through the many personas is the first decision every case meets: allocation.

Once a case goes to an agency, the agency works it on the policy's terms and is paid commission on the cash it collects. The non-workable pool, the customers least likely to pay, is referred out under the policy as well. In neither case do we need a persona-level strategy.

Only the cases we keep in-house need one: which offer, which agent, which channel.

So the question changes. It's no longer "a strategy for every persona". It's "which personas earn in-house effort, and what do we do with them".

### Slide 18 · How an account gets a tier: by what its persona actually paid

Here's how we'd sort personas into tiers, in three steps.

1. **Describe each account:** one state on each of the four axes, which together form its persona.
2. **Measure what it paid:** for each persona, take every account in May and add up everything it paid from June to August, divided by the number of accounts. That's an observed average, not a model, and it combines how often and how much. For example, 400 accounts paying 70,000 dirhams is 175 dirhams per account.
3. **Rank and cut:** rank the personas large enough to judge, which covers 97 percent of card accounts, and cut the list. 1,250 dirhams and above goes in-house, under 175 goes to the non-workable pool, and agency is in between.

These cut-offs are only illustrations from the data. GRR would set the real ones from the agency commission rate card and the in-house cost.

Testing added two refinements:

- **Pool the months.** A list built from a single month moves too much, so the table is pooled over several months.
- **Add a band around the cut.** A persona enters in-house only when it's clearly above the cut, and leaves only when it's clearly below it: about ten percent either side.

The cut itself matters far more than anything else. Moving it twenty percent either way takes the card in-house list from 70 personas to 44. Changing how we define reachability swaps only a handful.

### Slide 19 · In-house would take a sixth of card accounts and half the money collected

With those illustrative cut-offs, and tested on unseen months:

- **In-house** would take 17 percent of card accounts and 48 percent of the money collected, recovering about 10 percent of principal in three months.
- **Agency** takes 54 percent of accounts and 46 percent of the money.
- **Non-workable** is 29 percent of accounts but only about 6 percent of the money, recovering just over half a percent.

In-house is mostly customers curing now or cured before, who are credible or able. The non-workable pool is mostly those who stopped suddenly or never paid, and can't be reached.

Look at the call days: the non-workable pool still takes nearly 11 call days per account in three months, almost as many as in-house. That's collector time that could go elsewhere.

On loans the order holds as well, but the book is smaller and the list thinner. How stable these tiers are is on the next slide.

### Slide 20 · Keeping the tier list stable from month to month

This is work in progress. A tier list is only useful if it stays put from one run to the next, so we checked how often an account changes tier while its persona stays the same.

With today's method, one month per persona, that's 13 percent of card accounts and 35 percent of loan accounts, every month.

Most of it is chance rather than real change. Many personas hold only a handful of accounts, and one large payment moves their average across the cut. Two random resamples of the same month already disagree on 27 percent of loan tiers.

So the fix is more accounts behind each estimate:

- **Pooling** several months halves the churn.
- **A band around the cut**, or capping very large payments, helps a little more.
- **Broader groups:** deciding the tier on the deterioration family, reachability and whether the customer is credible or able brings it down to 1 percent on cards and 5 percent on loans.

A cut that moves with the book, or that keeps a fixed share of accounts, doesn't help on its own. And none of these options cost money collected.

Next, we want to pool over a longer window, using history from before 2026; try broader groups that keep location; and re-run the list every three months, with triggers for an earlier re-run if the in-house paid rate or the book's collection level leaves its usual range. All of this rests on five months of data, so we'll confirm it on later months once the payment data runs past August.

### Slide 21 · In-house is where we talk to customers, so that is where UC1 adds its signals

The transcript work, UC1, only has something to say where a conversation took place, and that differs sharply across the groups. In the last three months, 89 percent of in-house card accounts had a right-party contact, against 45 percent of the agency group and 16 percent of the non-workable pool.

The transcript signals are what customers tell us: their intent to pay, a change in income or job, a hardship reason, a dispute, a promise made on the call. These come from what customers say on calls, so most of them will come from the in-house cases. That's exactly where a strategy is needed, and where the extra detail is worth the most.

### Slide 22 · The in-house personas become a short list for GRR to give each a strategy

This is where it leads. Most personas fall to the agency or the non-workable pool and need nothing more from us. The in-house tier is a much shorter list: 51 personas on cards, and just 26 of them cover 80 percent of in-house accounts. On loans it's 11 of 16.

Here are the five largest on cards. All five are reachable, while credibility and ability vary, from low credibility with unknown ability to moderate credibility with low ability.

Reachability helps, but it doesn't decide who lands in-house: about one in five in-house card accounts, and two in five on loans, are not reachable.

We checked whether the list holds from month to month. On cards a core is steady: the personas that are in-house in every month cover over a third of in-house accounts, and about half with those in-house four months out of five. So for the workshop we'd build the list from several pooled months, not from one. On loans the list is still thin and moves, so we'd treat it as provisional.

The way we'd use it: the data proposes the list, UC1 refines it with what customers tell us, and GRR decides the offer, agent and channel for each persona in the strategy workshop. The simplification comes from GRR, not from us merging states.

That's the end of the discussion part. Thank you. Happy to take questions; the appendix has the detail.

---

## Appendix · use only when asked

### Slide 23 · Signals, rules and governance

The backup slides: where each signal comes from, the exact rules, and the status of each axis.

### Slide 24 · What each group could mean, for discussion

For discussion only, not agreed with GRR. Each group is paired with a treatment the policy already provides; nothing here is a new process.

- **In-house:** customers curing now or cured before, reachable, credible or able. Half of them pay within three months, so skilled collectors convert them with the existing tools: CARES settlements, a restructure or a deferral.
- **Agency:** mostly customers who stopped suddenly or cured before and can't be reached. Place them with agencies at 61 to 180, with skip tracing where they appear to be abroad.
- **Non-workable:** customers who stopped suddenly or never paid and can't be reached. The policy allows either referral to agencies with HOD approval, or no calling with dunning only, as for Dead Beat accounts.
- **At 180+:** the 12 percent with a positive signal are lifted out of the pool for an in-house attempt.

### Slide 25 · How a pilot could test it, if the strategy workshop takes it forward

If the workshop takes this forward, a pilot would test each group against business as usual, with a random split inside each tier for three months:

- **In-house:** skilled collectors with the settlement tools against the current process.
- **Agency:** placement at 61 to 180 against in-house calling.
- **Non-workable:** agency referral or dunning only against business as usual. That hold-out shows exactly what, if anything, is lost by taking collector time away.

We'd measure meaningful payments and roll rates, the amount collected per account, recovery of principal, and call days and cost per dirham collected; at 180+, the flagged group against the rest.

On sizing: for cards, the agency and non-workable tiers fill both arms in a single month for a five-point lift. In-house needs a ten-point target, and loans need ten points and pooling over months. The same policy and compliance rules apply to every arm, with a monthly readout and a stop rule.

### Slide 26 · Risk score: personas rank payers far better than the bucket

Is a risk score still worth building? We tested it on accounts and months the method had not seen.

Ranking power is measured as the area under the curve, where 0.5 is chance and 1 is perfect:

- the DPD bucket alone reaches 0.65 on cards and 0.62 on loans;
- the personas reach 0.83 and 0.77, better in every test;
- adding the bucket to the personas adds almost nothing;
- a simple model on the same inputs adds about two points.

So a model adds a little, consistently. Risk score modelling is planned for Phase 2, where a fuller model, using bureau and other domains the axes don't use yet, can be tested against the personas.

### Slide 27 · Appendix A: Signals and their sources

Every source is an existing dataset we already run; no new data feed is needed. Customer signals such as salary, CASA, bounces and logins are read across all of the customer's accounts, because the delinquent account is usually not where the salary lands. Windows are short and end at the month end: three months at 61 to 180, six at 180+.

### Slide 28 · Appendix B: The scoring rules at a glance

The exact rules, for detailed questions:

- **Deterioration** is a decision tree on the DPD history.
- **Locatability** combines location and reachability, with a Deceased override.
- **Credibility** adds up points: High from four, Moderate from two, and a refusal lowers one band.
- **Ability** counts strong evidence families.

Every threshold is in that axis's model specification document.

### Slide 29 · Appendix C: How a journey state is assigned

Deterioration is a short ordered tree. First a guard: if the history starts already delinquent, we can't see how the customer fell in, so the state is Unknown unless the account is stabilized. Then come early payment default, stabilized, repeat delinquent, straight roller split by tenure, and everything else is a slow roller. One-month glitches and billing-cycle jumps are repaired before the tree runs, and every repair is counted.

### Slide 30 · Appendix: New ability rule vs the old

This is how the new ability rule compares with the old one, which rested on income plus the CASA balance.

The old High needed a CASA balance above a floor. The bank sweeps balances against the overdue amount, so High almost never fired. The new rule counts four evidence families instead.

- **Share of accounts:** High grows four to nine times in every book. Low rises for loans and at 180+, mostly customers who keep another product current with us. Cards at 61 to 180 move slightly into Unknown, on purpose: those customers' only account activity was fees or payments on their own loan, which says nothing about ability.
- **Outcomes over the next three months:** cure here means below 61 DPD at month 3, pay means any payment, roll means a worse bucket. Every state orders all three in the right direction. For cards every step is significant, also within the same DPD bucket. For loans, High and Moderate can't be separated yet, because High is still small.

Remember: Unknown means we can't see the customer's money, not that they have none.

### Slide 31 · Appendix: A 30-day window to keep a promise ranks customers best

The credibility axis judges each promise to pay as kept or broken by whether the customer paid by a deadline. We back-tested three deadlines:

- **Today's rule:** the next statement for cards, the end of the following month for loans.
- **The end of the month of the promise:** proposed for loans and for all 180+ accounts.
- **A lenient 30 days** after the promise.

We scored March to May 2026 under each rule and asked how well the credibility state ranks customers on paying a monthly due over the next three months, in all four books. The number is the AUC: 0.5 is a coin toss, higher is better.

30 days ranks best or equal in every book: about 0.02 better than the statement for cards, and level with today's rule for loans. The end of the promise month ranks worst for loans and at 180+, by 0.01 to 0.02. Every gap of that size is outside the 95 percent interval and holds in each of the three months.

The reason is on the right. A loan customer who pays a promise in the following month goes on to pay just like one who paid on time. So a stricter deadline marks payers as broken, and the customers it moves down keep paying like the state they came from.

We also checked the accounts with no promise or payment record, which now sit in Low instead of Unknown. They pay less than the rest of Low in every book, so Low is the right place for them. Most are young accounts: early payment default, not unknown customers.

So the data favour 30 days: the most lenient rule for the customer is also the most predictive. The choice of rule is GRR's.

### Slide 32 · Appendix D: Status and sign-off

Where each axis stands:

- **Deterioration and locatability:** closed and signed off by GRR.
- **Credibility:** due for sign-off by 20 November.
- **Ability:** may be signed off by then too, or follow later.
- **UC1 transcript signals:** join between 20 November and 11 December.
