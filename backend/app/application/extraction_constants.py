"""Shared constants for field normalization, quality checks, and observability."""

MICROCHIP_MIN_DIGITS: int = 9
MICROCHIP_MAX_DIGITS: int = 15

WEIGHT_MIN_KG: float = 0.5
WEIGHT_MAX_KG: float = 120.0

MAX_VALUE_LENGTH: int = 80
PET_NAME_MIN_LENGTH: int = 1
CLINIC_NAME_MIN_LENGTH: int = 2
CLINIC_ADDRESS_MIN_LENGTH: int = 10
OWNER_ADDRESS_MAX_LENGTH: int = 120

MAX_PET_AGE_YEARS: int = 40
DAYS_PER_YEAR: float = 365.25

PHONE_DIGIT_COUNT: int = 9

QUALITY_SCORE_THRESHOLD: float = 0.60
