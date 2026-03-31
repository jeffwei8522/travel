"""
Extract districts from full Taiwan GeoJSON by county/town name.

Usage:
    python extract_region.py --counties "台南市" --output tainan.geojson
    python extract_region.py --counties "新竹市,新竹縣" --towns "新北市/林口區" --output hsinchu_linkou.geojson
    python extract_region.py --list-counties
"""
import json, sys, argparse, os

sys.stdout.reconfigure(encoding='utf-8')

FULL_GEOJSON = os.path.join(os.path.dirname(__file__), '..', 'data', 'tw_towns.geojson')

def load_full():
    with open(FULL_GEOJSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_counties(data):
    counties = sorted(set(f['properties']['COUNTYNAME'] for f in data['features']))
    for c in counties:
        towns = sorted(set(
            f['properties']['TOWNNAME'] for f in data['features']
            if f['properties']['COUNTYNAME'] == c
        ))
        print(f"{c}: {', '.join(towns)}")

def extract(data, counties=None, towns=None):
    counties = set(counties or [])
    towns = set(towns or [])  # format: "縣市/鄉鎮"

    features = []
    for feat in data['features']:
        p = feat['properties']
        county = p.get('COUNTYNAME', '')
        town = p.get('TOWNNAME', '')

        if county in counties or f"{county}/{town}" in towns:
            features.append(feat)

    return {"type": "FeatureCollection", "features": features}

def main():
    parser = argparse.ArgumentParser(description='Extract Taiwan district GeoJSON')
    parser.add_argument('--counties', help='Comma-separated county names (e.g. "台南市,新竹市")')
    parser.add_argument('--towns', help='Comma-separated county/town pairs (e.g. "新北市/林口區")')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--list-counties', action='store_true', help='List all counties and towns')
    args = parser.parse_args()

    data = load_full()

    if args.list_counties:
        list_counties(data)
        return

    counties = [c.strip() for c in args.counties.split(',')] if args.counties else []
    towns = [t.strip() for t in args.towns.split(',')] if args.towns else []

    result = extract(data, counties, towns)
    print(f"Extracted {len(result['features'])} districts")

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)
        size_kb = os.path.getsize(args.output) / 1024
        print(f"Saved: {args.output} ({size_kb:.0f} KB)")
    else:
        for feat in result['features']:
            p = feat['properties']
            print(f"  {p['COUNTYNAME']} / {p['TOWNNAME']}")

if __name__ == '__main__':
    main()
