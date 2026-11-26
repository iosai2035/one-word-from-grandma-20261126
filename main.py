#!/usr/bin/env python3
"""One Word From Grandma -- the Grandma Word Engine.

Picks the single word a grandma would text about AI, using the judge's
own five published criteria, in their published order:

  1. Reads as the single word a grandma would text about AI.
  2. Sounds like a real grandmother's texting voice: warm, a little baffled.
  3. Funny in one word; the joke lands with no caption or context.
  4. Tied to AI, robots or machines rather than fitting any subject.
  5. Fresh rather than the obvious pick, still instantly readable.

The judge goes through the criteria in order, lets the first one where
two words differ decide, and only lets a later one matter when it
differs by much more. This engine mirrors that: candidates are compared
criterion by criterion, in order, and the first differing criterion
decides. A tied score line is settled by the higher total, then the
shorter word, then alphabetical order, so the pick is fully
deterministic: no randomness, no time, no network, no environment
dependence, standard library only.

The winning word is written to /output/entry.txt (or to the path in
OUTPUT_PATH when that is set, for local testing only).
"""

import os
import sys
from functools import cmp_to_key

# The five published criteria, in the judge's published order.
CRITERIA = (
    "grandma_would_text_it",
    "grandma_voice",
    "funny_in_one_word",
    "tied_to_machines",
    "fresh_and_readable",
)

CRITERION_TITLES = {
    "grandma_would_text_it": "1. Grandma would text it about AI",
    "grandma_voice": "2. Warm, a little baffled grandma voice",
    "funny_in_one_word": "3. Funny in one word, no context needed",
    "tied_to_machines": "4. Tied to AI / robots / machines",
    "fresh_and_readable": "5. Fresh, not obvious, instantly readable",
}

