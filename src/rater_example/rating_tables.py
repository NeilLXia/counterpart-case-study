"""
This module handles the rating tables

It validates rating tables for proper format at construction
and exposes typed lookup methods used by the rating engine.

Currently, values are coerced to numeric when specified as such so "10" will be interpreted as 10. This is a design choice to allow for more flexibility in the input tables, however can expose the module to more input risk.
"""

from dataclasses import dataclass
from importlib import resources
import warnings
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from rater_example.table_loader import load_tables_from_csv

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

# Validates the presence and format of data columns and values


def _validate_columns(table_name: str, df: pd.DataFrame, schema: dict[str, str]) -> pd.DataFrame:
    df = df.copy()

    missing = set(schema) - set(df.columns)
    if missing:
        raise ValueError(f"{table_name} is missing columns: {missing}")

    if df.empty:
        raise ValueError(f"{table_name} cannot be empty")

    for col, col_type in schema.items():

        # NUMERIC: Ensure values are numeric or can be coerced to numeric
        if col_type == "numeric":
            bad_rows = df[pd.to_numeric(df[col], errors="coerce").isna()]

            if not bad_rows.empty:
                raise TypeError(
                    f"Column '{col}' must be numeric. Bad rows: {bad_rows.index.tolist()}"
                )

            df[col] = pd.to_numeric(df[col], errors="coerce")

        # CHARACTERS: All values can be coerced to strings, so it simply checks if the definition could've been numeric
        elif col_type == "string":
            numeric_like = pd.to_numeric(df[col], errors="coerce").notna()

            if numeric_like.all():
                warnings.warn(
                    f"Column '{col}' appears to be numeric, please confirm schema",
                    UserWarning
                )

            df[col] = df[col].astype("string")

        else:
            raise ValueError(f"Unsupported type: {col_type}")

    return df


def _validate_unique_key(table_name: str, df: pd.DataFrame, key_column: str) -> None:
    duplicated = df.loc[df[key_column].duplicated(), key_column].tolist()
    if duplicated:
        raise ValueError(
            f"{table_name} contains duplicate values in '{key_column}': {duplicated}"
        )


@dataclass
class RatingTables:
    base_premiums: pd.DataFrame
    limit_factors: pd.DataFrame
    retention_factors: pd.DataFrame
    industry_factors: pd.DataFrame

    # Class method to instantiate a RatingTables object
    @classmethod
    def from_csv_dir(cls, table_dir: Union[str, Path]) -> "RatingTables":
        tables = load_tables_from_csv(table_dir)
        return cls(
            base_premiums=tables["base_premiums"],
            limit_factors=tables["limit_factors"],
            retention_factors=tables["retention_factors"],
            industry_factors=tables["industry_factors"],
        )

    @classmethod
    def from_default_tables(cls) -> "RatingTables":
        table_dir = resources.files("rater_example") / "default_tables"
        with resources.as_file(table_dir) as path:
            return cls.from_csv_dir(path)

    def __post_init__(self) -> None:
        self.base_premiums = _validate_columns(
            "Base Premium Table", self.base_premiums, base_premium_schema)
        self.limit_factors = _validate_columns(
            "Limit Factor Table", self.limit_factors, limit_retention_factor_schema)
        self.retention_factors = _validate_columns(
            "Retention Factor Table", self.retention_factors, limit_retention_factor_schema)
        self.industry_factors = _validate_columns(
            "Industry Factor Table", self.industry_factors, industry_factor_schema)

        _validate_unique_key("Base Premium Table",
                             self.base_premiums, "asset_size")
        _validate_unique_key(
            "Limit Factor Table", self.limit_factors, "limit_retention_amount")
        _validate_unique_key(
            "Retention Factor Table", self.retention_factors, "limit_retention_amount")
        _validate_unique_key(
            "Industry Factor Table", self.industry_factors, "industry_group")

    def get_base_premium(self, asset_size: float) -> float:
        df = self.base_premiums.sort_values("asset_size")
        amounts = df["asset_size"].to_numpy()
        factors = df["base_rate"].to_numpy()

        if asset_size < amounts[0] or asset_size > amounts[-1]:
            raise ValueError(
                f"Asset size {asset_size} is outside the table range [{amounts[0]}, {amounts[-1]}]"
            )

        return float(np.interp(asset_size, amounts, factors))

    def get_limit_factor(self, limit: float) -> float:
        df = self.limit_factors.sort_values("limit_retention_amount")
        amounts = df["limit_retention_amount"].to_numpy()
        factors = df["limit_retention_factor"].to_numpy()

        if limit < amounts[0] or limit > amounts[-1]:
            raise ValueError(
                f"Limit {limit} is outside the table range [{amounts[0]}, {amounts[-1]}]"
            )

        return float(np.interp(limit, amounts, factors))

    def get_retention_factor(self, retention: float) -> float:
        df = self.retention_factors.sort_values("limit_retention_amount")
        amounts = df["limit_retention_amount"].to_numpy()
        factors = df["limit_retention_factor"].to_numpy()

        if retention < amounts[0] or retention > amounts[-1]:
            raise ValueError(
                f"Retention {retention} is outside the table range [{amounts[0]}, {amounts[-1]}]"
            )

        return float(np.interp(retention, amounts, factors))

    def get_industry_factor(self, industry: str) -> float:
        df = self.industry_factors
        match = df.loc[df["industry_group"] == industry]

        if match.empty:
            raise ValueError(
                f"No industry factor found for industry: {industry}")

        return match.iloc[0]["industry_factor"]
