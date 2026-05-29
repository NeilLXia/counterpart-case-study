import pytest
import pandas as pd
from pathlib import Path
from rater_example.rating_tables import RatingTables, _validate_columns

DATA_DIR = Path(__file__).parent.parent / "data" / "default_tables"


@pytest.fixture
def limit_retention_df():
    return pd.DataFrame({
        "limit_retention_amount": [10000, 100000, 500000],
        "limit_retention_factor": [-0.231, 0.350, 0.756],
    })


@pytest.fixture
def industry_factor_df():
    return pd.DataFrame({
        "industry_group": ["Hazard Group 1", "Hazard Group 2"],
        "industry_factor": [1.00, 1.25],
    })


@pytest.fixture
def rating_tables():
    return RatingTables.from_csv_dir(DATA_DIR)


class TestValidateColumns:
    def test_missing_column_raises(self, limit_retention_df, industry_factor_df):
        bad_df = pd.DataFrame({"asset_size": [1000000]})  # missing base_rate
        with pytest.raises(ValueError, match="missing columns"):
            RatingTables(
                base_premiums=bad_df,
                limit_factors=limit_retention_df,
                retention_factors=limit_retention_df,
                industry_factors=industry_factor_df,
            )

    def test_empty_table_raises(self, limit_retention_df, industry_factor_df):
        empty_df = pd.DataFrame({"asset_size": [], "base_rate": []})
        with pytest.raises(ValueError, match="cannot be empty"):
            RatingTables(
                base_premiums=empty_df,
                limit_factors=limit_retention_df,
                retention_factors=limit_retention_df,
                industry_factors=industry_factor_df,
            )

    def test_non_numeric_value_raises(self, limit_retention_df, industry_factor_df):
        bad_df = pd.DataFrame(
            {"asset_size": ["not_a_number"], "base_rate": [1819]})
        with pytest.raises(TypeError, match="must be numeric"):
            RatingTables(
                base_premiums=bad_df,
                limit_factors=limit_retention_df,
                retention_factors=limit_retention_df,
                industry_factors=industry_factor_df,
            )

    def test_numeric_string_in_numeric_column_raises(self, limit_retention_df, industry_factor_df):
        # "1819" is numeric-like but passed as a string — should still be accepted after coercion
        coercible_df = pd.DataFrame(
            {"asset_size": ["1000000"], "base_rate": ["1819"]})
        tables = RatingTables(
            base_premiums=coercible_df,
            limit_factors=limit_retention_df,
            retention_factors=limit_retention_df,
            industry_factors=industry_factor_df,
        )
        assert tables.base_premiums["base_rate"].dtype in [float, int]

    def test_numeric_like_string_column_warns(self, limit_retention_df):
        base_df = pd.DataFrame({"asset_size": [1000000], "base_rate": [1819]})
        numeric_industry_df = pd.DataFrame({
            "industry_group": ["1", "2"],
            "industry_factor": [1.0, 1.25],
        })
        with pytest.warns(UserWarning, match="appears to be numeric"):
            RatingTables(
                base_premiums=base_df,
                limit_factors=limit_retention_df,
                retention_factors=limit_retention_df,
                industry_factors=numeric_industry_df,
            )

    def test_unsupported_column_type_raises(self):
        df = pd.DataFrame({"col": [1, 2]})
        with pytest.raises(ValueError, match="Unsupported type"):
            _validate_columns("test table", df, {"col": "boolean"})

    def test_valid_tables_construct_successfully(self, rating_tables):
        assert rating_tables is not None


class TestGetBasePremium:
    def test_exact_match_lower_bound(self, rating_tables):
        assert rating_tables.get_base_premium(1000000) == 1819

    def test_exact_match_upper_bound(self, rating_tables):
        assert rating_tables.get_base_premium(5000000) == 3619

    def test_interpolates_between_two_rows(self, rating_tables):
        # 3000000 is 20% of the way between 2500000 (3966) and 5000000 (3619) → 3896.6
        result = rating_tables.get_base_premium(3000000)
        assert result == pytest.approx(3896.6)

    def test_below_minimum_raises(self, rating_tables):
        with pytest.raises(ValueError, match="outside the table range"):
            rating_tables.get_base_premium(0)

    def test_above_maximum_raises(self, rating_tables):
        with pytest.raises(ValueError, match="outside the table range"):
            rating_tables.get_base_premium(300000000)


class TestGetLimitFactor:
    def test_exact_match_lower_bound(self, rating_tables):
        assert rating_tables.get_limit_factor(10000) == pytest.approx(-0.231)

    def test_exact_match_upper_bound(self, rating_tables):
        assert rating_tables.get_limit_factor(500000) == pytest.approx(0.756)

    def test_interpolates_between_two_rows(self, rating_tables):
        # 55000 is 20% of the way between 50000 (0.175) and 75000 (0.277) → 0.1954
        result = rating_tables.get_limit_factor(55000)
        assert result == pytest.approx(0.1954)

    def test_below_minimum_raises(self, rating_tables):
        with pytest.raises(ValueError, match="outside the table range"):
            rating_tables.get_limit_factor(-1)

    def test_above_maximum_raises(self, rating_tables):
        with pytest.raises(ValueError, match="outside the table range"):
            rating_tables.get_limit_factor(9999999)


class TestGetRetentionFactor:
    def test_exact_match(self, rating_tables):
        assert rating_tables.get_retention_factor(100000) == pytest.approx(0.350)

    def test_exact_match_lower_bound(self, rating_tables):
        assert rating_tables.get_retention_factor(0) == pytest.approx(-0.760)

    def test_exact_match_upper_bound(self, rating_tables):
        assert rating_tables.get_retention_factor(5000000) == pytest.approx(1.986)

    def test_interpolates_between_two_rows(self, rating_tables):
        # 55000 is 20% of the way between 50000 (0.175) and 75000 (0.277) → 0.1954
        result = rating_tables.get_retention_factor(55000)
        assert result == pytest.approx(0.1954)

    def test_below_minimum_raises(self, rating_tables):
        with pytest.raises(ValueError, match="outside the table range"):
            rating_tables.get_retention_factor(-1)

    def test_above_maximum_raises(self, rating_tables):
        with pytest.raises(ValueError, match="outside the table range"):
            rating_tables.get_retention_factor(9999999)

    def test_uses_retention_factors_table_not_limit_factors(self, industry_factor_df):
        base_df = pd.DataFrame({"asset_size": [1000000], "base_rate": [1819]})
        limit_df = pd.DataFrame({
            "limit_retention_amount": [10000, 100000],
            "limit_retention_factor": [0.0, 1.0],
        })
        retention_df = pd.DataFrame({
            "limit_retention_amount": [10000, 100000],
            "limit_retention_factor": [5.0, 10.0],
        })
        tables = RatingTables(
            base_premiums=base_df,
            limit_factors=limit_df,
            retention_factors=retention_df,
            industry_factors=industry_factor_df,
        )
        assert tables.get_retention_factor(100000) == pytest.approx(10.0)


class TestGetIndustryFactor:
    def test_returns_correct_value(self, rating_tables):
        assert rating_tables.get_industry_factor("Hazard Group 1") == 1.00

    def test_returns_second_group_value(self, rating_tables):
        assert rating_tables.get_industry_factor("Hazard Group 2") == 1.25

    def test_returns_third_group_value(self, rating_tables):
        assert rating_tables.get_industry_factor("Hazard Group 3") == 1.50

    def test_missing_industry_raises(self, rating_tables):
        with pytest.raises(ValueError, match="No industry factor found"):
            rating_tables.get_industry_factor("Unknown Group")
