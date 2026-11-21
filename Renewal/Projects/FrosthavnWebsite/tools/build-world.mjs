import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir,copyFile} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {createHash} from 'node:crypto';
const require=createRequire(import.meta.url);
const root=fileURLToPath(new URL('../',import.meta.url));
let esbuild;try{esbuild=require('esbuild');}catch{esbuild=require('../../FrosthavnPromo/node_modules/esbuild');}
let threeFile;try{threeFile=require.resolve('three');}catch{threeFile=require.resolve('../../FrosthavnPromo/node_modules/three');}
const threeRoot=path.dirname(path.dirname(threeFile));
const components=existsSync(path.join(root,'src/WorldMap.tsx'))?path.join(root,'src'):path.join(root,'src/components/frosthavn');
const target=path.join(root,'public/assets/world');await mkdir(target,{recursive:true});
const result=await esbuild.build({entryPoints:[path.join(root,'tools/world/create-world.mjs')],bundle:true,format:'esm',platform:'browser',target:'es2020',minify:true,write:false,nodePaths:[path.dirname(threeRoot)],legalComments:'inline'});
const output=result.outputFiles[0].contents;
const hash=createHash('sha256').update(output).digest('hex').slice(0,12);
const name='worldBundle.mjs';await writeFile(path.join(components,name),output);
await copyFile(path.join(threeRoot,'LICENSE'),path.join(target,'THREE-LICENSE.txt'));
await writeFile(path.join(components,'worldAsset.ts'),`// Procedural scene extracted from the approved promotional film.\nexport const WORLD_POSTER = '/assets/world/frosthavn-winter-v1.webp';\n`);
console.log(JSON.stringify({name,bytes:output.length,three:'0.186.1',seed:271026}));
