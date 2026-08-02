def match_found(expected_frequencies: list, detected_frequencies: list) -> bool:
    # TODO: верни True, если хотя бы одна частота из expected_frequencies
    # встречается в detected_frequencies. Аналог твоего JS-цикла for + includes + break.
    for frequencies in expected_frequencies:
        if frequencies in detected_frequencies:
            return True
    return False
    pass
def test_match_found_when_overlap_exists():
    expected = [915, 1371, 1777]
    detected = [1371, 2000]
    assert match_found(expected, detected) is True
def test_match_found_when_no_overlap():
    expected = [915, 1371, 1777]
    detected = [100, 200]
    assert match_found(expected, detected) is False
def test_match_found_with_empty_detected_list():
    expected = [915, 1371, 1777]
    detected = []
    assert match_found(expected, detected) is False