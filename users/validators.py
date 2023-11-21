import phonenumbers
from django.core.exceptions import ValidationError


def validate_pnfl(value: str):
    if not len(value) == 14:
        raise ValidationError("invalid_pnfl_error")
    return value


def validate_passport(value: str):
    value = value.replace(" ", "")
    if (value[0].isdigit() or value[1].isdigit() or not value[2:].isdigit()) or not len(value) == 9:
        raise ValidationError("invalid_passport_error")
    return value


def validate_phone(value: str):
    try:
        phonenumbers.parse(value)
    except Exception:
        raise ValidationError("invalid_phone_number")
    return value
