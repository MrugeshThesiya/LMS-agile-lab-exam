import pytest

from app import MAX_FINE, calculate_fine


# Zero: returned on time -> no fine
def test_zero_days_no_fine():
    assert calculate_fine(0) == 0


# Valid: normal overdue values
@pytest.mark.parametrize(
    "days, expected",
    [(1, 10), (5, 50), (10, 100), (25, 250)],
)
def test_valid_days(days, expected):
    assert calculate_fine(days) == expected


# Boundary: around 0 and around the cap (cap of 500 is reached at 50 days)
@pytest.mark.parametrize(
    "days, expected",
    [
        (1, 10),            # just above zero
        (49, 490),          # just below the cap
        (50, MAX_FINE),     # exactly at the cap
        (51, MAX_FINE),     # just above the cap
        (1000, MAX_FINE),   # far above the cap
    ],
)
def test_boundary_days(days, expected):
    assert calculate_fine(days) == expected


def test_negative_one_is_rejected():
    # just below the lower boundary
    with pytest.raises(ValueError):
        calculate_fine(-1)


# Invalid: negative numbers
@pytest.mark.parametrize("days", [-1, -5, -100])
def test_negative_days_raise_value_error(days):
    with pytest.raises(ValueError):
        calculate_fine(days)


# Invalid: wrong types
@pytest.mark.parametrize("days", ["5", 2.5, None, [3], True, False])
def test_invalid_types_raise_type_error(days):
    with pytest.raises(TypeError):
        calculate_fine(days)

# Test change to show merging of branch