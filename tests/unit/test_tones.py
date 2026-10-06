"""Unit tests for the tone matching helpers in `utils.tones`."""

import allure
import pytest

from utils import tones

pytestmark = [pytest.mark.unit, allure.feature("Call-progress tone matching")]


@allure.story("Single frequency")
@pytest.mark.parametrize(
    ("expected_hz", "detected_hz", "close"),
    [
        (1371.0, 1371.0, True),
        (1371.0, 1372.0, True),
        (1371.0, 1396.0, True),
        (1371.0, 1396.1, False),
        (1371.0, 1500.0, False),
        (440.0, 415.0, True),
        (440.0, 400.0, False),
    ],
    ids=[
        "exact",
        "one-hz-of-drift",
        "exactly-at-the-tolerance-boundary",
        "just-past-the-boundary",
        "far-away",
        "drift-downwards",
        "too-far-downwards",
    ],
)
def test_is_close_honours_the_default_tolerance(expected_hz, detected_hz, close):
    assert tones.is_close(expected_hz, detected_hz) is close


@allure.story("Single frequency")
def test_tolerance_is_configurable_per_call():
    assert not tones.is_close(1371.0, 1420.0)
    assert tones.is_close(1371.0, 1420.0, tolerance_hz=50)


@allure.story("Frequency sets")
def test_find_matches_pairs_each_expectation_with_what_was_heard():
    matches = tones.find_matches(expected=[915, 1371, 1777], detected=[1372, 2000])
    assert matches == [(1371.0, 1372.0)]


@allure.story("Frequency sets")
def test_find_matches_reports_every_pair_not_just_the_first():
    matches = tones.find_matches(expected=[440, 480], detected=[441, 479])
    assert sorted(matches) == [(440.0, 441.0), (480.0, 479.0)]


@allure.story("Frequency sets")
@pytest.mark.parametrize(
    ("expected", "detected", "detected_at_all"),
    [
        ([915, 1371, 1777], [1371, 2000], True),
        ([915, 1371, 1777], [100, 200], False),
        ([915, 1371, 1777], [], False),
        ([], [915, 1371], False),
        ([], [], False),
    ],
    ids=["overlap", "no-overlap", "silence", "no-expectation", "both-empty"],
)
def test_any_detected(expected, detected, detected_at_all):
    assert tones.any_detected(expected, detected) is detected_at_all


@allure.story("Tone identification")
@pytest.mark.parametrize(
    ("detected", "name"),
    [
        ([350, 440], "dial"),
        ([440, 480], "ringback"),
        ([480, 620], "busy"),
        ([441, 479], "ringback"),
        ([440, 480, 1000], "ringback"),
        ([480], None),
        ([1371], None),
        ([], None),
    ],
    ids=[
        "dial",
        "ringback",
        "busy",
        "both-frequencies-drifting",
        "extra-noise-alongside-the-tone",
        "half-a-tone-is-ambiguous",
        "unknown-frequency",
        "silence",
    ],
)
def test_identify_tone_requires_both_frequencies_of_a_pair(detected, name):
    assert tones.identify_tone(detected) == name


@allure.story("Assertion helper")
def test_assert_tone_detected_is_silent_on_success():
    tones.assert_tone_detected(expected=[1371], detected=[1372])


@allure.story("Assertion helper")
def test_assert_tone_detected_reports_both_sides():
    with pytest.raises(AssertionError) as failure:
        tones.assert_tone_detected(expected=[1371], detected=[440, 480])

    message = str(failure.value)
    assert "1371" in message
    assert "440" in message
