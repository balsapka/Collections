# A3 check (new vs old vs b20) - all four model ids

Combined from summary_<model_id>.md. Every table is prefixed with a model_id column.
Run 2026-11-12. Lines are wrapped at 100 characters (continuations are indented).

## Run facts

```
| model_id    | month      | rows   | events_in_window | runtime_sec |
|-------------|------------|--------|------------------|-------------|
| cc_60_180   | 2026-08-31 | 19292  | 22201            | 216.1       |
| cc_180_plus | 2026-08-31 | 318663 | 25766            | 527.7       |
| rl_60_180   | 2026-08-31 | 3985   | 3383             | 151.1       |
| rl_180_plus | 2026-08-31 | 55371  | 3756             | 219.4       |
```

## A3 OUTPUT

### state (count, %)

```
| model_id    | state    | b20            | old            | new            |
|-------------|----------|----------------|----------------|----------------|
| cc_60_180   | high     | 490 (2.5%)     | 491 (2.5%)     | 490 (2.5%)     |
| cc_60_180   | low      | 12825 (66.5%)  | 15053 (78.0%)  | 15054 (78.0%)  |
| cc_60_180   | moderate | 3749 (19.4%)   | 3748 (19.4%)   | 3748 (19.4%)   |
| cc_60_180   | unknown  | 2228 (11.5%)   | -              | -              |
| cc_180_plus | high     | 222 (0.1%)     | 222 (0.1%)     | 159 (0.0%)     |
| cc_180_plus | low      | 50327 (15.8%)  | 309825 (97.2%) | 310214 (97.3%) |
| cc_180_plus | moderate | 8611 (2.7%)    | 8616 (2.7%)    | 8290 (2.6%)    |
| cc_180_plus | unknown  | 259503 (81.4%) | -              | -              |
| rl_60_180   | high     | 196 (4.9%)     | 196 (4.9%)     | 126 (3.2%)     |
| rl_60_180   | low      | 2413 (60.6%)   | 2676 (67.2%)   | 2879 (72.2%)   |
| rl_60_180   | moderate | 1113 (27.9%)   | 1113 (27.9%)   | 980 (24.6%)    |
| rl_60_180   | unknown  | 263 (6.6%)     | -              | -              |
| rl_180_plus | high     | 171 (0.3%)     | 171 (0.3%)     | 120 (0.2%)     |
| rl_180_plus | low      | 17672 (31.9%)  | 52814 (95.4%)  | 52962 (95.6%)  |
| rl_180_plus | moderate | 2386 (4.3%)    | 2386 (4.3%)    | 2289 (4.1%)    |
| rl_180_plus | unknown  | 35142 (63.5%)  | -              | -              |
```

### b20 x new (whole bundle)

```
| model_id    | b20      | new      | count  | %    |
|-------------|----------|----------|--------|------|
| cc_60_180   | high     | high     | 490    | 2.5  |
| cc_60_180   | low      | low      | 12825  | 66.5 |
| cc_60_180   | moderate | low      | 1      | 0.0  |
| cc_60_180   | moderate | moderate | 3748   | 19.4 |
| cc_60_180   | unknown  | low      | 2228   | 11.5 |
| cc_180_plus | high     | high     | 124    | 0.0  |
| cc_180_plus | high     | low      | 19     | 0.0  |
| cc_180_plus | high     | moderate | 79     | 0.0  |
| cc_180_plus | low      | high     | 6      | 0.0  |
| cc_180_plus | low      | low      | 50012  | 15.7 |
| cc_180_plus | low      | moderate | 309    | 0.1  |
| cc_180_plus | moderate | high     | 29     | 0.0  |
| cc_180_plus | moderate | low      | 681    | 0.2  |
| cc_180_plus | moderate | moderate | 7901   | 2.5  |
| cc_180_plus | unknown  | low      | 259502 | 81.4 |
| cc_180_plus | unknown  | moderate | 1      | 0.0  |
| rl_60_180   | high     | high     | 118    | 3.0  |
| rl_60_180   | high     | low      | 20     | 0.5  |
| rl_60_180   | high     | moderate | 58     | 1.5  |
| rl_60_180   | low      | low      | 2404   | 60.3 |
| rl_60_180   | low      | moderate | 9      | 0.2  |
| rl_60_180   | moderate | high     | 8      | 0.2  |
| rl_60_180   | moderate | low      | 192    | 4.8  |
| rl_60_180   | moderate | moderate | 913    | 22.9 |
| rl_60_180   | unknown  | low      | 263    | 6.6  |
| rl_180_plus | high     | high     | 111    | 0.2  |
| rl_180_plus | high     | low      | 11     | 0.0  |
| rl_180_plus | high     | moderate | 49     | 0.1  |
| rl_180_plus | low      | low      | 17638  | 31.9 |
| rl_180_plus | low      | moderate | 34     | 0.1  |
| rl_180_plus | moderate | high     | 9      | 0.0  |
| rl_180_plus | moderate | low      | 171    | 0.3  |
| rl_180_plus | moderate | moderate | 2206   | 4.0  |
| rl_180_plus | unknown  | low      | 35142  | 63.5 |
```

