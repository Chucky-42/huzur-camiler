# Huzur Vakti — mosque tiles

Static tiles of every mosque in OpenStreetMap (`amenity=place_of_worship` +
`religion=muslim`), read by the Huzur Vakti app's "nearby mosques" screen.

- `docs/t/<y>_<x>.json` — one 0.25° cell, `y = floor(lat*4)`, `x = floor(lon*4)`;
  `{"m": [[lat, lon, name], ...]}`. No file = no mosque in that cell.
- `docs/meta.json` — build date and counts.

Rebuilt monthly by `build.py` from the QLever OSM planet endpoint.

Data © OpenStreetMap contributors, available under the
[Open Database License (ODbL) 1.0](https://www.openstreetmap.org/copyright).
