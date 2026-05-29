import argparse

from rater_example.rating_engine import Rater, RiskInput
from rater_example.rating_tables import RatingTables
from rater_example.table_loader import load_rating_tables_from_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Run premium rating")

    parser.add_argument("--industry", required=True)
    parser.add_argument("--asset-size", type=float, required=True)
    parser.add_argument("--limit", type=float, required=True)
    parser.add_argument("--retention", type=float, required=True)
    parser.add_argument("--table-dir", default="data/default_tables")

    args = parser.parse_args()

    tables = load_rating_tables_from_csv(args.table_dir)

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


if __name__ == "__main__":
    main()
