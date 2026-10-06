"""Unit tests for the fuzzy transcript assertions in `utils.asr`.

These helpers decide whether a voice test passes, so a bug here either hides
real regressions or produces flaky failures. They are therefore pinned down
much more tightly than the UI and API suites.
"""

import allure
import pytest

from utils import asr

pytestmark = [pytest.mark.unit, allure.feature("ASR assertions")]


@allure.story("Normalisation")
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Hello, world!", "hello world", ),
        ("Hello    world", "hello world"),
        ("  Hi!!  there,  friend.  ", "hi there friend"),
        ("Your PIN is 1-2-3-4.", "your pin is 1234"),
        ("MIXED Case TEXT", "mixed case text"),
        ("", ""),
        ("   ", ""),
        ("!!!", ""),
    ],
    ids=[
        "strips-punctuation",
        "collapses-runs-of-spaces",
        "handles-both-plus-outer-padding",
        "strips-digit-separators",
        "lowercases",
        "empty-string",
        "whitespace-only",
        "punctuation-only",
    ],
)
def test_normalize_reduces_text_to_comparable_form(raw, expected):
    assert asr.normalize(raw) == expected


@allure.story("Normalisation")
def test_normalize_collapses_newlines_and_tabs_like_spaces():
    assert asr.normalize("line one\n\tline two") == "line one line two"


@allure.story("Similarity")
def test_identical_text_scores_one():
    assert asr.similarity("the call is being recorded", "the call is being recorded") == 1.0


@allure.story("Similarity")
def test_punctuation_and_casing_alone_do_not_lower_the_score():
    assert asr.similarity("The call is being recorded.", "the call is being recorded") == 1.0


@allure.story("Similarity")
def test_unrelated_text_scores_far_below_the_threshold():
    assert asr.similarity("press one for sales", "qwerty zxcvbn") < 0.5


@allure.story("Similarity")
def test_score_is_symmetric_in_its_arguments():
    first = asr.similarity("your balance is twelve euros", "your balance is twelve euro")
    second = asr.similarity("your balance is twelve euro", "your balance is twelve euros")
    assert first == second


@allure.story("Matching")
@pytest.mark.parametrize(
    ("expected", "actual"),
    [
        ("Please hold while we connect you.", "please hold while we connect you"),
        ("Your balance is twelve euros.", "Your balance is twelve euro"),
        ("The call is being recorded", "The  call   is being recorded!"),
    ],
    ids=["punctuation-drift", "single-word-misheard", "whitespace-drift"],
)
def test_realistic_engine_drift_still_matches(expected, actual):
    assert asr.matches(expected, actual)


@allure.story("Matching")
def test_a_different_utterance_does_not_match():
    assert not asr.matches("press one for sales", "press two for support")


@allure.story("Matching")
def test_threshold_of_one_demands_an_exact_normalised_match():
    assert asr.matches("twelve euros", "twelve euro", threshold=1.0) is False
    assert asr.matches("twelve euros", "Twelve euros!", threshold=1.0) is True


@allure.story("Matching")
def test_lowering_the_threshold_admits_looser_transcripts():
    expected, actual = "press one for sales", "press two for support"
    assert not asr.matches(expected, actual)
    assert asr.matches(expected, actual, threshold=0.5)


@allure.story("Keyword search")
@pytest.mark.parametrize(
    ("phrase", "transcript", "found"),
    [
        ("account 4421", "Your account, 4-4-2-1, is now active.", True),
        ("ACCOUNT 4421", "your account 4421 is now active", True),
        ("account 4422", "Your account, 4-4-2-1, is now active.", False),
        ("", "anything at all", True),
    ],
    ids=["ignores-separators", "ignores-casing", "rejects-wrong-number", "empty-phrase-is-trivially-present"],
)
def test_contains_phrase(phrase, transcript, found):
    assert asr.contains_phrase(phrase, transcript) is found


@allure.story("Assertion helper")
def test_assert_matches_is_silent_on_success():
    asr.assert_matches("the call is being recorded", "The call is being recorded!")


@allure.story("Assertion helper")
def test_assert_matches_reports_the_score_and_both_normalised_forms():
    with pytest.raises(AssertionError) as failure:
        asr.assert_matches("press one for sales", "qwerty zxcvbn")

    message = str(failure.value)
    assert "similarity" in message
    assert "press one for sales" in message
    assert "qwerty zxcvbn" in message
