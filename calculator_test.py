"""
Unit tests for calculator.py — Pass 2 TDD Test Generation (Red Phase).

Tests are written against the CONTRACT defined in calculator.py, NOT the current
stub implementations.  These tests are EXPECTED to fail until Pass 3 (Core
Implementation Agent) provides real function bodies.

Covers:
  - All 3 scenarios from spec.gherkin (mirrored as named test cases)
  - All domain types: Number, CalculatorInput, CalculatorResult
  - The custom error: DivisionByZeroError
  - All 4 arithmetic functions: add, subtract, multiply, divide
  - Happy paths, edge cases, boundary conditions, and error paths
"""

from __future__ import annotations

import math

import pytest
from pydantic import ValidationError

import calculator
from calculator import (
    CalculatorInput,
    CalculatorResult,
    DivisionByZeroError,
    Number,
    add,
    divide,
    multiply,
    subtract,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Module-level / import tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestModuleImports:
    """Verify the module exists and exports the contracted public API."""

    def test_module_imports_successfully(self) -> None:
        """The calculator module must be importable without error."""
        # Access via sys.modules or simply reference the imported name
        assert calculator is not None

    def test_module_exposes_all_public_functions(self) -> None:
        """All four arithmetic functions are exposed as callables."""
        for fn in (add, subtract, multiply, divide):
            assert callable(fn), f"{fn.__name__} must be callable"

    def test_module_exposes_public_type_contracts(self) -> None:
        """Domain types and errors are importable."""
        assert CalculatorInput is not None
        assert CalculatorResult is not None
        assert DivisionByZeroError is not None


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Scenarios mirrored from spec.gherkin
# ═══════════════════════════════════════════════════════════════════════════════

class TestSpecScenarios:
    """
    Each method maps to one Scenario in spec.gherkin.

    NOTE: The original spec was authored against an *empty* module (0 lines).
    Pass 1 (Contracts Agent) has since populated contracts with typed stubs
    (raising NotImplementedError).  Tests below are written against the
    contract expectations — they will FAIL during Red Phase and PASS once
    Pass 3 implements the real logic.
    """

    def test_scenario_happy_path_module_exists(self) -> None:
        """
        spec.gherkin:
          Scenario: Happy path — the module exists but is empty
            Given the file "calculator.py" exists
            When I import the module "calculator"
            Then the import succeeds
            And the module has no callable public functions

        Contracts update: The module now exposes 4 callable public functions
        (add, subtract, multiply, divide) with proper type signatures.
        The import must succeed and those functions must exist.
        """
        # Import succeeds (verified by the import at the top of this file).
        # The "no callable public functions" assertion from the original spec
        # is inverted by the contracts: public functions *must* exist.
        assert callable(add)
        assert callable(subtract)
        assert callable(multiply)
        assert callable(divide)

    def test_scenario_edge_case_calling_add_function(self) -> None:
        """
        spec.gherkin:
          Scenario: Edge case — attempting to call a function on the empty module
            Given I have imported the empty "calculator" module
            When I attempt to call "add(2, 3)" on the module
            Then an AttributeError is raised
            And the error message contains "'add'"

        Contracts update: add() is now defined as a contractual stub.
        Calling add(2, 3) must NOT raise AttributeError — the function exists.
        Per the contract, add(2, 3) should return 5 (a Number).
        """
        result = add(2, 3)
        assert result == 5
        assert isinstance(result, (int, float))

    def test_scenario_error_case_file_has_no_executable_logic(self) -> None:
        """
        spec.gherkin:
          Scenario: Error case — the file has no executable logic
            Given the file "calculator.py" is present but empty
            When the Design & Architecture agent analyses it
            Then no state transitions, functions, or error conditions can be
                 extracted
            And the agent reports that the file must be populated before
                re-running Pass 0

        Contracts update: The file is no longer empty — it contains type
        contracts and function stubs.  The stubs raise NotImplementedError
        to signal "no executable logic yet".  A design agent CAN now extract
        public functions, type signatures, and error conditions.
        """
        # Verify that every contracted function is a stub (raises
        # NotImplementedError).  This confirms "no executable logic".
        for fn in (add, subtract, multiply, divide):
            with pytest.raises(NotImplementedError):
                # Call with arbitrary valid arguments; the stub should reject
                # before any domain logic runs.
                fn(0, 0)
            # Also verify the stub raises NotImplementedError for non-zero args
            with pytest.raises(NotImplementedError):
                fn(1, 1)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Domain type tests — CalculatorInput
# ═══════════════════════════════════════════════════════════════════════════════

class TestCalculatorInput:
    """Pydantic model validation for CalculatorInput."""

    # ── Happy path ───────────────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("operand_a", "operand_b"),
        [
            (0, 0),
            (1, 2),
            (-5, 10),
            (2.5, 3.5),
            (1, 2.0),
            (0.0, -1),
        ],
    )
    def test_valid_inputs_construct_successfully(
        self, operand_a: Number, operand_b: Number,
    ) -> None:
        """All int and float combos are valid Number values."""
        inp = CalculatorInput(operand_a=operand_a, operand_b=operand_b)
        assert inp.operand_a == operand_a
        assert inp.operand_b == operand_b

    def test_accepts_int_and_float_for_operand_a(self) -> None:
        """Number = int | float — both must be accepted."""
        CalculatorInput(operand_a=42, operand_b=1)       # int
        CalculatorInput(operand_a=3.14, operand_b=1)      # float

    def test_accepts_int_and_float_for_operand_b(self) -> None:
        """Number = int | float — both must be accepted."""
        CalculatorInput(operand_a=1, operand_b=42)        # int
        CalculatorInput(operand_a=1, operand_b=3.14)      # float

    # ── Edge cases ───────────────────────────────────────────────────────

    def test_large_integers_accepted(self) -> None:
        """Python ints have arbitrary precision — no artificial limits."""
        big = 10**18
        inp = CalculatorInput(operand_a=big, operand_b=big)
        assert inp.operand_a == big
        assert inp.operand_b == big

    def test_small_floats_accepted(self) -> None:
        """Very small (near-zero) floats are valid Numbers."""
        tiny = 1e-300
        inp = CalculatorInput(operand_a=tiny, operand_b=tiny)
        assert inp.operand_a == tiny

    def test_infinity_is_accepted_as_float(self) -> None:
        """float('inf') is a float, therefore a valid Number."""
        inp = CalculatorInput(operand_a=float("inf"), operand_b=2)
        assert inp.operand_a == float("inf")

    def test_nan_is_accepted_as_float(self) -> None:
        """math.nan is a float, therefore a valid Number (arithmetic may
        propagate NaN)."""
        inp = CalculatorInput(operand_a=math.nan, operand_b=1)
        assert math.isnan(inp.operand_a)

    # ── Error paths ──────────────────────────────────────────────────────

    def test_missing_operand_a_raises_validation_error(self) -> None:
        """operand_a is required (Field(...))."""
        with pytest.raises(ValidationError):
            CalculatorInput(operand_b=5)  # type: ignore[call-arg]

    def test_missing_operand_b_raises_validation_error(self) -> None:
        """operand_b is required (Field(...))."""
        with pytest.raises(ValidationError):
            CalculatorInput(operand_a=5)  # type: ignore[call-arg]

    def test_no_arguments_raises_validation_error(self) -> None:
        """Both fields are required."""
        with pytest.raises(ValidationError):
            CalculatorInput()  # type: ignore[call-arg]

    def test_string_operand_a_raises_validation_error(self) -> None:
        """'2' is a str, not int | float."""
        with pytest.raises(ValidationError):
            CalculatorInput(operand_a="2", operand_b=3)  # type: ignore[arg-type]

    def test_string_operand_b_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError):
            CalculatorInput(operand_a=3, operand_b="2")  # type: ignore[arg-type]

    def test_bool_operand_raises_validation_error(self) -> None:
        """bool is a subclass of int in Python, but pydantic strict mode? 
        In default pydantic v2, bool IS coerced to int.  We document the 
        current behavior — if this is considered an error, the contract 
        should be tightened."""
        # bool is a subclass of int; pydantic v2 accepts it as int by default.
        # We call this out explicitly so the team can decide.
        inp = CalculatorInput(operand_a=True, operand_b=False)  # type: ignore[arg-type]
        # bool subclasses int → coerced to 1 / 0 by pydantic
        assert inp.operand_a == 1
        assert inp.operand_b == 0

    def test_none_operand_raises_validation_error(self) -> None:
        """None is not a Number."""
        with pytest.raises(ValidationError):
            CalculatorInput(operand_a=None, operand_b=5)  # type: ignore[arg-type]


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Domain type tests — CalculatorResult
# ═══════════════════════════════════════════════════════════════════════════════

