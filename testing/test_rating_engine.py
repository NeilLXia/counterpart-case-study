import dataclasses
import pytest
from unittest.mock import MagicMock
from rater_example.rating_engine import Rater, RiskInput, PremiumResult


@pytest.fixture
def mock_tables():
    tables = MagicMock()
    tables.get_base_premium.return_value = 1819.0
    tables.get_limit_factor.return_value = 0.350
    tables.get_retention_factor.return_value = -0.231
    tables.get_industry_factor.return_value = 1.25
    return tables


@pytest.fixture
def risk_input():
    return RiskInput(
        industry="Hazard Group 2",
        asset_size=1_000_000,
        limit=100_000,
        retention=10_000,
    )


class TestRater:
    def test_execute_returns_premium_result(self, mock_tables, risk_input):
        result = Rater(mock_tables).execute(**dataclasses.asdict(risk_input))
        assert isinstance(result, PremiumResult)

    def test_execute_passes_correct_args_to_tables(self, mock_tables, risk_input):
        Rater(mock_tables).execute(**dataclasses.asdict(risk_input))
        mock_tables.get_base_premium.assert_called_once_with(
            risk_input.asset_size)
        mock_tables.get_limit_factor.assert_called_once_with(risk_input.limit)
        mock_tables.get_retention_factor.assert_called_once_with(
            risk_input.retention)
        mock_tables.get_industry_factor.assert_called_once_with(
            risk_input.industry)

    def test_execute_propagates_input_fields(self, mock_tables, risk_input):
        result = Rater(mock_tables).execute(**dataclasses.asdict(risk_input))
        assert result.industry == risk_input.industry
        assert result.asset_size == risk_input.asset_size
        assert result.limit == risk_input.limit
        assert result.retention == risk_input.retention

    def test_execute_stores_intermediate_factors(self, mock_tables, risk_input):
        result = Rater(mock_tables).execute(**dataclasses.asdict(risk_input))
        assert result.base_premium == 1819.0
        assert result.limit_factor == 0.350
        assert result.retention_factor == -0.231
        assert result.industry_factor == 1.25

    def test_execute_calculates_final_premium(self, mock_tables, risk_input):
        result = Rater(mock_tables).execute(**dataclasses.asdict(risk_input))
        expected = round(1819.0 * (0.350 - (-0.231)) * 1.25 * 1.7, 2)
        assert result.final_premium == expected

    def test_execute_propagates_table_error(self, mock_tables, risk_input):
        mock_tables.get_base_premium.side_effect = ValueError(
            "outside the table range [1, 250000000]")
        with pytest.raises(ValueError, match="outside the table range"):
            Rater(mock_tables).execute(**dataclasses.asdict(risk_input))
