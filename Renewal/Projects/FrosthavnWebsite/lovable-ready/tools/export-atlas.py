import bpy,numpy as np,json,struct,gzip,sys
from pathlib import Path
from mathutils import Matrix,Vector
from collections import defaultdict
s=bpy.context.scene;s.frame_set(102)
dest=Path(sys.argv[sys.argv.index('--')+1]);groups=defaultdict(list)
lighting = []
airfield_markers = []
def light_kind(obj, mat):
 if not mat:return None
 name=mat.name
 if obj.name=='灯室':return 'Beacon'
 if name.startswith(('空港 · 边白','空港 · 入口绿','空港 · 末端红','空港 · 滑行蓝')):return 'Aviation'
 if name.startswith('琥珀灯') or name.startswith('空港 · 琥珀窗'):return 'Fixtures'
 if name.startswith(('暖窗','warm','反光玻璃','空港 · 大厅玻璃','塔台 · 通透夹胶')):
  return 'Windows'
 if name.startswith('叶利佐沃原型 · 玻璃') and not obj.name.startswith('机坪步行登机'):
  return 'Windows'
 return None
def lamp_position(obj, transform, purpose):
 xyz=transform.translation
 direction=transform.to_quaternion() @ Vector((0,0,-1))
 lighting.append(dict(
  position=[round(xyz.x,3),round(xyz.z,3),round(-xyz.y,3)],
  direction=[round(direction.x,5),round(direction.z,5),round(-direction.y,5)],
  purpose=purpose,
 ))
def aviation_dots(vertices, rgb, name):
 # Fixture lenses are separate in XY. A 0.95 m radius joins the polygons of the same lens.
 accepted=[]
 for x,y,z in sorted(vertices.tolist(),key=lambda pt:-pt[2]):
  if any((x-u)**2+(y-v)**2<.95**2 for u,v,_ in accepted):continue
  accepted.append((x,y,z))
  airfield_markers.append([round(x,3),round(z+.05,3),round(-y,3),
    *map(float,rgb),name.endswith('/ 13'),name.endswith('/ 31'),
    name.startswith('空港 · 末端红')])

def add(group,pts,idx,color):
 pts=np.ascontiguousarray(pts[:,[0,2,1]],dtype='<f4');pts[:,2]*=-1
 color=np.broadcast_to(np.array(color,dtype=float),(len(pts),3))
 groups[group].append((pts,np.asarray(idx,dtype='uint32').reshape(-1,3),np.round(np.clip(color,0,1)*255).astype('uint8')))
def attr(obj,key,n):
 a=np.empty(len(obj)*n,'f');obj.foreach_get(key,a);return a.reshape(-1,n)
g=bpy.data.objects['基岩、海岸阶地与东部雪原'];me=g.data
grid=np.r_[np.arange(0,751,2)];q=attr(me.vertices,'co',3).reshape(751,751,3)[grid[:,None],grid].reshape(-1,3);N=len(grid);i=np.arange(N*N).reshape(N,N)[:-1,:-1].ravel()
weights=np.array([attr(me.attributes['地表占比 · '+n].data,'value',1).reshape(751,751)[grid[:,None],grid].ravel() for n in ['裸露基岩','冰碛砾地','冻融构造土','苔原土被']]);colors=weights.T@np.array([[.27,.285,.28],[.48,.407,.297],[.38,.393,.315],[.265,.344,.21]])
colors*= (1+.013*np.sin(q[:,0]/32+q[:,1]/29)+.009*np.cos(q[:,0]/17-q[:,1]/35))[:,None]
add('Terrain',q,np.stack([i,i+1,i+N+1,i,i+N+1,i+N],axis=1),colors)
# Original ice and full settlement meshes, flatten Blender collection instances, omit off-map scenery and tiny botanical specimens.
allow=['候机楼 ·','飞行情报塔 ·','航空目视灯具 ·','公共照明 ·','15 建筑、路灯','02 水面','03 公共步道','04 镇区','05 郊外','06 双向','10 西岸','11 冰川','交通 ·','北坡教堂','外海漂冰','岩肩种子库 ·','灯市摊位','住宅环巷','工艺院','公共台地','日常镇街','滨港作业带','西台地科考营','季节性雪屋']
def collect(o,M,grp):
 if o.type=='LIGHT' and o.name.startswith(('灯罩下射光束','隧道 · 内嵌拱灯','设施照明 · 门廊下照','门前与桩灯 · 暖光')):
  if M.translation.length>100:lamp_position(o,M,'road' if o.data.type=='SPOT' else 'entrance')
  return
 if o.instance_collection:
  A=M@Matrix.Translation(-o.instance_collection.instance_offset)
  for ch in o.instance_collection.objects:
   if not ch.hide_render:collect(ch,A@ch.matrix_world,grp)
  return
 if o.type not in {'MESH','CURVE','FONT'}:return
 if o.type=='MESH':
  me=o.data
 else:
  evaluated=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
  me=evaluated.to_mesh()
 try:
  collect_mesh(o,me,M,grp)
 finally:
  if o.type!='MESH':evaluated.to_mesh_clear()