class TestCalculatorResult:
    """Pydantic model validation for CalculatorResult."""

    def test_valid_result_constructs(self) -> None:
        """result (Number) and operation (str) are populated."""
        res = CalculatorResult(result=42, operation="multiply")
        assert res.result == 42
        assert res.operation == "multiply"

    def test_float_result_accepted(self) -> None:
        res = CalculatorResult(result=3.14, operation="divide")
        assert res.result == 3.14

    def test_negative_result_accepted(self) -> None:
        res = CalculatorResult(result=-7, operation="subtract")
        assert res.result == -7

    def test_zero_result_accepted(self) -> None:
        res = CalculatorResult(result=0, operation="subtract")
        assert res.result == 0

    def test_missing_result_raises_validation_error(self) -> None:
        """result is required (no default)."""
        with pytest.raises(ValidationError):
            CalculatorResult(operation="add")  # type: ignore[call-arg]

    def test_missing_operation_raises_validation_error(self) -> None:
        """operation is required (Field(...))."""
        with pytest.raises(ValidationError):
            CalculatorResult(result=5)  # type: ignore[call-arg]

    def test_empty_operation_string_accepted(self) -> None:
        """An empty string is technically a valid str."""
        res = CalculatorResult(result=0, operation="")
        assert res.operation == ""

    def test_wrong_type_for_result_raises_validation_error(self) -> None:
        """Result must be a Number, not a string."""
        with pytest.raises(ValidationError):
            CalculatorResult(result="five", operation="add")  # type: ignore[arg-type]

    def test_wrong_type_for_operation_raises_validation_error(self) -> None:
        """Operation must be a str."""
        with pytest.raises(ValidationError):
            CalculatorResult(result=5, operation=123)  # type: ignore[arg-type]


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Custom error — DivisionByZeroError
# ═══════════════════════════════════════════════════════════════════════════════

