"""Tests for the Grandma Word Engine (main.py).

Run from the repository root with:
    python3 -m unittest discover -s tests -v
"""

import contextlib
import io
import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, REPO_ROOT)
import main as engine


def run_engine(output_path):
    """Run main.py once in-process, writing to the given path.

    Returns the entry file's bytes. The run's printed table is
    captured and discarded; only the written file is checked here.
    """
    old_value = os.environ.get("OUTPUT_PATH")
    os.environ["OUTPUT_PATH"] = output_path
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            engine.main()
    finally:
        if old_value is None:
            del os.environ["OUTPUT_PATH"]
        else:
            os.environ["OUTPUT_PATH"] = old_value
    with open(output_path, "rb") as handle:
        return handle.read()


class TestEngine(unittest.TestCase):
    def test_two_runs_are_byte_identical(self):
        """Determinism: two runs must produce byte-identical output."""
        with tempfile.TemporaryDirectory() as tmp:
            first = run_engine(os.path.join(tmp, "first.txt"))
            second = run_engine(os.path.join(tmp, "second.txt"))
        self.assertEqual(first, second)

    def test_output_passes_the_sealed_gate(self):
        """The gate: UTF-8 text, 1-30 chars, a single non-blank word."""
        with tempfile.TemporaryDirectory() as tmp:
            raw = run_engine(os.path.join(tmp, "entry.txt"))
        text = raw.decode("utf-8")
        self.assertTrue(1 <= len(text) <= 30, "length %d" % len(text))
        self.assertEqual(text.strip(), text, "no surrounding whitespace")
        self.assertFalse(any(ch.isspace() for ch in text), "single word")
        self.assertTrue(text.strip(), "not only whitespace")

    def test_winner_beats_the_obvious_picks(self):
        """The chosen word must beat ROBOT, SKYNET and LOL on the rubric."""
        winner = engine.select_winner()
        by_word = {c["word"]: c for c in engine.LEXICON}
        for obvious in ("ROBOT", "SKYNET", "LOL"):
            self.assertTrue(
                engine.beats(winner, by_word[obvious]),
                "%s should beat %s" % (winner["word"], obvious),
            )

    def test_scoring_order_is_deterministic(self):
        """Ranking twice gives the same order, and the ranking is sorted."""
        first = [c["word"] for c in engine.rank_candidates(engine.LEXICON)]
        second = [c["word"] for c in engine.rank_candidates(engine.LEXICON)]
        self.assertEqual(first, second)
        ranked = engine.rank_candidates(engine.LEXICON)
        for upper, lower in zip(ranked, ranked[1:]):
            self.assertTrue(
                engine.beats(upper, lower) or upper["word"] == lower["word"],
                "%s should rank above %s" % (upper["word"], lower["word"]),
            )

    def test_first_criterion_decides(self):
        """The judge's order: a lead on criterion 1 beats a lead on 4."""
        leader = {
            "word": "AAA",
            "scores": {c: 0 for c in engine.CRITERIA},
        }
        leader["scores"]["grandma_would_text_it"] = 5
        trailer = {
            "word": "BBB",
            "scores": {c: 0 for c in engine.CRITERIA},
        }
        trailer["scores"]["tied_to_machines"] = 5
        self.assertTrue(engine.beats(leader, trailer))

    def test_winner_is_a_real_lexicon_word(self):
        """The winner comes from the curated lexicon, not from thin air."""
        winner = engine.select_winner()
        self.assertIn(winner["word"], [c["word"] for c in engine.LEXICON])
        self.assertEqual(engine.validate(winner["word"]), winner["word"])

    def test_validate_rejects_bad_words(self):
        """Validation must refuse blanks, phrases, punctuation and long words."""
        for bad in ("", "   ", "TWO WORDS", "HELLO!", "ABC123",
                    "X" * 31, "DOOHICKEY\n"):
            with self.assertRaises(ValueError, msg=repr(bad)):
                engine.validate(bad)

    def test_every_candidate_has_scores_and_notes(self):
        """Every candidate scores every criterion and explains each score."""
        for candidate in engine.LEXICON:
            self.assertEqual(set(candidate["scores"]), set(engine.CRITERIA))
            self.assertEqual(set(candidate["notes"]), set(engine.CRITERIA))
            for score in candidate["scores"].values():
                self.assertTrue(0 <= score <= 5, "%s score %r" % (candidate["word"], score))
            for note in candidate["notes"].values():
                self.assertTrue(note.strip(), "%s has an empty note" % candidate["word"])

    def test_ranking_matches_beats_pairwise(self):
        """The full ranking must agree with beats() for every pair."""
        ranked = engine.rank_candidates(engine.LEXICON)
        for i, upper in enumerate(ranked):
            for lower in ranked[i + 1:]:
                self.assertTrue(
                    engine.beats(upper, lower),
                    "%s should beat %s" % (upper["word"], lower["word"]),
                )


if __name__ == "__main__":
    unittest.main()
