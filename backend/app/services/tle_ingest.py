import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple

import requests
from sqlalchemy.orm import Session

from app.db.models import Satellite, TLE
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

# Database configuration from .env
CELESTRAK_GP_URL: str = os.getenv("CELESTRAK_API_URL", "link")

def _parse_tle_epoch(line1: str) -> datetime:
    """
    Parse the epoch from a TLE line 1.

    TLE format (line 1) fields:
    - Columns 19-20: Epoch year (last two digits)
    - Columns 21-32: Epoch day of year (with fractional part)
    """
    try:
        year_str = line1[18:20]
        day_str = line1[20:32]

        year_two_digits = int(year_str)
        # NORAD convention: years < 57 are 2000+, else 1900+
        year_full = 2000 + year_two_digits if year_two_digits < 57 else 1900 + year_two_digits

        day_of_year = float(day_str)

        start_of_year = datetime(year_full, 1, 1, tzinfo=timezone.utc)
        epoch = start_of_year + timedelta(days=day_of_year - 1)
        return epoch
    except Exception:  # noqa: BLE001
        logger.warning("Failed to parse TLE epoch from line1 '%s', using current UTC time", line1)
        return datetime.now(timezone.utc)


def _parse_tle_text(tle_text: str) -> List[Dict[str, Any]]:
    """
    Parse raw TLE text into a list of records with name, NORAD ID, and TLE lines.

    The text is expected to come in 3-line blocks:
    - Line 0: satellite name
    - Line 1: TLE line 1
    - Line 2: TLE line 2
    """
    lines = [ln.strip() for ln in tle_text.splitlines() if ln.strip()]
    records: List[Dict[str, Any]] = []

    for i in range(0, len(lines) - 2, 3):
        name = lines[i]
        line1 = lines[i + 1]
        line2 = lines[i + 2]

        # Basic validation of TLE lines
        if not (line1.startswith("1 ") and line2.startswith("2 ")):
            continue

        try:
            # Standard TLE: satellite number is columns 3-7 (index 2:7)
            norad_id = int(line1[2:7])
        except ValueError:
            logger.warning("Failed to parse NORAD ID from TLE line1 '%s'", line1)
            continue

        epoch = _parse_tle_epoch(line1)

        records.append(
            {
                "OBJECT_NAME": name,
                "NORAD_CAT_ID": norad_id,
                "TLE_LINE1": line1,
                "TLE_LINE2": line2,
                "EPOCH": epoch,
            }
        )

    return records


def fetch_gp_data(group: str = "active") -> List[Dict[str, Any]]:
    """
    Fetch GP (general perturbations) orbital data from Celestrak in **TLE text** format
    and parse it into structured records.

    :param group: Celestrak GROUP parameter, e.g. 'active', 'starlink', etc.
    :return: List of dicts with OBJECT_NAME, NORAD_CAT_ID, TLE_LINE1, TLE_LINE2, and EPOCH.
    """
    params = {"GROUP": group, "FORMAT": "tle"}
    try:
        response = requests.get(CELESTRAK_GP_URL, params=params, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:  # noqa: PERF203
        msg = f"Failed to fetch TLE data from Celestrak for group '{group}': {exc}"
        logger.error(msg)
        raise RuntimeError(msg) from exc

    tle_text = response.text
    return _parse_tle_text(tle_text)


def upsert_satellite(db: Session, name: str, norad_id: int) -> Tuple[Satellite, bool]:
    """
    Find an existing satellite by NORAD ID or create a new one.

    :return: (satellite, created_flag)
    """
    sat = db.query(Satellite).filter(Satellite.norad_id == norad_id).one_or_none()

    if sat is None:
        sat = Satellite(
            name=name,
            description=f"{name} (imported from Celestrak)",
            norad_id=norad_id,
        )
        db.add(sat)
        db.commit()
        db.refresh(sat)
        return sat, True

    # Optionally update name if it changed
    if sat.name != name:
        sat.name = name
        db.commit()
        db.refresh(sat)

    return sat, False


def store_tle_for_satellite(
    db: Session,
    satellite: Satellite,
    line1: str,
    line2: str,
    epoch: datetime,
) -> TLE:
    """
    Create a new TLE record linked to the given satellite.
    """
    tle = TLE(
        satellite_norad_id=satellite.norad_id,
        line1=line1,
        line2=line2,
        timestamp=epoch,
    )
    db.add(tle)
    db.commit()
    db.refresh(tle)
    return tle


def import_gp_group(db: Session, group: str = "active") -> Dict[str, Any]:
    """
    High-level function to import a Celestrak GP group into the local database.

    - Fetches GP TLE data for the given group
    - Parses it into structured records
    - Upserts satellites by NORAD ID
    - Creates TLE records for each entry

    :return: Summary dict with counts.
    """
    data = fetch_gp_data(group)

    satellites_created = 0
    satellites_updated = 0
    tles_inserted = 0

    for item in data:
        try:
            name = item.get("OBJECT_NAME")
            norad_id = int(item.get("NORAD_CAT_ID"))
            line1 = item.get("TLE_LINE1")
            line2 = item.get("TLE_LINE2")
            epoch = item.get("EPOCH")

            if not (name and norad_id and line1 and line2 and epoch):
                # Skip incomplete or unparsable records
                continue

            sat, created = upsert_satellite(db, name=name, norad_id=norad_id)
            if created:
                satellites_created += 1
            else:
                satellites_updated += 1

            store_tle_for_satellite(db, sat, line1=line1, line2=line2, epoch=epoch)
            tles_inserted += 1
        except Exception as exc:  # noqa: BLE001
            logger.warning("Skipping GP record due to error: %s", exc)
            db.rollback()
            continue

    summary = {
        "group": group,
        "records_received": len(data),
        "satellites_created": satellites_created,
        "satellites_updated": satellites_updated,
        "tles_inserted": tles_inserted,
    }

    logger.info("Celestrak GP import summary: %s", summary)
    return summary