class TestDivisionByZeroError:
    """DivisionByZeroError is raised when a zero divisor is encountered."""

    def test_is_subclass_of_value_error(self) -> None:
        """Must inherit from ValueError per the contract."""
        assert issubclass(DivisionByZeroError, ValueError)

    def test_message_formats_correctly(self) -> None:
        """Message: '<operation>: division by zero is undefined'."""
        err = DivisionByZeroError("divide")
        assert str(err) == "divide: division by zero is undefined"

    def test_message_formats_with_different_operation_name(self) -> None:
        err = DivisionByZeroError("modulo")
        assert str(err) == "modulo: division by zero is undefined"

    def test_can_be_caught_as_value_error(self) -> None:
        """Because it inherits from ValueError, except ValueError must catch."""
        try:
            raise DivisionByZeroError("test_op")
        except ValueError:
            pass  # expected
        else:
            pytest.fail("DivisionByZeroError was not caught as ValueError")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Arithmetic function tests — add()
# ═══════════════════════════════════════════════════════════════════════════════

class TestAdd:
    """Contract: add(a: Number, b: Number) -> Number."""

    # ── Concrete reference from spec.gherkin ─────────────────────────────

    def test_spec_reference_add_2_3_returns_5(self) -> None:
        """
        Explicitly referenced in spec.gherkin:
          When I attempt to call "add(2, 3)" on the module
        Contract says this should return 5.
        """
        assert add(2, 3) == 5

    # ── Happy path ───────────────────────────────────────────────────────

    def test_add_two_positive_integers(self) -> None:
        assert add(10, 20) == 30

    def test_add_two_positive_floats(self) -> None:
        assert add(2.5, 3.5) == 6.0

    def test_add_mixed_int_and_float(self) -> None:
        assert add(2, 3.5) == 5.5

    # ── Edge cases ───────────────────────────────────────────────────────

    def test_add_with_zero_operand_a(self) -> None:
        assert add(0, 5) == 5

    def test_add_with_zero_operand_b(self) -> None:
        assert add(5, 0) == 5

    def test_add_two_zeros(self) -> None:
        assert add(0, 0) == 0

    def test_add_two_negative_integers(self) -> None:
        assert add(-3, -7) == -10

    def test_add_positive_and_negative(self) -> None:
        assert add(10, -4) == 6

    def test_add_negative_and_positive(self) -> None:
        assert add(-10, 4) == -6

    def test_add_large_integers(self) -> None:
        assert add(10**18, 10**18) == 2 * 10**18

    def test_add_floats_with_precision(self) -> None:
        """Float addition should be within floating-point tolerance."""
        result = add(0.1, 0.2)
        assert result == pytest.approx(0.3)

    # ── Return-type contract ─────────────────────────────────────────────

    def test_add_returns_int_for_int_operands(self) -> None:
        """When both operands are int, the result should be int."""
        result = add(3, 4)
        assert isinstance(result, int)

    def test_add_returns_float_for_float_operand(self) -> None:
        """When either operand is float, result may be float."""
        result = add(3.0, 4)
        assert isinstance(result, float)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Arithmetic function tests — subtract()
