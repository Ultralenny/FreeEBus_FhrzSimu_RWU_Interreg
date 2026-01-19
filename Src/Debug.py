import csv
import numbers
from pathlib import Path

DEBUG_CSV_FIELDS = [
    "index",
    "strecke_m",
    "strecke_km",
    "steigung_deg",
    "velocity_m_s",
    "acceleration_m_s2",
    "f_roll_n",
    "f_luft_n",
    "f_steig_n",
    "f_beschl_n",
    "f_ges_n",
    "n_motor_rpm",
    "trq_motor_nm",
    "eta_ltb",
    "fahrleistung_el_kw",
    "energie_verbrauch_kwh",
    "state_of_charge_pct",
]


def _format_debug_value(value, float_format, decimal_separator):
    if value is None:
        return ""
    if isinstance(value, numbers.Real) and not isinstance(value, bool):
        if isinstance(value, int):
            return value
        text = format(float(value), float_format)
        if decimal_separator != ".":
            text = text.replace(".", decimal_separator)
        return text
    return value


def write_debug_csv(
    path,
    rows,
    delimiter=";",
    decimal_separator=",",
    float_format=".6f",
):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file_handle:
        writer = csv.DictWriter(
            file_handle,
            fieldnames=DEBUG_CSV_FIELDS,
            extrasaction="ignore",
            delimiter=delimiter,
        )
        writer.writeheader()
        formatted_rows = (
            {
                key: _format_debug_value(value, float_format, decimal_separator)
                for key, value in row.items()
            }
            for row in rows
        )
        writer.writerows(formatted_rows)
