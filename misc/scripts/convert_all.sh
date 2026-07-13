#!/usr/bin/env bash
# Convert every extracted Kenney pack's FBX -> ASCII OpenUSD (Blender), with
# materials/textures/normals, namespaced per pack. Resumable: a pack whose
# models/<slug>/*.usda already exist is skipped.
# Usage: bash convert_all.sh <dl_dir>
set -u
DL="${1:-_dl}"
CONVERT="$(dirname "$0")/models_to_usda_batch.py"
done=0; skipped=0; failed=""
for d in "$DL"/*/; do
  slug="$(basename "$d")"
  ls "$d"*.fbx >/dev/null 2>&1 || find "$d" -iname '*.fbx' | grep -q . || continue
  out="models/$slug"
  if [ -d "$out" ] && ls "$out"/*.usda >/dev/null 2>&1; then
    echo "SKIP $slug"; skipped=$((skipped+1)); continue
  fi
  mkdir -p "$out"
  echo "==== $slug ===="
  blender --background --factory-startup --python "$CONVERT" -- "$d" "$out" 2>&1 | grep -E "CONVERTED|FAIL " | tail -2
  ls "$out"/*.usda >/dev/null 2>&1 && done=$((done+1)) || failed="$failed $slug"
done
echo "================ DONE converted=$done skipped=$skipped FAILED:$failed"