def collect_mesh(o,me,M,grp):
 me.calc_loop_triangles()
 if not len(me.loop_triangles):return
 vs=attr(me.vertices,'co',3);m=np.array(M);vs=vs@m[:3,:3].T+m[:3,3]
 ids=np.empty(len(me.loop_triangles)*3,'i');me.loop_triangles.foreach_get('vertices',ids);ids=ids.reshape(-1,3);mi=np.empty(len(ids),'i');me.loop_triangles.foreach_get('material_index',mi)
 for k in np.unique(mi):
  mat=me.materials[k] if k<len(me.materials) else None
  rgb=np.array(mat.diffuse_color[:3] if mat else [.35,.40,.40])
  if grp=='Sea':rgb=[.08,.245,.30]
  if grp=='Berg' and '远海冰山' not in (mat.name if mat else ''):rgb=np.maximum(rgb,[.24,.48,.57])
  if grp=='Glacier':rgb=[.57,.79,.82] if '碎石' not in o.name else [.38,.36,.30]
  inds,rev=np.unique(ids[mi==k],return_inverse=True)
  kind=light_kind(o,mat)
  add(('Lit-'+kind) if kind else grp,vs[inds],rev,rgb)
  if kind=='Aviation':aviation_dots(vs[inds],rgb,mat.name)
for o in s.objects:
 c=o.users_collection[0].name
 if c.startswith('季节性雪屋') or o.hide_render:continue
 if not c.startswith(tuple(allow)) and not (o.instance_collection and '铸铁码头灯' in o.instance_collection.name):continue
 if o.name.startswith(('样本归档','岩内冷藏','岩内廊道','冰缘薄碛')):continue
 grp='Berg' if c.startswith('外海漂冰') else 'Structures' if c.startswith(('候机楼','飞行情报塔','住宅环巷','工艺院','公共台地','北坡教堂','岩肩种子库','日常镇街','滨港作业带','西台地科考营')) else 'Sea' if o.name=='方形图幅内海面' else 'Glacier' if o.name.startswith('北界冰舌') else 'Coast'
 if c=='交通 · 主干与徒步网' and o.animation_data and '主干' not in o.name and '跑道' not in o.name:grp='Footpaths'
 if any(t in o.name for t in ['车道','机坪','栈桥','人行','地坪','道面','主干','驿路']) and grp=='Coast':
  grp='Roads'
 collect(o,o.matrix_world,grp)
# Compact seasonal plants reuse the real native mesh on sampled near-route tundra, including flowers and red leaves.
rng=np.random.default_rng(801)
near=[(850,1320),(660,1370),(550,1590),(840,1610),(35,1610),(510,550),(-450,1570)]
plants=[o for c in ['真实地表 · 局部岩形与植株','季节植群 · 远郊及岛屿补布'] for o in bpy.data.collections[c].objects if o.instance_collection and '苔原土被' in o.instance_collection.name]
pick=[]
for x,y in near:
 candidates=[o for o in plants if (o.location.x-x)**2+(o.location.y-y)**2<155**2]
 if candidates:pick.extend(rng.choice(candidates,min(29,len(candidates)),replace=False))
pick={o.name:o for o in pick}.values()
for frame,season in [(97,'spring'),(98,'summer'),(99,'autumn')]:
 s.frame_set(frame)
 for o in pick:
  for child in o.instance_collection.objects:
   if child.name.startswith(('苔原土被','苔垫','匍匐柳')) or child.hide_render:continue
   collect(child,o.matrix_world@child.matrix_world,'Plants-'+season)
s.frame_set(103)
for o in bpy.data.collections['季节性雪屋 · 可切换'].objects:
 collect(o,o.matrix_world,'Snowhouses')
for o in bpy.data.collections['01 地形 · 四米网格'].objects:
 if o.name in ('地表剖面','沙盘底板','剖面基线'):collect(o,o.matrix_world,'Base')
