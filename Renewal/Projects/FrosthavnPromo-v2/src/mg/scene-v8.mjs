import {extendTown} from './town-v6.mjs';
import {AIRPORT,flightState,yearState} from './motion-v6.mjs';
import {createTicketShot} from './ticket-v5.mjs';
import * as T from 'three';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
// Deterministic, authored geometry. No photographs, game screenshots or generated-image textures.
const timeline=await (await fetch('/public/mg-v6-timing.json')).json();
const W=1920,H=1080,canvas=document.getElementById('film'),ctx=canvas.getContext('2d',{alpha:false});
const renderer=new T.WebGLRenderer({canvas:document.getElementById('stage'),antialias:true,preserveDrawingBuffer:true,alpha:false,powerPreference:'high-performance'});
renderer.setPixelRatio(1);renderer.setSize(W,H,false);renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.1;
const scene=new T.Scene();scene.fog=new T.FogExp2(0xc1d4d9,.0028);
const camera=new T.PerspectiveCamera(42,W/H,.1,1400);scene.add(camera);
const composer=new EffectComposer(renderer);composer.addPass(new RenderPass(scene,camera));const bloom=new UnrealBloomPass(new T.Vector2(W,H),.19,.35,.72);composer.addPass(bloom);composer.addPass(new OutputPass());let rw=W,rh=H;function renderWorld(w,h){if(rw!==w||rh!==h){renderer.setSize(w,h,false);composer.setSize(w,h);rw=w;rh=h}composer.render()}
let seed=271026;const rand=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296};
const clamp=x=>Math.max(0,Math.min(1,x));const smooth=(a,b,x)=>{let q=clamp((x-a)/(b-a));return q*q*(3-2*q)};
const mix=(a,b,t)=>a+(b-a)*t;
const C=x=>new T.Color(x);
const materials={},statics=new Map(),animated=[];
function mat(name,color,rough=.82,metal=0){const m=new T.MeshStandardMaterial({color,roughness:rough,metalness:metal});materials[name]=m;return m}
const snow=mat('seasonal snow',0xe8edf0),rock=mat('gneiss',0x667982),wood=mat('weathered timber',0x6d6359),darkwood=mat('dark timber',0x434e52),ivory=mat('painted frames',0xedeadd),roof=mat('snow roof',0xe5e9e8),steel=mat('galvanised metal',0x859799,.48,.25),navy=mat('deep blue paint',0x214453),red=mat('ochre red',0xa65749),gold=mat('ochre yellow',0xb69a62),blue=mat('fjord blue',0x496d7b),green=mat('sage wood',0x688077),black=mat('window glass',0x203a47,.32,.15);
const paint=[red,blue,gold,green,navy];
roof.side=T.DoubleSide;
const windowMats=Array.from({length:8},(_,i)=>{const m=mat('window '+i,0xdac795,.5);m.emissive=C(0xffa34c);m.emissiveIntensity=0;return m});
function mesh(geo,m,pos=[0,0,0],rot=[0,0,0],s=[1,1,1],parent=null,merge=true){const o=new T.Mesh(geo,m);o.position.set(...pos);o.rotation.set(...rot);o.scale.set(...s);o.castShadow=true;o.receiveShadow=true;if(parent){parent.add(o)}else if(merge){o.updateMatrix();const g=geo.clone().applyMatrix4(o.matrix);if(!statics.has(m))statics.set(m,[]);statics.get(m).push(g)}else scene.add(o);return o}
const boxGeo=new T.BoxGeometry(1,1,1),sphereGeo=new T.SphereGeometry(1,16,10),cylGeo=new T.CylinderGeometry(1,1,1,10),rockGeo=new T.DodecahedronGeometry(1,0);
function box(m,x,y,z,w,h,d,parent=null,rot=0){return mesh(boxGeo,m,[x,y,z],[0,rot,0],[w,h,d],parent)}
function cylinder(m,x,y,z,r,h,parent=null){return mesh(cylGeo,m,[x,y,z],[0,0,0],[r,h,r],parent)}
function rod(m,a,b,r=.035,parent=null){const av=new T.Vector3(...a),bv=new T.Vector3(...b),d=bv.clone().sub(av);const q=new T.Quaternion().setFromUnitVectors(new T.Vector3(0,1,0),d.clone().normalize());const g=new T.CylinderGeometry(r,r,d.length(),6);g.applyQuaternion(q);const p=av.add(bv).multiplyScalar(.5);return mesh(g,m,p.toArray(),[0,0,0],[1,1,1],parent)}
function polygeo(v,inds){const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(v.flat(),3));g.setIndex(inds);g.computeVertexNormals();return g}
function coast(x){return 8+10*Math.sin(x*.038)+5*Math.sin(x*.083)-19*Math.exp(-Math.pow((x-18)/24,2))+48*Math.exp(-Math.pow((x+190)/40,4))}
function height(x,z){const d=coast(x)-z;if(d<0)return -1.2-Math.min(5,-d*.15);let base=.6+Math.min(5,d*.075)+2.8*Math.exp(-((x+7)**2+(z+24)**2)/800)+.55*Math.sin(x*.17)*Math.sin(z*.14)*smooth(0,12,d);let ridge=smooth(55,110,-z)*(8+8*Math.sin(x*.028+.6)**2+5*Math.sin(x*.057+1.4)**2)*Math.exp(-Math.pow((z+145)/100,2));let back=smooth(150,220,-z)*(9+10*Math.sin(x*.019+1)**2);ridge=12*Math.exp(-Math.pow((z+135+15*Math.sin(x*.026))/38,2))*(.5+.5*Math.abs(Math.sin(x*.033+.9)))+8*Math.exp(-Math.pow((z+210+12*Math.sin(x*.021+1))/45,2));let all=base+ridge+back+smooth(80,150,-z)*2.8*Math.sin(x*.13+z*.09)*Math.sin(z*.06);let runway=(1-smooth(8,24,Math.abs(x+190)))*smooth(-204,-185,z)*(1-smooth(35,47,z));let apron=(1-smooth(14,29,Math.abs(x+162)))*smooth(-160,-140,z)*(1-smooth(-8,12,z));return mix(all,4,Math.max(runway,apron))}
const groundGeo=new T.PlaneGeometry(640,650,500,300);groundGeo.rotateX(-Math.PI/2);const pa=groundGeo.attributes.position,colors=[];
for(let i=0;i<pa.count;i++){const x=pa.getX(i),z=pa.getZ(i)-240;pa.setXYZ(i,x,height(x,z),z);let k=.88+.06*Math.sin(x*.61+z*.2)*Math.sin(z*.51)+.06*rand();if(z<-80)k*=.78+.19*Math.sin(x*.12+z*.05)**2;colors.push(k,k,k)}groundGeo.setAttribute('color',new T.Float32BufferAttribute(colors,3));groundGeo.computeVertexNormals();
const groundMat=mat('tundra and snow',0xe8edf0);groundMat.vertexColors=true;mesh(groundGeo,groundMat,[0,0,0],[0,0,0],[1,1,1],null,false);
// Melt fronts follow relief and wind-scoured patches; spring is a state of its own.
const landU={snow:{value:1},autumn:{value:0}};
groundMat.onBeforeCompile=sh=>{sh.uniforms.seasonSnow=landU.snow;sh.uniforms.seasonAutumn=landU.autumn;
 sh.vertexShader='varying vec3 landPosition;\n'+sh.vertexShader;
 sh.vertexShader=sh.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n landPosition=position;');
 sh.fragmentShader='varying vec3 landPosition;uniform float seasonSnow,seasonAutumn;\n'+sh.fragmentShader;
 sh.fragmentShader=sh.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
 float meltPatch=.47+.16*sin(landPosition.x*.19+sin(landPosition.z*.13))+.14*cos(landPosition.z*.25+landPosition.x*.07)+.10*sin(landPosition.x*.51-landPosition.z*.31);
 float snowCover=smoothstep(meltPatch-.10,meltPatch+.10,seasonSnow+max(0.,landPosition.y-14.)*.014);
 vec3 tundra=mix(vec3(.25,.34,.27),vec3(.46,.27,.13),seasonAutumn);
 vec3 terrainNormal=normalize(cross(dFdx(landPosition),dFdy(landPosition)));float slope=1.-abs(terrainNormal.y);
 float grain=.5+.5*sin(landPosition.y*4.2+landPosition.x*.35+landPosition.z*.13+sin(landPosition.x*.17));
 vec3 stone=mix(vec3(.24,.29,.31),vec3(.43,.47,.47),grain);float exposed=smoothstep(.09,.32,slope)*smoothstep(7.,17.,landPosition.y);
 tundra=mix(tundra,stone,exposed);snowCover*=1.-exposed*.72;
 float wet=exp(-abs(landPosition.y-1.5)*.6)*.18;
 diffuseColor.rgb*=mix(tundra*(1.-wet),vec3(.86,.91,.92),snowCover);`);
};
roof.onBeforeCompile=sh=>{sh.uniforms.roofSnow=landU.snow;sh.vertexShader='varying vec3 roofP;\n'+sh.vertexShader;sh.vertexShader=sh.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n roofP=position;');sh.fragmentShader='varying vec3 roofP;uniform float roofSnow;\n'+sh.fragmentShader;sh.fragmentShader=sh.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
 float roofPatch=.42+.13*sin(roofP.x*.65+roofP.z*.41)+.12*cos(roofP.z*.77)+.08*sin(roofP.y*3.);float cover=smoothstep(roofPatch-.18,roofPatch+.18,roofSnow);float corrugation=.94+.06*sin(roofP.z*45.);diffuseColor.rgb*=mix(vec3(.21,.28,.30)*corrugation,vec3(.86,.91,.92),cover);`);};