# Each candidate: the word, one score 0-5 per criterion, and a short
# note per criterion saying why the score fits. Scores are honest
# readings of the published brief, not numbers tuned to a favourite:
# the obvious picks (ROBOT, SKYNET, AI, LOL, HELLO) are scored too,
# as controls, and they lose on the early criteria.
#
# Why the gadget-word family leads: real grandma texting is full of
# old-fashioned gadget words for things she cannot name -- doohickey,
# thingamajig, whatchamacallit -- the exact word she reaches for when
# a grandchild shows her a new machine. That is warm, baffled, funny,
# and tied to machines all at once.
LEXICON = (
    {
        "word": "DOOHICKEY",
        "scores": {
            "grandma_would_text_it": 5,
            "grandma_voice": 5,
            "funny_in_one_word": 4,
            "tied_to_machines": 3,
            "fresh_and_readable": 4,
        },
        "notes": {
            "grandma_would_text_it": "The word a grandma uses for any gadget she cannot name; exactly how she would name AI.",
            "grandma_voice": "Warm, baffled, old-generation voice; the classic grandma gadget word.",
            "funny_in_one_word": "The joke lands at once: she calls the smartest machine ever built a doohickey.",
            "tied_to_machines": "A gadget word, tied to machines in general rather than AI in particular.",
            "fresh_and_readable": "Not the obvious pick, and every reader knows it at a glance.",
        },
    },
    {
        "word": "THINGAMAJIG",
        "scores": {
            "grandma_would_text_it": 5,
            "grandma_voice": 5,
            "funny_in_one_word": 4,
            "tied_to_machines": 3,
            "fresh_and_readable": 3,
        },
        "notes": {
            "grandma_would_text_it": "A grandma gadget word, right up there with doohickey.",
            "grandma_voice": "Warm and baffled, pure grandma vocabulary.",
            "funny_in_one_word": "Funny on its own: she names the future with a word from 1950.",
            "tied_to_machines": "A gadget word, tied to machines in general.",
            "fresh_and_readable": "Well known, so a touch less fresh than doohickey.",
        },
    },
    {
        "word": "WHATCHAMACALLIT",
        "scores": {
            "grandma_would_text_it": 5,
            "grandma_voice": 5,
            "funny_in_one_word": 4,
            "tied_to_machines": 2,
            "fresh_and_readable": 3,
        },
        "notes": {
            "grandma_would_text_it": "The grandma word for the thing whose name she forgot.",
            "grandma_voice": "Very much her voice: baffled, affectionate, unbothered.",
            "funny_in_one_word": "Funny because it is a shrug in word form.",
            "tied_to_machines": "It names anything unnamed, not machines in particular.",
            "fresh_and_readable": "Long but readable; a familiar word, not a surprise.",
        },
    },
    {
        "word": "CONTRAPTION",
        "scores": {
            "grandma_would_text_it": 4,
            "grandma_voice": 4,
            "funny_in_one_word": 3,
            "tied_to_machines": 4,
            "fresh_and_readable": 4,
        },
        "notes": {
            "grandma_would_text_it": "An old-fashioned machine word a grandma would use.",
            "grandma_voice": "Old-generation voice, though a little formal for a text.",
            "funny_in_one_word": "Mildly funny: AI as a Rube Goldberg device.",
            "tied_to_machines": "Squarely a machine word.",
            "fresh_and_readable": "Fresh and readable, not an obvious pick.",
        },
    },
    {
        "word": "WITCHCRAFT",
        "scores": {
            "grandma_would_text_it": 3,
            "grandma_voice": 4,
            "funny_in_one_word": 4,
            "tied_to_machines": 2,
            "fresh_and_readable": 4,
        },
        "notes": {
            "grandma_would_text_it": "A grandma might call AI witchcraft, but it is a reaction, not her name for it.",
            "grandma_voice": "Old-generation suspicion of new tech, warmly put.",
            "funny_in_one_word": "Funny: the new magic is sorcery to her.",
            "tied_to_machines": "Fits any mysterious thing, not machines in particular.",
            "fresh_and_readable": "Fresh, instantly readable.",
        },
    },
    {
        "word": "BEEPBOOP",
        "scores": {
            "grandma_would_text_it": 3,
            "grandma_voice": 3,
            "funny_in_one_word": 4,
            "tied_to_machines": 5,
            "fresh_and_readable": 3,
        },
        "notes": {
            "grandma_would_text_it": "Grandma imitating the robot's noises; plausible, but a sound, not a word she would send.",
            "grandma_voice": "Playful, but more grandchild than grandma.",
            "funny_in_one_word": "Funny on its own: the robot goes beep boop.",
            "tied_to_machines": "Pure robot sound, tied to machines exactly.",
            "fresh_and_readable": "Readable, though a little meme-flavoured.",
        },
    },
    {
        "word": "GIZMO",
        "scores": {
            "grandma_would_text_it": 4,
            "grandma_voice": 3,
            "funny_in_one_word": 2,
            "tied_to_machines": 4,
            "fresh_and_readable": 3,
        },
        "notes": {
            "grandma_would_text_it": "A gadget word she might use.",
            "grandma_voice": "A gadget word, but more dad than grandma.",
            "funny_in_one_word": "Only mildly funny on its own.",
            "tied_to_machines": "A machine word.",
            "fresh_and_readable": "Familiar, not a surprise.",
        },
    },
    {
        "word": "DOODAD",
        "scores": {
            "grandma_would_text_it": 4,
            "grandma_voice": 4,
            "funny_in_one_word": 3,
            "tied_to_machines": 2,
            "fresh_and_readable": 3,
        },
        "notes": {
            "grandma_would_text_it": "A grandma word for a small unnamed thing.",
            "grandma_voice": "Warm and old-fashioned.",
            "funny_in_one_word": "Gentle humour, not a laugh on its own.",
            "tied_to_machines": "Names any small thing, not machines.",
            "fresh_and_readable": "Familiar, readable.",
        },
    },
    {
        "word": "WHATSIT",
        "scores": {
            "grandma_would_text_it": 4,
            "grandma_voice": 4,
            "funny_in_one_word": 2,
            "tied_to_machines": 2,
            "fresh_and_readable": 3,
        },
        "notes": {
            "grandma_would_text_it": "Grandma shorthand for the thing she cannot name.",
            "grandma_voice": "Her voice, but clipped and flat.",
            "funny_in_one_word": "Barely a joke on its own.",
            "tied_to_machines": "Names anything, not machines.",
            "fresh_and_readable": "Readable, ordinary.",
        },
    },
    {
        "word": "THINGY",
        "scores": {
            "grandma_would_text_it": 4,
            "grandma_voice": 3,
            "funny_in_one_word": 2,
            "tied_to_machines": 2,
            "fresh_and_readable": 2,
        },
        "notes": {
            "grandma_would_text_it": "She would say it, but it is any-generation slang.",
            "grandma_voice": "More teenager than grandma.",
            "funny_in_one_word": "Not funny on its own.",
            "tied_to_machines": "Names anything at all.",
            "fresh_and_readable": "Common, not fresh.",
        },
    },
    # Controls: the obvious picks, scored honestly so the engine has to
    # beat them on the rubric rather than by ignoring them.
    {
        "word": "ROBOT",
        "scores": {
            "grandma_would_text_it": 3,
            "grandma_voice": 2,
            "funny_in_one_word": 1,
            "tied_to_machines": 5,
            "fresh_and_readable": 1,
        },
        "notes": {
            "grandma_would_text_it": "The literal word for the thing, but not how a grandma texts.",
            "grandma_voice": "Flat and factual, no warmth or bafflement.",
            "funny_in_one_word": "No joke at all on its own.",
            "tied_to_machines": "Exactly a machine word.",
            "fresh_and_readable": "The most obvious pick there is.",
        },
    },
    {
        "word": "SKYNET",
        "scores": {
            "grandma_would_text_it": 2,
            "grandma_voice": 1,
            "funny_in_one_word": 2,
            "tied_to_machines": 5,
            "fresh_and_readable": 2,
        },
        "notes": {
            "grandma_would_text_it": "A film reference, not a word a grandma would text.",
            "grandma_voice": "No grandma voice in it at all.",
            "funny_in_one_word": "A wink for film fans only, not a joke in one word.",
            "tied_to_machines": "Tied to machines, strongly.",
            "fresh_and_readable": "Readable, but a cliche of AI talk.",
        },
    },
    {
        "word": "AI",
        "scores": {
            "grandma_would_text_it": 2,
            "grandma_voice": 1,
            "funny_in_one_word": 0,
            "tied_to_machines": 5,
            "fresh_and_readable": 0,
        },
        "notes": {
            "grandma_would_text_it": "The initials, not a word she would text.",
            "grandma_voice": "No voice in it at all.",
            "funny_in_one_word": "No joke.",
            "tied_to_machines": "It is the subject itself.",
            "fresh_and_readable": "The single most obvious pick.",
        },
    },
    {
        "word": "LOL",
        "scores": {
            "grandma_would_text_it": 1,
            "grandma_voice": 2,
            "funny_in_one_word": 1,
            "tied_to_machines": 1,
            "fresh_and_readable": 1,
        },
        "notes": {
            "grandma_would_text_it": "Text-speak, but about nothing in particular.",
            "grandma_voice": "Grandmas do type LOL, often meaning lots of love.",
            "funny_in_one_word": "A laugh label, not a joke.",
            "tied_to_machines": "Fits any subject at all.",
            "fresh_and_readable": "The most tired text-speak there is.",
        },
    },
    {
        "word": "HELLO",
        "scores": {
            "grandma_would_text_it": 1,
            "grandma_voice": 2,
            "funny_in_one_word": 0,
            "tied_to_machines": 0,
            "fresh_and_readable": 1,
        },
        "notes": {
            "grandma_would_text_it": "A greeting, not a word about AI.",
            "grandma_voice": "Warm, but says nothing about the subject.",
            "funny_in_one_word": "No joke.",
            "tied_to_machines": "Nothing to do with machines.",
            "fresh_and_readable": "Ordinary to the point of invisible.",
        },
    },
)

