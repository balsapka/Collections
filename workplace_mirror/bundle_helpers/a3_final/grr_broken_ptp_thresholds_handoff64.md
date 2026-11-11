# Handoff 64: Teams chat with GRR (Architha Vemprala), broken-PTP thresholds

## Context for Claude Code

- Source: 1 phone photo of a Microsoft Teams chat on a Dell laptop (not the VS Code screen). Chat header: "GRR (Architha Vemprala)", tabs Chat / Shared / Notes / Recap / Storyline. Search bar text: "Search or ask Copilot (Ctrl+E)".
- Message sent by GRR (Architha Vemprala) at 11:28 AM, addressed to "Balazs" (Bala). The date is not visible. It reads as the GRR answer on how to define a broken promise-to-pay (PTP) for the persona work. It is the first answer ("Let us start with 61-180 DPD").
- Above the message, on the right, a grey bubble from Bala reads "This message has been delete(d)", cut off at the screen edge. That is a deleted message of his, with no content.
- The message is shown as three grey blocks (separate Teams messages sent together, with a thin gap between them). I mark the blocks below.
- Bullets are real bullets in the chat. I copied the text as written, including its spelling ("committment", "stmt", "e.g.," and the missing full stop after "honored PTP").

## Transcription

```
GRR (Architha Vemprala)  11:28 AM

[Block 1]
Hi Balazs. Let us start with 61-180 DPD.

  • If a card customer does not pay within the statement date, I will consider it a broken PTP.
  • For a loan customer, month-end will be the threshold.

The above can be considered regardless of the gap between PTP date and these thresholds (stmt date or
month-end).

So for e.g., a card customer with a statement date of 25th gives a PTP for 15th. He does not pay by 15th,
but pays before 25th. I will still consider it a honored PTP and NOT broken.

[Block 2]
For 180+ DPD, the threshold, regardless of product, will be month-end, i.e., last day of the month.

So for e.g., a customer commits for a payment on 18th, but pays on 30th - honored PTP
On the contrary, he committed for 18th, and pays 5th of next month - broken PTP for that committed
month.

[Block 3]
if the committtment crosses the threshold in either scenario, then you can track payment as per that day
with no grace period.
```

Message box at the bottom: "Type a message". Nothing typed.

## Notes on specific spots

- Rules as stated, for building the broken-PTP definition:
  - 61-180 DPD, cards: a PTP is broken only if the customer has not paid by the statement date. The PTP date itself does not matter.
  - 61-180 DPD, loans: the threshold is month-end.
  - 180+ DPD, all products: the threshold is month-end (last day of the month).
  - If the commitment date is after the threshold in either scenario, track payment as of that day (the threshold day), with no grace period. Block 3 says "crosses the threshold"; read as "the PTP date falls beyond the threshold". The wording is ambiguous, so confirm with GRR before coding it.
- Worked examples in the message: card with statement date the 25th and PTP on the 15th, pays between the 16th and 24th: honored. 180+ with PTP on the 18th: pays on the 30th is honored, pays on the 5th of next month is broken for the committed month.
- The first example says "pays before 25th". It does not say what happens if he pays exactly on the 25th (statement date). Not stated.
- "stmt date" means statement date. "honored" is spelled that way in the chat.
- Block 3 starts with a lowercase "if" and has the typo "committtment" (three t's). Kept as written.
- Not visible: the date of the message, anything above Bala's deleted message, and whether more messages follow below (the chat ends at the compose box, so this looks like the last message).
