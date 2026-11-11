# Handoff 63: `collections_policy_facts.md` (policy facts for the allocation tiers), lines 1-304

## Context for Claude Code

- Source: 6 phone photos of VS Code, file `tmp_validation/persona_deck/collections_policy_facts.md`, in the dev container `retail.collections.risk_profiling`. Open tabs: `pipeline_registry.py`, `fill_in.md`, `fill_in_changes.md`, the PDF `Emirates NBD Services - FR Policy on Operations - Jul2025.pdf`, and `Extension of PLUS and CARES 2026.docx`.
- This is the written-up file behind the terminal answer in handoff 62 (agency commission vs outright sale). It extracts policy facts from the two documents in `data/input/docs/`. Editor blame text on line 1 reads "You, 3 seconds ago • Add collections policy facts for allocation tie…" (that is editor ghost text, not file content, and it is cut off at the screen edge).
- Photos merged by editor line number. Lines 1-304 are covered. Line 304 is the last line I can see; it is empty, and I can't tell whether the file continues below it.
- Format: `NNN  text`, NNN is the editor line number. The file is hard-wrapped, so each editor line is one row. Nesting is shown by the leading spaces after the number (continuation lines of a bullet are indented 2 spaces).
- Quotation marks are straight as shown. The `…` (ellipsis character) and `§` are real characters in the source.

## Transcription

