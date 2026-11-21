"""Build original folding-paper airline CG. Native game footage is never used here."""
import bpy, math, os, sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=20
scene.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL';prefs.refresh_devices()
for device in prefs.devices:device.use=device.type=='METAL'
scene.cycles.device='GPU'
scene.render.resolution_x=1280;scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.render.fps=30;scene.frame_start=1;scene.frame_end=180
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.world.color=(.075,.095,.115)

def mat(name,color,rough=.5,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 m.node_tree.nodes.clear()
 p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.name='Principled BSDF'
 out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface'])
 p.inputs['Base Color'].default_value=(*color,1)
 p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 return m
paper=mat('warm cotton paper',(.88,.84,.74),.76)
n=paper.node_tree.nodes;links=paper.node_tree.links;p=n.get('Principled BSDF')
tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'public/ticket-print.png'));links.new(tex.outputs['Color'],p.inputs['Base Color'])
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=380;noise.inputs['Roughness'].default_value=.72
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.018
links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
navy=mat('deep blue set',(.018,.044,.059),.47)
amber=mat('warm copper route',(.7,.25,.07),.28,.5)
pp=amber.node_tree.nodes.get('Principled BSDF');pp.inputs['Emission Color'].default_value=(.65,.17,.02,1);pp.inputs['Emission Strength'].default_value=.17
ivory=mat('folded aircraft',(.045,.115,.145),.5)

# Articulated accordion fold, each panel retains its physical length.
cuts=[-6,-4.8,-2.5,-1.4,.2,1,2.8,4.2,6]
angles=[-.16,.36,-.4,.7,-.8,.68,-.35,.12]
def smooth(a,b,v):
 u=max(0,min(1,(v-a)/(b-a)));return u*u*(3-2*u)
def point(x,y,t):
 phase=smooth(1.05,4.6,t);px=cuts[0];pz=0
 for i in range(len(cuts)-1):
  length=max(0,min(x,cuts[i+1])-cuts[i]);a=angles[i]*phase
  px+=length*math.cos(a);pz+=length*math.sin(a)
  if x<=cuts[i+1]:break
 # A gentle sheet-edge curl, lifted from the tabletop; no flat image push.
 pz+=.10+phase*(.24+.12*(y/2.44)**2)
 return Vector((px+phase*.23,y,pz))

NX,NY=240,98
verts=[];uvs=[];faces=[]
for j in range(NY+1):
 for i in range(NX+1):
  x=-6+12*i/NX;y=-2.44+4.88*j/NY
  verts.append(tuple(point(x,y,0)));uvs.append((i/NX,j/NY))
for j in range(NY):
 for i in range(NX):
  x=-6+12*(i+.5)/NX;y=-2.44+4.88*(j+.5)/NY
  # Real geometric slots at the two stub perforations.
  if (abs(x-3)<.026 or abs(x-4.5)<.026) and abs((y+2.44)% .25-.125)<.055:continue
  a=j*(NX+1)+i;faces.append((a,a+1,a+NX+2,a+NX+1))
mesh=bpy.data.meshes.new('articulated ticket mesh');mesh.from_pydata(verts,[],faces);mesh.update()
ticket=bpy.data.objects.new('boarding pass becomes paper fjord',mesh);bpy.context.collection.objects.link(ticket);ticket.data.materials.append(paper)
uv=mesh.uv_layers.new(name='Print UV')
for poly in mesh.polygons:
 for idx in poly.loop_indices:uv.data[idx].uv=uvs[mesh.loops[idx].vertex_index]
