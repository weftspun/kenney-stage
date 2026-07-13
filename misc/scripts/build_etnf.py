"""Build the ETNF parquet catalog for the Kenney OpenUSD assets.

Essential Tuple Normal Form: one 1:1 relation keyed by a UUIDv5 `asset_uuid`, derived from a
stable natural key. Keys share the vsk-session-item-recommendation lake namespace (same
`asset:<natural_key>` rule), so this catalog joins that lake and the sibling corpora directly.
Kenney reuses model names across packs, so the natural key is namespaced by pack:
`kenney:<pack>/<model>`.

Usage: python build_etnf.py <models_dir> <kenney_manifest.parquet> <out.parquet>
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

import pandas as pd

# Fixed lake namespace (identical to vsk_recsys/data/etnf.py) so keys line up.
NAMESPACE = uuid.uuid5(
    uuid.NAMESPACE_URL,
    "https://github.com/V-Sekai-fire/vsk-session-item-recommendation-01",
)

SOURCE = "kenney.nl"
SOURCE_URL = "https://kenney.itch.io/kenney-game-assets"
LICENSE = "CC0-1.0"


def asset_uuid(natural_key: str) -> str:
    return str(uuid.uuid5(NAMESPACE, f"asset:{natural_key}"))


def build(models_dir: str, manifest_file: str, out: str) -> pd.DataFrame:
    name_by_slug = {}
    if Path(manifest_file).exists():
        man = pd.read_parquet(manifest_file)
        name_by_slug = dict(zip(man["slug"], man["name"]))

    rows = []
    for usd in sorted(Path(models_dir).glob("*/*.usda")):
        pack = usd.parent.name
        model = usd.stem
        natural_key = f"kenney:{pack}/{model}"
        rows.append(
            {
                "asset_uuid": asset_uuid(natural_key),
                "natural_key": natural_key,
                "pack": pack,
                "pack_name": name_by_slug.get(pack, pack),
                "name": model,
                "usd_file": f"models/{pack}/{model}.usda",
                "source": SOURCE,
                "source_url": SOURCE_URL,
                "up_axis": "Y",
                "forward_axis": "-Z",
                "handedness": "right",
                "meters_per_unit": 1.0,
                "license": LICENSE,
            }
        )

    frame = pd.DataFrame(rows)
    if frame["asset_uuid"].nunique() != len(frame):
        raise SystemExit("PK collision: asset_uuid not unique")
    frame.to_parquet(out, index=False)
    print(f"wrote {out}: {len(frame)} assets across {frame['pack'].nunique()} packs, PK-unique")
    print(frame[["natural_key", "up_axis", "handedness"]].head(3).to_string(index=False))
    return frame


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2], sys.argv[3])