```
  1  # Collections policy facts for the allocation tiers
  2  
  3  Read-only extraction from the two documents in `data/input/docs/`. Nothing is inferred or taken from general industry
  4  knowledge.
  5  
  6  **Document keys**
  7  - **FRP** = *Emirates NBD Services - Financial Remediation Policy on Operations*, Version 1.2, July 2025 (14 pages;
  8    cover dated 4 July 2025; "Policy Date May 2023"; next review July 2027). File: `Emirates NBD Services - FR Policy on
  9    Operations - Jul2025.pdf`.
 10  - **PC** = *Extension of PLUS and CARES Settlement Programs for Delinquent Customers* (2026 proposal; figures to Nov
 11    2025). File: `Extension of PLUS and CARES 2026.docx`. No page numbers, so it is cited by heading and table.
 12  
 13  **Status flags that apply throughout**
 14  - FRP is not marked draft or superseded. It states it is "reviewed and updated every two years, or whenever there is a
 15    significant change" (§1b, p.3). The sign-off page (p.14) lists names and the approved date July 2025; the text
 16    extraction shows no visible signatures.
 17  - PC is a **proposal** ("recommend extending", Proposal). It shows no approval block, date or author, so its 2026 status
 18    is unconfirmed.
 19  - Three documents that FRP defers to are **not in the folder**: the "FR Incentive Structure Document" (§8, p.10), the BI
 20    "Allocation Process" document (§4, p.5), and the "approved DOA memo" (§6, p.9).
 21  
 22  ---
 23  
 24  ## Part 1 - Answers
 25  
 26  ### A. Allocation at 61-180 DPD
 27  
 28  **1. How are 61-180 DPD accounts allocated? Criteria?**
 29  - **Both in-house teams and agencies.** The allocation is rule-based, run by BI, from GRR segmentation models and
 30    strategies.
 31    - FRP §4 Allocation Process, p.5: "Using the DPD level and product as the foundation, the delinquent pool is
 32      distributed amongst the teams (in-house and agencies) based on pre-defined guidelines."
 33    - FRP §1 Introduction, p.3: "The allocation is rule-based and is done by the Business Intelligence ('BI') team." The
 34      logic "is coded in Dcore".
 35  - **Guidelines listed** (FRP §4, p.5): "Customer level tagging", "Optimal ACR", "Pool level precedence", "Equal
 36    balancing amongst teams".
 37  - **Criteria for referral to agencies** (FRP §8 Commission Payout, p.10): "Based on the product, DPD stage,
 38    contactability, charge-off vintage (if account is in 180+ DPD) and the strategy, accounts are referred to 3rd party
 39    collection agencies".
 40  - The in-house vs agency split by "difficulty in collection and contactability" is stated only for the Recovery Stage,
 41    180+ (FRP §2c, p.3).
 42  - Balance or score thresholds for the 61-180 split: **not found in the documents** (detail is in the separate BI
 43    Allocation Process document). PC: not found in the documents.
 44  
 45  **2. Can accounts below 180 DPD be placed with agencies? Conditions, approver, minimum DPD / balance limit?**
 46  - **Yes, the policy treats agency placement below 180 as existing practice.**
 47    - FRP §3, p.4 (Appointment of Third-Party Agency Letter): "for any delinquent account (upto 180+ DPD) allocated to the
 48      agencies where TOS > 0."
 49    - FRP §10 Retention Criteria, p.11: "allocated to external agencies (buckets/recoveries) should not exceed beyond 6
 50      months."
 51    - FRP §8, p.10: "Approved commission structure for each DPD stage and product."
 52  - **Conditions:** product, DPD stage, contactability and strategy (quote under Q1).
 53  - **Approver:** for the non-workable pool, "with an approval from HOD" (FRP §4, p.5). Changes, extensions or exceptions
 54    to allocation logic go to "Head of FR or the team managers" (FRP §4, p.5).
 55  - **Card handling:** FRP §5 II(g), p.9: "All cards allocated to agency are raised for bulk cancellation prior to
 56    allocation as per PCI DSS." Also: "For all credit cards reaching 61 DPD and above, a bulk cancellation (block X)
 57    request is raised."
 58  - Minimum DPD or balance limit for agency placement below 180: **not found in the documents**.
 59  
 60  **3. "Non-workable", "non-contactable", "least likely to pay"?**
 61  - **Yes, one concept.** FRP §4, p.5: "the non-workable pool of accounts, particularly those non contactable, least
 62    probable to pay are referred to the external agencies based on internal assessments."
 63  - Purpose: "improved collection and focus on workable accounts" and to optimise the in-house "Account Coverage Rate
 64    ('ACR')", "with an approval from HOD" (FRP §4, p.5).
 65  - The text gives **no DPD scope** (it sits in the general allocation section) and **no formal or numeric definition**:
 66    not found in the documents.
 67  - Related, undefined category: "Dead Beat Accounts classified by GRR" (see Q4).
 68  
 69  **4. Rule for reducing or stopping effort before 180+?**
 70  - **Yes, a no-calling rule that keeps letters/SMS/e-mail.** FRP §3, p.5: "No Calling activities on pre-due to charge off
 71    accounts with following conditions however dunning strategy (sms, emails, letters) to continue:"
 72    - "Credit Cards Principal Balance < AED 1000."
 73    - "Loan's Principal Balance < AED 1000."
 74    - "Dead Beat Accounts classified by GRR (exceptional accounts can be allocated based on FR HOD approval)."
 75  - Dunning exclusion grid (FRP §3, pp.4-5) includes "Outstanding less than 5000 or overdue amount less than 100 No Yes"
 76    (CPR "No", Non-CPR "Yes"). The text does not define what the Yes/No values mean.
 77  - Zero-principal cards: FRP §5 II(h), p.9: "Delinquent cards (31+DPD) having an outstanding of AED 25k or lower, with
 78    principal outstanding of AED 0 are raised for bulk write-off to NI/AST team".
 79  - Deviations from the grids: "approved by the FR Managers" (FRP §3, p.5).
 80  - PC: not found in the documents.
 81  
 82  ### B. Agency economics
 83  
 84  **5. How are agencies paid? Rate card?**
 85  - **Commission on cash collected; no fixed fee is mentioned.** FRP §8 Commission Payout, p.10: "Commission is paid to
 86    the agencies based on cash collection." and "Commission varies with the DPD stage and charge-off vintage of the
 87    account."
 88  - Other commission lines (FRP §8, pp.10-11): "Commission based on data enrichment for skip tracing activity.",
 89    "Commission for car repossession.", "Payout for any rolled out spot incentive programs or booster programs for
 90    remedial solutions."
 91  - **Rate card by DPD stage, charge-off vintage and product: not found in the documents.** No percentage or fee figure
 92    appears. It is held in the separate "FR Incentive Structure Document" (FRP §8, p.10).
 93  - Governance (FRP §8, p.11): "The agency commission structures are proposed by the FR team and approved by the Group
 94    Retail Risk and GCRO." and "The overall commission percentage will be maintained within the proposed levels."
 95  - **The only agency figures in the documents:**
 96    - Civil cases, FRP §8, p.11 (columns: Entity / Scenario 1 / Scenario 2):
 97      - In-House (incentive):
 98        - Scenario 1 - If POS and Legal cost are covered fully: "Eligible for incentive on 100% of cash collected"
 99        - Scenario 2 - If any POS or Legal cost are not fully covered: "70% of the cash collected will be considered for
100          incentive calculation,"
101      - Agency (commission):
102        - Scenario 1 - "Eligible for commission on 100% of cash collected"
103        - Scenario 2 - "Full Legal cost will be deducted from the cash collection for commission calculation"
104  
105    - Deceased cases, FRP §9, p.11: "In case of agency referral (Buckets/Recovery stage), if there is a payment through
106      insurance then agency commission payout is 10% of collected amount."
107  - PC: no agency commission content.
108  
109  **6. Placement types and terms?**
110  - "Standard commission rate card for agencies handling multiple consecutive buckets." (FRP §8, p.10). No further detail.
111  - Placement duration (FRP §10, p.11): "should not exceed beyond 6 months. The agencies are allowed to retain upto 15% up
112    to 1 year." Deviation needs "Head of Recoveries (Level 3) and AVP - collection Agency (Level 4)"; retention beyond 12
113    months needs "FR Head of Department (Level 2)".
114  - Allocation timing for cards (FRP §5 II(g), p.9): bulk cancellation "performed beginning of every cyclical allocation".
115  - Priority vs bulk, primary/secondary/tertiary placement, recall rules: **not found in the documents**.
116  
117  **7. Agency targets, minimum effort, recall?**
118  - Numeric targets, minimum effort requirements, recall rules: **not found in the documents**. The only related provision
119    is the retention limit (Q6).
120  - Qualitative oversight only, FRP §11 iii, pp.12-13: "The Agency Governance team ensures external collection agencies
121    meet bank policies and CPR"; "regular reviews of call standards and contract compliance". The metrics are not given.
122  
123  **8. Cost of in-house collection?**
124  - **No cost figure** (per account, per collector or per call): not found in the documents.
125  - In-house **incentives**, which are not costs: civil cases 100% / 70% of cash collected (Q5 table); deceased cases FRP
126    §9, p.11: "the agent's payout is 70% of the cash collected from insurance payout." Scorecards: FRP §8, p.10:
127    "dedicated scorecards for the calling and support teams with relevant KPIs".
128  - The optimal "Account to Collector Ratio ('ACR')" is named (FRP §4, p.5) with no value. The same section also expands
129    ACR as "Account Coverage Rate" (inconsistent in the source).
130  
131  ### C. Sale and write-off
132  
133  **9. Any sale of delinquent or charged-off debt to a third party?**
134  - **Not found in the documents.**
135  - Terms searched in both documents: sale, sell, sold, buyer, portfolio sale, debt sale, assignment, assign, transfer of
136    receivables, transfer, purchase, third party, 3rd party.
137  - Hits rejected, none being a sale of debt:
138    - Auction of repossessed property or vehicles (FRP §5 I c-d, p.7; also PC footnote **: "Only for accounts having a
139      shortfall balance post auction of repossessed vehicle").
140    - Fund and account "transfer" wording (FRP §5 II c, e, p.8).
141    - Placement with collection agencies for collection and commission (FRP §3, p.4; §8, p.10). No transfer of ownership
142      is stated.
143  
144  **10. When is an account charged off or written off? Does collection continue? Who collects?**
145  - **Charge-off:** the only DPD state stated. FRP §2 Treatment of Accounts table, p.3: "Charge-off Cycle 9 180+ DPD" (Credit
146    Cards cycle / Loans DPD). The row above reads "Bucket 6 Cycle 7 151-180 DPD".
147  - **Collection continues at 180+.** FRP §2c, p.3: "Recovery Stage (180+ DPD)… allocated to the in-house recoveries team
148    or to collection agencies based on the difficulty in collection and contactability." The 180+ dunning strategy runs to
149    "Legal Notice - Legal Action - Field Visit*" (FRP §3, p.4); legal action is by "in-house legal team or external legal
150    partners" (FRP §5 I, pp.5-6). The no-calling carve-out for small balances and Dead Beat accounts applies "pre-due to
151    charge off" (FRP §3, p.5).
152  - **Write-off:** appears only as a process, with no general DPD trigger and no loan write-off rule.
153    - Settlement Desk handles "writing off the liabilities for honored settlements" (FRP §5 II b, p.8).
154    - Zero-principal cards (31+ DPD, AED 25k or lower): quoted under Q4.
155  - **Provisioning:** FRP §13 Retail Provisioning Policy, p.13, in full: "Provisioning policy for retail products is
156    managed and governed by the GRR team." No thresholds.
157  - **Left undefined by the documents:**
158    - "GWO" (PC uses it without expansion: "90+ DPD and GWO stocks"; chart "Product of Flows (30 to GWO)"). The documents
159      do not say GWO equals charge-off.
160    - "NPA" (PC Background).
161    - Who collects after a formal write-off, and whether a written-off account leaves the books.
162    - "NI/AST team".
163  
164  ### D. Conduct and customer rules
165  
166  **11. Contact frequency, channels, timing?**
167  - **Maximum number of calls, call-time windows, contact-frequency rules: not found in the documents.** This holds for
168    in-house teams and agencies. PC has nothing on this.
169  - **Channels by stage** (FRP §3 Dunning Strategy, p.4; headed "All Products", not split in-house vs agency):
170    - Pre-due (high risk only) and 1-30 DPD: "SMS - Call - e-mail - Letters".
171    - 31-60 DPD: adds "Legal Notice - Field Visit".
172    - 61-90 through 180+ DPD: adds "Legal Action - Field Visit*".
173    - "The dunning strategies are compliant with the Consumer Protection Regulation (CPR) guidelines." (p.4)
174    - Field visits: "allowed for customers who have provided consent on their applications post 15th July 2022 for Loans
175      and 10th October 2022 for Credit Cards." (p.4)
176  - **Letters** (FRP §3, p.5): "Letters will only be sent to customers who do not have a formal e-mail address registered
177    with the bank."
178  - **Agency-specific:** the Appointment of Third-Party Agency Letter (Q2) and Agency Governance monitoring of
179    "communication quality, service standards, and compliance" (FRP §11 iii, p.12).
180  - **SQ and complaints** (FRP §11, pp.11-13): quality oversight by call-listening sampling; the complaint TAT value is
181    not given. No numeric standard.
182  - The no-calling rule is quoted under Q4.
183  
184  **12. Restrictions on using agencies for accounts that are not charged off?**
185  - **Not found in the documents.** No provision restricts agency use on customer-experience, branding, complaints or
186    regulator grounds.
187  - Related provisions (not restrictions): the 6-month retention limit (Q6); bulk card cancellation before agency
188    allocation (Q2); Agency Governance oversight "with a strong focus on ethical practices and customer rights" (FRP §11
189    iii, p.12); the Appointment of Third-Party Agency Letter (Q2).
190  
191  ### E. Settlements and programmes
192  
193  **13. PLUS and CARES: offers, DPD stages, vintages, results**
194  - **What they are.** PC Background: "launched in 2021 to handle the increased 90+ DPD and GWO stocks in Personal Loans
195    and Credit Cards respectively", later extended to "the 30+ DPD environment and recoveries across PILS, PCL and Credit
196    Cards and the front-end DPD buckets in Credit Cards". FRP §7, p.10 names them as "Pre-approved Settlement Programs…
197    pre-defined waivers on the principal outstanding", including "PLUS and enhanced PLUS for PILS and PCL and the CARES
198    program for Credit Cards". "Enhanced PLUS" is not defined in either document.
199  - **2026 position.** PC Proposal: "recommend extending the PLUS and CARES programs as BAU remedial solutions to
200    financially impacted customers in 2026." Change: "The CARES program… will no longer be offered to 1-30 DPD cases".
201    Otherwise "the 2025 settlement criteria are being recommended for extension into 2026."
202  - **Eligibility tables** (PC Annexure, as written). Segment / Reg Segment Flag is "All accounts" on every card row.
203    **The extracted table layout is partly ambiguous (see flags below).**
204  
205    CARES Credit Cards [31-180 DPD]:
206  
207    | Settlement offer | Tenor |
208    |---|---|
209    | 50% of Principal OS | One-shot |
210    | 70% of Principal OS * | up-to 3 months |
211    | 80% of Principal OS * | up-to 6 months |
212    | 85% of Principal OS * | up-to 15 months |
213    | 100% of Principal OS | up-to 18 months |
214    | 100% of POS + 5% of Interest | up-to 18 months |
215  
216    Footnote: "* Minimum due to be covered every month throughout the tenor".
217  
218    CARES Credit Cards [180+ DPD] (two sub-tables in the source; Mandatory Criteria is filled only on the first row of
219    each block):
220  
221    | Settlement offer | Tenor | Mandatory criteria |
222    |---|---|---|
223    | 50% of Principal OS | One Shot | Only for booking vintages between June 2022 to March 2023 |
224    | 60% of Principal OS | up-to 6 months | (blank) |
225    | 65% of Principal OS | up-to 12 months | (blank) |
226    | 70% of Principal OS | One Shot | All Charge-off vintages |
227    | 80% of Principal OS | up-to 6 months | (blank) |
228    | 85% of Principal OS | up-to 12 months | (blank) |
229  
230    PLUS PILS and PCL [30+ DPD]: 80% of loan amount * One-shot; 85% * up-to 6 months; 90% * up-to 12 months; 100% * up-to
231    18 months. Footnote: "* The settlement offer considers the installments paid so far".
232  
233    PLUS PILS and PCL [180+ DPD]: 40% of Principal OS* One-shot; 50% One-shot; 55% up-to 6 months; 60% up-to 12 months;
234    65% up-to 18 months; 70% up-to 24 months. Footnote: "* This option is only applicable for Personal Cash Loans".
235  
236    Fleet Finance**, Micro-SME Business Vehicles** and Business Loans [180+ DPD]: 50% of Principal OS One-shot; 55% up-to
237    6 months; 60% up-to 12 months. Footnote: "** Only for accounts having a shortfall balance post auction of repossessed
238    vehicle".
239  
240  - **Delegation** (PC Existing Rules and Delegation): settlements within programme norms "do not require approval based
241    on individual delegation"; "Any deviation from the eligible settlement amount of up-to AED 50,000 can be approved by
242    Group Head of Retail Risk"; deviation on "tenor and/or split" and "any further modification and/or extension… within
243    the year" likewise by the Group Head of Retail Risk.
244  - **Results** (PC Annexure - Results of 2025 PLUS and CARES settlement programs), as written:
245    - "The POF (30 to GWO) has stabilized across PILS and PCL since 2022 with significant improvement observed in 2025
246      despite book growth." Chart: 53.68% (2022), 53.73% (2023), 53.72% (2024), 51.24% (2025).
247    - Personal Loans 30+ DPD: "0.90% in Nov25 as compared to 1.05% in Dec24 on account of the PLUS settlement program.";
248      "Loss rate has improved in 2025 at 1.55% as compared to 1.71% in 2024."
249    - Personal Cash Loans 30+ DPD: "30+ % has remained stable in 2025 at 2.82% as compared to 2024."; "Loss rate has
250      improved in 2025 at 5.72% as compared to 5.84% in 2024."
251    - "YTD Nov25 actuals of AED 257 Million as against the plan of AED 218 Million." Chart "2025 Recoveries - Plan vs.
252      Actual" (no unit label): PILS and PCL 69.60 plan / 76.94 actual; Credit Cards 148.50 plan / 180.08 actual.
253    - No take-up, cure or success rates and no results by DPD bucket are given. The results are portfolio-level
254      aggregates.
255  - **Flags:** column alignment of the card tables is partly lost in extraction (check the original docx); the "*"
256    minimum-due footnote appears on the 70% and 80% rows only; "% of loan amount" (30+) vs "% of Principal OS" (180+) is
257    not reconciled; "split of the settlement amount" is undefined.
258  
259  **14. Other settlement, restructuring or hardship programmes at 61-180 DPD?**
260  - FRP §7 Remedial Solutions, pp.9-10: "The Financial Remediation Unit offers various remedial solutions to customers
261    with impacted payment capacity." They "are product and delinquency stage specific"; the list is "some examples of the
262    tools that are available".
263    - a. One-shot or Long-term settlements, for customers "with the willingness to pay but have impacted payment
264      capability"; "The approved DOA matrix is followed".
265    - b. Loan Deferral, "relief for a month or two".
266    - c. Loan Restructure, "either increasing the tenor or through interest rate reduction, or both".
267    - d. Pre-approved Settlement Programs (PLUS, CARES).
268    - e. Balance Conversion (Balcon) Plan, 12 and 24 months, for "P & G Blocked Credit Cards", "without AECB impact".
269    - f. Rewrite Program, 24, 36 and 48 months, "with AECB impact, by cancelling the credit card permanently"; "Currently
270      the plan is offered with 0 % interest rate".
271    - Special-asset products (Mortgages, MSME Business Loans, MSME Business Vehicles, Fleet Finance): Grading (Interest
272      Only) and Tenure Extension.
273  - Approval: "All above mentioned solutions are approved as per the DOA/ program parameters and with customer consent."
274    (p.10). "There are detailed criteria for all remedial programs, and these are approved individually and managed by the
275    GRR Team." DOA levels and amounts: not found in the documents (the "approved DOA memo", §6, p.9, is not provided).
276  - DPD eligibility for items b-f and the special-asset tools: **not found in the documents**.
277  
278  ---
279  
280  ## Part 2 - What this means for the three groups
281  
282  - **Agency placement before 180+ is allowed in the documents.** The agency letter covers accounts "upto 180+ DPD",
283    retention is defined for "buckets/recoveries", and the "non-workable pool… non contactable, least probable to pay" is
284    referred to agencies (FRP §3, §10, §4). The non-workable wording has no stated DPD scope and no numeric definition.
285  - **Commission terms:** paid "based on cash collection" and varying "with the DPD stage and charge-off vintage". No
286    rate, % or fee appears in either document; it sits in the unprovided "FR Incentive Structure Document".
287  - **What stops it:** no minimum DPD or balance limit is stated. The documented requirements are HOD approval for the
288    non-workable pool, bulk card cancellation (block X) before allocation, and the 6-month retention limit (15% may stay
289    up to 1 year).
290  - **In-house effort reduction:** the only stated rule is no calling (letters/SMS/e-mail continue) when principal is
291    below AED 1000 or the account is a GRR-classified Dead Beat. Nothing sets a low-yield tier or a call cap.
292  - **No document gives** an in-house cost per account/collector/call, an agency performance target or recall rule, or a
293    debt-sale route.
294  
295  ---
296  
297  ## Part 3 - Documents that could not be read
298  
299  None. Both documents were fully readable. The PDF was converted with `pypdf` (no `pdftotext` available) and the DOCX
300  with the Python standard library (`zipfile`); the three embedded images (two results charts and a logo) were viewed
301  directly. Residual limitations: table layouts in both documents were flattened by text extraction (flagged in place),
302  and `word/media/image4.svg` (a vector asset) was not viewed. The files in `data/input/docs/` are the only two documents
303  present.
304  
```

