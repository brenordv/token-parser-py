# -*- coding: utf-8 -*-
import ast
from datetime import datetime, timedelta
import random
import pytz
from dateutil.parser import parse
import json
from dateutil.relativedelta import relativedelta
from uuid import uuid4

from utils import ISO8601_DATE_FORMAT_UTC

MAP = {
    "$now()": "datetime.now()",
    "$utcNow()": "datetime.utcnow()",
    "$now(dt_string_ref)": "datetime(dt_string_ref)",
    "$utcNow(dt_string_ref)": "utc datetime(dt_string_ref)",
    "$dateAdd(dt_string_ref, {microseconds?: int, milliseconds?: int, seconds?: int, minutes?: int, hours?: int, days?: int, months?: int, weeks?: int years?: int})":
        "date added of options parameters",
    "$int(n)": "int(n)",
    "$int(a, b)": "rand int a <= N <= b",
    "$int(a, b, c, ..., x)": "a || b || c || ... || x",
    "$float(n)": "float(n)",
    "$float(a, b)": "rand float a <= N <= b",
    "$float(a, b, c, ..., x)": "float: a || b || c || ... || x",
    "$inc(incBy:int=1)": "will start counting from zero + inbBy",
    "$dec(decBy:int=1)": "will start counting from zero - decBy",
    "$guid(keep: bool = False)": "returns a guid string. if keep is true, will always return the same guid."
}

CURRENT_INC_VALUE = 0
DEFAULT_INC_BY_VALUE = 1
CURRENT_DEC_VALUE = 0
DEFAULT_DEC_BY_VALUE = 1
CURRENT_GUID = None


def _get_now_(now_ref, is_utc: bool):
    if now_ref is None:
        return datetime.now() if not is_utc else datetime.utcnow().astimezone(pytz.utc)

    return now_ref if not is_utc else now_ref.astimezone(pytz.utc)


def _get_number_(required, num_type):
    req_num_size = len(required)

    if req_num_size == 0:
        return 0

    if req_num_size == 1:
        return num_type(required[0])

    if req_num_size == 2:
        if num_type == float:
            return random.uniform(num_type(required[0]), num_type(required[1]))
        else:
            return random.randint(num_type(required[0]), num_type(required[1]))

    return random.choice([num_type(n) for n in required])


def _get_int_(text) -> int:
    required_numbers = text.replace("$int(", "").replace(")", "").split(",")
    return _get_number_(required_numbers, int)


def _get_float_(text) -> float:
    required_numbers = text.replace("$float(", "").replace(")", "").split(",")
    return _get_number_(required_numbers, float)


def _prepare_base_date_(dt_text, dt_ref, is_utc):
    if dt_ref is not None:
        return dt_ref

    if dt_text == "now":
        return datetime.now()

    elif dt_text == "utcNow":
        return datetime.utcnow().astimezone(pytz.utc)

    try:
        dt = datetime.strptime(dt_text, ISO8601_DATE_FORMAT_UTC)
        if is_utc:
            dt = dt.replace(tzinfo=pytz.utc)
        return dt

    except ValueError:
        return parse(dt_text)


def _parse_options_json_(options_txt) -> dict:
    try:
        return json.loads(options_txt)
    except (TypeError, ValueError):
        return ast.literal_eval(options_txt)


def _get_date_added_(dt_text, options_txt, dt_ref: datetime = None):
    base_dt = _prepare_base_date_(dt_text, dt_ref, is_utc=dt_text.upper().endswith("Z"))
    options = _parse_options_json_(options_txt) if len(options_txt) > 0 else {}

    for op_key in ["microseconds", "milliseconds", "seconds", "minutes", "hours", "days", "weeks", "months", "years"]:
        val = options.get(op_key)
        if val is None:
            continue

        if op_key in ["months", "years"]:
            base_dt += relativedelta(**{op_key: val})
        else:
            base_dt += timedelta(**{op_key: val})

    return base_dt


def _get_inc_by_(text: str) -> int:
    global CURRENT_INC_VALUE
    global DEFAULT_INC_BY_VALUE

    inc_by_str = text.replace("$inc(", "").replace(")", "").strip()
    CURRENT_INC_VALUE += DEFAULT_INC_BY_VALUE if inc_by_str == "" else int(inc_by_str)
    return CURRENT_INC_VALUE


def _reset_inc_by_() -> None:
    global CURRENT_INC_VALUE
    CURRENT_INC_VALUE = 0


def _get_dec_by_(text: str) -> int:
    global CURRENT_DEC_VALUE
    global DEFAULT_DEC_BY_VALUE

    inc_by_str = text.replace("$dec(", "").replace(")", "").strip()
    CURRENT_DEC_VALUE -= DEFAULT_DEC_BY_VALUE if inc_by_str == "" else int(inc_by_str)
    return CURRENT_DEC_VALUE


def _reset_dec_by_() -> None:
    global CURRENT_DEC_VALUE
    CURRENT_DEC_VALUE = 0


def _extract_date_add_params_(date_add):
    params = [s.strip() for s in date_add.split(",")]
    if len(params) > 2:
        params = [
            params[0],
            ", ".join(params[1:])
        ]
    return params


def _get_guid_(text):
    global CURRENT_GUID

    keep_str = text.replace("$guid(", "").replace(")", "").strip()
    keep = keep_str.upper() == "TRUE"
    if keep and CURRENT_GUID is None:
        CURRENT_GUID = str(uuid4())

    return CURRENT_GUID if keep else str(uuid4())


def parse_token(text: str) -> any:
    if text is None or text.strip() == "":
        return None

    _text = text.strip()

    if _text in ["$now()", "$utcNow()"]:
        is_utc = _text == "$utcNow()"
        return _get_now_(now_ref=None, is_utc=is_utc)

    if any(x in _text for x in ["$now(", "$utcNow("]) and _text.endswith(")"):
        is_utc = _text.startswith("$utcNow")
        dt_text = _text.replace("$utcNow(", "").replace("$now(", "")
        return _get_now_(
            now_ref=_prepare_base_date_(
                dt_text=dt_text[:len(dt_text) - 1], dt_ref=None, is_utc=is_utc
            ),
            is_utc=is_utc
        )

    if _text.startswith("$int(") and _text.endswith(")"):
        return _get_int_(_text)

    if _text.startswith("$float(") and _text.endswith(")"):
        return _get_float_(_text)

    if _text.startswith("$inc(") and _text.endswith(")"):
        return _get_inc_by_(_text)

    if _text.startswith("$incReset(") and _text.endswith(")"):
        _reset_inc_by_()
        return True

    if _text.startswith("$dec(") and _text.endswith(")"):
        return _get_dec_by_(_text)

    if _text.startswith("$decReset(") and _text.endswith(")"):
        _reset_dec_by_()
        return True

    if _text.startswith("$dateAdd(") and _text.endswith(")"):
        date_add = _text.replace("$dateAdd(", "")
        date_add = date_add[:len(date_add) - 1]
        date_add_parts = _extract_date_add_params_(date_add)

        if len(date_add_parts) == 1:
            date_add_parts.append("{}")

        return _get_date_added_(*date_add_parts)

    if _text.startswith("$guid(") and _text.endswith(")"):
        return _get_guid_(_text)

    return text


if __name__ == '__main__':
    now = datetime.now()
    now_str = now.strftime(ISO8601_DATE_FORMAT_UTC)
    parsed_token = parse_token(f"$now({now_str})")
    print(parsed_token)
