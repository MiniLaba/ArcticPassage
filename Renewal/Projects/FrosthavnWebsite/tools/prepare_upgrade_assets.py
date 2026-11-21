"""Extract existing mod art and real QA captures; no generated or personal art."""
from pathlib import Path
from PIL import Image
import json
import shutil

root = Path(__file__).resolve().parents[1]
mod = root.parent / 'ArcticPassage'
assets = root / 'public/assets'
assets.mkdir(parents=True, exist_ok=True)
for person in ['Ada', 'Mira', 'Roan']:
    Image.open(mod / f'ContentPack/assets/portraits/{person}.png').crop((0, 0, 64, 64)).save(assets / f'portrait-{person.lower()}.webp', lossless=True)
    Image.open(mod / f'ContentPack/assets/characters/{person}.png').crop((0, 0, 64, 32)).save(assets / f'walk-{person.lower()}.png')
for name, source in {'airport': 'Airstrip', 'town': 'Town', 'harbour': 'HarborReady', 'fjord': 'Icefjord', 'tundra': 'Tundra', 'camp': 'WinterCamp', 'trail': 'SledTrail', 'glacier': 'Glacier'}.items():
    scene = mod / f'ContentPack/assets/maps/{source}_winter_scene.png'
    if not scene.exists():
        scene = mod / f'Code/ArcticPassage/Runtime/assets/guide/{source}_winter.png'
    Image.open(scene).save(assets / f'scene-{name}.webp', lossless=True)
for name, source in {'letter': 'letter_ticket', 'checkin': 'checkin_final', 'arrival': 'landed_first'}.items():
    capture = Image.open(mod / f'previews/InGame_Airline_{source}_077.jpg').convert('RGB')
    capture.thumbnail((1100, 720))
    capture.save(assets / f'guide-{name}.webp', quality=86)
shutil.copy2(mod / 'ContentPack/assets/items/cuisine.png', assets / 'cuisine.png')
credits_path = root / 'docs/ASSETS.json'
credits = json.loads(credits_path.read_text()) if credits_path.exists() else {}
credits.update({
    'residents': 'First 64×64 frame of existing mod portraits and native four-frame walking rows. No invented residents.',
    'scenes': 'Existing winter game-map scene textures, not screenshots or an exact stitched map.',
    'guide': 'Actual local 0.7.7 invitation, check-in and arrival QA captures, labelled as test-character captures.',
    'landing': 'Website-only SVG ski-aircraft and runway drawn in code; not in-game footage.',
    'sound': 'Local seeded low-pass noise and triangle propeller synthesis. Default muted; no bird recordings or external audio.'
})
credits_path.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + '\n')
print('Prepared eight map scenes, three residents and boarding guide captures.')