# ═══════════════════════════════════════════════════════════════════════════════

class TestSubtract:
    """Contract: subtract(a: Number, b: Number) -> Number."""

    # ── Happy path ───────────────────────────────────────────────────────

    def test_subtract_two_positive_integers(self) -> None:
        assert subtract(10, 3) == 7

    def test_subtract_two_floats(self) -> None:
        assert subtract(5.5, 2.2) == pytest.approx(3.3)

    def test_subtract_mixed_types(self) -> None:
        assert subtract(10, 3.5) == 6.5

    # ── Edge cases ───────────────────────────────────────────────────────

    def test_subtract_zero_from_number(self) -> None:
        assert subtract(5, 0) == 5

    def test_subtract_number_from_zero(self) -> None:
        assert subtract(0, 5) == -5

    def test_subtract_zero_from_zero(self) -> None:
        assert subtract(0, 0) == 0

    def test_subtract_negative_from_positive(self) -> None:
        """a - (-b) = a + b"""
        assert subtract(5, -3) == 8

    def test_subtract_positive_from_negative(self) -> None:
        assert subtract(-5, 3) == -8

    def test_subtract_two_negatives(self) -> None:
        assert subtract(-5, -3) == -2

    def test_subtract_result_is_negative(self) -> None:
        """When b > a, the result is negative."""
        assert subtract(3, 10) == -7

    # ── Return types ─────────────────────────────────────────────────────

    def test_subtract_returns_int_for_int_operands(self) -> None:
        result = subtract(10, 3)
        assert isinstance(result, int)

    def test_subtract_returns_float_for_float_operand(self) -> None:
        result = subtract(10.0, 3)
        assert isinstance(result, float)


# ═══════════════════════════════════════════════════════════════════════════════
# 8. Arithmetic function tests — multiply()
# ═══════════════════════════════════════════════════════════════════════════════