## Notes on specific spots

- Line numbers 1-304 are all covered, with overlaps between photos checked against each other (lines 54-58, 105-108, 149-151, 199-203, 250-254 appear in two photos each, and matched).
- Line 304 is the last one visible. It is empty. I can't tell if more lines follow.
- Line 111: "retain upto 15% up to 1 year" is as printed. Line 289 restates it as "(15% may stay up to 1 year)".
- Line 145-146: "Charge-off Cycle 9 180+ DPD", and the row above "Bucket 6 Cycle 7 151-180 DPD", copied as printed (no cycle 8 shown).
- Line 56: "(block X)" is as printed, with a capital X.
- Line 138-139 and 236-238: the `**` after "footnote" and after "Fleet Finance" / "Micro-SME Business Vehicles" is literal text (a footnote marker), not bold. In the editor it is highlighted like bold, so the `**` on line 236 could in principle be markdown. I kept it literal.
- Line 246 chart values (53.68 / 53.73 / 53.72 / 51.24) and line 247-250 percentages are at OCR risk. They were readable on screen, but they are decimals in a small font.
- Check on lines 251-252: plan 69.60 + 148.50 = 218.10 (the text says AED 218 million), and actual 76.94 + 180.08 = 257.02 (the text says AED 257 million). Both tie.
- Terms like "GCRO", "NI/AST", "NPA", "GWO", "POF", "TOS" and "Dcore" are as printed.
- The CARES 180+ table (lines 221-228) has 6 data rows. The "Mandatory criteria" column is "(blank)" for rows 2, 3, 5 and 6, as printed.
- Related earlier handoff: handoff 62 holds the terminal answer that summarises this file ("Agencies on commission is confirmed. An outright sale is not documented.").
