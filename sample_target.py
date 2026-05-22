"""
sample_target — Basic arithmetic operations module.

This module provides a minimal set of pure functions for performing
addition, subtraction, multiplication, and division. All functions are
stateless and side-effect-free (except for ``divide``, which raises a
``ZeroDivisionError`` when the divisor is zero).

Architecture
------------
Each function accepts two numeric operands and returns the result of the
corresponding arithmetic operation. No external dependencies or
configuration are required.

.. seealso:: ``design.mmd`` — high-level architectural diagram.
"""


def add(a, b):
    """Return the sum of two numbers.

    Args:
        a (int | float): The first addend.
        b (int | float): The second addend.

    Returns:
        int | float: The result of ``a + b``.

    Example:
        >>> add(3, 5)
        8
    """
    return a + b


def subtract(a, b):
    """Return the difference between two numbers.

    Args:
        a (int | float): The minuend.
        b (int | float): The subtrahend.

    Returns:
        int | float: The result of ``a - b``.

    Example:
        >>> subtract(10, 3)
        7
    """
    return a - b


def multiply(a, b):
    """Return the product of two numbers.

    Args:
        a (int | float): The first factor.
        b (int | float): The second factor.

    Returns:
        int | float: The result of ``a * b``.

    Example:
        >>> multiply(4, 5)
        20
    """
    return a * b


def divide(a, b):
    """Return the quotient of two numbers.

    Args:
        a (int | float): The dividend (numerator).
        b (int | float): The divisor (denominator).

    Returns:
        float: The result of ``a / b``.

    Raises:
        ZeroDivisionError: If ``b`` is zero.

    Example:
        >>> divide(10, 2)
        5.0
        >>> divide(5, 0)
        Traceback (most recent call last):
            ...
        ZeroDivisionError: division by zero
    """
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b

