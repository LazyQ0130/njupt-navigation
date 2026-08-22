"""Fetch a cached OSM extract for NJUPT Xianlin from Overpass."""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "data" / "raw" / "osm" / f"xianlin-{date.today().isoformat()}.overpass.json"
ENDPOINT = "https://overpass-api.de/api/interpreter"
USER_AGENT = "njupt-navigation-phase1.5/0.1 (https://github.com/LazyQ0130/njupt-navigation)"

# The bounding box comes from OSM way 89910254 plus a small review margin.
QUERY = """
[out:json][timeout:90][bbox:32.1065,118.9190,32.1242,118.9310];
(
  way(89910254);
  way[building];
  relation[building];
  way[highway];
  node[amenity]; way[amenity]; relation[amenity];
  node[shop]; way[shop];
  node[entrance];
  way[leisure]; relation[leisure];
  way[natural=water]; relation[natural=water];
  way[landuse]; relation[landuse];
);
out body geom qt;
""".strip()


def fetch(output: Path, force: bool = False, endpoint: str = ENDPOINT) -> Path:
    if output.is_file() and not force:
        print(f"Using cached OSM response: {output}")
        return output
    output.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        endpoint,
        data=urllib.parse.urlencode({"data": QUERY}).encode("utf-8"),
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        method="POST",
    )
    last_error: Exception | None = None
    for attempt, delay in enumerate((0, 8, 20), start=1):
        if delay:
            time.sleep(delay)
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = response.read()
            parsed = json.loads(payload)
            if "elements" not in parsed:
                raise RuntimeError("Overpass response does not contain elements")
            output.write_bytes(payload)
            print(f"Saved {len(parsed['elements'])} OSM elements to {output}")
            return output
        except Exception as error:  # network errors are retried with bounded backoff
            last_error = error
            print(f"Overpass attempt {attempt} failed: {error}")
    raise RuntimeError("Unable to fetch OSM data after 3 attempts") from last_error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--endpoint", default=ENDPOINT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    fetch(args.output.resolve(), args.force, args.endpoint)


if __name__ == "__main__":
    main()
