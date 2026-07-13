# kenney-stage

OpenUSD (`.usda`) copy of [Kenney](https://kenney.nl)'s CC0 3D asset packs — FBX-sourced (topology-preserving; glTF triangulates), with materials + textures + normals carried through. Y-up, −Z forward, right-handed, real-world meters. ETNF catalog in `data/kenney.parquet`, keyed `kenney:<pack>/<model>` (shares the vsk lake namespace).

## Layout
- `models/<pack>/<Model>.usda` (+ `models/<pack>/textures/`) — the meshes and their textures
- `data/kenney.parquet` — ETNF catalog; `data/kenney_manifest.parquet` — pack list
- `misc/scripts/` — `extract_3d.py`, `models_to_usda_batch.py` (Blender FBX→usda + materials), `convert_all.sh`, `build_etnf.py`

## Rebuild
From the Kenney Game Assets All-in-1 bundle (itch.io, CC0):
```bash
python misc/scripts/extract_3d.py _dl/kenney-allinone.zip _dl   # 3D FBX + textures per pack
bash   misc/scripts/convert_all.sh _dl                          # Blender → .usda (resumable)
python misc/scripts/build_etnf.py models data/kenney_manifest.parquet data/kenney.parquet
```

License: **CC0-1.0** (Kenney). See `LICENSE`.
