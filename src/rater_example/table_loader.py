'''
This is a general helper function that reads in a specified list of files to import from a given path.
'''

from pathlib import Path
from typing import Union

import pandas as pd

TABLE_FILES = {
    "base_premiums": "base_premium.csv",
    "limit_factors": "limit_retention_factor.csv",
    "retention_factors": "limit_retention_factor.csv",
    "industry_factors": "industry_factor.csv",
}


def _read_csv_table(path: Path, table_name: str) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"{table_name} file not found: {path}")
    except pd.errors.EmptyDataError:
        raise ValueError(f"{table_name} file is empty: {path}")
    except pd.errors.ParserError as e:
        raise ValueError(f"{table_name} file could not be parsed: {path}. {e}")


def load_tables_from_csv(table_dir: Union[str, Path]) -> dict[str, pd.DataFrame]:
    return {
        table_name: _read_csv_table(Path(table_dir) / file_name, table_name)
        for table_name, file_name in TABLE_FILES.items()
    }
