# Huzur Vakti — mosque tiles

Static tiles of every mosque in OpenStreetMap (`amenity=place_of_worship` +
`religion=muslim`), read by the Huzur Vakti app's "nearby mosques" screen.

- `docs/t/<y>_<x>.json` — one 0.25° cell, `y = floor(lat*4)`, `x = floor(lon*4)`;
  `{"m": [[lat, lon, name], ...]}`. No file = no mosque in that cell.
- `docs/meta.json` — build date and counts.

Rebuilt weekly by `build.py` (scheduled task HuzurCamilerHaftalik → `yenile.py`) from the QLever OSM planet endpoint.

Published twice: `huzurvakti/camiler` (https://huzurvakti.github.io/camiler/, read by app versions after 30 Oct 2026)
and `Chucky-42/huzur-camiler` (https://chucky-42.github.io/huzur-camiler/, read by older versions). `yenile.py`
pushes to both remotes (`org` and `origin`).

Data © OpenStreetMap contributors, available under the
[Open Database License (ODbL) 1.0](https://www.openstreetmap.org/copyright).
