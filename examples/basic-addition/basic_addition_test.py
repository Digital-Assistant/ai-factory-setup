"""Unit tests for the sample_target arithmetic module.

These tests directly reflect the Scenarios defined in spec.gherkin and
the architecture constraints in design.mmd. Each test is independent,
deterministic, and idempotent — no shared mutable state is used.
"""

import math
import sys

import pytest

# Import the module under test from the same directory.
# We use importlib so tests work regardless of the caller's CWD.
from importlib import util as _import_util

_spec = _import_util.spec_from_file_location(
    "sample_target", __file__.rsplit("/", 1)[0] + "/sample_target.py"
)
_sample_target = _import_util.module_from_spec(_spec)
_spec.loader.exec_module(_sample_target)

# Convenience aliases to keep test bodies short and readable.
add = _sample_target.add
subtract = _sample_target.subtract
multiply = _sample_target.multiply
divide = _sample_target.divide


# ---------------------------------------------------------------------------
# Happy-path tests — directly mapped to spec.gherkin Scenarios
# ---------------------------------------------------------------------------

class TestAdd:
    """Tests for the ``add`` function."""

    # Scenario: Add two positive integers
    def test_add_two_positive_integers(self):
        assert add(2, 3) == 5

    # Scenario: Add two floating point numbers
    def test_add_two_floating_point_numbers(self):
        assert add(2.5, 3.5) == 6.0

    # Scenario: Add negative numbers
    def test_add_two_negative_numbers(self):
        assert add(-5, -3) == -8

    # Additional edge cases
    def test_add_positive_and_negative(self):
        assert add(10, -3) == 7
        assert add(-10, 3) == -7

    def test_add_with_zero(self):
        assert add(0, 5) == 5
        assert add(5, 0) == 5
        assert add(0, 0) == 0

    def test_add_large_integers(self):
        assert add(10**18, 10**18) == 2 * 10**18

    def test_add_float_and_int(self):
        result = add(2, 3.5)
        assert result == 5.5
        assert isinstance(result, float)

    def test_add_very_small_floats(self):
        # Near zero, close to but not at underflow
        small = sys.float_info.min * 2
        result = add(small, small)
        assert math.isclose(result, small * 2, rel_tol=1e-15)

    def test_add_infinity(self):
        assert add(float("inf"), 1) == float("inf")
        assert add(float("-inf"), -1) == float("-inf")

    def test_add_nan_propagates(self):
        result = add(float("nan"), 1)
        assert math.isnan(result)


class TestSubtract:
    """Tests for the ``subtract`` function."""

    # Scenario: Subtract a smaller number from a larger number
    def test_subtract_smaller_from_larger(self):
        assert subtract(5, 3) == 2

    # Scenario: Subtract a larger number from a smaller number
    def test_subtract_larger_from_smaller(self):
        assert subtract(3, 5) == -2

    # Additional edge cases
    def test_subtract_negative_numbers(self):
        assert subtract(-5, -3) == -2
        assert subtract(-3, -5) == 2

    def test_subtract_with_zero(self):
        assert subtract(5, 0) == 5
        assert subtract(0, 5) == -5
        assert subtract(0, 0) == 0

    def test_subtract_float_and_int(self):
        result = subtract(5.5, 2)
        assert result == 3.5
        assert isinstance(result, float)

    def test_subtract_identical_values(self):
        assert subtract(7, 7) == 0
        assert subtract(3.14, 3.14) == 0.0
        assert subtract(-42, -42) == 0

    def test_subtract_large_numbers(self):
        assert subtract(10**18, 10**17) == 9 * 10**17

    def test_subtract_infinity(self):
        assert subtract(float("inf"), 1) == float("inf")
        assert subtract(float("-inf"), -1) == float("-inf")

    def test_subtract_nan_propagates(self):
        result = subtract(float("nan"), 1)
        assert math.isnan(result)


class TestMultiply:
    """Tests for the ``multiply`` function."""

    # Scenario: Multiply two positive integers
    def test_multiply_two_positive_integers(self):
        assert multiply(4, 3) == 12

    # Scenario: Multiply by zero
    def test_multiply_by_zero(self):
        assert multiply(5, 0) == 0

    # Scenario: Multiply two negative numbers
    def test_multiply_two_negative_numbers(self):
        assert multiply(-4, -3) == 12

    # Additional edge cases
    def test_multiply_positive_and_negative(self):
        assert multiply(4, -3) == -12
        assert multiply(-4, 3) == -12

    def test_multiply_with_one(self):
        assert multiply(1, 42) == 42
        assert multiply(42, 1) == 42

    def test_multiply_with_negative_one(self):
        assert multiply(-1, 42) == -42
        assert multiply(42, -1) == -42

    def test_multiply_floats(self):
        result = multiply(2.5, 4.0)
        assert result == 10.0
        assert isinstance(result, float)

    def test_multiply_int_and_float(self):
        result = multiply(3, 2.5)
        assert result == 7.5
        assert isinstance(result, float)

    def test_multiply_large_numbers(self):
        assert multiply(10**9, 10**9) == 10**18

    def test_multiply_zero_by_zero(self):
        assert multiply(0, 0) == 0

    def test_multiply_infinity_by_positive(self):
        assert multiply(float("inf"), 2) == float("inf")

    def test_multiply_infinity_by_negative(self):
        assert multiply(float("inf"), -2) == float("-inf")

    def test_multiply_nan_propagates(self):
        result = multiply(float("nan"), 1)
        assert math.isnan(result)


