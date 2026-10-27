/** Render code-authored SVG expressions. Install @resvg/resvg-js as a dev tool;
 * pass its absolute package.json as the first argument when it is not local. */
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';import {createRequire} from 'node:module';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const require=createRequire(process.argv[2]||import.meta.url);const {Resvg}=require('@resvg/resvg-js');
const dir=path.join(root,'art/source/code-portraits');
for(const n of ['nora','levin','amma'])for(let i=0;i<6;i++){
 const base='portrait-'+n+(i?'-'+i:'');
 fs.writeFileSync(path.join(dir,base+'.png'),new Resvg(fs.readFileSync(path.join(dir,base+'.svg')),{fitTo:{mode:'width',value:512}}).render().asPng());
}
console.log('Rendered 18 original 512px expression frames.');