ticket.shape_key_add(name='Basis');fold=ticket.shape_key_add(name='Folded paper')
for i,v in enumerate(fold.data):
 x=-6+12*(i%(NX+1))/NX;y=-2.44+4.88*(i//(NX+1))/NY;v.co=point(x,y,5)
for f,value in [(1,0),(31,0),(139,1),(180,1)]:fold.value=value;fold.keyframe_insert(data_path='value',frame=f)
sol=ticket.modifiers.new('physical paper thickness','SOLIDIFY');sol.thickness=.018
bevel=ticket.modifiers.new('soft cut edges','BEVEL');bevel.width=.008;bevel.segments=2

# A flight line is drawn through real 3D space over the folding terrain.
curve=bpy.data.curves.new('drawn space route','CURVE');curve.dimensions='3D';curve.resolution_u=32
sp=curve.splines.new('POLY');sp.points.add(120)
def route(u):return Vector((-4.7+9.1*u,-.8+1.7*math.sin(u*math.pi),1.1+1.9*math.sin(u*math.pi*.85)))
for i,pnt in enumerate(sp.points):pnt.co=(*route(i/120),1)
curve.bevel_depth=.018;curve.bevel_resolution=4
obj=bpy.data.objects.new('copper flight path',curve);bpy.context.collection.objects.link(obj);obj.data.materials.append(amber)
for f,v in [(1,0),(80,0),(160,1),(180,1)]:curve.bevel_factor_end=v;curve.keyframe_insert(data_path='bevel_factor_end',frame=f)

# A folded paper aircraft, deliberately abstract rather than a game replica.
plane_mesh=bpy.data.meshes.new('original folded aircraft')
plane_mesh.from_pydata([(0.48,0,0),(-.28,0,.05),(-.40,.5,-.08),(-.18,.05,.10),(-.40,-.5,-.08),(-.18,-.05,.10)],[],[(0,1,3),(0,3,2),(0,5,1),(0,4,5)])
plane=bpy.data.objects.new('paper aircraft',plane_mesh);bpy.context.collection.objects.link(plane);plane.data.materials.append(ivory)
sol=plane.modifiers.new('aircraft paper thickness','SOLIDIFY');sol.thickness=.012
for f in range(1,181):
 t=(f-1)/30;u=smooth(2.6,5.4,t);pos=route(u)
 plane.location=pos;nextp=route(min(1,u+.002));direction=nextp-pos
 plane.rotation_euler=(0,-.1,math.atan2(direction.y,direction.x))
 plane.scale=(.02,.02,.02) if t<2.6 else (.95,.95,.95)
 plane.keyframe_insert(data_path='location',frame=f);plane.keyframe_insert(data_path='rotation_euler',frame=f);plane.keyframe_insert(data_path='scale',frame=f)

bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.04));bpy.context.object.name='matte blue stage';bpy.context.object.data.materials.append(navy)
def area(name,loc,power,color,size,target=(0,0,0)):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color;o.data.shape='DISK';o.data.size=size
 o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('large soft northern key',(-3,-2,10),1700,(.75,.86,1),8)
area('low warm grazing light',(6,-3,3),850,(1,.65,.36),6)
area('cold edge separation',(-4,6,5),1300,(.46,.70,1),7)

bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='PERSP';cam.data.lens=49
for f,loc,target in [(1,(.3,-10.8,15.8),(0,0,0)),(30,(.3,-10.8,15.8),(0,0,0)),(90,(1.2,-12,14.8),(0,.1,.35)),(180,(2.2,-12.5,14),(0,.2,.6))]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f)

(ROOT/'renders/cg-frames').mkdir(parents=True,exist_ok=True)
scene.render.filepath=str(ROOT/'renders/cg-frames/frame-')
scene['asset_role']='Original airline theme CG; no gameplay claim.'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'src/airline-fold.blend'))
scene.frame_set(int(os.environ.get('CG_FRAME','1')))
if os.environ.get('CG_ANIMATE')=='1':
 scene.render.engine='BLENDER_EEVEE'
 if hasattr(scene.eevee,'taa_render_samples'):scene.eevee.taa_render_samples=16
 bpy.ops.render.render(animation=True)
else:
 scene.render.filepath=str(ROOT/f'renders/airline-cg-frame-{scene.frame_current:03d}.png')
 bpy.ops.render.render(write_still=True)