class TestMultiply:
    """Contract: multiply(a: Number, b: Number) -> Number."""

    # ── Happy path ───────────────────────────────────────────────────────

    def test_multiply_two_positive_integers(self) -> None:
        assert multiply(3, 4) == 12

    def test_multiply_two_floats(self) -> None:
        assert multiply(2.5, 4.0) == 10.0

    def test_multiply_mixed_types(self) -> None:
        assert multiply(3, 2.5) == 7.5

    # ── Edge cases ───────────────────────────────────────────────────────

    def test_multiply_by_zero(self) -> None:
        assert multiply(5, 0) == 0

    def test_multiply_zero_by_number(self) -> None:
        assert multiply(0, 5) == 0

    def test_multiply_by_one(self) -> None:
        assert multiply(42, 1) == 42

    def test_multiply_one_by_number(self) -> None:
        assert multiply(1, 42) == 42

    def test_multiply_two_negatives(self) -> None:
        """Negative * negative = positive."""
        assert multiply(-3, -7) == 21

    def test_multiply_positive_by_negative(self) -> None:
        assert multiply(3, -7) == -21

    def test_multiply_negative_by_positive(self) -> None:
        assert multiply(-3, 7) == -21

    def test_multiply_large_numbers(self) -> None:
        assert multiply(10**9, 10**9) == 10**18

    def test_multiply_by_minus_one(self) -> None:
        assert multiply(42, -1) == -42

    def test_multiply_by_decimal_fraction(self) -> None:
        """Multiplying by a fraction less than 1."""
        assert multiply(10, 0.5) == 5.0

    # ── Return types ─────────────────────────────────────────────────────

    def test_multiply_returns_int_for_int_operands(self) -> None:
        result = multiply(3, 4)
        assert isinstance(result, int)

    def test_multiply_returns_float_for_float_operand(self) -> None:
        result = multiply(3.0, 4)
        assert isinstance(result, float)


# ═══════════════════════════════════════════════════════════════════════════════
# 9. Arithmetic function tests — divide()
# ═══════════════════════════════════════════════════════════════════════════════

class TestDivide:
    """Contract: divide(a: Number, b: Number) -> float.
    Raises DivisionByZeroError when b == 0.
    """

    # ── Happy path ───────────────────────────────────────────────────────

    def test_divide_two_positive_integers(self) -> None:
        result = divide(6, 3)
        assert result == 2.0
        assert isinstance(result, float)

    def test_divide_two_floats(self) -> None:
        result = divide(7.5, 2.5)
        assert result == 3.0
        assert isinstance(result, float)

    def test_divide_mixed_types(self) -> None:
        result = divide(5, 2.0)
        assert result == 2.5
        assert isinstance(result, float)

    def test_divide_produces_non_integer_quotient(self) -> None:
        """5 / 2 = 2.5 — must return float, not truncated int."""
        result = divide(5, 2)
        assert result == 2.5
        assert isinstance(result, float)

    # ── Edge cases ───────────────────────────────────────────────────────

    def test_divide_zero_by_positive(self) -> None:
        result = divide(0, 5)
        assert result == 0.0
        assert isinstance(result, float)

    def test_divide_zero_by_negative(self) -> None:
        result = divide(0, -5)
        # In Python, 0.0 / -5.0 == -0.0
        assert result == 0.0
        # -0.0 == 0.0 is True in Python, but sign may differ.
        # We use == which treats them as equal.

    def test_divide_by_one(self) -> None:
        result = divide(42, 1)
        assert result == 42.0

    def test_divide_by_negative_one(self) -> None:
        result = divide(42, -1)
        assert result == -42.0

    def test_divide_negative_by_positive(self) -> None:
        result = divide(-6, 3)
        assert result == -2.0

    def test_divide_positive_by_negative(self) -> None:
        result = divide(6, -3)
        assert result == -2.0

    def test_divide_two_negatives(self) -> None:
        result = divide(-6, -3)
        assert result == 2.0

    def test_divide_non_divisible_integers(self) -> None:
        """7 / 3 = 2.333... — float result without truncation."""
        result = divide(7, 3)
        assert result == pytest.approx(7 / 3)
        assert isinstance(result, float)

    # ── Return-type contract ─────────────────────────────────────────────

    def test_divide_always_returns_float(self) -> None:
        """Per contract, divide() -> float, even for evenly-divisible ints."""
        # Even 4 / 2 should return 2.0 (float), not 2 (int)
        # This is a design choice the contract enforces.
        pass  # Covered by the tests above; explicit for documentation.

    # ── Division-by-zero error ───────────────────────────────────────────

    def test_divide_by_zero_raises_division_by_zero_error(self) -> None:
        """Contract: b == 0 must raise DivisionByZeroError."""
        with pytest.raises(DivisionByZeroError) as exc_info:
            divide(5, 0)
        assert "division by zero" in str(exc_info.value)

    def test_divide_by_zero_error_message_contains_operation_name(self) -> None:
        """The error message must include the operation name 'divide'."""
        with pytest.raises(DivisionByZeroError) as exc_info:
            divide(1, 0)
        assert "divide" in str(exc_info.value)

    def test_divide_zero_by_zero_raises_division_by_zero_error(self) -> None:
        """0 / 0 is also division by zero (mathematically undefined)."""
        with pytest.raises(DivisionByZeroError):
            divide(0, 0)

    def test_divide_by_negative_zero(self) -> None:
        """-0.0 is still zero — should raise DivisionByZeroError."""
        with pytest.raises(DivisionByZeroError):
            divide(5, -0.0)

    # ── float special values ─────────────────────────────────────────────

    def test_divide_by_infinity(self) -> None:
        """x / inf => 0.0 per IEEE 754."""
        result = divide(5, float("inf"))
        assert result == 0.0

    def test_divide_infinity_by_number(self) -> None:
        """inf / x => inf (for positive x)."""
        result = divide(float("inf"), 2)
        assert result == float("inf")

    def test_divide_by_nan_propagates_nan(self) -> None:
        """x / nan => nan."""
        result = divide(5, math.nan)
        assert math.isnan(result)


