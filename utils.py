import pandas as pd

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts column names to a consistent format:
    - strips spaces
    - lowercase
    - spaces -> underscores
    """
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def ensure_numeric(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Converts a column to numeric safely.
    If conversion fails, bad values become NaN (then you can handle NaN if needed).
    """
    df = df.copy()
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def ensure_datetime(df: pd.DataFrame, col: str, dayfirst: bool = True) -> pd.DataFrame:
    """
    Converts a column to datetime safely.
    Invalid dates become NaT.
    """
    df = df.copy()
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], dayfirst=dayfirst, errors="coerce")
    return df


def detect_dataset_type(df: pd.DataFrame) -> str:
    """
    Detect dataset type based on required columns (after standardization).
    Returns: 'sales', 'churn', or 'unknown'
    """
    cols = set(df.columns)
    if {"order_date", "sales"}.issubset(cols):
        return "sales"
    if {"churn"}.issubset(cols):
        return "churn"
    return "unknown"
