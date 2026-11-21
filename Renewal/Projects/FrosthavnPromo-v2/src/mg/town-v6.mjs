// Authored seasonal places shared by the arrival, annual shot and location reveals.
export function extendTown(A){
 const {T,scene,mesh,box,cylinder,rod,polygeo,house,height,coast,mat,rock,wood,darkwood,ivory,navy,red,gold,steel,roof,snow,rand,houses}=A;
 const clamp=x=>Math.max(0,Math.min(1,x)),smooth=(a,b,t)=>{const q=clamp((t-a)/(b-a));return q*q*(3-2*q)};
 const market=house(-16,-9,5.9,4.4,2.8,1,0,'fish-market');
 const station=house(-37,-69,6.3,5.1,3.1,0,0,'research');
 const hall=house(10,-66,6.8,6,3.4,2,0,'community');
 // Fish-market workbench, two awnings, stacked crates and drying racks.
 box(wood,-16,market.y+.55,-5.9,6.5,.18,1.2);
 for(const x of [-18.5,-13.5]){rod(ivory,[x,market.y,-5.4],[x,market.y+2.6,-5.4],.045);box(navy,x,market.y+2.6,-5.5,1.9,.12,1.1)}
 for(let i=0;i<5;i++){box(wood,-19+i*.62,market.y+.34,-5.4,.53,.5,.62);box(darkwood,-19+i*.62,market.y+.45,-5.07,.55,.025,.02)}
 const fishMat=mat('silver catch',0x789396,.48,.18);
 for(let i=0;i<6;i++)mesh(new T.ConeGeometry(.06,.34,8),fishMat,[-17.5+i*.36,market.y+.7,-5.6],[0,0,Math.PI/2],[1,1,1]);
 // Research instruments: mast, wind cups and a small observation dome.
 const sy=station.y;rod(steel,[-31,sy,-69],[-31,sy+7,-69],.045);
 const anemometer=new T.Group();anemometer.position.set(-31,sy+7,-69);scene.add(anemometer);
 for(let i=0;i<3;i++){const a=i*Math.PI*2/3;rod(steel,[0,0,0],[Math.cos(a)*.65,0,Math.sin(a)*.65],.018,anemometer);mesh(new T.SphereGeometry(.15,12,8,0,Math.PI*2,0,Math.PI/2),ivory,[Math.cos(a)*.65,0,Math.sin(a)*.65],[0,0,Math.PI/2],[1,1,1],anemometer)}
 cylinder(ivory,-43,sy+.8,-71,1.2,1.6);mesh(new T.SphereGeometry(1.22,24,12,0,Math.PI*2,0,Math.PI/2),ivory,[-43,sy+1.6,-71]);
 rod(steel,[-43,sy+1.65,-71],[-42.8,sy+3.4,-71.4],.04);
 // Community porch and square stay readable at aerial scale.
 box(wood,10,hall.y+.35,-61.5,8,.23,2);for(const x of [6,14])rod(ivory,[x,hall.y+.3,-60.8],[x,hall.y+2.9,-60.8],.065);
 for(const x of [5.2,14.8]){box(wood,x,hall.y+.6,-57.5,2.3,.13,.55);for(const dx of [-.8,.8])rod(darkwood,[x+dx,hall.y,-57.5],[x+dx,hall.y+.6,-57.5],.05)}
 // Separate winter teaching camp, with true curved block geometry and open tunnel.
 const camp={x:69,z:-83,y:height(69,-83)},igloos=new T.Group();scene.add(igloos);
 const snowBlocks=Array.from({length:5},(_,i)=>{const m=mat('camp snow block '+i,new T.Color(0xe2edf0).multiplyScalar(.94+i*.016));m.transparent=true;return m});
 const campFloor=new T.MeshStandardMaterial({color:0x18323e,roughness:1,transparent:true});
 const sled=new T.Group();scene.add(sled);
 const bases=[];
 for(const [dx,dz,r]of [[0,0,2.8],[10,-3,2.35],[-3,-11,2.15]]){
  const x=camp.x+dx,z=camp.z+dz,y=height(x,z);bases.push({x,z,y,r});
  for(let row=0;row<7;row++){
   const p0=row/7*Math.PI/2+.003,p1=(row+1)/7*Math.PI/2-.003,n=Math.max(5,Math.round(21*Math.cos((p0+p1)/2)));
   for(let j=0;j<n;j++){
    const a0=(j+(row%2)*.5)*Math.PI*2/n+.003,a1=a0+Math.PI*2/n-.006,ac=(a0+a1)/2;
    if(row<2&&Math.abs(Math.atan2(Math.sin(ac-Math.PI/2),Math.cos(ac-Math.PI/2)))<.24)continue;
    const vertices=[],indices=[];
    for(const rr of [r-.26,r])for(const pp of [p0,p1])for(const aa of [a0,a1])vertices.push([rr*Math.cos(pp)*Math.cos(aa),rr*Math.sin(pp),rr*Math.cos(pp)*Math.sin(aa)]);
    for(const f of [[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]])indices.push(f[0],f[1],f[2],f[0],f[2],f[3]);
    mesh(polygeo(vertices,indices),snowBlocks[(row+j)%5],[x,y,z],[0,0,0],[1,1,1],igloos);
   }
  }
  const arch=new T.Shape();arch.moveTo(-1.02,0);arch.absarc(0,0,1.02,Math.PI,0,true);arch.lineTo(.74,0);arch.absarc(0,0,.74,0,Math.PI,false);arch.closePath();
  const archGeo=new T.ExtrudeGeometry(arch,{depth:1.6,bevelEnabled:false,steps:1,curveSegments:20});mesh(archGeo,snowBlocks[2],[x,y+.16,z+r-.35],[0,0,0],[1,1,1],igloos);
  mesh(new T.CircleGeometry(r-.33,28),campFloor,[x,y+.02,z],[-Math.PI/2,0,0],[1,1,1],igloos);
  // A stone ring survives spring; it never becomes a summer igloo.
  for(let j=0;j<14;j++){const a=j/14*Math.PI*2;mesh(new T.DodecahedronGeometry(.16,0),rock,[x+(r+.3)*Math.cos(a),y+.06,z+(r+.3)*Math.sin(a)],[0,a,0],[1,.45,.8])}
 }
 const sx=camp.x+5,sz=camp.z+4,sh=height(sx,sz);
 for(const x of [sx-.48,sx+.48]){rod(darkwood,[x,sh+.13,sz-1.5],[x,sh+.13,sz+1.2],.055,sled);rod(darkwood,[x,sh+.13,sz+1.2],[x,sh+.46,sz+1.8],.055,sled);rod(wood,[x,sh+.15,sz-1],[x,sh+.62,sz-1],.04,sled)}
 box(wood,sx,sh+.49,sz,.96,.10,2.4,sled);box(red,sx,sh+.72,sz-.2,.7,.36,1.2,sled);rod(wood,[sx-.48,sh+.65,sz-1.3],[sx-.48,sh+1.3,sz-1.6],.035,sled);rod(wood,[sx+.48,sh+.65,sz-1.3],[sx+.48,sh+1.3,sz-1.6],.035,sled);rod(wood,[sx-.48,sh+1.3,sz-1.6],[sx+.48,sh+1.3,sz-1.6],.035,sled);
 // Shelters and a wind marker give the camp scale without duplicating homes.
 for(let i=0;i<2;i++){const x=camp.x-8+i*2.2,z=camp.z+2,y=height(x,z);box(darkwood,x,y+.42,z,1.4,.8,1.45);mesh(new T.ConeGeometry(1.1,.65,4),red,[x,y+1.03,z],[0,Math.PI/4,0]);box(navy,x,y+.37,z+.74,.45,.6,.02)}
 const flags=[];for(const [x,z]of [[61,-78],[77,-87],[22,-128],[25,-151]]){let y=height(x,z);rod(steel,[x,y,z],[x,y+2.9,z],.025);const flag=mesh(new T.PlaneGeometry(.9,.45,8,1),new T.MeshStandardMaterial({color:0xc36c49,side:T.DoubleSide}),[x+.43,y+2.65,z],[0,0,0],[1,1,1],null,false);flags.push({flag,base:flag.geometry.attributes.position.array.slice()})}
 // Glacier walk and lookout: actual planks and two rails lead toward blue ice.
 const glacier={x:24,z:-145,y:height(24,-145)+2.1};
 for(let z=-123;z>=-152;z-=.45){const y=glacier.y+(z+145)*.025;box(wood,24,y,z,2.7,.12,.40);for(const side of [-1,1])if(Math.round((z+123)/.45)%5===0)rod(steel,[24+side*1.38,y,z],[24+side*1.38,y+1.05,z],.025)}
 for(const side of [-1,1])rod(steel,[24+side*1.38,glacier.y+1.6,-123],[24+side*1.38,glacier.y+.88,-152],.035);
 box(wood,24,glacier.y-.2,-154,7,.18,5);for(const x of [20.5,27.5]){rod(steel,[x,glacier.y-.2,-156.5],[x,glacier.y+1,-156.5],.04);rod(steel,[x,glacier.y+.9,-156.5],[x,glacier.y+.9,-151.5],.03)}rod(steel,[20.5,glacier.y+.9,-156.5],[27.5,glacier.y+.9,-156.5],.03);
 // Crevassed blue glacier face has grounded, asymmetric vertical wedges.
 const glacierBlue=mat('compressed glacier blue',0x99bdcc,.72);
 for(let i=0;i<18;i++){const x=4+i*2.9,z=-178-Math.sin(i*.7)*3,y=height(x,z)-1,h=5.5+Math.sin(i*1.7)*2;
  mesh(polygeo([[-1.9,0,2],[1.8,0,2.4],[1.6,0,-4],[-1.7,0,-4],[-1.4,h,1.2],[1.2,h*.82,1.6],[1.5,h*.94,-3],[-1.5,h*1.08,-3]], [0,1,5,0,5,4,1,2,6,1,6,5,2,3,7,2,7,6,3,0,4,3,4,7,4,5,6,4,6,7]),glacierBlue,[x,y,z]);
 }
 for(let z=-125;z>=-155;z-=4)for(const x of [22.7,25.3])rod(darkwood,[x,height(x,z)-.2,z],[x,glacier.y+(z+145)*.025,z],.075);
 // Low tundra and small flowers, never temperate trees.
 const shrubMat=mat('dwarf tundra',0x6b7760,.95),flowerMat=mat('arctic saxifrage',0x9f7e93,.95);
 const plants=new T.Group();scene.add(plants);const shrubs=[];
 for(let i=0;i<420;i++){
  const x=-110+rand()*240,z=-120+rand()*125;if(z>coast(x)-3||houses.some(h=>Math.abs(x-h.x)<h.w*.8&&Math.abs(z-h.z)<h.d*.8)||Math.hypot(x-camp.x,z-camp.z)<17)continue;
  const y=height(x,z),s=.18+rand()*.34;const o=mesh(new T.IcosahedronGeometry(1,0),shrubMat,[x,y+.06,z],[0,rand()*6,0],[s,.12+s*.27,s*.7],plants);o.userData.baseY=o.scale.y;shrubs.push(o);
  if(i%6===0)mesh(new T.IcosahedronGeometry(.055,0),flowerMat,[x,y+.2,z],[0,0,0],[1,1,1],plants);
 }
 const summerBoats=new T.Group();scene.add(summerBoats);for(let i=0;i<2;i++){const x=-23+i*2.3,z=-2.4,y=height(x,z);mesh(new T.SphereGeometry(1,18,10),i?gold:red,[x,y+.35,z],[0,.1,0],[.35,.22,1.65],summerBoats);box(navy,x,y+.55,z,.35,.04,.65,summerBoats)}
 // Chimney air follows one continuous time input; it becomes more visible in winter.
 const vapourMat=new T.MeshBasicMaterial({color:0xc0ced3,transparent:true,opacity:.055,depthWrite:false});const vapour=[];
 for(const H of houses.filter(h=>h.kind==='home').slice(0,6))for(let k=0;k<5;k++){const o=mesh(new T.SphereGeometry(1,10,8),vapourMat,[0,0,0],[0,0,0],[1,1,1],null,false);o.castShadow=false;vapour.push({o,H,k})}
 const walkers=[];for(const color of [red,navy,gold]){const g=new T.Group();scene.add(g);mesh(new T.CapsuleGeometry(.18,.42,4,8),color,[0,.75,0],[0,0,0],[1,1,1],g);mesh(new T.SphereGeometry(.16,12,8),ivory,[0,1.24,0],[0,0,0],[1,1,1],g);const legs=[];for(const side of [-1,1]){const l=mesh(new T.CylinderGeometry(.065,.055,.48,8),navy,[side*.1,.28,0],[0,0,0],[1,1,1],g);legs.push(l)}walkers.push({g,legs,phase:rand()*6.28})}
 function seasonalMaterials(group){const a=[];group.traverse(o=>{if(o.isMesh){o.material=o.material.clone();o.material.transparent=true;a.push(o.material)}});return a}
 const sledMats=seasonalMaterials(sled),kayakMats=seasonalMaterials(summerBoats);
 function fadeGroup(g,mats,a){g.visible=a>.002;for(const m of mats){m.opacity=a;m.depthWrite=a>.98}}
 function update(t,sn,night,autumn){
  const winter=smooth(.35,.88,sn);for(const m of snowBlocks){m.opacity=winter;m.depthWrite=winter>.98}igloos.visible=winter>.002;campFloor.opacity=winter;fadeGroup(sled,sledMats,winter);
  for(const o of shrubs)o.scale.y=o.userData.baseY*(.22+.78*(1-sn));shrubMat.color.copy(new T.Color(0x63735b)).lerp(new T.Color(0x9c6242),autumn).lerp(new T.Color(0xa1aaa0),sn*.65);flowerMat.color.copy(new T.Color(0xa27b91)).lerp(new T.Color(0x66715e),Math.max(sn,autumn));
  fadeGroup(summerBoats,kayakMats,1-smooth(.2,.65,sn));summerBoats.position.y=-smooth(.2,.5,sn)*.22;anemometer.rotation.y=t*1.8;
  for(const {flag,base}of flags){const a=flag.geometry.attributes.position;for(let i=0;i<a.count;i++){const x=base[i*3];a.setZ(i,Math.sin(t*2.2+x*7)*.08*(x+.45))}a.needsUpdate=true;flag.geometry.computeVertexNormals()}
  vapourMat.opacity=.018+.045*sn;for(const {o,H,k}of vapour){const q=(t*.19+k*.2)%1;o.position.set(H.x+H.w*.28+q*1.3,H.y+H.h+.45+H.w*.38+.4+q*3.8,H.z-H.d*.17+q*.4);o.scale.setScalar((.14+q*.55)*Math.sin(Math.PI*q))}
  walkers.forEach(({g,legs,phase},i)=>{const q=(t*.012+i*.31)%1,x=-31+q*61,z=-15-2*Math.sin(q*Math.PI*2);g.position.set(x,height(x,z)+.05,z);g.rotation.y=Math.PI/2;legs[0].rotation.x=Math.sin(t*4+phase)*.25;legs[1].rotation.x=-Math.sin(t*4+phase)*.25});
 }
 return {market,station,hall,camp,glacier,igloos,snowBlocks,update,bases};
}
