"""Fuzzy assertions over speech-recognition output.

An ASR engine never returns byte-identical text twice for the same audio:
punctuation and casing drift between runs, whitespace collapses differently,
and individual words get misheard outright. Comparing transcripts with `==`
therefore produces tests that fail for reasons unrelated to the feature under
test, so this module normalises both sides first and then compares them with a
similarity threshold.

The threshold is deliberately a parameter rather than a constant: a short
IVR prompt tolerates far less drift than a thirty-second utterance, and the
caller is the only one who knows which it is looking at.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher

#: Characters an engine may add or drop freely without changing the meaning.
_PUNCTUATION = re.compile(r"""[.,!?;:$%@&*_~`'"(){}\[\]<>+=\\/|-]""")
_WHITESPACE = re.compile(r"\s+")

#: Ratio above which two transcripts are treated as the same utterance.
DEFAULT_THRESHOLD = 0.85


def normalize(text: str) -> str:
    """Reduce a transcript to the form that is actually worth comparing."""
    return _WHITESPACE.sub(" ", _PUNCTUATION.sub("", text)).strip().lower()


def similarity(expected: str, actual: str) -> float:
    """Return how close two transcripts are, from 0.0 to 1.0, after normalising."""
    return SequenceMatcher(None, normalize(expected), normalize(actual)).ratio()


def matches(expected: str, actual: str, threshold: float = DEFAULT_THRESHOLD) -> bool:
    """Whether `actual` is close enough to `expected` to count as the same text."""
    return similarity(expected, actual) >= threshold


def contains_phrase(phrase: str, transcript: str) -> bool:
    """Whether `phrase` appears in `transcript`, ignoring punctuation and casing.

    Useful when only a keyword matters -- an account number read back by a bot,
    say -- and the surrounding wording is free to vary.
    """
    return normalize(phrase) in normalize(transcript)


def assert_matches(
    expected: str,
    actual: str,
    threshold: float = DEFAULT_THRESHOLD,
) -> None:
    """Fail with both normalised forms and the score, not just "strings differ".

    A bare comparison failure forces whoever reads the report to re-run the test
    locally to find out *how* far off the transcript was, so the score and both
    normalised strings go into the message.
    """
    score = similarity(expected, actual)
    if score >= threshold:
        return
    raise AssertionError(
        f"Transcript similarity {score:.3f} is below the required {threshold:.3f}\n"
        f"  expected (normalised): {normalize(expected)!r}\n"
        f"  actual   (normalised): {normalize(actual)!r}"
    )
