"""Builds the mosque tiles the app reads (t/<y>_<x>.json) from OpenStreetMap.

Source: QLever's OSM planet SPARQL endpoint (one query, ~20 s, every
amenity=place_of_worship + religion=muslim with its centroid). Overpass was
the app's live source until every public instance stopped answering; static
tiles on GitHub Pages need no live third party at all.

Tile = 0.25 x 0.25 degree cell, key floor(lat*4)_floor(lon*4). A missing
tile means no mosque in that cell; meta.json proves the set itself exists.

Usage: python build.py            (download + build)
       python build.py --offline  (rebuild from all.tsv)
"""
import datetime, json, math, os, re, shutil, sys, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENDPOINT = 'https://qlever.dev/api/osm-planet'
CELL = 4  # cells per degree
MIN_EXPECTED = 200_000  # a truncated download must never replace good tiles

def download():
    q = open(os.path.join(HERE, 'query.rq'), encoding='utf-8').read()
    req = urllib.request.Request(
        ENDPOINT, data=urllib.parse.urlencode({'query': q}).encode(),
        headers={'Accept': 'text/tab-separated-values',
                 'User-Agent': 'HuzurVakti-tiles/1.0 (com.lutfu.huzurvakti)'})
    with urllib.request.urlopen(req, timeout=600) as r:
        data = r.read()
    with open(os.path.join(HERE, 'all.tsv'), 'wb') as f:
        f.write(data)

def literal(v):
    v = v.strip()
    if not v:
        return ''
    m = re.match(r'^"(.*)"(?:@[\w-]+|\^\^<[^>]*>)?$', v, re.S)
    if not m:
        return v
    s = m.group(1)
    return re.sub(r'[\\](.)', lambda x: {'t': '\t', 'n': ' ', 'r': ''}.get(x.group(1), x.group(1)), s).strip()

def main():
    if '--offline' not in sys.argv:
        download()
    rows = open(os.path.join(HERE, 'all.tsv'), encoding='utf-8').read().splitlines()
    if not rows or not rows[0].startswith('?osm'):
        sys.exit('unexpected header: %r' % rows[:1])
    seen = {}
    for line in rows[1:]:
        cols = line.split('\t')
        if len(cols) < 2:
            continue
        osm = cols[0].strip('<>').rsplit('/', 2)
        m = re.search(r'POINT\(([-\d.eE]+) ([-\d.eE]+)\)', cols[1])
        if not m:
            continue
        lon, lat = float(m.group(1)), float(m.group(2))
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        key = osm[-2][0] + osm[-1]  # n123 / w123 / r123
        names = [literal(c) for c in (cols + ['', '', ''])[2:5]]
        name, tr, en = names
        best = tr or name or en
        if key not in seen or (best and not seen[key][2]):
            seen[key] = (round(lat, 5), round(lon, 5), best)
    if len(seen) < MIN_EXPECTED:
        sys.exit('only %d mosques - refusing to publish' % len(seen))

    tiles = {}
    for k, (lat, lon, name) in seen.items():
        t = '%d_%d' % (math.floor(lat * CELL), math.floor(lon * CELL))
        tiles.setdefault(t, []).append([lat, lon, name])
    out = os.path.join(HERE, 'docs', 't')
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    for t, items in tiles.items():
        items.sort()
        with open(os.path.join(out, t + '.json'), 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'m': items}, f, ensure_ascii=False, separators=(',', ':'))
    meta = {'v': 1, 'cellsPerDegree': CELL, 'mosques': len(seen), 'tiles': len(tiles),
            'built': datetime.date.today().isoformat(),
            'source': 'OpenStreetMap contributors, ODbL 1.0 (openstreetmap.org/copyright)'}
    with open(os.path.join(HERE, 'docs', 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False)
    open(os.path.join(HERE, 'docs', '.nojekyll'), 'w').close()
    print(json.dumps(meta))

if __name__ == '__main__':
    main()