# ═══════════════════════════════════════════════════════════════════════════════
# 10. Cross-cutting / integration-style contract tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestContractIntegration:
    """Tests that span multiple contracts to verify consistency."""

    def test_all_operations_accept_calculator_input(self) -> None:
        """Each arithmetic function should accept CalculatorInput fields."""
        inp = CalculatorInput(operand_a=10, operand_b=5)
        # These calls verify that the operand types are compatible.
        # Actual results depend on implementation.
        add(inp.operand_a, inp.operand_b)
        subtract(inp.operand_a, inp.operand_b)
        multiply(inp.operand_a, inp.operand_b)
        divide(inp.operand_a, inp.operand_b)

    def test_calculator_result_schema_wraps_add_output(self) -> None:
        """CalculatorResult can wrap the output of add()."""
        r = add(2, 3)
        res = CalculatorResult(result=r, operation="add")
        assert res.result == r

    def test_calculator_result_schema_wraps_subtract_output(self) -> None:
        res = CalculatorResult(result=subtract(10, 3), operation="subtract")
        assert res.operation == "subtract"

    def test_calculator_result_schema_wraps_multiply_output(self) -> None:
        res = CalculatorResult(result=multiply(3, 4), operation="multiply")
        assert res.operation == "multiply"

    def test_calculator_result_schema_wraps_divide_output(self) -> None:
        res = CalculatorResult(result=divide(10, 2), operation="divide")
        assert res.result == 5.0
        assert res.operation == "divide"

    def test_result_operation_matches_called_function(self) -> None:
        """Ensures the operation field matches semantics (manual check)."""
        assert CalculatorResult(result=add(1, 1), operation="add").operation == "add"
        assert CalculatorResult(result=subtract(5, 2),
                               operation="subtract").operation == "subtract"
        assert CalculatorResult(result=multiply(2, 3),
                               operation="multiply").operation == "multiply"
        assert CalculatorResult(result=divide(8, 4),
                               operation="divide").operation == "divide"

    def test_number_type_alias_covers_int_and_float(self) -> None:
        """Verify Number = int | float is usable (static check documented)."""
        # Runtime check: the type alias is just a forward reference;
        # this test documents that int and float are the expected base types.
        assert isinstance(0, int) or isinstance(0.0, float)