- cc_60_180: changed 2229 (11.6%)
- cc_180_plus: changed 260626 (81.8%)
- rl_60_180: changed 550 (13.8%)
- rl_180_plus: changed 35416 (64.0%)

### b20 x old (Unknown rule)

```
| model_id    | b20      | old      | count  | %    |
|-------------|----------|----------|--------|------|
| cc_60_180   | high     | high     | 490    | 2.5  |
| cc_60_180   | low      | low      | 12824  | 66.5 |
| cc_60_180   | low      | moderate | 1      | 0.0  |
| cc_60_180   | moderate | high     | 1      | 0.0  |
| cc_60_180   | moderate | low      | 1      | 0.0  |
| cc_60_180   | moderate | moderate | 3747   | 19.4 |
| cc_60_180   | unknown  | low      | 2228   | 11.5 |
| cc_180_plus | high     | high     | 222    | 0.1  |
| cc_180_plus | low      | low      | 50322  | 15.8 |
| cc_180_plus | low      | moderate | 5      | 0.0  |
| cc_180_plus | moderate | moderate | 8611   | 2.7  |
| cc_180_plus | unknown  | low      | 259503 | 81.4 |
| rl_60_180   | high     | high     | 196    | 4.9  |
| rl_60_180   | low      | low      | 2413   | 60.6 |
| rl_60_180   | moderate | moderate | 1113   | 27.9 |
| rl_60_180   | unknown  | low      | 263    | 6.6  |
| rl_180_plus | high     | high     | 171    | 0.3  |
| rl_180_plus | low      | low      | 17672  | 31.9 |
| rl_180_plus | moderate | moderate | 2386   | 4.3  |
| rl_180_plus | unknown  | low      | 35142  | 63.5 |
```

- cc_60_180: changed 2231 (11.6%)
- cc_180_plus: changed 259508 (81.4%)
- rl_60_180: changed 263 (6.6%)
- rl_180_plus: changed 35142 (63.5%)

### old x new (deadline)

```
| model_id    | old      | new      | count  | %    |
|-------------|----------|----------|--------|------|
| cc_60_180   | high     | high     | 490    | 2.5  |
| cc_60_180   | high     | moderate | 1      | 0.0  |
| cc_60_180   | low      | low      | 15053  | 78.0 |
| cc_60_180   | moderate | low      | 1      | 0.0  |
| cc_60_180   | moderate | moderate | 3747   | 19.4 |
| cc_180_plus | high     | high     | 124    | 0.0  |
| cc_180_plus | high     | low      | 19     | 0.0  |
| cc_180_plus | high     | moderate | 79     | 0.0  |
| cc_180_plus | low      | high     | 6      | 0.0  |
| cc_180_plus | low      | low      | 309510 | 97.1 |
| cc_180_plus | low      | moderate | 309    | 0.1  |
| cc_180_plus | moderate | high     | 29     | 0.0  |
| cc_180_plus | moderate | low      | 685    | 0.2  |
| cc_180_plus | moderate | moderate | 7902   | 2.5  |
| rl_60_180   | high     | high     | 118    | 3.0  |
| rl_60_180   | high     | low      | 20     | 0.5  |
| rl_60_180   | high     | moderate | 58     | 1.5  |
| rl_60_180   | low      | low      | 2667   | 66.9 |
| rl_60_180   | low      | moderate | 9      | 0.2  |
| rl_60_180   | moderate | high     | 8      | 0.2  |
| rl_60_180   | moderate | low      | 192    | 4.8  |
| rl_60_180   | moderate | moderate | 913    | 22.9 |
| rl_180_plus | high     | high     | 111    | 0.2  |
| rl_180_plus | high     | low      | 11     | 0.0  |
| rl_180_plus | high     | moderate | 49     | 0.1  |
| rl_180_plus | low      | low      | 52780  | 95.3 |
| rl_180_plus | low      | moderate | 34     | 0.1  |
| rl_180_plus | moderate | high     | 9      | 0.0  |
| rl_180_plus | moderate | low      | 171    | 0.3  |
| rl_180_plus | moderate | moderate | 2206   | 4.0  |
```

