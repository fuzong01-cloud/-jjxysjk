import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any


ID_WEIGHTS = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
ID_CHECK_CODES = "10X98765432"


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).replace("\u3000", " ").strip()
    return text or None


def normalize_id_card(value: Any, validate_checksum: bool = True) -> str:
    text = re.sub(r"\s+", "", clean_text(value) or "").upper()
    if not re.fullmatch(r"\d{17}[\dX]", text):
        raise ValueError("身份证号必须为18位，末位可以是X")
    try:
        datetime.strptime(text[6:14], "%Y%m%d")
    except ValueError as exc:
        raise ValueError("身份证号中的出生日期无效") from exc
    if validate_checksum:
        code = ID_CHECK_CODES[sum(int(text[i]) * ID_WEIGHTS[i] for i in range(17)) % 11]
        if code != text[-1]:
            raise ValueError("身份证号校验码不正确")
    return text


def birth_date_from_id_card(value: str) -> date:
    return datetime.strptime(value[6:14], "%Y%m%d").date()


def gender_from_id_card(value: str) -> str:
    return "男" if int(value[16]) % 2 else "女"


def normalize_phone(value: Any) -> str | None:
    text = re.sub(r"[\s\-]", "", clean_text(value) or "")
    if not text:
        return None
    if not re.fullmatch(r"1[3-9]\d{9}", text):
        raise ValueError("手机号格式不正确")
    return text


def parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = clean_text(value)
    if not text:
        return None
    text = text.replace("年", "-").replace("月", "-").replace("日", "").replace("/", "-").replace(".", "-")
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError("日期格式无法识别")


def parse_year(value: Any) -> int | None:
    if value in (None, ""):
        return None
    match = re.search(r"(19|20)\d{2}", str(value))
    if not match:
        raise ValueError("年份格式无法识别")
    year = int(match.group())
    if not 1900 <= year <= date.today().year + 5:
        raise ValueError("年份超出合理范围")
    return year


def parse_decimal(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    text = re.sub(r"[,，￥¥元万元\s]", "", str(value))
    try:
        return Decimal(text).quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise ValueError("金额格式无法识别") from exc


def parse_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(str(value).strip()))
    except ValueError as exc:
        raise ValueError("整数格式无法识别") from exc

