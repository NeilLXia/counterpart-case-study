from rater_example import Rater, RatingTables

tables = RatingTables.from_default_tables()
tables_updated = RatingTables.from_csv_dir("data/updated_tables")
rater = Rater(tables)
rater_updated = Rater(tables_updated)

result = rater.execute(
    industry="Hazard Group 2",
    asset_size=10_000_000,
    limit=500_000,
    retention=25_000,
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
print("\n")

result = rater_updated.execute(
    industry="Hazard Group 2",
    asset_size=10_000_000,
    limit=500_000,
    retention=25_000,
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
print("\n")
