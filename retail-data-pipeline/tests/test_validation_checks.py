import pandas as pd

from src.validation.checks import (
    check_duplicate_ids,
    check_email_format,
    check_foreign_key,
    check_missing_values,
    combine_reasons,
    split_by_reasons,
)


def test_check_missing_values_flags_blank_fields() -> None:
    df = pd.DataFrame([{"customer_id": "1", "name": "", "email": "a@b.com", "city": "Delhi"}])
    reasons = check_missing_values(df, ["customer_id", "name", "email", "city"])

    assert reasons.iloc[0] == "missing_value:name"


def test_check_duplicate_ids_keeps_first_occurrence() -> None:
    df = pd.DataFrame([{"customer_id": "1"}, {"customer_id": "1"}, {"customer_id": "2"}])
    reasons = check_duplicate_ids(df, "customer_id")

    assert reasons.iloc[0] == ""
    assert reasons.iloc[1] == "duplicate_customer_id"
    assert reasons.iloc[2] == ""


def test_check_email_format() -> None:
    df = pd.DataFrame([{"email": "valid@test.com"}, {"email": "invalid"}])
    reasons = check_email_format(df)

    assert reasons.iloc[0] == ""
    assert reasons.iloc[1] == "invalid_email_format"


def test_check_foreign_key() -> None:
    df = pd.DataFrame([{"customer_id": "1"}, {"customer_id": "99"}])
    reasons = check_foreign_key(df, "customer_id", {"1", "2"})

    assert reasons.iloc[0] == ""
    assert reasons.iloc[1] == "invalid_foreign_key:customer_id"


def test_combine_reasons_merges_multiple_issues() -> None:
    first = pd.Series(["", "missing_value:name"])
    second = pd.Series(["duplicate_customer_id", ""])
    combined = combine_reasons(first, second)

    assert combined.iloc[0] == "duplicate_customer_id"
    assert combined.iloc[1] == "missing_value:name"


def test_split_by_reasons() -> None:
    df = pd.DataFrame([{"customer_id": "1"}, {"customer_id": "2"}])
    reasons = pd.Series(["", "duplicate_customer_id"])
    valid, rejected = split_by_reasons(df, reasons, "rejection_reason")

    assert len(valid) == 1
    assert len(rejected) == 1
    assert rejected.iloc[0]["rejection_reason"] == "duplicate_customer_id"