# GLB with indexed meshes and linear vertex colours, portable with all textures embedded.
doc={'asset':{'version':'2.0','generator':'Frosthavn Blender atlas export'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'buffers':[],'bufferViews':[],'accessors':[],'materials':[{'pbrMetallicRoughness':{'metallicFactor':0,'roughnessFactor':.9},'doubleSided':True}]};buf=bytearray()
def write(a,dtype,typ,mode,normalized=False,bounds=False):
 while len(buf)%4:buf.append(0)
 a=np.ascontiguousarray(a);off=len(buf);buf.extend(a.tobytes());v=len(doc['bufferViews']);doc['bufferViews'].append(dict(buffer=0,byteOffset=off,byteLength=a.nbytes,target=mode))
 acc=dict(bufferView=v,componentType=dtype,count=len(a),type=typ)
 if normalized:acc['normalized']=True
 if bounds:acc.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
 doc['accessors'].append(acc);return len(doc['accessors'])-1
for n,parts in groups.items():
 vs=np.concatenate([p[0] for p in parts]);ix=np.concatenate([p[1].ravel()+off for p,off in zip(parts,np.cumsum([0]+[len(p[0]) for p in parts[:-1]],dtype=np.uint32))]).astype('<u4')
 rgb=np.concatenate([p[2] for p in parts]);rgba=np.column_stack([rgb,np.full(len(rgb),255,'uint8')])
 prim=dict(attributes={'POSITION':write(vs,5126,'VEC3',34962,bounds=True),'COLOR_0':write(rgba,5121,'VEC4',34962,True)},indices=write(ix,5125,'SCALAR',34963),material=0)
 j=len(doc['meshes']);doc['meshes'].append(dict(name=n,primitives=[prim]));doc['nodes'].append(dict(name=n,mesh=j));doc['scenes'][0]['nodes'].append(j);print(n,len(ix)//3)
# Author triplanar ground colours once from the same mapped vegetation weights.
mask=weights[3].astype(float)
patch=np.clip(.5+.22*np.sin(q[:,0]*.054+q[:,1]*.016)+.14*np.cos(q[:,0]*.027-q[:,1]*.047)+.10*np.sin(q[:,0]*.135-q[:,1]*.062),0,1)
fall=np.stack([np.interp(patch,[0,.47,.8,1],v) for v in [[.25,.39,.55,.25],[.065,.145,.32,.23],[.037,.050,.075,.085]]],axis=1)
spring=colors*(1-mask[:,None]*.43)+np.array([.30,.38,.154])*mask[:,None]*.43
autumn=colors*(1-mask[:,None]*.90)+fall*mask[:,None]*.90
steep=np.hypot(*np.gradient(q[:,2].reshape(N,N),8)).ravel()
dry=q[:,2]>.43
winter=np.clip((.96-.53*np.clip(steep,0,1)-.36*weights[0])*dry,0,.96)
springSnow=np.clip((patch-.58)*3.5,0,.82)*dry*(1-np.clip(steep,0,1))
spring=spring*(1-springSnow[:,None])+np.array([.72,.81,.82])*springSnow[:,None]
winterColor=colors*(1-winter[:,None])+np.array([.84,.90,.91])*winter[:,None]
terrainAttrs=doc['meshes'][0]['primitives'][0]['attributes']
for season,palette in [('SPRING',spring),('AUTUMN',autumn),('WINTER',winterColor)]:
 terrainAttrs['_'+season]=write(np.column_stack([np.round(palette.clip(0,1)*255).astype('uint8'),np.full(len(q),255,'uint8')]),5121,'VEC4',34962,True)
doc['scenes'][0]['extras']={'terrainGrid':N,'lighting':lighting,'aviationMarkers':airfield_markers,'walkStarts':{'market':[848,1323,110],'port':[955,1232,120],'air':[-549.8,1533.4,-14],'station':[25,1595,0],'church':[675,1353,0],'lookout':[855,1614,165]}}
doc['buffers']=[dict(byteLength=len(buf))];j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*(-len(j)%4);buf+=b'\0'*(-len(buf)%4)
raw=struct.pack('<4sII',b'glTF',2,28+len(j)+len(buf))+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(buf),b'BIN\0')+buf
assert len(airfield_markers)>100 and sum(l['purpose']=='road' for l in lighting)>=19
assert {'Lit-Windows','Lit-Aviation','Lit-Fixtures','Lit-Beacon'}.issubset(groups)
print('Light positions',len(lighting),'aviation heads',len(airfield_markers),flush=True)
(dest/'frosthavn-polar-lights.glb.gz').write_bytes(gzip.compress(raw,compresslevel=7,mtime=0))
