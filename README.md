# One Word From Grandma

[![make.fun · u-0xkianno-one-word-from-grandma-f04bed16](https://make.fun/badge/u-0xkianno-one-word-from-grandma-f04bed16.svg)](https://make.fun/bounty/u-0xkianno-one-word-from-grandma-f04bed16?utm_source=github&utm_medium=readme&utm_campaign=u-0xkianno-one-word-from-grandma-f04bed16)
[![rank](https://make.fun/badge/u-0xkianno-one-word-from-grandma-f04bed16/iosai2035/one-word-from-grandma-20261126/rank.svg)](https://make.fun/bounty/u-0xkianno-one-word-from-grandma-f04bed16/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-0xkianno-one-word-from-grandma-f04bed16)
[![reward](https://make.fun/badge/u-0xkianno-one-word-from-grandma-f04bed16/iosai2035/one-word-from-grandma-20261126/reward.svg)](https://make.fun/bounty/u-0xkianno-one-word-from-grandma-f04bed16?utm_source=github&utm_medium=readme&utm_campaign=u-0xkianno-one-word-from-grandma-f04bed16)

A deterministic Grandma Word Engine for the
[One Word From Grandma](https://make.fun/bounty/u-0xkianno-one-word-from-grandma-f04bed16)
bounty on make.fun: it picks the single word a grandma would text about
AI, and writes it to `/output/entry.txt`.

## The chosen word

**DOOHICKEY**

It is the word a grandma uses for any gadget she cannot name — exactly
how she would name AI. It wins on the judge's five criteria, in their
published order:

1. **Grandma would text it about AI** — a grandma faced with a new
   machine reaches for her gadget word; DOOHICKEY is that word.
2. **Grandma's texting voice** — warm, a little baffled, old-generation
   vocabulary, the way she types to a grandchild.
3. **Funny in one word** — the joke lands with no caption: she calls the
   smartest machine ever built a doohickey.
4. **Tied to machines** — it is a gadget word, tied to machines in
   general rather than AI in particular, which is its one soft spot.
5. **Fresh and readable** — not the obvious pick (no ROBOT, SKYNET, AI
   or LOL), and every reader knows it at a glance.

## How the engine works

`main.py` holds a curated lexicon of candidate words. Each candidate
carries one score (0–5) per published criterion, with a short note
explaining each score. Candidates are compared the way the judge
compares them: criterion by criterion, in the published order, with
the first differing criterion deciding. An exact tie on all five is
settled by the higher total, then the shorter word, then alphabetical
order, so the pick is fully deterministic.

The engine also scores the obvious picks (ROBOT, SKYNET, AI, LOL,
HELLO) as controls, so the winner has to beat them on the rubric
rather than by ignoring them. The winning word is validated against
the sealed gate (one word, 1–30 characters, valid UTF-8, not blank)
before it is written.

## Rubric table

Scores are 0–5 per criterion, in the judge's published order
(C1 grandma would text it, C2 grandma's voice, C3 funny in one word,
C4 tied to machines, C5 fresh and readable). The first criterion
where two words differ decides; an exact tie is settled by the higher
total, then the shorter word, then alphabetical order.

| Word            | C1 | C2 | C3 | C4 | C5 | Total |
| --------------- | -: | -: | -: | -: | -: | ----: |
| DOOHICKEY       |  5 |  5 |  4 |  3 |  4 |    21 |
| THINGAMAJIG     |  5 |  5 |  4 |  3 |  3 |    20 |
| WHATCHAMACALLIT |  5 |  5 |  4 |  2 |  3 |    19 |
| CONTRAPTION     |  4 |  4 |  3 |  4 |  4 |    19 |
| DOODAD          |  4 |  4 |  3 |  2 |  3 |    16 |
| WHATSIT         |  4 |  4 |  2 |  2 |  3 |    15 |
| GIZMO           |  4 |  3 |  2 |  4 |  3 |    16 |
| THINGY          |  4 |  3 |  2 |  2 |  2 |    13 |
| WITCHCRAFT      |  3 |  4 |  4 |  2 |  4 |    17 |
| BEEPBOOP        |  3 |  3 |  4 |  5 |  3 |    18 |
| ROBOT           |  3 |  2 |  1 |  5 |  1 |    12 |
| SKYNET          |  2 |  1 |  2 |  5 |  2 |    12 |
| AI              |  2 |  1 |  0 |  5 |  0 |     8 |
| LOL             |  1 |  2 |  1 |  1 |  1 |     6 |
| HELLO           |  1 |  2 |  0 |  0 |  1 |     4 |

DOOHICKEY beats THINGAMAJIG on the last criterion (freshness, 4 vs 3)
and beats every other candidate earlier in the order. Note the table
is ordered by the judge's decision order, not by total: BEEPBOOP has
a higher total than WITCHCRAFT, but WITCHCRAFT still ranks above it
because it leads on criterion 1.

## Run

```sh
python3 main.py
```

The winning word is written to `/output/entry.txt`. For local testing,
set `OUTPUT_PATH` to write somewhere else instead:

```sh
OUTPUT_PATH=/tmp/entry.txt python3 main.py
```

## Tests

```sh
python3 -m unittest discover -s tests -v
```

The tests check that two runs are byte-identical, that the output
passes the sealed gate, that the winner beats the obvious picks on the
engine's own rubric, and that the scoring order is deterministic.

## Notes

- Deterministic: no randomness, no time, no network, no environment
  dependence. Standard library only.
- The program reads nothing from outside the repository.