- cc_60_180: changed 2 (0.0%)
- cc_180_plus: changed 1127 (0.4%)
- rl_60_180: changed 287 (7.2%)
- rl_180_plus: changed 274 (0.5%)

## A3 PROMISES

### outcome, concluded events (count, %)

```
| model_id    | outcome | old           | new           |
|-------------|---------|---------------|---------------|
| cc_60_180   | none    | 12310 (57.7%) | 12310 (57.7%) |
| cc_60_180   | paid    | 7838 (36.8%)  | 7839 (36.8%)  |
| cc_60_180   | partial | 1173 (5.5%)   | 1172 (5.5%)   |
| cc_180_plus | none    | 18152 (75.3%) | 20569 (79.8%) |
| cc_180_plus | paid    | 4892 (20.3%)  | 4199 (16.3%)  |
| cc_180_plus | partial | 1068 (4.4%)   | 998 (3.9%)    |
| rl_60_180   | none    | 521 (16.8%)   | 1215 (35.9%)  |
| rl_60_180   | paid    | 2183 (70.5%)  | 1582 (46.8%)  |
| rl_60_180   | partial | 391 (12.6%)   | 586 (17.3%)   |
| rl_180_plus | none    | 1398 (40.0%)  | 1929 (51.4%)  |
| rl_180_plus | paid    | 1650 (47.2%)  | 1296 (34.5%)  |
| rl_180_plus | partial | 451 (12.9%)   | 531 (14.1%)   |
```

- cc_60_180: old concluded 21321; new concluded 21321
- cc_180_plus: old concluded 24112; new concluded 25766
- rl_60_180: old concluded 3095; new concluded 3383
- rl_180_plus: old concluded 3499; new concluded 3756

### concluded under both, outcome old x new

```
| model_id    | old     | new     | count | %    |
|-------------|---------|---------|-------|------|
| cc_60_180   | none    | none    | 12310 | 57.7 |
| cc_60_180   | paid    | paid    | 7838  | 36.8 |
| cc_60_180   | partial | paid    | 1     | 0.0  |
| cc_60_180   | partial | partial | 1172  | 5.5  |
| cc_180_plus | none    | none    | 17330 | 71.9 |
| cc_180_plus | none    | paid    | 593   | 2.5  |
| cc_180_plus | none    | partial | 229   | 0.9  |
| cc_180_plus | paid    | none    | 1547  | 6.4  |
| cc_180_plus | paid    | paid    | 3286  | 13.6 |
| cc_180_plus | paid    | partial | 59    | 0.2  |
| cc_180_plus | partial | none    | 346   | 1.4  |
| cc_180_plus | partial | paid    | 44    | 0.2  |
| cc_180_plus | partial | partial | 678   | 2.8  |
| rl_60_180   | none    | none    | 521   | 16.8 |
| rl_60_180   | paid    | none    | 388   | 12.5 |
| rl_60_180   | paid    | paid    | 1501  | 48.5 |
| rl_60_180   | paid    | partial | 294   | 9.5  |
| rl_60_180   | partial | none    | 140   | 4.5  |
| rl_60_180   | partial | partial | 251   | 8.1  |
| rl_180_plus | none    | none    | 1398  | 40.0 |
| rl_180_plus | paid    | none    | 262   | 7.5  |
| rl_180_plus | paid    | paid    | 1187  | 33.9 |
| rl_180_plus | paid    | partial | 201   | 5.7  |
| rl_180_plus | partial | none    | 154   | 4.4  |
| rl_180_plus | partial | partial | 297   | 8.5  |
```

