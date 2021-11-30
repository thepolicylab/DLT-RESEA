"""Sets of functions exclusively for reading and validating Fixed Width Files from DLT"""
from datetime import date
from pathlib import Path
from typing import List, Optional

import pandas as pd

from .config import get_global_config
from .types import DatetimeType, FilenameType


def _read_weekly_data(
    layout: pd.DataFrame,
    weekly_filepath: FilenameType = None,
) -> pd.DataFrame:
    # Verify that the weekly filepath actually exists
    assert Path(weekly_filepath).exists()
    # Ensure that the column names of layout is correct
    layout.columns = [
        "index",
        "type",
        "beg_pos",
        "end_pos",
        "decimal",
        "field_name",
        "byte_size",
        "description",
    ]

    # Read weekly
    data = pd.read_fwf(weekly_filepath, header=None, widths=list(layout.byte_size))
    data.columns = [col.strip() for col in layout.field_name]
    return data


def get_weekly_raw_data_dir(dt: Optional[DatetimeType] = None) -> Path:
    if dt is None:
        dt = date.today().strftime("%Y-%m-%d")
    return Path(get_global_config().DATA_DIR) / "raw" / dt


def read_all_files(dt: Optional[DatetimeType] = None) -> List[pd.DataFrame]:
    DATA_DIR = get_weekly_raw_data_dir(dt)
    # collect all the file list
    file_list = list(DATA_DIR.glob("*.txt"))
    # sort the file names to ensure that there is some ordering
    file_list.sort()

    # verify that the ordering is as expected
    print([filename.name.split("_")[0] for filename in file_list])
    return list(map(read_fwf_file, file_list))


def read_fwf_file(
    weekly_filepath: FilenameType = None,
    layout_filepath: Optional[FilenameType] = None,
) -> pd.DataFrame:
    """
    Reading fixed width structured data
    """
    if layout_filepath is None:
        # If no file path is provided, take defaults in .env depending on weekly filepath name
        if "reaext" in weekly_filepath.name.lower():
            layout_filepath = get_global_config().REAEXT_LAYOUT
        if "reawage" in weekly_filepath.name.lower():
            layout_filepath = get_global_config().WAGE_LAYOUT
        if "reaint420" in weekly_filepath.name.lower():
            layout_filepath = get_global_config().INT420_LAYOUT
        if "realedg" in weekly_filepath.name.lower():
            layout_filepath = get_global_config().LEDGER_LAYOUT

    # Read Layout
    layout = pd.read_csv(layout_filepath, header=None)
    return _read_weekly_data(layout=layout, weekly_filepath=weekly_filepath)
