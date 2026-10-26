Fixes the `crx_cc_a1_ability_b03_check` failure in `build_internal_returns`
(`a1_ability/signals.py:351`: `TypeError: '>' not supported between instances of
'datetime.date' and 'str'`).

`prm_casa_return_events` is partitioned by `event_month`, written as a `yyyy-MM-dd` string.
On read, Spark turns the partition folder values back into dates, so the coverage guard
compared a date with the ISO string from `lookback_floor`. Both sides are now compared as
ISO strings. The `event_month >= since` filter itself was already fine (Spark casts it).
