import { cp, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const target = path.join(root, 'lovable-ready/src/components/frosthavn');
await mkdir(target, { recursive: true });
for (const name of ['Frosthavn.tsx', 'Frosthavn.css', 'content.ts', 'Upgrade.css', 'FlightScene.tsx', 'InstallGuide.tsx', 'NorthernAudio.ts', 'NorthernMusic.ts', 'Prologue.css', 'Expedition.tsx', 'ExpeditionContent.ts', 'ScrollJourney.tsx', 'ScrollJourney.css', 'WindowFlight.tsx', 'SeasonVoyage.tsx', 'PlayerExperience.css', 'Trailer.tsx', 'Trailer.css', 'film.ts', 'WorldMap.tsx', 'WorldMap.css', 'worldAsset.ts', 'worldBundle.mjs', 'worldBundle.d.mts']) {
  await cp(path.join(root, 'src', name), path.join(target, name));
}
await cp(path.join(root, 'public'), path.join(root, 'lovable-ready/public'), { recursive: true });
console.log('Lovable page and assets updated. Existing framework and project identity preserved.');
