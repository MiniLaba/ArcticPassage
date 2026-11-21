// The terrain is the Blender survey grid. Local road and wall triangles use a spatial index.
export function navigation(model, size) {
  const grid = model.getObjectByName('Terrain').geometry.attributes.position;
  const firstX = grid.getX(0), firstZ = grid.getZ(0);
  const dx = grid.getX(1) - firstX, dz = grid.getZ(size) - firstZ;
  const cell = 8;
  const tiles = new Map();
  const key = (x,z) => `${x}/${z}`;
  for (const name of ['Roads', 'Footpaths', 'Structures', 'Snowhouses']) {
    const geometry = model.getObjectByName(name)?.geometry;
    if (!geometry) continue;
    const points = geometry.attributes.position;
    const index = geometry.index.array;
    const floor = name === 'Roads' || name === 'Footpaths';
    for (let i=0;i<index.length;i+=3) {
      const p=[index[i],index[i+1],index[i+2]].map(j=>[points.getX(j),points.getY(j),points.getZ(j)]);
      const x=p.map(v=>v[0]), y=p.map(v=>v[1]), z=p.map(v=>v[2]);
      const yMin=Math.min(...y),yMax=Math.max(...y);
      if (!floor && yMax-yMin<.12) continue;
      const minX=Math.floor(Math.min(...x)/cell),maxX=Math.floor(Math.max(...x)/cell);
      const minZ=Math.floor(Math.min(...z)/cell),maxZ=Math.floor(Math.max(...z)/cell);
      if ((maxX-minX+1)*(maxZ-minZ+1)>2000) continue;
      const tri={p,yMin,yMax,name,floor};
      for(let a=minX;a<=maxX;a++) for(let b=minZ;b<=maxZ;b++){
        const k=key(a,b);
        if(!tiles.has(k)) tiles.set(k,[]);
        tiles.get(k).push(tri);
      }
    }
  }
  const tile=(x,z)=>tiles.get(key(Math.floor(x/cell),Math.floor(z/cell)))??[];
  const active=t=>model.getObjectByName(t.name)?.visible;
  function elevation(x,z,max=Infinity){
    const u=(x-firstX)/dx, v=(z-firstZ)/dz;
    const i=Math.floor(u), j=Math.floor(v);
    if(i<0||i>=size-1||j<0||j>=size-1)return -10;
    const a=u-i,b=v-j,k=j*size+i;
    const p=grid.getY(k),q=grid.getY(k+1),r=grid.getY(k+size),s=grid.getY(k+size+1);
    let ground=a>b?p+(q-p)*a+(s-q)*b:p+(r-p)*b+(s-r)*a;
    for(const t of tile(x,z)){
      if(!t.floor||t.yMax<ground||t.yMin>max||!active(t))continue;
      const [l,m,n]=t.p;
      const bx=m[0]-l[0], bz=m[2]-l[2], cx=n[0]-l[0], cz=n[2]-l[2], xx=x-l[0], zz=z-l[2];
      const d=bx*cz-cx*bz;
      if(Math.abs(d)<.000001)continue;
      const e=(xx*cz-cx*zz)/d, f=(bx*zz-xx*bz)/d;
      if(e<0||f<0||e+f>1)continue;
      const height=l[1]+e*(m[1]-l[1])+f*(n[1]-l[1]);
      if(height<=max)ground=Math.max(ground,height);
    }
    return ground;
  }
  function hitsWall(x,y,z){
    for(const t of tile(x,z)){
      if(t.floor||t.yMax<y||t.yMin>y||!active(t))continue;
      const ends=[];
      for(let i=0;i<3;i++){
        const a=t.p[i],b=t.p[(i+1)%3];
        if((a[1]<=y)===(b[1]<=y))continue;
        const k=(y-a[1])/(b[1]-a[1]);
        ends.push([a[0]+(b[0]-a[0])*k,a[2]+(b[2]-a[2])*k]);
      }
      if(ends.length!==2)continue;
      const [a,b]=ends, u=b[0]-a[0], v=b[1]-a[1];
      const f=Math.min(1,Math.max(0,((x-a[0])*u+(z-a[1])*v)/(u*u+v*v||1)));
      if((x-a[0]-u*f)**2+(z-a[1]-v*f)**2<.31**2)return true;
    }
    return false;
  }
  return {elevation,hitsWall};
}
