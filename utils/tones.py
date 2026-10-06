"""Matching detected audio frequencies against expected call-progress tones.

Tone detection is inherently approximate. An FFT bin lands a few hertz either
side of the nominal frequency, and carriers do not agree on exact values, so a
detected 1372 Hz has to satisfy an expectation of 1371 Hz. Everything here
therefore compares within a tolerance; nothing compares for equality.
"""

from __future__ import annotations

from typing import Iterable

#: How far a detected frequency may sit from the nominal one and still match.
#: 25 Hz comfortably covers FFT bin width at the window sizes we record with,
#: while staying well inside the ~40 Hz gap between ringback and busy tones.
DEFAULT_TOLERANCE_HZ = 25.0

#: Standard North American call-progress tones, as frequency pairs.
#: Congestion is absent on purpose: it uses the same 480/620 Hz pair as busy and
#: differs only in cadence, so telling them apart needs timing data that
#: frequency detection alone does not provide.
CALL_PROGRESS_TONES: dict[str, tuple[float, float]] = {
    "dial": (350.0, 440.0),
    "ringback": (440.0, 480.0),
    "busy": (480.0, 620.0),
}


def is_close(
    expected_hz: float,
    detected_hz: float,
    tolerance_hz: float = DEFAULT_TOLERANCE_HZ,
) -> bool:
    """Whether a single detected frequency satisfies a single expectation."""
    return abs(expected_hz - detected_hz) <= tolerance_hz


def find_matches(
    expected: Iterable[float],
    detected: Iterable[float],
    tolerance_hz: float = DEFAULT_TOLERANCE_HZ,
) -> list[tuple[float, float]]:
    """Pair up every expectation with the detected frequencies that satisfy it.

    Returning the pairs rather than a bare boolean is what makes a failure
    diagnosable: the report shows which tone was expected and what was actually
    heard near it.
    """
    detected = list(detected)
    return [
        (expected_hz, detected_hz)
        for expected_hz in expected
        for detected_hz in detected
        if is_close(expected_hz, detected_hz, tolerance_hz)
    ]


def any_detected(
    expected: Iterable[float],
    detected: Iterable[float],
    tolerance_hz: float = DEFAULT_TOLERANCE_HZ,
) -> bool:
    """Whether at least one expected frequency was heard."""
    return bool(find_matches(expected, detected, tolerance_hz))


def identify_tone(
    detected: Iterable[float],
    tolerance_hz: float = DEFAULT_TOLERANCE_HZ,
) -> str | None:
    """Name the call-progress tone made up of `detected`, if it is one.

    Both frequencies of a pair have to be present: a lone 480 Hz is ambiguous
    between ringback and busy, and guessing between them would turn a detection
    bug into a passing test.
    """
    detected = list(detected)
    for name, frequencies in CALL_PROGRESS_TONES.items():
        if all(
            any(is_close(frequency, heard, tolerance_hz) for heard in detected)
            for frequency in frequencies
        ):
            return name
    return None


def assert_tone_detected(
    expected: Iterable[float],
    detected: Iterable[float],
    tolerance_hz: float = DEFAULT_TOLERANCE_HZ,
) -> None:
    """Fail with the frequencies on both sides, so the report stands on its own."""
    expected, detected = list(expected), list(detected)
    if any_detected(expected, detected, tolerance_hz):
        return
    raise AssertionError(
        f"None of the expected tones were detected within {tolerance_hz:g} Hz\n"
        f"  expected: {expected}\n"
        f"  detected: {detected}"
    )