- cc_60_180: concluded under both = 21321
- cc_180_plus: concluded under both = 24112
- rl_60_180: concluded under both = 3095
- rl_180_plus: concluded under both = 3499

### changed outcome, by event kind

```
| model_id    | kind          | count | %     |
|-------------|---------------|-------|-------|
| cc_60_180   | table_only    | 1     | 100.0 |
| cc_180_plus | followup_only | 970   | 34.4  |
| cc_180_plus | matched       | 622   | 22.1  |
| cc_180_plus | table_only    | 1226  | 43.5  |
| rl_60_180   | followup_only | 492   | 59.9  |
| rl_60_180   | matched       | 236   | 28.7  |
| rl_60_180   | table_only    | 94    | 11.4  |
| rl_180_plus | followup_only | 270   | 43.8  |
| rl_180_plus | matched       | 115   | 18.6  |
| rl_180_plus | table_only    | 232   | 37.6  |
```

- cc_60_180: changed outcome = 1
- cc_180_plus: changed outcome = 2818
- rl_60_180: changed outcome = 822
- rl_180_plus: changed outcome = 617

### by promise day of month

```
| model_id    | day   | changed outcome (n, %) | all concluded-under-both (n, %) |
|-------------|-------|------------------------|---------------------------------|
| cc_60_180   | 01-10 | -                      | 7307 (34.3%)                    |
| cc_60_180   | 11-20 | -                      | 6243 (29.3%)                    |
| cc_60_180   | 21-31 | 1 (100.0%)             | 7771 (36.4%)                    |
| cc_180_plus | 01-10 | 731 (25.9%)            | 6131 (25.4%)                    |
| cc_180_plus | 11-20 | 563 (20.0%)            | 5762 (23.9%)                    |
| cc_180_plus | 21-31 | 1524 (54.1%)           | 12219 (50.7%)                   |
| rl_60_180   | 01-10 | 234 (28.5%)            | 914 (29.5%)                     |
| rl_60_180   | 11-20 | 263 (32.0%)            | 1012 (32.7%)                    |
| rl_60_180   | 21-31 | 325 (39.5%)            | 1169 (37.8%)                    |
| rl_180_plus | 01-10 | 118 (19.1%)            | 775 (22.1%)                     |
| rl_180_plus | 11-20 | 161 (26.1%)            | 868 (24.8%)                     |
| rl_180_plus | 21-31 | 338 (54.8%)            | 1856 (53.0%)                    |
```

### accounts with promises

```
| model_id    | metric                  | old   | new   |
|-------------|-------------------------|-------|-------|
| cc_60_180   | >= 1 concluded promise  | 7905  | 7905  |
| cc_60_180   | >= 1 kept               | 4274  | 4274  |
| cc_180_plus | >= 1 concluded promise  | 15063 | 16126 |
| cc_180_plus | >= 1 kept               | 3701  | 3331  |
| rl_60_180   | >= 1 concluded promise  | 1310  | 1389  |
| rl_60_180   | >= 1 kept               | 991   | 818   |
| rl_180_plus | >= 1 concluded promise  | 2139  | 2299  |
| rl_180_plus | >= 1 kept               | 1085  | 929   |
```

## A3 LEVELS

### level (count, %)

