import pytest
from pathlib import Path
from rater_example.table_loader import load_tables_from_csv


DATA_DIR = Path(__file__).parent.parent / "data" / "default_tables"

# Minimal valid CSVs for building partial directories in tmp_path tests
BASE_PREMIUM_CSV = "asset_size,base_rate\n1000000,1819\n"
LIMIT_RETENTION_CSV = "limit_retention_amount,limit_retention_factor\n100000,0.350\n"
INDUSTRY_FACTOR_CSV = "industry_group,industry_factor\nHazard Group 1,1.00\n"


class TestLoadRatingTablesFromCsv:
    def test_returns_dict(self):
        tables = load_tables_from_csv(DATA_DIR)
        assert isinstance(tables, dict)

    def test_base_premiums_has_expected_columns(self):
        tables = load_tables_from_csv(DATA_DIR)
        assert "asset_size" in tables["base_premiums"].columns
        assert "base_rate" in tables["base_premiums"].columns

    def test_limit_factors_has_expected_columns(self):
        tables = load_tables_from_csv(DATA_DIR)
        assert "limit_retention_amount" in tables["limit_factors"].columns
        assert "limit_retention_factor" in tables["limit_factors"].columns

    def test_retention_factors_has_expected_columns(self):
        tables = load_tables_from_csv(DATA_DIR)
        assert "limit_retention_amount" in tables["retention_factors"].columns
        assert "limit_retention_factor" in tables["retention_factors"].columns

    def test_industry_factors_has_expected_columns(self):
        tables = load_tables_from_csv(DATA_DIR)
        assert "industry_group" in tables["industry_factors"].columns
        assert "industry_factor" in tables["industry_factors"].columns

    def test_tables_are_not_empty(self):
        tables = load_tables_from_csv(DATA_DIR)
        assert not tables["base_premiums"].empty
        assert not tables["limit_factors"].empty
        assert not tables["retention_factors"].empty
        assert not tables["industry_factors"].empty

    def test_lookups_work_after_load(self):
        tables = load_tables_from_csv(DATA_DIR)
        bp = tables["base_premiums"]
        assert bp[bp["asset_size"] == 1000000]["base_rate"].iloc[0] == 1819
        ind = tables["industry_factors"]
        assert ind[ind["industry_group"] ==
                   "Hazard Group 1"]["industry_factor"].iloc[0] == 1.00


class TestMissingTableFiles:
    def test_nonexistent_directory_raises(self):
        with pytest.raises(FileNotFoundError):
            load_tables_from_csv("/nonexistent/path/to/tables")

    def test_missing_base_premium_csv_raises(self, tmp_path):
        (tmp_path / "limit_retention_factor.csv").write_text(LIMIT_RETENTION_CSV)
        (tmp_path / "industry_factor.csv").write_text(INDUSTRY_FACTOR_CSV)
        with pytest.raises(FileNotFoundError, match="base_premiums"):
            load_tables_from_csv(tmp_path)

    def test_missing_limit_retention_csv_raises(self, tmp_path):
        (tmp_path / "base_premium.csv").write_text(BASE_PREMIUM_CSV)
        (tmp_path / "industry_factor.csv").write_text(INDUSTRY_FACTOR_CSV)
        with pytest.raises(FileNotFoundError, match="limit_factors"):
            load_tables_from_csv(tmp_path)

    def test_missing_industry_factor_csv_raises(self, tmp_path):
        (tmp_path / "base_premium.csv").write_text(BASE_PREMIUM_CSV)
        (tmp_path / "limit_retention_factor.csv").write_text(LIMIT_RETENTION_CSV)
        with pytest.raises(FileNotFoundError, match="industry_factors"):
            load_tables_from_csv(tmp_path)


class TestMalformedTableFiles:
    def test_empty_base_premium_csv_raises(self, tmp_path):
        (tmp_path / "base_premium.csv").write_text("")
        (tmp_path / "limit_retention_factor.csv").write_text(LIMIT_RETENTION_CSV)
        (tmp_path / "industry_factor.csv").write_text(INDUSTRY_FACTOR_CSV)
        with pytest.raises(ValueError, match="base_premiums.*empty"):
            load_tables_from_csv(tmp_path)

    def test_empty_limit_retention_csv_raises(self, tmp_path):
        (tmp_path / "base_premium.csv").write_text(BASE_PREMIUM_CSV)
        (tmp_path / "limit_retention_factor.csv").write_text("")
        (tmp_path / "industry_factor.csv").write_text(INDUSTRY_FACTOR_CSV)
        with pytest.raises(ValueError, match="limit_factors.*empty"):
            load_tables_from_csv(tmp_path)

    def test_empty_industry_factor_csv_raises(self, tmp_path):
        (tmp_path / "base_premium.csv").write_text(BASE_PREMIUM_CSV)
        (tmp_path / "limit_retention_factor.csv").write_text(LIMIT_RETENTION_CSV)
        (tmp_path / "industry_factor.csv").write_text("")
        with pytest.raises(ValueError, match="industry_factors.*empty"):
            load_tables_from_csv(tmp_path)

    def test_malformed_base_premium_csv_raises(self, tmp_path):
        # Unclosed quote causes a genuine pd.errors.ParserError
        (tmp_path / "base_premium.csv").write_text('asset_size,base_rate\n"unclosed,1819\n')
        (tmp_path / "limit_retention_factor.csv").write_text(LIMIT_RETENTION_CSV)
        (tmp_path / "industry_factor.csv").write_text(INDUSTRY_FACTOR_CSV)
        with pytest.raises(ValueError, match="base_premiums.*could not be parsed"):
            load_tables_from_csv(tmp_path)
