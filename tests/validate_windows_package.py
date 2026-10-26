"""Cross-platform install ZIP audit; also run on a real GitHub Windows runner.

This checks installation/CLR portability, not a licensed Windows game session.
"""
from pathlib import Path, PurePosixPath
import json
import hashlib
import re
import struct
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def managed_anycpu(data):
    require(data[:2] == b'MZ', 'Runtime is not a PE assembly')
    pe = struct.unpack_from('<I', data, 0x3c)[0]
    require(data[pe:pe + 4] == b'PE\0\0', 'Invalid PE header')
    machine, sections = struct.unpack_from('<HH', data, pe + 4)
    optional_size = struct.unpack_from('<H', data, pe + 20)[0]
    optional = pe + 24
    require(struct.unpack_from('<H', data, optional)[0] == 0x10b, 'Expected portable PE32 CLR assembly')
    cli_rva, cli_size = struct.unpack_from('<II', data, optional + 96 + 14 * 8)
    require(cli_rva and cli_size >= 72, 'Missing managed CLR header')
    section_table = optional + optional_size
    cli_offset = None
    for n in range(sections):
        offset = section_table + n * 40
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from('<IIII', data, offset + 8)
        if virtual_address <= cli_rva < virtual_address + max(virtual_size, raw_size):
            cli_offset = raw_pointer + cli_rva - virtual_address
            break
    require(cli_offset is not None, 'CLR header is outside the PE sections')
    flags = struct.unpack_from('<I', data, cli_offset + 16)[0]
    require(machine == 0x14c and flags & 1 and not flags & 2 and not flags & 0x20000,
            f'Not an IL-only AnyCPU assembly: machine={machine:#x}, flags={flags:#x}')
    require(b'.NETCoreApp,Version=v6.0' in data, 'Runtime framework must match Stardew Valley 1.6 (.NET 6)')
    return flags


def audit(path):
    print('PACKAGE SHA256 ' + hashlib.sha256(Path(path).read_bytes()).hexdigest())
    with zipfile.ZipFile(path) as archive:
        require(archive.testzip() is None, 'ZIP checksum failed')
        files = {name: archive.read(name) for name in archive.namelist() if not name.endswith('/')}
    folded = {}
    reserved = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}
    for name in files:
        p = PurePosixPath(name)
        require(not p.is_absolute() and '..' not in p.parts and '\\' not in name, f'Unsafe path: {name}')
        require(len(name) < 200, f'Insufficient room for a normal Windows Steam installation path: {name}')
        for part in p.parts:
            require(not re.search(r'[<>:"|?*\x00-\x1f]', part) and not part.endswith((' ', '.')), f'Windows-invalid name: {name}')
            require(part.split('.')[0].upper() not in reserved, f'Windows reserved name: {name}')
        require(name.casefold() not in folded, f'Case-insensitive collision: {name} / {folded.get(name.casefold())}')
        folded[name.casefold()] = name
    require('ArcticPassage/manifest.json' in files and 'ArcticPassage.Runtime/manifest.json' in files,
            'ZIP must contain both installable mod roots')
    pack = json.loads(files['ArcticPassage/manifest.json'])
    runtime = json.loads(files['ArcticPassage.Runtime/manifest.json'])
    require(pack['Version'] == runtime['Version'], 'Mod versions differ')
    dll = 'ArcticPassage.Runtime/' + runtime['EntryDll']
    require([n for n in files if n.lower().endswith(('.dll', '.exe', '.dylib', '.xnb'))] == [dll],
            'Player ZIP contains game/native binaries or an unexpected executable')
    flags = managed_anycpu(files[dll])
    source_root = ROOT / 'Code/ArcticPassage'
    if source_root.exists():
        for source in source_root.glob('*.cs'):
            require(not re.search(r'\b(DllImport|LibraryImport|ComImport)\b', source.read_text()),
                    f'Unreviewed platform-native dependency: {source.name}')

    def exact(name):
        require(name in files, f'Resource missing or case differs on disk: {name}')

    content = json.loads(files['ArcticPassage/content.json'])
    for change in content['Changes']:
        source = change.get('FromFile')
        if source:
            for season in ('spring', 'summer', 'fall', 'winter'):
                exact('ArcticPassage/' + source.replace('{{MapSeason}}', season))
    maps = 0
    for name, data in files.items():
        if name.endswith('.tmx'):
            for image in ET.fromstring(data).findall('.//image'):
                source = image.get('source')
                require(source and not source.startswith(('/', '\\')) and ':' not in source,
                        f'Nonportable map image path in {name}')
                exact(str(PurePosixPath(name).parent / source))
            maps += 1
    for lang in ('default', 'zh'):
        exact(f'ArcticPassage/i18n/{lang}.json')
        exact(f'ArcticPassage.Runtime/i18n/{lang}.json')
    print(f'PASS Windows ZIP: {len(files)} files, {maps} TMX maps, case-safe paths, two mod roots, matching version {pack["Version"]}')
    print(f'PASS CLR portability: IL-only AnyCPU .NET 6, CorFlags={flags:#x}; no bundled game/native executables')
    print('LIMIT: Windows Stardew Valley + SMAPI startup, rendering, audio and saves still require the licensed game; this audit does not launch it.')


if __name__ == '__main__':
    archive = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'dist/ArcticPassage-0.7.10-install.zip'
    audit(archive)
