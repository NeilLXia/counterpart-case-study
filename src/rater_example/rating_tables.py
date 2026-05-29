"""
This module handles the rating tables

It validates rating tables for proper format at construction
and exposes typed lookup methods used by the rating engine.
"""

from dataclasses import dataclass
import warnings

import pandas as pd

# The table lookup columns referenced in the functions below should match the column names in the schemas here
base_premium_schema = {
    "asset_size": "numeric",
    "base_rate": "numeric"
}

limit_retention_factor_schema = {
    "limit_retention_amount": "numeric",
    "limit_retention_factor": "numeric"
}

industry_factor_schema = {
    "industry_group": "string",
    "industry_factor": "numeric"
}


@dataclass
class RatingTables:
    base_premium_table: pd.DataFrame
    limit_factor_table: pd.DataFrame
    retention_factor_table: pd.DataFrame
    industry_factor_table: pd.DataFrame

    def __post_init__(self) -> None:
        self.base_premium_table = self._validate_columns(
            "Base Premium Table", self.base_premium_table, base_premium_schema)
        self.limit_factor_table = self._validate_columns(
            "Limit Factor Table", self.limit_factor_table, limit_retention_factor_schema)
        self.retention_factor_table = self._validate_columns(
            "Retention Factor Table", self.retention_factor_table, limit_retention_factor_schema)
        self.industry_factor_table = self._validate_columns(
            "Industry Factor Table", self.industry_factor_table, industry_factor_schema)

    def _validate_columns(self, table_name: str, df: pd.DataFrame, schema: dict[str, str]) -> pd.DataFrame:
        df = df.copy()

        # Validate table to contain specified columns
        missing = set(schema) - set(df.columns)
        if missing:
            raise ValueError(f"{table_name} is missing columns: {missing}")

        if df.empty:
            raise ValueError(f"{table_name} cannot be empty")

        for col, col_type in schema.items():
            if col_type == "numeric":
                bad_rows = df[pd.to_numeric(df[col], errors="coerce").isna()]

                if not bad_rows.empty:
                    raise TypeError(
                        f"Column '{col}' must be numeric. Bad rows: {bad_rows.index.tolist()}"
                    )

                # Convert any number-like values to numbers
                df[col] = pd.to_numeric(df[col], errors="coerce")

            elif col_type == "string":
                numeric_like = pd.to_numeric(df[col], errors="coerce").notna()

                if numeric_like.all():
                    warnings.warn(
                        f"Column '{col}' appears to be numeric, please confirm schema",
                        UserWarning
                    )

                # All values can be converted to a string-like value
                df[col] = df[col].astype("string")

            elif col_type == "date":
                bad_rows = df[pd.to_datetime(df[col], errors="coerce").isna()]

                if not bad_rows.empty:
                    raise TypeError(
                        f"Column '{col}' must be date-like. Bad rows: {bad_rows.index.tolist()}"
                    )

                # Convert any date-like values to numbers
                df[col] = pd.to_datetime(df[col], errors="coerce")

            else:
                raise ValueError(f"Unsupported type: {col_type}")

        return df

    def get_base_premium(self, asset_size: float) -> float:
        df = self.base_premium_table
        match = df.loc[df["asset_size"] == asset_size]

        if match.empty:
            raise ValueError(
                f"No base premium found for asset size: {asset_size}")

        return match.iloc[0]["base_rate"]

    def get_limit_factor(self, limit: float) -> float:
        df = self.limit_factor_table
        match = df.loc[df["limit_retention_amount"] == limit]

        if match.empty:
            raise ValueError(
                f"No limit factor found for limit={limit}"
            )

        return match.iloc[0]["limit_retention_factor"]

    def get_retention_factor(self, retention: float) -> float:
        df = self.limit_factor_table
        match = df.loc[df["limit_retention_amount"] == retention]

        if match.empty:
            raise ValueError(
                f"No lretention factor found for retention={retention}"
            )

        return match.iloc[0]["limit_retention_factor"]

    def get_industry_factor(self, industry: str) -> float:
        df = self.industry_factor_table
        match = df.loc[df["industry_group"] == industry]

        if match.empty:
            raise ValueError(
                f"No industry factor found for industry: {industry}")

        return match.iloc[0]["industry_factor"]
