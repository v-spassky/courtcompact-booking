import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat


class InvalidPhoneNumber(ValueError):
    pass


def normalize_phone(raw_phone_number: str) -> str:
    stripped = raw_phone_number.strip()
    if not stripped.startswith('+'):
        stripped = '+' + stripped
    try:
        parsed = phonenumbers.parse(stripped)
    except NumberParseException as e:
        raise InvalidPhoneNumber(f'Cannot parse phone number: {raw_phone_number!r}') from e
    if not phonenumbers.is_valid_number(parsed):
        raise InvalidPhoneNumber(f'Invalid phone number: {raw_phone_number!r}')
    return phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
