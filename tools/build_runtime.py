"""Build and stage only this project's SMAPI runtime, never game assemblies."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
WORKSPACE=ROOT.parent
PROJECT=ROOT/'Code/ArcticPassage'
env=dict(os.environ, DOTNET_CLI_HOME=str(WORKSPACE/'.development/cli'),
         NUGET_PACKAGES=str(WORKSPACE/'.development/nuget'), DOTNET_CLI_TELEMETRY_OPTOUT='1')
subprocess.run([sys.executable, str(ROOT/'tools/build_wildlife_art.py')], check=True)
subprocess.run([str(WORKSPACE/'.development/dotnet/dotnet'),'build',
                str(PROJECT/'ArcticPassage.Runtime.csproj'),'-c','Release'],env=env,check=True)
assembly=PROJECT/'bin/Release/net6.0/ArcticPassage.Runtime.dll'
if assembly.stat().st_size<8192:raise RuntimeError('Runtime assembly unexpectedly small; check compilation inputs')
stage=WORKSPACE/'.development/RuntimeMod'
stage.mkdir(parents=True,exist_ok=True)
shutil.copy2(assembly,stage/assembly.name)
shutil.copy2(PROJECT/'Runtime/manifest.json',stage/'manifest.json')
shutil.copy2(PROJECT/'Runtime/lighting.json',stage/'lighting.json')
shutil.copytree(PROJECT/'Runtime/i18n',stage/'i18n',dirs_exist_ok=True)
# Small real-scene plates for the route book, rebuilt from the shipped map art.
plates=PROJECT/'Runtime/assets/guide'
plates.mkdir(parents=True,exist_ok=True)
for name in ['Town','Harbor','Icefjord','Tundra','WinterCamp','Airstrip','SledTrail','Glacier']:
 for season in ['spring','summer','fall','winter']:
  scene=f'{name}_snow_scene.png' if name=='Airstrip' else f'{name}_{season}_scene.png'
  with Image.open(ROOT/f'ContentPack/assets/maps/{scene}') as source:
   source.convert('RGB').resize((256,192),Image.Resampling.NEAREST).save(plates/f'{name}_{season}.png')
shutil.copytree(PROJECT/'Runtime/assets',stage/'assets',dirs_exist_ok=True)
print('Staged project-owned runtime:',stage)