// A shader-driven sea with moving capillary waves, long sun reflection and warm harbour glints.
const seaU={time:{value:0},night:{value:0},sunDir:{value:new T.Vector3(-.4,.3,-.7)},seaColor:{value:C(0x1e5369)}};
const seaMat=new T.ShaderMaterial({uniforms:seaU,vertexShader:`varying vec3 p;varying vec3 wp;uniform float time;void main(){p=position;vec3 v=position;v.y+=0.055*sin(v.x*.55+time*.7)+0.04*sin(v.z*.72+time*.5);wp=(modelMatrix*vec4(v,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*vec4(wp,1.);}`,fragmentShader:`varying vec3 wp;uniform float time,night;uniform vec3 sunDir,seaColor;void main(){float a=wp.x*.63+wp.z*.31+time*.65+sin(wp.z*.15),b=wp.z*.89-wp.x*.21+time*.48+sin(wp.x*.12);vec3 n=normalize(vec3(-.016*cos(a),1.,-.025*cos(b)));float dist=length(cameraPosition-wp);vec3 V=normalize(cameraPosition-wp);float fr=pow(1.-max(0.,dot(n,V)),4.);float spec=pow(max(0.,dot(reflect(-normalize(sunDir),n),V)),90.);vec3 base=mix(seaColor,vec3(.43,.59,.63),fr*.65)*(1.-night*.76);float rip=pow(max(0.,sin(a*.7+b*.3)),22.)*.006*(1.-smoothstep(35.,170.,dist));vec3 col=base+vec3(.9,.66,.34)*spec*.6*(1.-night)+rip*(1.-night*.65);float lane=exp(-pow((wp.x-14.)/2.8,2.))*exp(-abs(wp.z-8.)*.055)*pow(max(0.,sin(b*1.3)),14.);col+=vec3(.58,.25,.055)*lane*night*.45;float coast=8.+10.*sin(wp.x*.038)+5.*sin(wp.x*.083)-19.*exp(-pow((wp.x-18.)/24.,2.))+48.*exp(-pow((wp.x+190.)/40.,4.));float foam=exp(-abs(wp.z-coast)*1.8)*(.65+.35*sin(a+b));col+=vec3(.11,.15,.15)*foam*(1.-night*.7);col=mix(col,mix(vec3(.54,.65,.69),vec3(.07,.12,.20),night),smoothstep(170.,500.,dist));gl_FragColor=vec4(col,1.);#include <tonemapping_fragment>\n#include <colorspace_fragment>}`});
// GLSL preprocessor directives must begin at a new line.
seaMat.fragmentShader=seaMat.fragmentShader.replace(';#include',';\n#include');const seaGeo=new T.PlaneGeometry(1200,1200,100,100);seaGeo.rotateX(-Math.PI/2);mesh(seaGeo,seaMat,[0,-.03,0],[0,0,0],[1,1,1],null,false).castShadow=false;
const skyU={night:{value:0},warm:{value:0},time:{value:0}};
const skyMat=new T.ShaderMaterial({side:T.BackSide,depthWrite:false,uniforms:skyU,vertexShader:`varying vec3 dir;void main(){dir=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,fragmentShader:`varying vec3 dir;uniform float night,warm,time;void main(){vec3 n=normalize(dir);float h=smoothstep(-.05,.7,n.y);vec3 day=mix(vec3(.46,.61,.69),vec3(.085,.25,.40),h);day=mix(day,mix(vec3(.74,.57,.38),vec3(.19,.36,.50),h),warm*.55);vec3 dark=mix(vec3(.16,.23,.34),vec3(.018,.045,.10),h);gl_FragColor=vec4(mix(day,dark,night),1.);}`});
mesh(new T.SphereGeometry(700,32,24),skyMat,[0,0,0],[0,0,0],[1,1,1],null,false).castShadow=false;
const hemi=new T.HemisphereLight(0xd6e8f0,0x65716e,2.1);scene.add(hemi);const sun=new T.DirectionalLight(0xffe4bc,3.2);sun.position.set(-60,65,10);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-115,right:115,top:115,bottom:-115,near:1,far:400});sun.shadow.bias=-.00025;sun.shadow.normalBias=.12;sun.shadow.radius=3;sun.target.position.set(0,0,-20);scene.add(sun,sun.target);
const sunBall=new T.Mesh(new T.SphereGeometry(5,24,16),new T.MeshBasicMaterial({color:0xffdf9e}));scene.add(sunBall);
// Mountains: layered facets with code-generated snow caps and atmospheric depth.
for(let i=0;i<190;i++){const x=rand()*205-102,z=rand()*135-95;if(coast(x)-z<0)continue;if(Math.abs(x+190)<26&&z>-200&&z<45)continue;const s=.35+rand()*1.15,y=height(x,z);mesh(rockGeo,rock,[x,y+.12,z],[rand(),rand()*6,rand()],[s,s*.45,s*.7]);if(rand()<.7)mesh(rockGeo,snow,[x,y+s*.18,z],[0,rand()*6,0],[s*.94,s*.2,s*.66]);}
const shoreVerts=[],shoreIdx=[];for(let i=0;i<=800;i++){const x=-200+i*.5,z=coast(x);shoreVerts.push([x,-.35,z+.10],[x,.62,z],[x,height(x,z-3.2)+.08,z-3.2]);if(i<800){const j=i*3;shoreIdx.push(j,j+3,j+4,j,j+4,j+1,j+1,j+4,j+5,j+1,j+5,j+2)}}mesh(polygeo(shoreVerts,shoreIdx),snow);
// Paths are actual ribbons on the terrain, with small edging stones.
const pathMat=mat('packed snow paths',0xd3d5cb);
function path(points,width=1.5){const c=new T.CatmullRomCurve3(points.map(([x,z])=>new T.Vector3(x,height(x,z)+.22,z)));const pts=c.getPoints(160),verts=[],idx=[];for(let i=0;i<pts.length;i++){const p=pts[i],dir=c.getTangent(i/(pts.length-1));const side=new T.Vector3(-dir.z,0,dir.x).normalize().multiplyScalar(width/2);verts.push(p.clone().add(side).toArray(),p.clone().sub(side).toArray());if(i<pts.length-1){let j=i*2;idx.push(j,j+1,j+2,j+1,j+3,j+2)}}mesh(polygeo(verts,idx),pathMat);}
path([[-57,-18],[-37,-13],[-20,-15],[-5,-17],[12,-15],[32,-19],[48,-31]],2.2);path([[-26,-35],[-19,-25],[-12,-10],[0,-3],[12,0],[25,-2]],1.8);path([[0,-3],[-3,8],[-9,17]],1.7);path([[12,-15],[23,-33],[36,-47]],1.5);
// Houses share Greenlandic weatherboard, steep roofs, framed windows and raised foundations.
const houses=[];
function house(x,z,w,d,h,paintIndex,rot=0,kind='home'){
 w*=1.20;d*=1.18;h*=1.12;const y=height(x,z),g=new T.Group();g.position.set(x,y,z);g.rotation.y=rot;const color=paint[paintIndex%paint.length];
 const add=(m,X,Y,Z,W,H,D)=>box(m,X,Y,Z,W,H,D,g);
 add(rock,0,.28,0,w+.35,.55,d+.35);add(color,0,h/2+.45,0,w,h,d);
 const peak=h+.45+w*.38;const eave=h+.45;
 mesh(polygeo([[-w/2,eave,d/2],[w/2,eave,d/2],[0,peak,d/2],[-w/2,eave,-d/2],[0,peak,-d/2],[w/2,eave,-d/2]],[0,1,2,3,4,5]),color,[0,0,0],[0,0,0],[1,1,1],g);
 const over=.3;mesh(polygeo([[-w/2-over,eave,d/2+over],[0,peak+.06,d/2+over],[0,peak+.06,-d/2-over],[-w/2-over,eave,-d/2-over],[0,peak+.06,d/2+over],[w/2+over,eave,d/2+over],[w/2+over,eave,-d/2-over],[0,peak+.06,-d/2-over]],[0,1,2,0,2,3,4,5,6,4,6,7]),roof,[0,0,0],[0,0,0],[1,1,1],g);
 for(let yy=.7;yy<h+.3;yy+=.25){add(color,-.01,yy,d/2+.018,w,.035,.025);add(darkwood,-w/2-.01,yy,0,.022,.018,d);}
 for(const xx of [-w/2+.08,w/2-.08]){add(ivory,xx,h/2+.48,d/2+.05,.10,h,.10);add(ivory,xx,h/2+.48,-d/2-.05,.10,h,.10)}
 for(const xx of [-w*.29,w*.29])for(const zz of [-d/2-.045,d/2+.045]){
  add(ivory,xx,h*.58+.45,zz,w*.23,h*.37,.11);add(windowMats[houses.length%8],xx,h*.58+.45,zz+(zz>0?.07:-.07),w*.18,h*.29,.035);add(ivory,xx,h*.58+.45,zz+(zz>0?.10:-.10),.045,h*.32,.035);add(ivory,xx,h*.58+.45,zz+(zz>0?.10:-.10),w*.19,.045,.035);
 }
 for(const side of [-1,1])for(const zz of [-d*.26,d*.26]){add(ivory,side*(w/2+.05),h*.58+.45,zz,.11,h*.37,w*.23);add(windowMats[houses.length%8],side*(w/2+.12),h*.58+.45,zz,.035,h*.29,w*.18);add(ivory,side*(w/2+.15),h*.58+.45,zz,.035,.045,w*.19);add(ivory,side*(w/2+.15),h*.58+.45,zz,.035,h*.32,.045)}
 for(const side of [-1,1]){add(ivory,side*(w/2+.2),eave-.035,0,.14,.13,d+.6);rod(ivory,[-w/2-.28,eave,d/2+.32],[0,peak+.05,d/2+.32],.055,g);rod(ivory,[0,peak+.05,d/2+.32],[w/2+.28,eave,d/2+.32],.055,g)}
 add(ivory,0,1.04,d/2+.05,.92,1.55,.13);add(navy,0,.99,d/2+.14,.72,1.39,.07);add(steel,.23,1.03,d/2+.19,.055,.055,.04);
 for(let j=0;j<3;j++)add(wood,0,.40-j*.10,d/2+.4+j*.22,1.15,.16,.4);
 add(darkwood,w*.28,peak-.45,-d*.17,.34,1.5,.35);add(steel,w*.28,peak+.33,-d*.17,.45,.1,.46);
 if(kind==='inn'){
  add(wood,0,.24,d/2+1.05,w+1,.22,1.8);
  for(const xx of [-w/2-.2,w/2+.2]){add(ivory,xx,1.0,d/2+1.65,.1,1.5,.1);rod(ivory,[xx,.8,d/2+.3],[xx,.8,d/2+1.65],.045,g)}
  add(navy,0,2.18,d/2+.12,2.3,.42,.14);
 }
 g.updateMatrixWorld(true);g.traverse(o=>{if(o.isMesh){const gg=o.geometry.clone().applyMatrix4(o.matrixWorld);if(!statics.has(o.material))statics.set(o.material,[]);statics.get(o.material).push(gg)}});
 houses.push({x,z,w,d,y,h,kind,rot});return houses.at(-1);
}
const inn=house(-8,-19,6.6,5.8,3.8,1,0,'inn');
const plots=[[-29,-25,0],[-25,-9,2],[-18,-40,0],[5,-29,0],[12,-12,2],[23,-24,1],[34,-31,3],[42,-44,0],[3,-46,3],[-39,-36,1],[-35,-51,0],[20,-48,2],[-15,-54,2],[33,-62,0],[-2,-9,0],[29,-10,1],[43,-18,2],[-44,-6,3]];
for(const [x,z,c]of plots)house(x,z,3.8+rand()*1.4,3.5+rand()*1.4,2.4+rand()*.8,c,(rand()-.5)*.22);
// Docks, pilings, nets, fish racks and working boats.
function pier(x,z,w,d,y=1.1){box(wood,x,y,z,w,.35,d);for(let zz=z-d/2;zz<z+d/2;zz+=.35)box(darkwood,x,y+.185,zz,w,.025,.035);for(let zz=z-d/2;zz<=z+d/2;zz+=3){for(let xx of [x-w/2,x+w/2]){cylinder(darkwood,xx,.75,zz,.16,2.1);cylinder(ivory,xx,1.85,zz,.18,.08)}}}
pier(9,3,25,3);pier(18,11,2.4,16);pier(1,10,2.4,13);pier(22,19,12,2.4);
for(let i=0;i<8;i++){const x=-1+i*2.2;box(wood,x,1.7,2,1,.9,.9);for(let yy=1.4;yy<2.2;yy+=.2)box(darkwood,x,yy,2.46,1.03,.035,.03)}
for(let x of [-4,-1,2]){rod(darkwood,[x,1.3,-.3],[x,3.8,-.3],.07);rod(darkwood,[x,3.6,-.3],[x+2.2,3.6,-.3],.06);for(let i=0;i<5;i++)mesh(new T.ConeGeometry(.07,.65,5),gold,[x+.25+i*.35,3.15,-.3],[0,0,.05]);}
const boats=[];
function boat(x,z,s,rot){const g=new T.Group();g.position.set(x,.3,z);g.rotation.y=rot;g.scale.setScalar(s);scene.add(g);
 const hull=polygeo([[-1,0,2.9],[1,0,2.9],[1.2,0,-1.9],[0,0,-3],[-1.2,0,-1.9],[-.65,-.6,2.5],[.65,-.6,2.5],[.8,-.6,-1.6],[0,-.6,-2.5],[-.8,-.6,-1.6]],[0,1,6,0,6,5,1,2,7,1,7,6,2,3,8,2,8,7,3,4,9,3,9,8,4,0,5,4,5,9,0,4,3,0,3,2,0,2,1]);mesh(hull,red,[0,0,0],[0,0,0],[1,1,1],g);
 box(ivory,0,.16,0,1.8,.16,4.3,g);box(ivory,0,.85,.4,1.4,1.3,1.6,g);box(navy,0,1.0,-.42,1.13,.54,.03,g);box(navy,-.72,1,.4,.03,.55,1.25,g);box(navy,.72,1,.4,.03,.55,1.25,g);box(navy,0,1.58,.4,1.7,.16,1.9,g);rod(steel,[0,1.6,.45],[0,4.7,.45],.04,g);rod(steel,[-1.2,3.7,.45],[1.2,3.7,.45],.035,g);rod(ivory,[-.8,.4,-1.8],[-.8,1,-1.8],.03,g);rod(ivory,[.8,.4,-1.8],[.8,1,-1.8],.03,g);rod(ivory,[-.8,1,-1.8],[.8,1,-1.8],.03,g);boats.push({g,x,z,rot,phase:rand()*6});}
boat(5,11,1.1,.1);boat(22,13,.95,-.2);boat(29,22,1.2,.8);boat(-15,38,.75,-.7);
// A separate airport peninsula, with an actual buffer and road to the settlement.
const runY=AIRPORT.y;box(pathMat,AIRPORT.x,runY,AIRPORT.z,AIRPORT.width,.12,AIRPORT.length);
box(snow,AIRPORT.x,runY+.065,AIRPORT.z,10.7,.015,AIRPORT.length-3);
for(let z=-177;z<29;z+=12)box(ivory,AIRPORT.x,runY+.09,z,.28,.025,5);
for(const z of [26,-177])for(let i=0;i<6;i++)box(ivory,AIRPORT.x-4.5+i*1.8,runY+.09,z,.6,.025,5);
const runwayBulbs=[];for(let z=-182;z<=32;z+=12){for(let x of [AIRPORT.x-7.5,AIRPORT.x+7.5]){cylinder(steel,x,runY+.32,z,.035,.6);const b=mesh(sphereGeo,windowMats[4],[x,runY+.68,z],[0,0,0],[.10,.10,.10],null,false);runwayBulbs.push(b)}}
const terminal=house(-157,-36,7.5,5.8,2.6,0,0,'airport-terminal');const hangar=house(-159,-105,8.5,10,3.6,1,0,'airport-hangar');
box(pathMat,-166,runY+.02,-63,28,.08,34);
rod(steel,[-172,runY,-14],[-172,runY+5.3,-14],.055);
const windsock=new T.Group();windsock.position.set(-172,runY+5.2,-14);scene.add(windsock);for(let i=0;i<6;i++)mesh(new T.CylinderGeometry(.22-i*.018,.24-i*.018,.34,12),i%2?ivory:red,[i*.32,0,0],[0,0,Math.PI/2],[1,1,1],windsock);
path([[-150,-33],[-126,-24],[-108,-34],[-87,-25],[-67,-23],[-57,-18]],2.5);
path([[30,-34],[48,-57],[61,-72],[69,-78]],1.4);path([[-19,-37],[-25,-53],[-34,-64]],1.5);path([[15,-65],[23,-96],[24,-121]],1.4);
// A parked twin-prop gives the apron purpose and establishes aircraft scale.
const parked=new T.Group();parked.position.set(-161,runY+.75,-65);parked.rotation.y=.12;scene.add(parked);
mesh(new T.CylinderGeometry(.45,.65,5.7,16),ivory,[0,.65,0],[Math.PI/2,0,0],[1,1,1],parked);mesh(new T.SphereGeometry(.55,16,10),ivory,[0,.65,2.85],[0,0,0],[1,1,1.25],parked);box(red,0,1.02,-.2,8.8,.12,1.15,parked);box(red,0,1.13,-2.3,2.6,.1,.7,parked);box(red,0,1.57,-2.25,.10,1.35,.8,parked);for(const x of [-2.2,2.2]){mesh(new T.CylinderGeometry(.27,.30,1.3,12),steel,[x,.93,.6],[Math.PI/2,0,0],[1,1,1],parked);box(navy,x,.93,1.29,.10,1.6,.045,parked);box(navy,x,.93,1.29,1.6,.10,.045,parked)}
const features=extendTown({T,scene,mesh,box,cylinder,rod,polygeo,house,height,coast,mat,rock,wood,darkwood,ivory,navy,red,gold,steel,roof,snow,rand,houses});const igloos=features.igloos;
// Lamps use emissive glass plus subtle projected pools; no billboard halo over the whole scene.
function radialTexture(){let c=document.createElement('canvas');c.width=c.height=128;let a=c.getContext('2d'),g=a.createRadialGradient(64,64,0,64,64,64);g.addColorStop(0,'rgba(255,204,119,.65)');g.addColorStop(.3,'rgba(255,181,90,.24)');g.addColorStop(1,'rgba(255,166,70,0)');a.fillStyle=g;a.fillRect(0,0,128,128);return new T.CanvasTexture(c)}
const poolMat=new T.MeshBasicMaterial({map:radialTexture(),transparent:true,opacity:0,depthWrite:false,blending:T.AdditiveBlending});const lampBulbs=[];
for(const [x,z]of [[-28,-12],[-17,-16],[-4,-13],[10,-7],[22,-18],[35,-26],[16,2],[18,12],[26,19],[-7,9],[-47,-12]]){let y=z>0?1.3:height(x,z);rod(darkwood,[x,y,z],[x,y+3.6,z],.045);rod(darkwood,[x,y+3.5,z],[x+.6,y+3.5,z],.045);box(navy,x+.6,y+3.4,z,.35,.12,.35);box(windowMats[(lampBulbs.length+1)%8],x+.6,y+3.15,z,.23,.4,.23);box(navy,x+.6,y+2.92,z,.32,.08,.32);const pool=mesh(new T.PlaneGeometry(6,6),poolMat,[x+.6,y+.16,z],[-Math.PI/2,0,0],[1,1,1],null,false);pool.castShadow=false;lampBulbs.push(pool)}
const warmLights=[];for(const [x,z] of [[-8,-15.5],[12,-9],[23,-20],[16,2]]){const l=new T.PointLight(0xffb765,0,16,2);l.position.set(x,height(x,z)+2.1,z);scene.add(l);warmLights.push(l)}
// Lighthouse anchors the far point of the shore.
const lx=61,lz=coast(61)-2,ly=height(lx,lz);cylinder(ivory,lx,ly+2.5,lz,.85,5);cylinder(red,lx,ly+2,lz,.87,.7);cylinder(navy,lx,ly+5.15,lz,1.1,.22);cylinder(windowMats[0],lx,ly+5.65,lz,.65,.75);mesh(new T.ConeGeometry(1.1,.7,8),navy,[lx,ly+6.35,lz]);
// Icebergs are asymmetric closed geometry, not image planes.
const iceGroups=[];
for(let k=0;k<14;k++){const x=-95+rand()*200,z=30+rand()*110,s=1.4+rand()*4;const g=new T.Group();g.position.set(x,0,z);scene.add(g);mesh(rockGeo,mat('ice '+k,k%2?0xbadce0:0xdbe8e8),[0,0,0],[rand()*.4,rand()*6,rand()*.3],[s,s*.7,s*.6],g);mesh(rockGeo,blue,[0,-.65,0],[0,rand()*6,0],[s*1.08,.4,s*.7],g);iceGroups.push({g,x,z,phase:rand()*6})}
// Broken shore-fast ice: actual low prisms, with an open harbour approach.
const shoreIce=new T.Group();scene.add(shoreIce);const shoreIceMat=new T.MeshStandardMaterial({color:0xb5d5dc,roughness:.76,transparent:true,opacity:1});
for(let i=0;i<70;i++){let x=-190+rand()*360;if(x>-66&&x<75)continue;let z=coast(x)+1.5+rand()*10,r=1.4+rand()*3.6;const g=new T.CylinderGeometry(r,r*.9,.19,6);const p=g.attributes.position;for(let j=0;j<p.count;j++){p.setX(j,p.getX(j)*(1+.12*Math.sin(p.getZ(j)*2.3+i)));}mesh(g,shoreIceMat,[x,.02,z],[0,rand()*6,0],[1,1,.62],shoreIce);}
// Light cloud banks: deterministic soft alpha texture, placed in actual 3D depth.
function cloudTexture(){let c=document.createElement('canvas');c.width=512;c.height=256;let a=c.getContext('2d');for(let i=0;i<45;i++){let x=70+rand()*370,y=90+rand()*70,r=35+rand()*50;let g=a.createRadialGradient(x,y,0,x,y,r);g.addColorStop(0,'rgba(240,245,243,.11)');g.addColorStop(1,'rgba(240,245,243,0)');a.fillStyle=g;a.fillRect(0,0,512,256)}return new T.CanvasTexture(c)}
const cloudMat=new T.SpriteMaterial({map:cloudTexture(),transparent:true,opacity:.6,depthWrite:false,color:0xf6f5ed});const clouds=[];
for(let i=0;i<18;i++){let o=new T.Sprite(cloudMat);o.position.set(-180+rand()*360,28+rand()*40,-130+rand()*240);o.scale.set(35+rand()*55,14+rand()*20,1);scene.add(o);clouds.push({o,x:o.position.x,z:o.position.z})}
// Thin auroral curtains: drifting vertical rays follow curved ribbons, physically separate from the sky.
const auroraU={time:{value:0},strength:{value:0}};const auroraMat=new T.ShaderMaterial({uniforms:auroraU,transparent:true,side:T.DoubleSide,depthWrite:false,blending:T.AdditiveBlending,vertexShader:`varying vec2 v;uniform float time;void main(){v=uv;vec3 p=position;p.z+=sin(p.x*.023+time*.25)*7.;p.y+=sin(p.x*.022-time*.15)*13.+sin(p.x*.049+time*.12)*3.;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}`,fragmentShader:`varying vec2 v;uniform float time,strength;void main(){float rays=.5+.25*sin(v.x*310.+sin(v.x*21.+time*.3)*4.)+.25*sin(v.x*710.);float base=pow(1.-v.y,1.8)*smoothstep(0.,.08,v.y);float edge=smoothstep(0.,.12,v.x)*(1.-smoothstep(.88,1.,v.x));vec3 col=mix(vec3(.18,.59,.43),vec3(.28,.35,.56),v.y);gl_FragColor=vec4(col,base*edge*(.3+rays*.7)*strength);}`});
for(let k=0;k<2;k++){const g=new T.PlaneGeometry(650,90,180,18);const p=g.attributes.position;for(let i=0;i<p.count;i++){let x=p.getX(i);p.setZ(i,Math.sin(x*.025+k)*14)}mesh(g,auroraMat,[0,140+k*25,-400-k*20],[0,.05,0],[1,1,1],null,false).castShadow=false}
// Stars appear only with the deep winter sky.
const starsGeo=new T.BufferGeometry(),starP=[];for(let i=0;i<650;i++){let a=rand()*Math.PI*2,el=.12+rand()*1.3;starP.push(Math.cos(a)*Math.cos(el)*400,Math.sin(el)*400,Math.sin(a)*Math.cos(el)*400)}starsGeo.setAttribute('position',new T.Float32BufferAttribute(starP,3));const starMat=new T.PointsMaterial({color:0xe1e8ec,size:.55,transparent:true,opacity:0,sizeAttenuation:true,depthWrite:false});scene.add(new T.Points(starsGeo,starMat));
for(const m of paint){m.onBeforeCompile=shader=>{shader.vertexShader='varying vec3 timberPosition;\n'+shader.vertexShader;shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n timberPosition=position;');shader.fragmentShader='varying vec3 timberPosition;\n'+shader.fragmentShader;shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>','#include <color_fragment>\n float grain=fract(sin(dot(timberPosition.xz*12.,vec2(12.9898,78.233)))*43758.5453);float board=step(.94,fract(timberPosition.y*4.));diffuseColor.rgb*=.94+grain*.07-board*.07;');};}
// Close-readable physical joinery, snow lips and folded curtains at the inn.
const windowFocus=new T.Vector3(inn.x+inn.w*.29,inn.y+inn.h*.58+.45,inn.z+inn.d/2+.18);
const curtainMat=mat('linen curtains',0xd9bd91,.95);curtainMat.emissive=C(0x9b5421);curtainMat.emissiveIntensity=.12;
const warmInner=mat('inn amber window',0x4b392a,.85);warmInner.emissive=C(0x915c2d);warmInner.emissiveIntensity=.45;
const lampShade=mat('warm fabric lampshade',0xddb873,.85);lampShade.emissive=C(0xffb858);lampShade.emissiveIntensity=.55;
const bookMats=[mat('book ochre',0x806c43),mat('book terracotta',0x895144),mat('book slate',0x4f6567)];
for(const side of [-1,1]){
 const X=inn.x+side*inn.w*.29,Z=inn.z+inn.d/2+.19,Y=windowFocus.y;
 box(warmInner,X,Y,Z,inn.w*.177,inn.h*.285,.022);
 const shadeGeo=new T.CylinderGeometry(.11,.18,.19,24,1,true);
 mesh(shadeGeo,lampShade,[X+.28,Y-.20,Z+.06],[0,0,0],[1,1,.3]);
 rod(gold,[X+.28,Y-.30,Z+.07],[X+.28,Y-.48,Z+.07],.012);box(darkwood,X+.28,Y-.49,Z+.07,.20,.025,.08);
 const vases=mat('ceramic '+side,0xb49b79,.7);mesh(new T.SphereGeometry(.065,16,12),vases,[X-.22,Y-.48,Z+.07],[0,0,0],[1,1.3,.4]);
 for(let k=0;k<3;k++)box(bookMats[k],X-.10+k*.055,Y-.47+(k%2)*.025,Z+.06,.045,.14+(k%2)*.05,.05);
 for(const sign of [-1,1]){
  const g=new T.PlaneGeometry(.23,inn.h*.26,20,20),p=g.attributes.position;
  for(let i=0;i<p.count;i++){const x=p.getX(i),y=p.getY(i);p.setXYZ(i,x*(.8+.18*(.5-y/(inn.h*.26))),y,.025*Math.cos(x*130)+.008*Math.sin(y*4));}g.computeVertexNormals();
  mesh(g,curtainMat,[X+sign*inn.w*.073,Y-.01,Z+.043],[0,0,0],[1,1,1]);
 }
 box(ivory,X,Y,Z+.10,.045,inn.h*.32,.035);box(ivory,X,Y,Z+.10,inn.w*.19,.045,.035);
 box(ivory,X,Y-inn.h*.195,Z+.04,inn.w*.255,.10,.32);
 // Overlapping low snow mounds blend into one wind-shaped sill, rather than repeated balls.
 box(snow,X,Y-inn.h*.172,Z+.08,inn.w*.25,.07,.26);
 for(let k=0;k<11;k++){const xx=X-inn.w*.112+k*inn.w*.022;mesh(sphereGeo,snow,[xx,Y-inn.h*.163,Z+.06],[0,0,0],[.19,.025+.012*Math.sin(k*1.7),.13]);}
}
const snowTrim=new T.Group();scene.add(snowTrim);const snowLip=mat('seasonal eave accumulation',0xe1e9ec);snowLip.transparent=true;
for(const H of houses){const g=new T.Group();g.position.set(H.x,H.y,H.z);g.rotation.y=H.rot||0;snowTrim.add(g);for(const side of [-1,1])box(snowLip,side*(H.w/2+.24),H.h+.48,0,.20,.13,H.d+.62,g);}
// The snow particles are world-space, sparse and slow; no full-screen sparkle wash.
const driftGeo=new T.BufferGeometry(),driftBase=[],driftP=[];
for(let i=0;i<150;i++){const x=inn.x-18+rand()*38,y=inn.y+rand()*18,z=inn.z+4+rand()*46;driftBase.push({x,y,z,phase:rand()*6.28,speed:.1+rand()*.22});driftP.push(x,y,z)}
driftGeo.setAttribute('position',new T.Float32BufferAttribute(driftP,3));const driftMat=new T.PointsMaterial({color:0xc8d8e4,size:.032,transparent:true,opacity:.3,depthWrite:false});const driftingSnow=new T.Points(driftGeo,driftMat);scene.add(driftingSnow);
const reflectionGeo=new T.PlaneGeometry(inn.w*.176,inn.h*.283);
const reflectionMat=new T.ShaderMaterial({transparent:true,depthWrite:false,uniforms:{},vertexShader:`varying vec2 v;void main(){v=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,fragmentShader:`varying vec2 v;void main(){float edge=min(min(v.x,1.-v.x),min(v.y,1.-v.y));float noise=fract(sin(dot(floor(v*970.),vec2(12.9898,78.233)))*43758.5453);float frost=pow(1.-smoothstep(0.,.048,edge+noise*.012),2.);float line=exp(-pow((v.x-v.y*.18-.19)/.045,2.))*.13;gl_FragColor=vec4(mix(vec3(.55,.70,.79),vec3(.78,.84,.85),frost),frost*.34+line);}`});
const reflection=new T.Mesh(reflectionGeo,reflectionMat);reflection.position.copy(windowFocus).add(new T.Vector3(0,0,.12));scene.add(reflection);
// Merge static architecture per material: consistent shadows, low render overhead.
for(const [m,geos]of statics){const uniformGeos=geos.map(g=>{const u=g.index?g.toNonIndexed():g.clone();for(const name of Object.keys(u.attributes))if(!['position','normal'].includes(name))u.deleteAttribute(name);return u});const merged=mergeGeometries(uniformGeos,false);if(merged){const o=new T.Mesh(merged,m);o.castShadow=true;o.receiveShadow=true;scene.add(o)}for(const g of geos)g.dispose()}statics.clear();
// Passenger wing geometry is attached to camera, preserving a stable cabin point of view.
const wing=new T.Group();camera.add(wing);
// The right-side window looks a little ahead: aircraft forward projects left.
// Reflect the complete wing assembly, so the near root is left and the outboard
// tip sweeps aft to the right. Do not mirror the world, cabin text or flight path.
wing.scale.x=-1;const wingMat=mat('brushed ivory wing',0xb8c7cd,.46,.3);wingMat.side=T.DoubleSide;red.side=T.DoubleSide;
mesh(polygeo([[3,-1.3,-2],[-1.45,-.55,-6.5],[-.75,-.48,-7.15],[3.4,-.87,-3.1]],[0,1,2,0,2,3]),wingMat,[0,0,0],[0,0,0],[1,1,1],wing);
mesh(polygeo([[-1.45,-.55,-6.5],[-1.58,-.15,-6.6],[-1.32,-.14,-6.85],[-.75,-.48,-7.15]],[0,1,2,0,2,3]),red,[0,0,0],[0,0,0],[1,1,1],wing);
rod(steel,[2.7,-1.14,-2.4],[-1.2,-.53,-6.6],.012,wing);rod(steel,[2.4,-1.09,-2.6],[2.6,-.91,-3.2],.008,wing);rod(steel,[1.2,-.91,-3.8],[1.5,-.76,-4.3],.008,wing);
const seasonal={snow:1,night:0,autumn:0};
function lighting(t,season,night,autumn,sunAngle=.7,warm=.2,sunOverride=null){
 features.update(t,season,night,autumn);snowLip.opacity=smooth(.22,.9,season);snowTrim.visible=snowLip.opacity>.002;driftingSnow.visible=night>.65&&season>.8;reflection.visible=night>.65;const dp=driftGeo.attributes.position;for(let i=0;i<driftBase.length;i++){const b=driftBase[i];dp.setXYZ(i,b.x+Math.sin(t*.11+b.phase)*1.4,b.y-((t*b.speed)%9),b.z+Math.sin(t*.08+b.phase)*.8)}dp.needsUpdate=true;shoreIce.visible=season>.08;shoreIceMat.opacity=smooth(.08,.72,season)*.92;seasonal.snow=season;seasonal.night=night;seasonal.autumn=autumn;landU.snow.value=season;landU.autumn.value=autumn;
 const soil=C(0x718078).lerp(C(0x99755c),autumn);groundMat.color.set(0xffffff);snow.color.copy(C(0x697b80)).lerp(C(0xe8edf0),season);roof.color.set(0xffffff);pathMat.color.copy(C(0xb1ada0)).lerp(C(0xd8dedc),season);
 const sy=night>.5?-.07:Math.max(.09,sunAngle);const az=-Math.PI*.5+.38*Math.sin(t*.25);const sd=sunOverride?new T.Vector3(...sunOverride).normalize():new T.Vector3(Math.cos(az),sy*2,Math.sin(az)).normalize();sun.position.copy(sd).multiplyScalar(150);sun.position.z-=20;sun.target.position.set(0,0,-20);sun.intensity=mix(2.5,.07,night);sun.color.copy(C(0xffe3ba)).lerp(C(0xa6bfeb),night);hemi.intensity=mix(1.4,1.10,night);hemi.color.copy(C(0xcbdfe6)).lerp(C(0x8da6d6),night);hemi.groundColor.copy(C(0x677974)).lerp(C(0x293750),night);
 sunBall.position.copy(sd).multiplyScalar(400);sunBall.visible=sd.y>-.012;seaU.time.value=t;seaU.night.value=night;seaU.sunDir.value.copy(sd);seaU.seaColor.value.copy(C(0x1c5268)).lerp(C(0x173a50),season*.4);skyU.night.value=night;skyU.warm.value=warm;
 scene.fog.color.copy(C(0xc7d7dc)).lerp(C(0x30405c),night);scene.fog.density=mix(.0012,.0022,night);renderer.toneMappingExposure=mix(1.02,1.02,night);
 for(let i=0;i<windowMats.length;i++){const n=smooth(.18+i*.047,.4+i*.047,night);windowMats[i].emissiveIntensity=.04+n*.95;windowMats[i].color.copy(C(0x61747a)).lerp(C(0xdba15d),n)}poolMat.opacity=night*.42;for(const l of warmLights)l.intensity=night*19;starMat.opacity=smooth(.5,.98,night)*.85;auroraU.time.value=t;auroraU.strength.value=smooth(.72,1,night)*.34;cloudMat.opacity=mix(.08,.045,night);cloudMat.color.copy(C(0xf2f4ed)).lerp(C(0x6c7891),night);
 for(const b of boats){b.g.position.y=.3+Math.sin(t*.8+b.phase)*.08;b.g.rotation.z=Math.sin(t*.65+b.phase)*.015}
 for(const b of iceGroups){b.g.position.y=Math.sin(t*.3+b.phase)*.025;b.g.rotation.y=Math.sin(t*.05+b.phase)*.015}
 for(const c of clouds)c.o.position.x=c.x+Math.sin(t*.025)*12;windsock.rotation.y=.3+Math.sin(t*.8)*.14;windsock.rotation.z=Math.sin(t*2)*.025;
}
function roundedRect(x,y,w,h,r){const p=new Path2D();p.roundRect(x,y,w,h,r);return p}
function text(s,x,y,size,color='#f0eee5',font='PingFang SC',weight=400,align='left',spacing=0){ctx.save();ctx.fillStyle=color;ctx.font=`${weight} ${size}px "${font}", sans-serif`;ctx.textAlign=align;ctx.textBaseline='alphabetic';if(spacing&&ctx.letterSpacing!==undefined)ctx.letterSpacing=spacing+'px';ctx.fillText(s,x,y);ctx.restore()}
function fadeText(alpha,fn){ctx.save();ctx.globalAlpha=clamp(alpha);fn();ctx.restore()}
function drawWindow(t){
 const state=flightState(t),forward=new T.Vector3(state.velocity[0],0,state.velocity[2]).normalize(),right=new T.Vector3().crossVectors(forward,new T.Vector3(0,1,0));
 camera.position.set(...state.position);const pitch=mix(-.65,-.13,smooth(7,18,t))+.105*smooth(21.5,24,t);
 const gaze=right.clone().addScaledVector(forward,.25);gaze.y=pitch;camera.lookAt(camera.position.clone().add(gaze));camera.rotateZ(-state.bank);
 camera.aspect=760/940;camera.fov=60;camera.updateProjectionMatrix();wing.visible=true;wing.rotation.z=t>24?Math.sin((t-24)*29)*Math.exp(-(t-24)*5)*.003:0;
 lighting(t,1,.22,0,.12,.35);scene.fog.density=.0009;cloudMat.opacity=.06;renderWorld(1520,1880);
 const bg=ctx.createLinearGradient(0,0,W,H);bg.addColorStop(0,'#e9e9e3');bg.addColorStop(.45,'#d3dce0');bg.addColorStop(1,'#a7bac7');ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);
 // Cabin panel joins and a restrained wash of light give the frame physical context.
 ctx.strokeStyle='rgba(48,73,90,.10)';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(1700,0);ctx.bezierCurveTo(1580,420,1680,720,1720,1080);ctx.stroke();
 const zoom=1+smooth(25,28,t)*2.45,cx=1230,cy=540,w=760,h=940;ctx.save();ctx.translate(cx,cy);ctx.scale(zoom,zoom);ctx.translate(-cx,-cy);
 const x=cx-w/2,y=cy-h/2,ap=roundedRect(x,y,w,h,[250,250,260,260]);
 ctx.shadowColor='rgba(25,48,63,.30)';ctx.shadowBlur=35;ctx.shadowOffsetX=-12;ctx.shadowOffsetY=20;ctx.fillStyle='#c0ced4';ctx.fill(roundedRect(x-45,y-45,w+90,h+90,[295,295,305,305]));ctx.shadowBlur=0;ctx.shadowOffsetX=ctx.shadowOffsetY=0;
 const rim=ctx.createLinearGradient(x-30,y,x+w,y+h);rim.addColorStop(0,'#f9f8ef');rim.addColorStop(.34,'#d9e1e2');rim.addColorStop(.67,'#91a5b1');rim.addColorStop(1,'#eef1eb');ctx.fillStyle=rim;ctx.fill(roundedRect(x-28,y-28,w+56,h+56,[278,278,288,288]));ctx.fillStyle='#293f4b';ctx.fill(roundedRect(x-6,y-6,w+12,h+12,[256,256,266,266]));
 ctx.save();ctx.clip(ap);ctx.drawImage(renderer.domElement,x,y,w,h);
 const glass=ctx.createLinearGradient(x,y,x+w,y+h);glass.addColorStop(0,'rgba(255,255,255,.15)');glass.addColorStop(.23,'rgba(225,242,247,.015)');glass.addColorStop(1,'rgba(16,42,58,.025)');ctx.fillStyle=glass;ctx.fillRect(x,y,w,h);
 ctx.strokeStyle='rgba(245,253,255,.09)';ctx.lineWidth=13;ctx.beginPath();ctx.moveTo(x+70,y+190);ctx.bezierCurveTo(x+120,y+65,x+210,y+55,x+330,y+56);ctx.stroke();ctx.restore();ctx.restore();
 const ta=(1-smooth(22.5,24.5,t))*smooth(0,.7,t);fadeText(ta,()=>{text('MOONBIRD AIR',112,176,22,'#496571','Avenir Next',500,'left',4);ctx.fillStyle='#b68b58';ctx.fillRect(112,210,42,2);text('下一站',108,422,56,'#415d6d','PingFang SC',300);text('霜灯港',104,532,104,'#15384a','PingFang SC',400);text('F R O S T H A V N',112,594,27,'#4f6e7c','Avenir Next',400);void 0;text('MM027  /  NORTHBOUND',112,927,18,'#6f8894','Avenir Next',500,'left',2)});
}
function drawPanorama(t){
 const y=yearState(t);lighting(t+30,y.snow,y.night,y.autumn,.2,.20+.35*y.autumn,y.sunDirection);wing.visible=false;
 // A slow aerial arc: no reset between seasons, no still-image crossfades.
 const theta=.27+t*.0039,radius=170-t*.23;camera.position.set(Math.sin(theta)*radius,65-t*.16,Math.cos(theta)*radius-18);
 camera.lookAt(6+t*.08,10.5,-35);camera.fov=43;camera.aspect=W/H;camera.updateProjectionMatrix();renderWorld(W,H);ctx.drawImage(renderer.domElement,0,0,W,H);
 const grad=ctx.createLinearGradient(0,0,0,280);grad.addColorStop(0,y.night>.5?'rgba(5,15,30,.20)':'rgba(235,239,236,.15)');grad.addColorStop(1,'rgba(18,46,64,0)');ctx.fillStyle=grad;ctx.fillRect(0,0,W,280);
 const label=(a,b,zh,en)=>{const opacity=smooth(a,a+.8,t)*(1-smooth(b-.8,b,t));fadeText(opacity,()=>{text(zh,108,151,54,y.night>.5?'#e7ebef':'#214350','PingFang SC',400);text(en,110,197,20,y.night>.5?'#bdceda':'#45616a','Avenir Next',500,'left',2.5)})};
 label(.1,3.5,'同一座海湾','A YEAR IN FROSTHAVN');label(3.8,10.5,'春 · 冰雪松动','SPRING / THAW');label(11,17.7,'夏 · 午夜太阳','SUMMER / MIDNIGHT SUN');label(18.1,24.0,'秋 · 苔原染金','AUTUMN / TUNDRA GOLD');label(24.4,29.8,'冬 · 漫长暮光','WINTER / POLAR NIGHT');
}
function drawReveal(kind,t){
 const q=smooth(.1,4.65,t);wing.visible=false;lighting(t+18,1,.20,0,.18,.3);
 let start,end,targetStart,targetEnd,title,eng;
 if(kind==='harbour-reveal'){start=new T.Vector3(108,66,137);end=new T.Vector3(33,19,36);targetStart=new T.Vector3(0,8,-18);targetEnd=new T.Vector3(12,1.7,7);title='港湾日常';eng='THE WORKING HARBOUR';}
 else if(kind==='camp-reveal'){const c=features.camp;start=new T.Vector3(99,65,72);end=new T.Vector3(c.x+9,c.y+7.5,c.z+15);targetStart=new T.Vector3(15,11,-38);targetEnd=new T.Vector3(c.x,c.y+1.25,c.z);title='雪屋营地';eng='THE WINTER CAMP';}
 else{const c=features.glacier;start=new T.Vector3(98,72,25);end=new T.Vector3(c.x+13,c.y+8,c.z+29);targetStart=new T.Vector3(21,15,-84);targetEnd=new T.Vector3(c.x,c.y+1,c.z-7);title='冰川尽头';eng='THE GLACIER LOOKOUT';}
 camera.position.copy(start).lerp(end,q);camera.lookAt(targetStart.clone().lerp(targetEnd,q));camera.fov=mix(44,37,q);camera.aspect=W/H;camera.updateProjectionMatrix();renderWorld(W,H);ctx.drawImage(renderer.domElement,0,0,W,H);
 fadeText(smooth(.2,.8,t)*(1-smooth(2.5,3.5,t)),()=>{text(title,108,151,54,'#214350','PingFang SC',400);text(eng,111,197,20,'#45616a','Avenir Next',500,'left',2.4)});
}
// One continuous, authored dolly: same window, same town, no composited camera jump.
function drawOutro(t){
 wing.visible=false;lighting(60+t,1,1,0,.1,0);
 const travel=smooth(1.0,4.5,t),distance=(Math.exp(travel*3.45)-1)/(Math.exp(3.45)-1);
 const close=windowFocus.clone().add(new T.Vector3(.12,.07,2.9)),wide=new T.Vector3(33,40,112);
 warmLights[0].intensity=mix(2.8,14,travel);camera.position.copy(close).lerp(wide,distance);
 const target=windowFocus.clone().lerp(new T.Vector3(-34,13,-18),smooth(1.8,4.65,t));
 camera.lookAt(target);camera.aspect=W/H;camera.fov=mix(40,38,travel);camera.updateProjectionMatrix();renderWorld(W,H);ctx.drawImage(renderer.domElement,0,0,W,H);
 const gradient=ctx.createLinearGradient(0,0,1500,0);const g=smooth(2.7,4.4,t);gradient.addColorStop(0,`rgba(6,22,36,${g*.88})`);gradient.addColorStop(.55,`rgba(6,22,36,${g*.58})`);gradient.addColorStop(1,'rgba(6,22,36,0)');ctx.fillStyle=gradient;ctx.fillRect(0,0,W,H);
 const a=smooth(3.3,4.4,t);fadeText(a,()=>{
  text('FROSTHAVN',112,450,90,'#f2eee3','Avenir Next',300,'left',6);
  text('霜 灯 港',116,530,43,'#e8e8dd','PingFang SC',400);
  text('长夜里，有灯等你。',116,610,31,'#bacbd1','PingFang SC',300);
  text('frosthavn-siming.lovable.app',116,758,27,'#e6b778','Avenir Next',400);
  text('《星露谷物语》PC 模组',116,812,23,'#a3b8c2','PingFang SC',300);
 });
 const glow=windowFocus.clone().project(camera),px=(glow.x+1)*W/2,py=(1-glow.y)*H/2;
 // The destination is projected from the actual inn window, never guessed in screen space.
 fadeText(smooth(4.45,5.35,t),()=>{ctx.strokeStyle='rgba(220,174,111,.58)';ctx.lineWidth=1.3;ctx.beginPath();ctx.moveTo(117,682);ctx.bezierCurveTo(540,655,px-280,py+35,px,py);ctx.stroke();ctx.fillStyle='#edc383';ctx.beginPath();ctx.arc(px,py,3,0,Math.PI*2);ctx.fill();});
 fadeText(smooth(3.8,4.55,t),()=>{text('Music: Life in Silico — Scott Buckley · CC BY 4.0',116,905,20,'#8da6b3','Avenir Next',400);text('www.scottbuckley.com.au · Edited excerpt',116,936,18,'#839eac','Avenir Next',400)});
}
const drawTicket=createTicketShot(T,renderer,ctx,W,H);
window.renderFrame=(kind,t)=>{ctx.globalAlpha=1;ctx.setTransform(1,0,0,1,0,0);if(kind==='ticket')drawTicket(t);else if(kind==='window')drawWindow(t);else if(kind==='panorama')drawPanorama(t);else if(kind.endsWith('-reveal'))drawReveal(kind,t);else drawOutro(t);return canvas.toDataURL('image/jpeg',.96).split(',')[1]};
window.sceneInfo={buildings:houses.length,boats:boats.length,procedural:true,seed:271026,engine:'Three.js',shots:timeline.shots,geometry:'actual 3D terrain, architecture, wing and sea; no image-generated assets or screenshot textures'};
window.sceneDiagnostics={airport:AIRPORT,minimumHomeRunwayEdgeDistance:Math.min(...houses.filter(h=>h.kind==='home'||h.kind==='inn').map(h=>Math.abs(h.x-AIRPORT.x)-h.w/2-AIRPORT.width/2)),features:{market:features.market,station:features.station,camp:features.camp,glacier:features.glacier},seasons:[0,6,14,21,29.9].map(t=>({t,...yearState(t)})),flight:[0,8,11,15,18,24,26,27.99].map(t=>({t,...flightState(t),groundHeight:height(...[flightState(t).position[0],flightState(t).position[2]])}))};
window.ready=true;window.renderFrame(new URLSearchParams(location.search).get('shot')||'panorama',0);
