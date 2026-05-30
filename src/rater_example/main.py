"""
The main function allows for the user to run the package directly using a CLI command
run: "pip install -e ." to install and then use the "rate" command in the CLI

Your required input options are: industry, asset-size, limit, and retention.
Use table-dir to override the packaged default rating tables.
"""

import argparse

from rater_example.rating_engine import Rater
from rater_example.rating_tables import RatingTables


def main() -> None:
    parser = argparse.ArgumentParser(description="Run premium rating")

    parser.add_argument("--industry", required=True)
    parser.add_argument("--asset-size", type=float, required=True)
    parser.add_argument("--limit", type=float, required=True)
    parser.add_argument("--retention", type=float, required=True)
    parser.add_argument("--table-dir")

    args = parser.parse_args()

    if args.table_dir:
        tables = RatingTables.from_csv_dir(args.table_dir)
    else:
        tables = RatingTables.from_default_tables()

    rater = Rater(tables)

    result = rater.execute(
        industry=args.industry,
        asset_size=args.asset_size,
        limit=args.limit,
        retention=args.retention,
    )

    print(f"Industry: {result.industry}")
    print(f"Asset size: ${result.asset_size:,.0f}")
    print(f"Limit: ${result.limit:,.0f}")
    print(f"Retention: ${result.retention:,.0f}")
    print(f"Base premium: ${result.base_premium:,.0f}")
    print(f"Limit factor: {result.limit_factor:,.3f}")
    print(f"Retention factor: {result.retention_factor:,.3f}")
    print(f"Industry factor: {result.industry_factor:,.3f}")
    print(f"Final premium: ${result.final_premium:,.2f}")


if __name__ == "__main__":  # pragma: no cover
    main()
