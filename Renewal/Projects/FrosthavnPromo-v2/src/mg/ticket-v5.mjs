import {TessellateModifier} from 'three/addons/modifiers/TessellateModifier.js';
// Original typography, physical perforations and a deterministic thin-paper fold.
// This is an authored title shot, never a substitute for native game footage.
export function createTicketShot(T,renderer,ctx,W,H){
 const scene=new T.Scene();scene.background=new T.Color('#102c3a');
 const camera=new T.PerspectiveCamera(38,W/H,.05,80);
 const hemi=new T.HemisphereLight(0xdce7e8,0x142b35,2);scene.add(hemi);
 const key=new T.DirectionalLight(0xffe4b7,3.3);key.position.set(-5,6,10);key.castShadow=true;key.shadow.mapSize.set(2048,2048);Object.assign(key.shadow.camera,{left:-9,right:9,top:8,bottom:-8,near:.1,far:30});key.shadow.bias=-.00015;scene.add(key);
 const fill=new T.PointLight(0x95bfce,45,22,2);fill.position.set(4,-3,6);scene.add(fill);
 const floor=new T.Mesh(new T.PlaneGeometry(80,80),new T.MeshStandardMaterial({color:0x123342,roughness:.93}));floor.position.z=-.35;floor.receiveShadow=true;scene.add(floor);
 const cw=3600,ch=1464,c=document.createElement('canvas');c.width=cw;c.height=ch;const a=c.getContext('2d');
 const ink='#183d4a',gold='#ad7944',muted='#71868a';a.fillStyle='#eae6d9';a.fillRect(0,0,cw,ch);
 let seed=2710;const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296};
 for(let i=0;i<48000;i++){const v=random();a.fillStyle=`rgba(83,75,57,${.025+v*.026})`;a.fillRect(random()*cw,random()*ch,.7+random()*2,.5+random()*1.8)}
 for(let k=0;k<25;k++){a.strokeStyle='#d9ddd3';a.lineWidth=1.5;a.beginPath();for(let j=0;j<=400;j++){const x=1640+j*2.5,y=80+k*47+40*Math.sin(j*.024+k*.11)+16*Math.sin(j*.057);j?a.lineTo(x,y):a.moveTo(x,y)}a.stroke()}
 const txt=(s,x,y,size,color=ink,font='Avenir Next',weight=400)=>{a.font=`${weight} ${size}px "${font}"`;a.fillStyle=color;a.fillText(s,x,y)};
 a.fillStyle=gold;a.fillRect(105,94,53,5);txt('MOONBIRD AIR',186,117,37,ink,'Avenir Next',600);txt('月月鸟航空',105,187,44,muted,'PingFang SC');
 txt('BOARDING PASS',108,325,31,muted);txt('向北，去有灯的海湾。',105,435,71,ink,'PingFang SC');
 txt('CAN',104,830,195,ink,'Avenir Next',500);txt('FHV',1740,830,195,ink,'Avenir Next',500);
 txt('广州白云',111,904,43,muted,'PingFang SC');txt('霜灯港北辰',1747,904,43,muted,'PingFang SC');
 a.strokeStyle=gold;a.lineWidth=5;a.beginPath();a.moveTo(615,766);a.bezierCurveTo(865,442,1350,442,1620,766);a.stroke();
 for(const x of [615,1620]){a.fillStyle=gold;a.beginPath();a.arc(x,766,11,0,Math.PI*2);a.fill()}
 txt('霜灯港',108,1154,137,ink,'PingFang SC',400);txt('F R O S T H A V N',119,1247,52,muted);
 a.strokeStyle='#b6bdb4';a.lineWidth=2;a.beginPath();a.moveTo(115,1330);a.lineTo(2530,1330);a.stroke();
 txt('MM027',115,1400,35,ink,'Avenir Next',600);txt('27 OCTOBER 2026',2050,1400,29,muted);
 // Two distinct stubs with common hierarchy, no false machine-readable credential.
 a.fillStyle=ink;a.fillRect(2735,92,354,1250);
 txt('MM027',2770,185,50,'#ece7d9','Avenir Next',600);txt('FHV',2770,560,88,'#ece7d9','Avenir Next',500);txt('27 OCT',2770,1100,37,'#c7cabc');txt('01',2770,1264,43,'#c7cabc');
 txt('MM',3230,185,49);txt('027',3215,560,95,ink,'Avenir Next',500);txt('FHV',3220,1110,54);txt('02',3220,1264,43,muted);
 const tex=new T.CanvasTexture(c);tex.colorSpace=T.SRGBColorSpace;tex.anisotropy=8;
 const w=10.8,h=w*ch/cw,shape=new T.Shape();shape.moveTo(-w/2,-h/2);shape.lineTo(w/2,-h/2);shape.lineTo(w/2,h/2);shape.lineTo(-w/2,h/2);shape.closePath();
 for(const x of [2.7,4.05])for(let y=-h/2+.13;y<h/2-.1;y+=.145){let hole=new T.Path();hole.absarc(x,y,.025,0,Math.PI*2,true);shape.holes.push(hole)}
 const tessellate=new TessellateModifier(.45,6);
 const bodyGeo=tessellate.modify(new T.ExtrudeGeometry(shape,{depth:.026,bevelEnabled:true,bevelSegments:2,steps:1,bevelSize:.006,bevelThickness:.004,curveSegments:5}));
 const frontGeo=tessellate.modify(new T.ShapeGeometry(shape,5));const pos=frontGeo.attributes.position,uv=[];for(let i=0;i<pos.count;i++)uv.push((pos.getX(i)+w/2)/w,(pos.getY(i)+h/2)/h);frontGeo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));frontGeo.translate(0,0,.095);
 const body=new T.Mesh(bodyGeo,new T.MeshStandardMaterial({color:0xdcd6c4,roughness:.91,side:T.DoubleSide}));body.castShadow=true;body.receiveShadow=true;
 const paper=new T.Mesh(frontGeo,new T.MeshStandardMaterial({map:tex,roughness:.89,metalness:0,side:T.DoubleSide,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-4}));paper.castShadow=false;paper.receiveShadow=false;
 const group=new T.Group();group.add(body,paper);group.rotation.z=-.085;scene.add(group);
 const geometries=[bodyGeo,frontGeo].map(g=>({g,base:g.attributes.position.array.slice()}));
 const smooth=(a,b,t)=>{const q=Math.max(0,Math.min(1,(t-a)/(b-a)));return q*q*(3-2*q)};
 function draw(t){
  const fold=.09*Math.sin(t*.7)+.15*smooth(.35,1.7,t)-.12*smooth(2.1,3.8,t);
  for(const {g,base}of geometries){const p=g.attributes.position;for(let i=0;i<p.count;i++){let x=base[i*3],y=base[i*3+1],z=base[i*3+2];const bx=Math.max(0,x-2.7),ang=fold;const curl=.0022*(x+2.0)**2+.002*y*y;const xx=x>2.7?2.7+bx*Math.cos(ang):x;z+=curl+bx*Math.sin(ang);p.setXYZ(i,xx,y,z)}p.needsUpdate=true;if(g===frontGeo){const n=g.attributes.normal;for(let i=0;i<p.count;i++){const x=base[i*3],y=base[i*3+1],nx=-(.0044*(x+2)+(x>2.7?Math.sin(fold):0)),ny=-.004*y,nz=x>2.7?Math.cos(fold):1,len=Math.hypot(nx,ny,nz);n.setXYZ(i,nx/len,ny/len,nz/len)}n.needsUpdate=true}else g.computeVertexNormals()}
  // Hold a complete title for the thumbnail; then travel along the printed route.
  const q=smooth(.32,3.75,t),r=smooth(2.05,3.8,t);
  camera.position.set(-1.2+q*3.2, -3.1+q*2.2,13.1-q*7.0);
  camera.lookAt(-.25+q*1.55,.05+q*.3,.15);camera.rotateZ(-.04+q*.025);
  key.position.x=-5+t*.5;group.rotation.z=-.085+q*.022;
  renderer.setSize(W,H,false);renderer.render(scene,camera);ctx.drawImage(renderer.domElement,0,0,W,H);
  const vignette=ctx.createRadialGradient(960,530,340,960,530,1200);vignette.addColorStop(0,'rgba(0,15,24,0)');vignette.addColorStop(1,'rgba(0,15,24,.25)');ctx.fillStyle=vignette;ctx.fillRect(0,0,W,H);
 }
 return draw;
}