DEFAULT_OUTPUT_PATH = "/output/entry.txt"


def score_tuple(candidate):
    """The candidate's scores as a tuple, in the judge's criterion order."""
    return tuple(candidate["scores"][criterion] for criterion in CRITERIA)


def total_score(candidate):
    """The plain sum of a candidate's five criterion scores."""
    return sum(score_tuple(candidate))


def compare(first, second):
    """Compare two candidates the way the judge compares two words.

    Returns -1 when `first` should rank above `second`, 1 when it
    should rank below, and 0 only when the two are indistinguishable
    under every rule. Walk the criteria in their published order; the
    first criterion where the two differ decides. A later criterion
    only matters when it differs by much more -- on a 0-5 scale, with
    the early criteria already equal, the total-score step below is
    the bounded form of that: a word that is far stronger across the
    remaining criteria still wins the tie. An exact tie on every
    criterion is settled by the higher total, then the shorter word,
    then alphabetical order, so the result is always deterministic.
    """
    first_scores = score_tuple(first)
    second_scores = score_tuple(second)
    for a, b in zip(first_scores, second_scores):
        if a != b:
            return -1 if a > b else 1
    if total_score(first) != total_score(second):
        return -1 if total_score(first) > total_score(second) else 1
    if len(first["word"]) != len(second["word"]):
        return -1 if len(first["word"]) < len(second["word"]) else 1
    if first["word"] == second["word"]:
        return 0
    return -1 if first["word"] < second["word"] else 1


