"""Small, pure validation check functions."""

import pandas as pd


def _is_blank(value: object) -> bool:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return True
    return str(value).strip() == ""


def _append_reason(existing: str, new_reason: str) -> str:
    if not new_reason:
        return existing
    if not existing:
        return new_reason
    return f"{existing}; {new_reason}"


def check_missing_values(df: pd.DataFrame, required_columns: list[str]) -> pd.Series:
    """Return per-row rejection reasons for blank required fields."""
    reasons = pd.Series("", index=df.index, dtype=str)
    for col in required_columns:
        if col not in df.columns:
            reasons = reasons.apply(lambda r: _append_reason(r, f"missing_column:{col}"))
            continue
        blank_mask = df[col].apply(_is_blank)
        reasons.loc[blank_mask] = reasons.loc[blank_mask].apply(
            lambda r: _append_reason(r, f"missing_value:{col}")
        )
    return reasons


def check_duplicate_ids(df: pd.DataFrame, id_column: str) -> pd.Series:
    """Keep the first row per ID; mark subsequent duplicates for rejection."""
    reasons = pd.Series("", index=df.index, dtype=str)
    if id_column not in df.columns:
        return reasons.apply(lambda _: f"missing_column:{id_column}")

    duplicated = df.duplicated(subset=[id_column], keep="first")
    reasons.loc[duplicated] = reasons.loc[duplicated].apply(
        lambda r: _append_reason(r, f"duplicate_{id_column}")
    )
    return reasons


def check_integer_column(df: pd.DataFrame, column: str) -> pd.Series:
    """Return reasons for values that are not valid integers."""
    reasons = pd.Series("", index=df.index, dtype=str)
    if column not in df.columns:
        return reasons

    for idx, value in df[column].items():
        if _is_blank(value):
            continue
        try:
            int(str(value).strip())
        except ValueError:
            reasons.at[idx] = _append_reason(reasons.at[idx], f"invalid_integer:{column}")
    return reasons


def check_positive_integer_column(df: pd.DataFrame, column: str) -> pd.Series:
    """Return reasons for values that are not positive integers."""
    reasons = pd.Series("", index=df.index, dtype=str)
    if column not in df.columns:
        return reasons

    for idx, value in df[column].items():
        if _is_blank(value):
            continue
        try:
            parsed = int(str(value).strip())
            if parsed <= 0:
                reasons.at[idx] = _append_reason(
                    reasons.at[idx], f"non_positive_integer:{column}"
                )
        except ValueError:
            reasons.at[idx] = _append_reason(reasons.at[idx], f"invalid_integer:{column}")
    return reasons


def check_positive_float_column(df: pd.DataFrame, column: str) -> pd.Series:
    """Return reasons for values that are not valid positive numbers."""
    reasons = pd.Series("", index=df.index, dtype=str)
    if column not in df.columns:
        return reasons

    for idx, value in df[column].items():
        if _is_blank(value):
            continue
        try:
            parsed = float(str(value).strip())
            if parsed <= 0:
                reasons.at[idx] = _append_reason(
                    reasons.at[idx], f"non_positive_number:{column}"
                )
        except ValueError:
            reasons.at[idx] = _append_reason(reasons.at[idx], f"invalid_number:{column}")
    return reasons


def check_email_format(df: pd.DataFrame, column: str = "email") -> pd.Series:
    """Return reasons for email values missing an @ symbol."""
    reasons = pd.Series("", index=df.index, dtype=str)
    if column not in df.columns:
        return reasons

    for idx, value in df[column].items():
        if _is_blank(value):
            continue
        if "@" not in str(value):
            reasons.at[idx] = _append_reason(reasons.at[idx], "invalid_email_format")
    return reasons


def check_date_format(df: pd.DataFrame, column: str) -> pd.Series:
    """Return reasons for values that cannot be parsed as YYYY-MM-DD dates."""
    reasons = pd.Series("", index=df.index, dtype=str)
    if column not in df.columns:
        return reasons

    for idx, value in df[column].items():
        if _is_blank(value):
            continue
        parsed = pd.to_datetime(str(value).strip(), format="%Y-%m-%d", errors="coerce")
        if pd.isna(parsed):
            reasons.at[idx] = _append_reason(reasons.at[idx], f"invalid_date:{column}")
    return reasons


def check_foreign_key(
    df: pd.DataFrame,
    fk_column: str,
    valid_ids: set[str],
) -> pd.Series:
    """Return reasons for FK values not present in the valid parent ID set."""
    reasons = pd.Series("", index=df.index, dtype=str)
    if fk_column not in df.columns:
        return reasons

    for idx, value in df[fk_column].items():
        if _is_blank(value):
            continue
        normalized = str(value).strip()
        if normalized not in valid_ids:
            reasons.at[idx] = _append_reason(
                reasons.at[idx], f"invalid_foreign_key:{fk_column}"
            )
    return reasons


def combine_reasons(*reason_series: pd.Series) -> pd.Series:
    """Merge multiple per-row reason Series into one."""
    combined = pd.Series("", index=reason_series[0].index, dtype=str)
    for series in reason_series:
        for idx, reason in series.items():
            if reason:
                combined.at[idx] = _append_reason(combined.at[idx], reason)
    return combined


def split_by_reasons(
    df: pd.DataFrame, reasons: pd.Series, reason_column: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a DataFrame into valid and rejected sets based on rejection reasons."""
    working = df.copy()
    working[reason_column] = reasons
    rejected_mask = working[reason_column].str.strip().astype(bool)
    valid = working.loc[~rejected_mask].drop(columns=[reason_column]).reset_index(drop=True)
    rejected = working.loc[rejected_mask].reset_index(drop=True)
    return valid, rejected
