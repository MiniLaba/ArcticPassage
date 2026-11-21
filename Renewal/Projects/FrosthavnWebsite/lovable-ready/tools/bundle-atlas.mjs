import {readFileSync, writeFileSync} from 'node:fs';

const url = new URL('../src/components/atlas/viewer.mjs',import.meta.url);
const original = readFileSync(url,'utf8');
const vendor = original.split(/\/\* Atlas application \*\/|async function zv\(i,e,t\)/u)[0].trimEnd();
const input = readFileSync(new URL('./atlas-viewer.mjs',import.meta.url),'utf8');
const app = input.replace(/^import .*\n/gm,'');
const aliases = `const THREE = {WebGLRenderer:yo, Scene:Xs, Color:Re, PerspectiveCamera:vt, HemisphereLight:ar,
 DirectionalLight:Ii, PointLight:cr, SpotLight:lr, BufferGeometry:Ft, Float32BufferAttribute:kt, ShaderMaterial:tn, Points:Qs, Vector3:N, PCFShadowMap:Pi, MathUtils:Ui};
const OrbitControls=bo, GLTFLoader=To;`;
writeFileSync(url,vendor+'\n/* Atlas application */\nimport {navigation} from "./walk.mjs";\n'+aliases+'\n'+app);