class TestDivide:
    """Tests for the ``divide`` function."""

    # Scenario: Divide two positive numbers
    def test_divide_two_positive_numbers(self):
        assert divide(10, 2) == 5.0

    # Scenario: Divide resulting in a floating point quotient
    def test_divide_float_quotient(self):
        assert divide(7, 2) == 3.5

    # Scenario: Divide zero by a non-zero number
    def test_divide_zero_by_nonzero(self):
        assert divide(0, 5) == 0.0

    # Scenario: Divide negative numbers
    def test_divide_negative_numbers(self):
        assert divide(-10, 2) == -5.0

    # Scenario: Divide by zero raises ZeroDivisionError
    def test_divide_by_zero_raises_zero_division_error(self):
        """Scenario: Divide by zero raises ZeroDivisionError with message."""
        with pytest.raises(ZeroDivisionError, match="division by zero"):
            divide(5, 0)

    # Additional edge cases
    def test_divide_by_negative_zero_is_caught(self):
        """Negative zero should be treated the same as positive zero."""
        with pytest.raises(ZeroDivisionError):
            divide(5, -0.0)

    def test_divide_negative_by_negative(self):
        assert divide(-10, -2) == 5.0

    def test_divide_positive_by_negative(self):
        assert divide(10, -2) == -5.0

    def test_divide_int_returns_float(self):
        """Division of two ints always returns a float in Python 3."""
        result = divide(6, 3)
        assert result == 2.0
        assert isinstance(result, float)

    def test_divide_with_floats(self):
        assert divide(7.5, 2.5) == 3.0

    def test_divide_one_by_itself(self):
        assert divide(42, 42) == 1.0

    def test_divide_one_by_many(self):
        assert divide(1, 10**6) == pytest.approx(1e-6)

    def test_divide_by_one(self):
        assert divide(42, 1) == 42.0

    def test_divide_by_negative_one(self):
        assert divide(42, -1) == -42.0

    def test_divide_infinity_by_finite(self):
        assert divide(float("inf"), 2) == float("inf")

    def test_divide_negative_infinity_by_finite(self):
        assert divide(float("-inf"), 2) == float("-inf")

    def test_divide_finite_by_infinity(self):
        assert divide(42, float("inf")) == 0.0

    def test_divide_nan_propagates(self):
        result = divide(float("nan"), 1)
        assert math.isnan(result)


# ---------------------------------------------------------------------------
# Cross-cutting / robustness tests
# ---------------------------------------------------------------------------

class TestModuleIdentity:
    """Verify the module is correctly loadable and all functions are callable."""

    def test_all_functions_are_callable(self):
        assert callable(add)
        assert callable(subtract)
        assert callable(multiply)
        assert callable(divide)

    def test_all_functions_have_docstrings(self):
        assert add.__doc__ is not None
        assert subtract.__doc__ is not None
        assert multiply.__doc__ is not None
        assert divide.__doc__ is not None


class TestCommutativity:
    """Arithmetic properties tests."""

    def test_add_is_commutative(self):
        for a, b in [(3, 5), (3.5, 7.2), (-4, 9), (0, -7)]:
            assert add(a, b) == add(b, a)

    def test_multiply_is_commutative(self):
        for a, b in [(3, 5), (3.5, 7.2), (-4, 9), (0, -7)]:
            assert multiply(a, b) == multiply(b, a)


class TestIdentityElements:
    """Additive and multiplicative identity tests."""

    def test_additive_identity(self):
        for x in [0, 1, -1, 42, -99, 3.14]:
            assert add(x, 0) == x
            assert add(0, x) == x

    def test_multiplicative_identity(self):
        for x in [0, 1, -1, 42, -99, 3.14]:
            assert multiply(x, 1) == x
            assert multiply(1, x) == x

    @pytest.mark.parametrize(
        "a, b",
        [
            (0, 0),
            (0, 0.0),
            (0.0, 0),
            (0.0, 0.0),
            (-0.0, 0),
            (0, -0.0),
        ],
    )
    def test_divide_by_all_forms_of_zero_raises(self, a, b):
        """Any representation of zero as the divisor must raise."""
        with pytest.raises(ZeroDivisionError):
            divide(a, b)


class TestInverseRoundTrips:
    """Verify that subtraction inverts addition, and division inverts multiplication."""

    def test_subtraction_inverts_addition(self):
        for a, b in [(7, 3), (2.5, 1.5), (-4, 2)]:
            assert subtract(add(a, b), b) == a

    def test_division_inverts_multiplication(self):
        for a, b in [(6, 3), (10, 4), (-20, 5)]:
            assert divide(multiply(a, b), b) == float(a)
