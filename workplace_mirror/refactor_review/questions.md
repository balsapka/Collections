# Council run 2: questions for the user

Q-01 [A3 · rl_a3_payment_credibility + a3_credibility/signals.py `_paid_after_refusal`] On loans a
refusal is never lifted by a payment in the same month, even one made after the refusal day.
Now: RL cash is dated the 1st of the month and the rule needs a payment date after the refusal day;
cards lift it in the same case. Options: (a) keep (RL cash is only known by month) and say so in
the spec; (b) count the refusal month's cash on loans, in a fix after this bundle.
Recommendation: pending S6's review in round 1. Source: Cartographer, `inventory.md` §8.
