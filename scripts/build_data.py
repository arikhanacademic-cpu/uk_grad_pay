"""Rebuild the files in data/ from the DfE LEO provider-level download.

Usage:
    pip install pandas
    python scripts/build_data.py raw/leo-graduate-outcomes-provider-level-data_2022-23.zip

The zip comes from explore-education-statistics.service.gov.uk
("LEO Graduate and Postgraduate Outcomes", provider level data).
"""
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

from campuses import C

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data"
TAX_YEAR = "2022/2023"
NE_URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
          "geojson/ne_50m_admin_0_countries.geojson")


def open_provider_csv(zip_path):
    """The download is a zip holding another zip holding the ~790 MB CSV."""
    outer = zipfile.ZipFile(zip_path)
    inner_name = next(n for n in outer.namelist() if n.endswith("leo_provider_dashboard_underlying_data.zip"))
    inner = zipfile.ZipFile(io.BytesIO(outer.read(inner_name)))
    csv_name = next(n for n in inner.namelist() if n.startswith("provider_data") and n.endswith(".csv"))
    return inner.open(csv_name)


def main(zip_path):
    keep = []
    with open_provider_csv(zip_path) as f:
        for ch in pd.read_csv(f, encoding="latin1", chunksize=500_000, dtype=str):
            m = ((ch.tax_year == TAX_YEAR) & (ch.home_region_name == "Total")
                 & (ch.current_region_name == "Total")
                 & (ch.characteristic_type == "All graduates") & (ch.provider_type == "HEI"))
            keep.append(ch[m])
    d = pd.concat(keep)
    num = lambda s: pd.to_numeric(s, errors="coerce")

    # Per-university rows
    p = d[(d.provider_name != "Total") & (d.cah2_subject_name != "Total")].copy()
    print("No campus position, left off the map:", sorted(p[~p.ukprn.isin(C)].provider_name.unique()))
    p = p[p.ukprn.isin(C)]
    p["median"] = num(p.earnings_median)
    p = p[p["median"].notna()]          # drop suppressed figures
    p["lq"], p["uq"], p["grads"] = num(p.earnings_LQ), num(p.earnings_UQ), num(p.grads)
    p["key"] = p.ukprn + "|" + p.cah2_subject_name + "|" + p.YAG
    assert p.key.is_unique
    e = p.rename(columns={"provider_name": "university", "cah2_subject_name": "subject", "YAG": "yag"})
    e = e[["key", "ukprn", "university", "subject", "yag", "median", "lq", "uq", "grads"]]
    for c in ["median", "lq", "uq", "grads"]:
        e[c] = e[c].astype("Int64")
    e.to_csv(OUT / "leo_earnings_2022-23.csv", index=False)

    # UK-wide medians per subject
    n = d[(d.provider_name == "Total") & (d.provider_country_name == "Total")
          & (d.cah2_subject_name != "Total")].copy()
    n["key"] = n.cah2_subject_name + "|" + n.YAG
    assert n.key.is_unique
    n = n.rename(columns={"cah2_subject_name": "subject", "YAG": "yag"})
    n["median"], n["grads"] = num(n.earnings_median).astype("Int64"), num(n.grads).astype("Int64")
    n[["key", "subject", "yag", "median", "grads"]].to_csv(OUT / "leo_national_2022-23.csv", index=False)

    # Campus positions (hand-entered in campuses.py)
    used = set(e.ukprn)
    pd.DataFrame([dict(ukprn=k, short=v[0], lat=v[1], lon=v[2], russell_group="yes" if v[3] else "no")
                  for k, v in C.items() if k in used]).to_csv(OUT / "campus_positions.csv", index=False)

    # Coastline from Natural Earth (public domain)
    g = json.load(urllib.request.urlopen(NE_URL))
    rows, pid = [], 0
    for feat in g["features"]:
        name = feat["properties"]["ADMIN"]
        if name not in ("United Kingdom", "Ireland"):
            continue
        for poly in feat["geometry"]["coordinates"]:
            ring = poly[0]
            if len(ring) < 6:
                continue
            for lon, lat in ring:
                rows.append(dict(country="UK" if name == "United Kingdom" else "Ireland",
                                 part=pid, lon=round(lon, 3), lat=round(lat, 3)))
            pid += 1
    json.dump(rows, open(OUT / "uk_outline.json", "w"))
    print(f"Wrote {len(e)} university rows, {len(n)} national rows, {len(rows)} outline points.")


if __name__ == "__main__":
    default = ROOT / "raw" / "leo-graduate-outcomes-provider-level-data_2022-23.zip"
    main(sys.argv[1] if len(sys.argv) > 1 else default)