def beats(first, second):
    """True when `first` beats `second` under the judge's decision order."""
    return compare(first, second) < 0


def rank_candidates(candidates):
    """All candidates, best first, under the judge's decision order.

    The ranking uses the very same comparison as `beats`, so the two
    can never drift apart: one decision rule, used everywhere.
    """
    return sorted(candidates, key=cmp_to_key(compare))


def select_winner(candidates=LEXICON):
    """The top-ranked candidate."""
    return rank_candidates(candidates)[0]


def validate(word):
    """Check a word against the sealed gate: 1-30 chars, one word, UTF-8.

    A single word means letters only: no whitespace, no punctuation,
    no digits. The gate itself only asks for 1-30 non-blank UTF-8
    characters, so the letter check is stricter than the gate -- it
    keeps the entry a plain word, the way the brief asks.
    """
    if not isinstance(word, str):
        raise ValueError("entry must be text")
    if not word or word.strip() == "":
        raise ValueError("entry must not be blank")
    if len(word) > 30:
        raise ValueError("entry must be at most 30 characters")
    if any(ch.isspace() for ch in word):
        raise ValueError("entry must be a single word with no whitespace")
    if not word.isalpha():
        raise ValueError("entry must be letters only, no punctuation or digits")
    word.encode("utf-8")  # raises if the word is not valid UTF-8 text
    return word


def output_path():
    """Where the entry goes: /output/entry.txt, or OUTPUT_PATH for tests."""
    return os.environ.get("OUTPUT_PATH", DEFAULT_OUTPUT_PATH)


def rubric_table(candidates=LEXICON):
    """A readable table of every candidate and its per-criterion scores."""
    header = "WORD".ljust(16) + " ".join(
        ("C%d" % (i + 1)).rjust(3) for i in range(len(CRITERIA))
    ) + "  TOTAL"
    lines = [header]
    for candidate in rank_candidates(candidates):
        scores = score_tuple(candidate)
        line = candidate["word"].ljust(16) + " ".join(
            str(s).rjust(3) for s in scores
        ) + "  %5d" % total_score(candidate)
        lines.append(line)
    return "\n".join(lines)


def main():
    winner = select_winner()
    word = validate(winner["word"])
    path = output_path()
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(word)
    print(rubric_table())
    print()
    print("Why %s wins:" % word)
    for criterion in CRITERIA:
        print("  %s: %d -- %s" % (
            CRITERION_TITLES[criterion],
            winner["scores"][criterion],
            winner["notes"][criterion],
        ))
    print()
    print("Winner: %s -> %s" % (word, path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
