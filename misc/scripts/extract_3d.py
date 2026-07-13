"""Extract the 3D asset FBX (+ textures) from the Kenney Game Assets All-in-1 bundle.

The bundle (itch.io, owned; fetched via the itch API) has a top-level `3D assets/` subtree.
Per pack we take the topology-preserving **FBX** (glTF/GLB triangulate; OBJ deprioritized),
preserving each pack's `Textures/` folder so Blender resolves materials. The 4 animated-character
packs nest FBX by role — we keep `Models/`+`Accessories/` geometry and skip `Animations/`
(pose clips) and `Skins/` (runtime-swappable). Writes `_dl/<slug>/…` + `data/kenney_manifest.parquet`.

Usage: python extract_3d.py <bundle.zip> _dl
"""

from __future__ import annotations

import os
import re
import sys
import zipfile

import pandas as pd

ANIMATED = {
    "Animated Characters Bundle",
    "Animated Characters Protagonists",
    "Animated Characters Retro",
    "Animated Characters Survivors",
}


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def main() -> None:
    zip_path, out_dir = sys.argv[1], sys.argv[2]
    z = zipfile.ZipFile(zip_path)
    packs = sorted(
        {n.split("/")[1] for n in z.namelist() if n.startswith("3D assets/") and n.count("/") >= 2 and n.split("/")[1]}
    )

    rows, total = [], 0
    for pack in packs:
        sl = slug(pack)
        if pack in ANIMATED:
            # distinct geometry only; textures are swappable skins (no embedded material)
            members = [
                n for n in z.namelist()
                if n.startswith(f"3D assets/{pack}/") and n.lower().endswith(".fbx")
                and ("/Models/" in n or "/Accessories/" in n) and "/Animations/" not in n
            ]
            strip = f"3D assets/{pack}/"
        else:
            pref = f"3D assets/{pack}/Models/FBX format/"
            members = [n for n in z.namelist() if n.startswith(pref) and not n.endswith("/")]
            strip = pref

        n_fbx = sum(1 for n in members if n.lower().endswith(".fbx"))
        if not n_fbx:
            print("NO-FBX", pack)
            continue
        dest = os.path.join(out_dir, sl)
        for m in members:
            d = os.path.join(dest, m[len(strip):])
            os.makedirs(os.path.dirname(d), exist_ok=True)
            with open(d, "wb") as f:
                f.write(z.read(m))
        rows.append({"slug": sl, "name": pack, "n_fbx": n_fbx})
        total += n_fbx
        print(f"{sl}: {n_fbx} fbx")

    os.makedirs("data", exist_ok=True)
    pd.DataFrame(rows).to_parquet("data/kenney_manifest.parquet", index=False)
    print(f"extracted {len(rows)} packs, {total} fbx -> data/kenney_manifest.parquet")


if __name__ == "__main__":
    main()
