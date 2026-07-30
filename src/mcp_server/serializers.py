"""Conversion of domain objects into JSON-friendly structures for the MCP tools."""

from typing import Any

import numpy as np
from numpy.typing import NDArray
import pandas as pd

from src.interfaces import IPoints
from src.entities import Points


# Coordinates keep the 3 decimal places used in the xlsx files; measured values keep 4, matching the
# precision of the constants tables.
COORDINATE_DECIMALS: int = 3
VALUE_DECIMALS: int = 4


def points_to_list(points: IPoints | NDArray[np.float64]) -> list[list[float]]:
    """Convert a set of points into a list of `[x, y, z]` triples."""
    coordinates: NDArray[np.float64] = points.points if isinstance(points, IPoints) else points

    if len(coordinates) == 0:
        return []

    return [
        [round(float(value), COORDINATE_DECIMALS) for value in point]
        for point in np.asarray(coordinates, dtype=np.float64)
    ]


def list_to_points(coordinates: list[list[float]]) -> IPoints:
    """Convert a list of `[x, y, z]` triples into a set of points."""
    if not coordinates:
        return Points(points=np.array([]).reshape(0, 3))

    return Points(points=np.array(coordinates, dtype=np.float64).reshape(-1, 3))


def df_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Convert a DataFrame into a list of row dicts.

    MultiIndex column names (as returned by `get_distance_matrix`) are flattened into
    `"top level / bottom level"` keys.
    """
    flat_df: pd.DataFrame = df.copy()

    if isinstance(flat_df.columns, pd.MultiIndex):
        flat_df.columns = pd.Index([" / ".join(str(part) for part in col) for col in flat_df.columns])
    else:
        flat_df.columns = pd.Index([str(col) for col in flat_df.columns])

    return [
        {key: _to_json_value(value) for key, value in row.items()}
        for row in flat_df.to_dict(orient="records")
    ]


def name_value_df_to_dict(df: pd.DataFrame) -> dict[str, Any]:
    """Convert a `Name` / `Value` DataFrame (the constants tables) into a flat dict."""
    return {
        str(row["Name"]): _to_json_value(row["Value"])
        for _, row in df.iterrows()
    }


def _to_json_value(value: Any) -> Any:
    """Convert numpy scalars to plain Python and NaN to None."""
    if isinstance(value, (np.integer,)):
        return int(value)

    if isinstance(value, (np.floating, float)):
        float_value: float = float(value)
        return None if np.isnan(float_value) else round(float_value, VALUE_DECIMALS)

    if isinstance(value, (np.bool_,)):
        return bool(value)

    return value
