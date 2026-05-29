"""
The main function allows for the user to run the package directly using a CLI command
run: "pip install -e ." to install and then use the "rate" command in the CLI

Your required input options are: industry, asset-size, limit, retention, and table-dir (expressed as a path from src)
"""

import argparse

from rater_example.rating_engine import Rater, RiskInput
from rater_example.rating_tables import RatingTables


def main() -> None:
    parser = argparse.ArgumentParser(description="Run premium rating")

    parser.add_argument("--industry", required=True)
    parser.add_argument("--asset-size", type=float, required=True)
    parser.add_argument("--limit", type=float, required=True)
    parser.add_argument("--retention", type=float, required=True)
    parser.add_argument("--table-dir", default="data/default_tables")

    args = parser.parse_args()

    tables = RatingTables.from_csv_dir(args.table_dir)

    rater = Rater(tables)

    risk = RiskInput(
        industry=args.industry,
        asset_size=args.asset_size,
        limit=args.limit,
        retention=args.retention,
    )

    result = rater.execute(risk)

    print(f"Industry: {result.industry}")
    print(f"Asset size: {result.asset_size}")
    print(f"Limit: {result.limit}")
    print(f"Retention: {result.retention}")
    print(f"Base premium: {result.base_premium}")
    print(f"Limit factor: {result.limit_factor}")
    print(f"Retention factor: {result.retention_factor}")
    print(f"Industry factor: {result.industry_factor}")
    print(f"Final premium: {result.final_premium}")


if __name__ == "__main__":  # pragma: no cover
    main()
