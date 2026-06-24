from datetime import date
from decimal import Decimal

import pytest

from app.core.validators import birth_date_from_id_card, normalize_id_card, parse_date, parse_decimal, parse_year


def test_id_card_checksum_and_birth_date():
    value = normalize_id_card("11010519491231002x")
    assert value == "11010519491231002X"
    assert birth_date_from_id_card(value) == date(1949, 12, 31)


def test_invalid_id_card_rejected():
    with pytest.raises(ValueError): normalize_id_card("110105194912310021")


def test_date_year_and_money_normalization():
    assert parse_date("2024年1月2日") == date(2024, 1, 2)
    assert parse_year("2023年") == 2023
    assert parse_decimal("￥1,234.5万元") == Decimal("1234.50")

