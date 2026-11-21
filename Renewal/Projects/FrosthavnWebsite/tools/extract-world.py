"""Extract the approved V9 film's procedural town for a standalone web viewer.

The film sources stay unchanged. This deliberately drops ticket/cabin overlays,
frame export and the offline timeline while retaining authored geometry/shaders.
"""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
SOURCE=R.parent/'FrosthavnPromo-v2/src/mg'
out=R/'tools/world'
s=(SOURCE/'scene-v9.mjs').read_text()
body=s[s.index('let seed=271026;'):s.index('// Passenger wing geometry')]
body=body.replace('new T.PlaneGeometry(640,650,500,300)','new T.PlaneGeometry(640,650,190,140)')
light=s[s.index('const seasonal='):s.index('function roundedRect')]
header='''// Derived from FrosthavnPromo-v2 scene-v9.mjs, seed 271026.
import * as T from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {extendTown} from './town.mjs';
import {AIRPORT,yearState} from './motion.mjs';

export async function createWorld(host,options={}){
 const compact=matchMedia('(max-width:760px)').matches;
 const renderer=new T.WebGLRenderer({antialias:!compact,alpha:false,powerPreference:'default',preserveDrawingBuffer:false});
 renderer.setPixelRatio(Math.min(devicePixelRatio||1,compact?1.2:1.45));
 renderer.shadowMap.enabled=!compact;renderer.shadowMap.type=T.PCFSoftShadowMap;
 renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;
 renderer.toneMappingExposure=1.02;
 const canvas=renderer.domElement;canvas.setAttribute('role','img');canvas.setAttribute('aria-label',options.label||'Frosthavn three-dimensional bay');canvas.tabIndex=0;host.append(canvas);
 const scene=new T.Scene();scene.fog=new T.FogExp2(0xc1d4d9,.0012);
 const camera=new T.PerspectiveCamera(43,1,.3,1400);scene.add(camera);
'''
# Reuse deterministic model-space seasonal motion, without flight/ticket code.
motion=(SOURCE/'motion-v6.mjs').read_text()
(out/'motion.mjs').write_text(motion)
town=(SOURCE/'town-v6.mjs').read_text()
# Winter camp blocks are static shapes sharing five seasonal materials. Merge
# each material once; keep material opacity and igloo visibility from the film.
town=town.replace(' const snowBlocks=',' const snowBlocks=')
town=town.replace(' const sledMats=seasonalMaterials(sled),kayakMats=seasonalMaterials(summerBoats);','''
 // Merge static camp geometry and instance tundra plants, preserving their
 // seasonal transforms without hundreds of individual draw calls.
 A.optimiseStatic(igloos);A.optimiseStatic(sled);A.optimiseStatic(summerBoats);A.optimiseStatic(anemometer);
 const plantBatches=[];
 for(const [material,objects] of [...new Set(plants.children.map(o=>o.material))].map(m=>[m,plants.children.filter(o=>o.material===m)])){
  const batch=new T.InstancedMesh(objects[0].geometry,material,objects.length);
  batch.castShadow=false;batch.receiveShadow=true;
  objects.forEach((o,i)=>{o.updateMatrix();batch.setMatrixAt(i,o.matrix);plants.remove(o);});
  plants.add(batch);plantBatches.push({batch,objects});
 }
 let previousSnow=-1;
 const sledMats=seasonalMaterials(sled),kayakMats=seasonalMaterials(summerBoats);''')
town=town.replace('for(const o of shrubs)o.scale.y=o.userData.baseY*(.22+.78*(1-sn));','''if(Math.abs(previousSnow-sn)>.006){
   previousSnow=sn;
   for(const o of shrubs)o.scale.y=o.userData.baseY*(.22+.78*(1-sn));
   for(const {batch,objects}of plantBatches){objects.forEach((o,i)=>{o.updateMatrix();batch.setMatrixAt(i,o.matrix);});batch.instanceMatrix.needsUpdate=true;}
  }''')
# Flag normal recomputation is unnecessary for a tiny, gently displaced cloth.
town=town.replace('a.needsUpdate=true;flag.geometry.computeVertexNormals()','a.needsUpdate=true')
(out/'town.mjs').write_text(town)
# Static merge helper uses the same geometry utilities as the approved film.
helper='''
function optimiseStatic(group){
 const byMaterial=new Map(),objects=[];
 group.updateMatrixWorld(true);const inverse=group.matrixWorld.clone().invert();group.traverse(o=>{if(o.isMesh)objects.push(o);});
 for(const o of objects){
  const g=o.geometry.index?o.geometry.toNonIndexed():o.geometry.clone();g.applyMatrix4(new T.Matrix4().multiplyMatrices(inverse,o.matrixWorld));
  for(const a of Object.keys(g.attributes))if(!['position','normal'].includes(a))g.deleteAttribute(a);
  if(!byMaterial.has(o.material))byMaterial.set(o.material,[]);byMaterial.get(o.material).push(g);
 }
 group.clear();
 for(const [m,geometries]of byMaterial){const g=mergeGeometries(geometries,false);if(g){const o=new T.Mesh(g,m);o.castShadow=true;o.receiveShadow=true;group.add(o);}for(const old of geometries)old.dispose();}
}
'''
body=helper+body+'\nfor(const b of boats)optimiseStatic(b.g);optimiseStatic(parked);optimiseStatic(snowTrim);\n'
body=body.replace('rand,houses});const igloos','rand,houses,optimiseStatic});const igloos')
body=body.replace('sun.shadow.mapSize.set(2048,2048)','sun.shadow.mapSize.set(compact?512:1024,compact?512:1024)')
# The complete application lifecycle and controls are authored separately.
tail=(out/'viewer-tail.txt').read_text()
(out/'create-world.mjs').write_text(header+body+light+tail+'\n}\n')
print('Extracted V9 town, geometry seed 271026; film unchanged.')
