from dataclasses import dataclass
from typing import Any

import pandas as pd
from rater_example.rating_tables import RatingTables


@dataclass
class RiskInput:
    industry: str
    asset_size: float
    limit: float
    retention: float


@dataclass
class PremiumResult:
    industry: str
    asset_size: float
    limit: float
    retention: float
    base_premium: float
    limit_factor: float
    retention_factor: float
    industry_factor: float
    final_premium: float


class Rater:
    def __init__(
        self,
        tables: RatingTables
    ) -> None:
        self.tables = tables

    def execute(self, risk_inputs: RiskInput) -> PremiumResult:
        base_premium = self.tables.get_base_premium(risk_inputs.asset_size)
        limit_factor = self.tables.get_limit_factor(
            risk_inputs.limit
        )
        retention_factor = self.tables.get_retention_factor(
            risk_inputs.retention
        )
        industry_factor = self.tables.get_industry_factor(
            risk_inputs.industry)

        final_premium = round(base_premium *
                              (limit_factor - retention_factor) * industry_factor * 1.7, 2)

        return PremiumResult(
            industry=risk_inputs.industry,
            asset_size=risk_inputs.asset_size,
            limit=risk_inputs.limit,
            retention=risk_inputs.retention,
            base_premium=base_premium,
            limit_factor=limit_factor,
            retention_factor=retention_factor,
            industry_factor=industry_factor,
            final_premium=final_premium,
        )
