from rater_example.rating_engine import Rater, RiskInput, PremiumResult
from rater_example.rating_tables import RatingTables

tables = RatingTables.from_csv_dir("data/updated_tables")
rater = Rater(tables)

result = rater.execute(RiskInput(
    industry="Hazard Group 2",
    asset_size=10_000_000,
    limit=500_000,
    retention=25_000,
))

print(result.final_premium)
