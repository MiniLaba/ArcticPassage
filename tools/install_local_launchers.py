"""Stage the local-only macOS launchers; no game binaries or saves are edited."""
from pathlib import Path
import plistlib
import shutil
import json

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
BUNDLE = WORKSPACE / '北境航路.app'
HOST = BUNDLE / 'Contents/MacOS/StardewModdingAPI'
assert HOST.exists(), 'Existing local SMAPI app host required'
plist = BUNDLE / 'Contents/Info.plist'
data = plistlib.loads(plist.read_bytes())
assert data['CFBundleIdentifier'] == 'com.whitebay.arcticpassage'
assert data['CFBundleExecutable'] in ['StardewModdingAPI', 'ArcticPassageLauncher']
# SMAPI resolves its default mod directory relative to its managed assembly,
# which is linked into this local bundle. Keep that default free of QA and
# provide an explicit second mod set for the developer entry.
default_mods = WORKSPACE / '.development/TestGame/Mods'
qa_source = default_mods / 'ArcticQA'
qa_target = WORKSPACE / '.development/QA/InstalledArcticQA'
if qa_source.exists():
    assert not qa_target.exists(), 'Both QA locations exist; resolve without replacing either'
    qa_source.rename(qa_target)
assert qa_target.is_dir(), 'Dedicated QA module required for developer preview'
preview_mods = WORKSPACE / '.development/PreviewMods'
preview_mods.mkdir(exist_ok=True)
for source in [*(WORKSPACE / '.development/PlayableMods').iterdir(), qa_target]:
    if not source.is_dir():
        continue
    target = preview_mods / ('ArcticQA' if source == qa_target else source.name)
    if target.is_symlink():
        assert target.resolve() == source.resolve(), target
    else:
        assert not target.exists(), target
        target.symlink_to(source.resolve(), target_is_directory=True)
for source, target in [
    ('play.command', WORKSPACE / '启动北境航路·正常游玩.command'),
    ('preview.command', WORKSPACE / '启动北境航路·开发预览.command'),
]:
    shutil.copyfile(ROOT / 'tools/macos' / source, target)
    target.chmod(0o755)
data['CFBundleExecutable'] = 'StardewModdingAPI'
version = json.loads((ROOT / 'ContentPack/manifest.json').read_text())['Version']
data['CFBundleShortVersionString'] = version
data['CFBundleVersion'] = version
plist.write_bytes(plistlib.dumps(data, sort_keys=False))
print('Staged local normal-by-default application and explicit developer preview; SMAPI host and saves untouched.')
