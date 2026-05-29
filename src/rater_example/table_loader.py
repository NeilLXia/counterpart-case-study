from pathlib import Path

import pandas as pd

from rater_example.rating_tables import RatingTables


def load_rating_tables_from_csv(table_dir: str) -> RatingTables:
    table_dir = Path(table_dir)

    base_premium_table = pd.read_csv(table_dir / "base_premium.csv")
    limit_factor_table = pd.read_csv(table_dir / "limit_retention_factor.csv")
    retention_factor_table = pd.read_csv(
        table_dir / "limit_retention_factor.csv")
    industry_factor_table = pd.read_csv(table_dir / "industry_factor.csv")

    return RatingTables(
        base_premium_table=base_premium_table,
        limit_factor_table=limit_factor_table,
        retention_factor_table=retention_factor_table,
        industry_factor_table=industry_factor_table,
    )
