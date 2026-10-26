"""R02 existing camp exhibit action; no new map, items or rewards."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
TAG = 'R02 snow-block model'


def main():
    p = ROOT / 'ContentPack/content.json'
    data = json.loads(p.read_text())
    data['Changes'] = [change for change in data['Changes'] if change.get('LogName') != TAG]
    data['Changes'].append({
        'Action': 'EditMap', 'Target': 'Maps/ArcticPassage_WinterCamp', 'LogName': TAG,
        'MapTiles': [{'Position': {'X': 20, 'Y': 35}, 'Layer': 'Buildings',
                      'SetProperties': {'Action': 'ArcticPassageSnowShelter'}}]
    })
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print('Connected winter snow-block model to the existing camp exhibit; other seasons retain a notice.')


if __name__ == '__main__':
    main()