```
| model_id    | level       | old_level      | new_level      |
|-------------|-------------|----------------|----------------|
| cc_60_180   | broken      | 2621 (13.6%)   | 2621 (13.6%)   |
| cc_60_180   | kept        | 441 (2.3%)     | 441 (2.3%)     |
| cc_60_180   | partly_kept | 2686 (13.9%)   | 2686 (13.9%)   |
| cc_60_180   | thin        | 13544 (70.2%)  | 13544 (70.2%)  |
| cc_180_plus | broken      | 3428 (1.1%)    | 3982 (1.2%)    |
| cc_180_plus | kept        | 209 (0.1%)     | 146 (0.0%)     |
| cc_180_plus | partly_kept | 2838 (0.9%)    | 2483 (0.8%)    |
| cc_180_plus | thin        | 312188 (98.0%) | 312052 (97.9%) |
| rl_60_180   | broken      | 142 (3.6%)     | 343 (8.6%)     |
| rl_60_180   | kept        | 385 (9.7%)     | 192 (4.8%)     |
| rl_60_180   | partly_kept | 556 (14.0%)    | 480 (12.0%)    |
| rl_60_180   | thin        | 2902 (72.8%)   | 2970 (74.5%)   |
| rl_180_plus | broken      | 302 (0.5%)     | 437 (0.8%)     |
| rl_180_plus | kept        | 192 (0.3%)     | 100 (0.2%)     |
| rl_180_plus | partly_kept | 837 (1.5%)     | 734 (1.3%)     |
| rl_180_plus | thin        | 54040 (97.6%)  | 54100 (97.7%)  |
```

### old_level x new_level

```
| model_id    | old         | new         | count  | %    |
|-------------|-------------|-------------|--------|------|
| cc_60_180   | broken      | broken      | 2621   | 13.6 |
| cc_60_180   | kept        | kept        | 441    | 2.3  |
| cc_60_180   | partly_kept | partly_kept | 2686   | 13.9 |
| cc_60_180   | thin        | thin        | 13544  | 70.2 |
| cc_180_plus | broken      | broken      | 3277   | 1.0  |
| cc_180_plus | broken      | kept        | 11     | 0.0  |
| cc_180_plus | broken      | partly_kept | 140    | 0.0  |
| cc_180_plus | kept        | broken      | 44     | 0.0  |
| cc_180_plus | kept        | kept        | 87     | 0.0  |
| cc_180_plus | kept        | partly_kept | 78     | 0.0  |
| cc_180_plus | partly_kept | broken      | 403    | 0.1  |
| cc_180_plus | partly_kept | kept        | 45     | 0.0  |
| cc_180_plus | partly_kept | partly_kept | 1831   | 0.6  |
| cc_180_plus | partly_kept | thin        | 559    | 0.2  |
| cc_180_plus | thin        | broken      | 258    | 0.1  |
| cc_180_plus | thin        | kept        | 3      | 0.0  |
| cc_180_plus | thin        | partly_kept | 434    | 0.1  |
| cc_180_plus | thin        | thin        | 311493 | 97.7 |
| rl_60_180   | broken      | broken      | 140    | 3.5  |
| rl_60_180   | broken      | partly_kept | 2      | 0.1  |
| rl_60_180   | kept        | broken      | 80     | 2.0  |
| rl_60_180   | kept        | kept        | 180    | 4.5  |
| rl_60_180   | kept        | partly_kept | 125    | 3.1  |
| rl_60_180   | partly_kept | broken      | 100    | 2.5  |
| rl_60_180   | partly_kept | kept        | 8      | 0.2  |
| rl_60_180   | partly_kept | partly_kept | 334    | 8.4  |
| rl_60_180   | partly_kept | thin        | 114    | 2.9  |
| rl_60_180   | thin        | broken      | 23     | 0.6  |
| rl_60_180   | thin        | kept        | 4      | 0.1  |
| rl_60_180   | thin        | partly_kept | 19     | 0.5  |
| rl_60_180   | thin        | thin        | 2856   | 71.7 |
| rl_180_plus | broken      | broken      | 302    | 0.5  |
| rl_180_plus | kept        | broken      | 34     | 0.1  |
| rl_180_plus | kept        | kept        | 92     | 0.2  |
| rl_180_plus | kept        | partly_kept | 66     | 0.1  |
| rl_180_plus | partly_kept | broken      | 84     | 0.2  |
| rl_180_plus | partly_kept | kept        | 6      | 0.0  |
| rl_180_plus | partly_kept | partly_kept | 594    | 1.1  |
| rl_180_plus | partly_kept | thin        | 153    | 0.3  |
| rl_180_plus | thin        | broken      | 17     | 0.0  |
| rl_180_plus | thin        | kept        | 2      | 0.0  |
| rl_180_plus | thin        | partly_kept | 74     | 0.1  |
| rl_180_plus | thin        | thin        | 53947  | 97.4 |
```
