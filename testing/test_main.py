import pytest
from pathlib import Path
from unittest.mock import patch
from rater_example.main import main


UPDATED_DATA_DIR = str(Path(__file__).parent.parent / "data" / "updated_tables")

BASE_ARGV = [
    "rate",
    "--industry", "Hazard Group 1",
    "--asset-size", "1000000",
    "--limit", "100000",
    "--retention", "10000",
]


class TestMain:
    def test_output_contains_all_fields(self, capsys):
        with patch("sys.argv", BASE_ARGV):
            main()
        out = capsys.readouterr().out
        for field in ["Industry", "Asset size", "Limit", "Retention",
                      "Base premium", "Limit factor", "Retention factor",
                      "Industry factor", "Final premium"]:
            assert field in out

    def test_output_echoes_industry(self, capsys):
        with patch("sys.argv", BASE_ARGV):
            main()
        assert "Hazard Group 1" in capsys.readouterr().out

    def test_output_echoes_asset_size(self, capsys):
        with patch("sys.argv", BASE_ARGV):
            main()
        assert "$1,000,000" in capsys.readouterr().out

    def test_output_echoes_limit(self, capsys):
        with patch("sys.argv", BASE_ARGV):
            main()
        assert "$100,000" in capsys.readouterr().out

    def test_output_echoes_retention(self, capsys):
        with patch("sys.argv", BASE_ARGV):
            main()
        assert "$10,000" in capsys.readouterr().out

    def test_final_premium_is_numeric(self, capsys):
        with patch("sys.argv", BASE_ARGV):
            main()
        out = capsys.readouterr().out
        for line in out.splitlines():
            if line.startswith("Final premium:"):
                float(line.split(":", 1)[1].strip().lstrip("$").replace(",", ""))
                break
        else:
            pytest.fail("Final premium line not found in output")

    def test_default_table_dir_works_outside_repo_root(self, capsys, monkeypatch, tmp_path):
        argv = [
            "rate",
            "--industry", "Hazard Group 1",
            "--asset-size", "1000000",
            "--limit", "100000",
            "--retention", "10000",
        ]
        monkeypatch.chdir(tmp_path)
        with patch("sys.argv", argv):
            main()
        assert "Final premium:" in capsys.readouterr().out

    def test_missing_required_arg_exits(self):
        # --asset-size is omitted
        with patch("sys.argv", ["rate", "--industry", "Hazard Group 1",
                                "--limit", "100000", "--retention", "10000"]):
            with pytest.raises(SystemExit):
                main()

    def test_missing_limit_arg_exits(self):
        with patch("sys.argv", ["rate", "--industry", "Hazard Group 1",
                                "--asset-size", "1000000", "--retention", "10000"]):
            with pytest.raises(SystemExit):
                main()

    def test_missing_retention_arg_exits(self):
        with patch("sys.argv", ["rate", "--industry", "Hazard Group 1",
                                "--asset-size", "1000000", "--limit", "100000"]):
            with pytest.raises(SystemExit):
                main()

    def test_invalid_industry_raises(self):
        with patch("sys.argv", [
            "rate",
            "--industry", "Not A Real Group",
            "--asset-size", "1000000",
            "--limit", "100000",
            "--retention", "10000",
        ]):
            with pytest.raises(ValueError, match="No industry factor found"):
                main()

    def test_invalid_asset_size_raises(self):
        # 999999999 exceeds the table maximum of 250000000
        with patch("sys.argv", [
            "rate",
            "--industry", "Hazard Group 1",
            "--asset-size", "999999999",
            "--limit", "100000",
            "--retention", "10000",
        ]):
            with pytest.raises(ValueError, match="outside the table range"):
                main()

    def test_invalid_limit_raises(self):
        # 9999999 exceeds the limit table maximum of 5000000
        with patch("sys.argv", [
            "rate",
            "--industry", "Hazard Group 1",
            "--asset-size", "1000000",
            "--limit", "9999999",
            "--retention", "10000",
        ]):
            with pytest.raises(ValueError, match="outside the table range"):
                main()

    def test_invalid_retention_raises(self):
        # -1 is below the retention table minimum of 0
        with patch("sys.argv", [
            "rate",
            "--industry", "Hazard Group 1",
            "--asset-size", "1000000",
            "--limit", "100000",
            "--retention", "-1",
        ]):
            with pytest.raises(ValueError, match="outside the table range"):
                main()

    def test_negative_asset_size_raises(self):
        # -1000000 is below the asset size table minimum of 1
        with patch("sys.argv", [
            "rate",
            "--industry", "Hazard Group 1",
            "--asset-size", "-1000000",
            "--limit", "100000",
            "--retention", "10000",
        ]):
            with pytest.raises(ValueError, match="outside the table range"):
                main()

    def test_custom_table_dir_still_loads(self, capsys):
        with patch("sys.argv", BASE_ARGV + ["--table-dir", UPDATED_DATA_DIR]):
            main()
        assert "Industry factor: 0.935" in capsys.readouterr().out
