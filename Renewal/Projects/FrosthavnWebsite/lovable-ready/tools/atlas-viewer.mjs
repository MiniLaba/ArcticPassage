import * as THREE from 'three';
import {OrbitControls} from 'three/examples/jsm/controls/OrbitControls.js';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {navigation} from './walk.mjs';

export async function mount(canvas, signal, onReady) {
  const renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:false, powerPreference:'low-power'});
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#dbe4df');
  const camera = new THREE.PerspectiveCamera(36,1,.45,12500);
  const orbit = new OrbitControls(camera, canvas);
  orbit.minDistance=15; orbit.maxDistance=5900; orbit.maxPolarAngle=Math.PI*.487;
  const hemi = new THREE.HemisphereLight(0xf4faff,0x899c9f,1.45);
  const sun = new THREE.DirectionalLight(0xfff7e9,1.55);
  sun.position.set(-900,1600,850);scene.add(hemi,sun,sun.target);
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFShadowMap;
  sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.bias=-.0003;sun.shadow.normalBias=.09;
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.7));
  function draw(){if(!signal.aborted) renderer.render(scene,walking?walkCamera:camera)}
  orbit.addEventListener('change',draw);
  function size(){
    const w=canvas.clientWidth,h=canvas.clientHeight;
    if(!w||!h)return;
    renderer.setSize(w,h,false);camera.aspect=walkCamera.aspect=w/h;camera.updateProjectionMatrix();walkCamera.updateProjectionMatrix();draw();
  }
  const observer=new ResizeObserver(size);observer.observe(canvas);
  let model,terrain,houses,original,animation=0;
  let route, walkStarts, polarNight=false, walking=false, yaw=0, pitch=0, foot=0, last=0, drag=null;
  const emissiveSurfaces=[];
  const fixedLights=[];
  let markerCloud;
  function makeLighting(model){
    const gain={'Windows':.88,'Fixtures':1.22,'Aviation':1.45,'Beacon':1.95};
    for(const [kind,brightness] of Object.entries(gain)){
      const mesh=model.getObjectByName('Lit-'+kind);
      mesh.material=mesh.material.clone();
      const level={value:0};
      mesh.material.onBeforeCompile=shader=>{
        shader.uniforms.nightEmission=level;
        shader.fragmentShader='uniform float nightEmission;\n'+shader.fragmentShader.replace(
          '#include <emissivemap_fragment>',
          '#include <emissivemap_fragment>\ntotalEmissiveRadiance += vColor.rgb * nightEmission;');
      };
      mesh.material.customProgramCacheKey=()=> 'frosthavn-night-surface';
      emissiveSurfaces.push({level,brightness});
    }
    for(const data of model.userData.lighting){
      const road=data.purpose==='road';
      const light=road
        ? new THREE.SpotLight('#ffd39d',0,25,Math.PI*.27,.65,2)
        : new THREE.PointLight('#ffc084',0,14,2);
      light.position.fromArray(data.position);
      if(road){
        light.target.position.copy(light.position).add(new THREE.Vector3().fromArray(data.direction));
        scene.add(light.target);
      }
      fixedLights.push({light,power:road?250:40});
      scene.add(light);
    }
    const cape=new THREE.PointLight('#fff0cc',0,38,2);
    cape.position.set(1176,35.6,-974);scene.add(cape);
    fixedLights.push({light:cape,power:340});

    // Physical lamp heads remain in the mesh. A subdued point footprint preserves their
    // visibility in the all-map view, where some lenses occupy less than one pixel.
    const rows=model.userData.aviationMarkers;
    const values=[],positions=[],orientations=[];
    for(const [x,y,z,r,g,b,end13,end31,red] of rows){
      positions.push(x,y,z);values.push(r,g,b);
      orientations.push(end13?(red?1:-1):end31?(red?-1:1):0);
    }
    positions.push(1176,36.4,-974);values.push(1,.80,.48);orientations.push(0);
    const geometry=new THREE.BufferGeometry();
    geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
    geometry.setAttribute('lampColor',new THREE.Float32BufferAttribute(values,3));
    geometry.setAttribute('bearing',new THREE.Float32BufferAttribute(orientations,1));
    const paint=new THREE.ShaderMaterial({
      transparent:true, depthWrite:false,
      vertexShader:`
        attribute vec3 lampColor;
        attribute float bearing;
        varying vec3 tint;
        varying float facing;
        void main(){
          tint=lampColor;
          vec2 toViewer=normalize((cameraPosition-position).xz);
          facing=bearing==0.0?1.0:smoothstep(-0.22,0.45,bearing*dot(toViewer,vec2(.9703,.2419)));
          vec4 eye=modelViewMatrix*vec4(position,1.);
          gl_Position=projectionMatrix*eye;
          gl_PointSize=clamp(2.8+250.0/max(20.0,-eye.z),2.8,9.0);
        }`,
      fragmentShader:`
        varying vec3 tint;
        varying float facing;
        void main(){
          float p=length(gl_PointCoord-.5);
          float alpha=(1.0-smoothstep(.15,.50,p))*facing*.93;
          if(alpha<.025)discard;
          gl_FragColor=vec4(pow(tint,vec3(.455)),alpha);
        }`
    });
    markerCloud=new THREE.Points(geometry,paint);
    scene.add(markerCloud);
  }
  function setLighting(active){
    for(const {light,power} of fixedLights)light.intensity=active?power:0;
    for(const {level,brightness} of emissiveSurfaces)level.value=active?brightness:0;
    markerCloud.visible=active;
  }
  const input=new Set();
  const keys={w:'forward',ArrowUp:'forward',s:'back',ArrowDown:'back',a:'left',ArrowLeft:'left',d:'right',ArrowRight:'right'};
  const walkCamera=new THREE.PerspectiveCamera(68,1,.08,5500);
  function move(direction,pressed){
    if(pressed)input.add(direction);else input.delete(direction);
  }
  function orient(){
    walkCamera.rotation.set(pitch,yaw,0,'YXZ');
  }
  function walk(place){
    cancelAnimationFrame(animation);
    const start=walkStarts[place]??walkStarts.market;
    const [x,y,bearing]=start;
    foot=route.elevation(x,-y);
    if(foot<.19)return false;
    walking=true;orbit.enabled=false;input.clear();
    yaw=bearing*Math.PI/180;pitch=0;orient();
    walkCamera.position.set(x,foot+1.66,-y);
    sun.target.position.set(x,foot,-y);sun.position.copy(sun.target.position).add(sunVector.clone().normalize().multiplyScalar(168));
    const sh=sun.shadow.camera;Object.assign(sh,{left:-60,right:60,top:60,bottom:-60,near:1,far:310});sh.updateProjectionMatrix();
    canvas.focus({preventScroll:true});last=0;frame(performance.now());
    return true;
  }
  function frame(now){
    const dt=last?Math.min((now-last)/1000,.028):0;
    last=now;
    const p=walkCamera.position, fore=Number(input.has('forward'))-Number(input.has('back')), side=Number(input.has('right'))-Number(input.has('left'));
    if(fore||side){
      const speed=5.2*dt/Math.hypot(fore,side);
      const dx=(-Math.sin(yaw)*fore+Math.cos(yaw)*side)*speed;
      const dz=(-Math.cos(yaw)*fore-Math.sin(yaw)*side)*speed;
      function stride(x,z){
        const h=route.elevation(x,z,foot+.58);
        if(h<.20||Math.abs(h-foot)>.65||route.hitsWall(x,h+.91,z)||route.hitsWall(x,h+1.55,z))return;
        foot=h;p.set(x,h+1.66,z);
      }
      stride(p.x+dx,p.z);stride(p.x,p.z+dz);
      if(sun.target.position.distanceToSquared(p)>32**2){
        sun.target.position.set(p.x,foot,p.z);sun.position.copy(sun.target.position).add(sunVector.clone().normalize().multiplyScalar(168));
      }
      draw();
    }
    else if(!dt)draw();
    if(walking)animation=requestAnimationFrame(frame);
  }
  function stop(){
    if(!walking)return;
    walking=false;orbit.enabled=true;input.clear();drag=null;cancelAnimationFrame(animation);
  }
  const events={signal};
  canvas.addEventListener('keydown',e=>{
    const key=keys[e.key.length===1?e.key.toLowerCase():e.key];
    if(walking&&key){e.preventDefault();move(key,true)}
  },events);
  window.addEventListener('keyup',e=>{
    const key=keys[e.key.length===1?e.key.toLowerCase():e.key];
    if(key)move(key,false);
  },events);
  canvas.addEventListener('blur',()=>input.clear(),events);
  window.addEventListener('blur',()=>input.clear(),events);
  canvas.addEventListener('pointerdown',e=>{
    if(!walking)return;
    drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);canvas.focus({preventScroll:true});
  },events);
  canvas.addEventListener('pointermove',e=>{
    if(!drag||!walking)return;
    yaw-=(e.clientX-drag[0])*.0042;
    pitch=THREE.MathUtils.clamp(pitch-(e.clientY-drag[1])*.0042,-1.35,1.35);
    drag=[e.clientX,e.clientY];orient();draw();
  },events);
  for(const name of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(name,()=>{drag=null},events);

  function dispose() {
    cancelAnimationFrame(animation);observer.disconnect();orbit.dispose();
    model?.traverse(o=>{if(o.isMesh){o.geometry.dispose();o.material.dispose()}});
    markerCloud?.geometry.dispose();markerCloud?.material.dispose();
    renderer.dispose();
  }
  signal.addEventListener('abort',dispose,{once:true});
  function focus(place,animated=true) {
    stop();cancelAnimationFrame(animation);
    const [x,y,z,dist]=place||[330,860,5,Math.max(4320,3700/Math.min(camera.aspect,1.4))];
    const target=new THREE.Vector3(x,z,-y);
    const bearing=x===12?new THREE.Vector3(-.59,.51,-.73):new THREE.Vector3(.22,.72,.89);
    const pos=target.clone().add(bearing.normalize().multiplyScalar(dist));
    sun.target.position.copy(target);sun.position.copy(target).add(sunVector);
    const shadow=sun.shadow.camera, span=Math.max(55,Math.min(1650,dist*.57));
    Object.assign(shadow,{left:-span,right:span,top:span,bottom:-span,near:1,far:2200});shadow.updateProjectionMatrix();
    const a=orbit.target.clone(), b=camera.position.clone(),start=performance.now();
    function step(now){
      const t=animated&&!matchMedia('(prefers-reduced-motion: reduce)').matches?Math.min(1,(now-start)/590):1;
      const f=t*t*(3-2*t);orbit.target.lerpVectors(a,target,f);camera.position.lerpVectors(b,pos,f);orbit.update();draw();
      if(t<1)animation=requestAnimationFrame(step);
    }
    step(start);
  }
  orbit.addEventListener('start',()=>cancelAnimationFrame(animation));
  const climates={
    spring:['#cbdde0','#fff3d5',1.48,1.48,new THREE.Vector3(-260,310,330)],
    summer:['#dbe8e6','#fff6e7',1.60,1.50,new THREE.Vector3(-250,420,240)],
    autumn:['#d8d5c9','#ffe1b9',1.49,1.70,new THREE.Vector3(-360,220,240)],
    // The direction records a sun about 10° below the horizon. No direct sunlight reaches the scene.
    winter:['#142336','#8eaccd',.48,0,new THREE.Vector3(-320,-70,245)]
  };
  let sunVector=climates.summer[4];
  function season(value){
    if(!terrain)return;
    const [sky,tint,ambient,intensity,direction]=climates[value];
    sunVector=direction;
    polarNight=value==='winter';
    scene.background.set(sky);
    hemi.color.set(polarNight?'#abc9ff':'#f4faff');
    hemi.groundColor.set(polarNight?'#435571':'#899c9f');
    hemi.intensity=ambient;
    sun.intensity=intensity;sun.castShadow=!polarNight;sun.color.set(tint);
    setLighting(polarNight);
    sun.position.copy(sun.target.position).add(walking?direction.clone().normalize().multiplyScalar(168):direction);
    terrain.geometry.setAttribute('color',value==='summer'?original:terrain.geometry.attributes['_'+value]);
    houses.visible=value==='winter';
    const paths=model.getObjectByName('Footpaths');if(paths)paths.visible=value!=='winter';
    for(const name of ['spring','summer','autumn']){
      const plants=model.getObjectByName('Plants-'+name);
      if(plants)plants.visible=name===value;
    }
    draw();
  }
  try {
    const res=await fetch('/atlas/frosthavn-polar-lights.glb.gz',{signal});if(!res.ok)throw Error('model');
    const data=await res.arrayBuffer();let decoded=data;
    if(new Uint8Array(data)[0]===31){
      decoded=await new Response(new Blob([data]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
    }
    const asset=await new GLTFLoader().parseAsync(decoded,'');
    if(signal.aborted){asset.scene.traverse(o=>{if(o.isMesh){o.geometry.dispose();o.material.dispose()}});return}
    model=asset.scene;scene.add(model);model.traverse(o=>{if(o.isMesh){if(!o.geometry.attributes.normal)o.geometry.computeVertexNormals();o.receiveShadow=true;o.castShadow=['Snowhouses','Structures','Glacier','Berg'].includes(o.name)}});
    terrain=model.getObjectByName('Terrain');houses=model.getObjectByName('Snowhouses');
    original=terrain.geometry.attributes.color;
    const {terrainGrid,walkStarts:starts}=model.userData;
    walkStarts=starts;route=navigation(model,terrainGrid);
    makeLighting(model);
    size();focus(null,false);season('summer');onReady();
    return {focus,season,walk,move,zoom(f){const delta=camera.position.clone().sub(orbit.target);delta.setLength(THREE.MathUtils.clamp(delta.length()*f,orbit.minDistance,orbit.maxDistance));camera.position.copy(orbit.target).add(delta);orbit.update();draw()}};
  } catch(e){if(!signal.aborted)dispose();throw e}
}
