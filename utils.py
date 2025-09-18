from decimal import Decimal, InvalidOperation


def to_decimal_or_none(s):
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError, TypeError):
        return None