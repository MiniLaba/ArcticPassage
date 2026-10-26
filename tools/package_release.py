"""Build player/source archives from an explicit publish allowlist.

Game assemblies, saves, local test logs and personal ephemera are never candidates.
Import source_files() to build a GitHub publishing snapshot from the same inputs.
"""
from pathlib import Path
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parents[1]
PUBLIC_ROOT_FILES = ('README.md', 'INSTALL.zh-CN.md', 'LICENSE', 'CREDITS.md', 'CHANGELOG.md', '.gitignore')
PUBLIC_DOCS = ('PLAYER_STATUS.md', 'BUILDING.md', 'WINDOWS_COMPATIBILITY.md', 'RELEASE_0.7.9.md', 'RELEASE_0.7.10.md', 'MapPlan.md', 'RealWorldReferences.md', 'ArtDirection040.md', 'AudioDesign.md', 'SeafoodDesign063.md', 'build-index.json')
EXCLUDE_PARTS = {'bin', 'obj', '__pycache__', '.git', '.DS_Store', 'ephemera', 'archive', 'review-060'}


def tree_files(path):
    for p in sorted(path.rglob('*')):
        if p.is_file() and not p.is_symlink() and not any(n in EXCLUDE_PARTS for n in p.relative_to(R).parts):
            yield p


def source_files():
    """Exact portable publishing snapshot. All returned paths are inside this project."""
    for name in PUBLIC_ROOT_FILES:
        yield R / name
    for name in PUBLIC_DOCS:
        yield R / 'docs' / name
    for directory in ('.github/workflows', 'ContentPack', 'Code', 'tools', 'art/source', 'art/music', 'art/prompts', 'docs/licenses', 'docs/images', 'tests/NativeValidation', 'tests/RuntimeFixture', 'tests/QualityTradeRegression', 'tests/HarborProgressRegression', 'tests/PolarPhotoperiodRegression', 'tests/PolarWeatherRegression', 'tests/SnowShelterRegression'):
        yield from tree_files(R / directory)
    yield from sorted((R / 'tests').glob('validate_*.py'))


def main():
    output = R / 'dist'
    output.mkdir(exist_ok=True)
    version = json.loads((R / 'ContentPack/manifest.json').read_text())['Version']
    project = R / 'Code/ArcticPassage'
    manifest = json.loads((project / 'Runtime/manifest.json').read_text())
    assembly = project / 'bin/Release/net6.0/ArcticPassage.Runtime.dll'
    assert manifest['Version'] == version
    assert manifest['EntryDll'] == assembly.name and assembly.stat().st_size >= 8192
    assert any(d['UniqueID'] == manifest['UniqueID'] and d.get('IsRequired') and d.get('MinimumVersion') == version
               for d in json.loads((R / 'ContentPack/manifest.json').read_text())['Dependencies'])
    translations = [json.loads((project / f'Runtime/i18n/{lang}.json').read_text()) for lang in ('default', 'zh')]
    assert translations[0].keys() == translations[1].keys(), 'Runtime translations differ'

    own_dll = 'ArcticPassage.Runtime/' + assembly.name
    player_entries = [(p, 'ArcticPassage/' + p.relative_to(R / 'ContentPack').as_posix()) for p in tree_files(R / 'ContentPack')]
    player_entries += [(assembly, own_dll)]
    player_entries += [(p, 'ArcticPassage.Runtime/' + p.relative_to(project / 'Runtime').as_posix()) for p in tree_files(project / 'Runtime')]
    player_entries += [(R / name, name) for name in ('README.md', 'INSTALL.zh-CN.md', 'LICENSE', 'CREDITS.md', 'CHANGELOG.md')]
    player_entries += [(R / 'docs' / name, 'docs/' + name)
                       for name in ('PLAYER_STATUS.md', 'WINDOWS_COMPATIBILITY.md', 'RELEASE_0.7.10.md')]
    player_entries += [(p, p.relative_to(R).as_posix()) for p in tree_files(R / 'docs/licenses')]

    public_sources = list(source_files())
    assert len(public_sources) == len(set(public_sources))
    source_entries = [(p, 'ArcticPassage/' + p.relative_to(R).as_posix()) for p in public_sources]
    outputs = []
    for kind, entries in [('install', player_entries), ('source', source_entries)]:
        path = output / f'ArcticPassage-{version}-{kind}.zip'
        assert len(entries) == len({name for _, name in entries}), 'Duplicate archive entries'
        for p, name in entries:
            assert p.is_file() and not p.is_symlink(), p
            assert '..' not in Path(name).parts and not name.startswith('/')
            assert not any(part in EXCLUDE_PARTS for part in Path(name).parts), name
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
            for p, name in sorted(entries, key=lambda item: item[1]):
                z.write(p, name)
        with zipfile.ZipFile(path) as z:
            binaries = [n for n in z.namelist() if n.lower().endswith(('.dll', '.xnb', '.dylib', '.exe', '.pdb'))]
            assert binaries == ([own_dll] if kind == 'install' else []), binaries
            for p, name in entries:
                assert z.read(name) == p.read_bytes(), name
            assert z.testzip() is None
        outputs.append(path)
        print(f'{path.name}: {path.stat().st_size} bytes, {len(entries)} entries; binary allowlist, full byte equality and ZIP integrity PASS')
    sums = output / 'SHA256SUMS.txt'
    if sums.exists():
        previous = sums.read_text()
        for line in previous.splitlines():
            if '-install.zip' in line:
                old_version = line.split('ArcticPassage-', 1)[1].split('-install.zip', 1)[0]
                if old_version != version:
                    history = output / f'SHA256SUMS-{old_version}-historical.txt'
                    if not history.exists():
                        history.write_text(previous)
                break
    sums.write_text('\n'.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name for p in outputs) + '\n')
    print('Player archive has exactly the two mod roots plus player docs/licenses. Source and GitHub snapshot use the same allowlist.')


if __name__ == '__main__':
    main()
