"""Reuse project-owned rock/wood materials with deterministic minimum-cut quilting.

No outside images or generated bitmap service. Source images remain untouched.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[1]


def seam(error):
    """Minimum-cost vertical seam through an overlap, one column per row."""
    h,w=error.shape; cost=error.copy(); parent=np.zeros((h,w),dtype=np.int16)
    for y in range(1,h):
        previous=np.pad(cost[y-1],(1,1),constant_values=np.inf)
        candidates=np.stack([previous[:-2],previous[1:-1],previous[2:]])
        offset=np.argmin(candidates,axis=0)-1
        parent[y]=np.arange(w)+offset
        cost[y]+=np.min(candidates,axis=0)
    path=np.zeros(h,dtype=np.int16);path[-1]=np.argmin(cost[-1])
    for y in range(h-1,0,-1):path[y-1]=parent[y,path[y]]
    return path


def rock_ground(season):
    source=Image.open(ROOT/f'ContentPack/assets/maps/Tundra_{season}_scene.png').convert('RGB')
    # Only the western bare-rock bank. Exclude the stream, bridge, route signs,
    # supply box and northern lookout. Horizontal reflections keep lighting up.
    root=ET.parse(ROOT/f'ContentPack/assets/maps/Tundra_{season}.tmx').getroot()
    water_gids=set()
    for ts in root.findall('tileset'):
        for tile in ts.findall('tile'):
            if any(p.get('name')=='Water' for p in tile.findall('./properties/property')):
                water_gids.add(int(ts.get('firstgid'))+int(tile.get('id')))
    back=np.array([int(v) for v in root.find("./layer[@name='Back']/data").text.strip().split(',')]).reshape(48,64)
    wet=np.isin(back,list(water_gids))
    candidates=[];block=128;overlap=32;stride=96
    for x in [0,80,160,240]:
        for y in [0,96,192,288,384,480,576,640]:
            # Source ponds are not scenery for this dry inland camp. Test
            # native Water metadata, not a blue-pixel guess (rocks can be blue).
            if wet[y//16:(y+block+15)//16,x//16:(x+block+15)//16].any():continue
            patch=np.asarray(source.crop((x,y,x+block,y+block)))
            candidates.extend([patch,patch[:,::-1].copy()])
    if not candidates:raise ValueError('No dry tundra material; refusing to paint false water')
    out=np.zeros((800,1088,3),dtype=np.uint8)
    rng=np.random.default_rng(755)
    for y in range(0,673,stride):
        for x in range(0,961,stride):
            old=out[y:y+block,x:x+block]
            scores=[]
            for p in candidates:
                score=0
                if x:score+=np.mean((old[:,:overlap].astype(float)-p[:,:overlap])**2)
                if y:score+=np.mean((old[:overlap].astype(float)-p[:overlap])**2)
                scores.append(score)
            best=np.argsort(scores)[:3];p=candidates[int(rng.choice(best))].copy()
            keep=np.zeros((block,block),dtype=bool)
            if x:
                e=np.mean((old[:,:overlap].astype(float)-p[:,:overlap])**2,axis=2)
                cut=seam(e);keep[:,:overlap]|=np.arange(overlap)[None,:]<cut[:,None]
            if y:
                e=np.mean((old[:overlap].astype(float)-p[:overlap])**2,axis=2)
                cut=seam(e.T);keep[:overlap]|=np.arange(overlap)[:,None]<cut[None,:]
            p[keep]=old[keep];out[y:y+block,x:x+block]=p
    return Image.fromarray(out[:768,:1024])


def finish_camp(season,base,painted):
    terrain=rock_ground(season)
    mask=ImageChops.difference(base,painted).convert('L').point(lambda p:255 if p else 0)
    # The low-resolution planning ribbon only defines geometry. Remove it
    # before applying the native-pixel snow trail, including its hard border.
    ma=np.asarray(mask).copy();pa=np.asarray(painted)
    for color in ['#97accb','#c4d7ed','#dce8f4','#65777b','#b6b9a6','#c4c6b1','#acbfda','#bdcfe6','#8b998f','#a4ab99']:
        rgb=np.array([int(color[i:i+2],16) for i in [1,3,5]])
        ma[np.all(pa==rgb,axis=2)]=0
    mask=Image.fromarray(ma)
    overlay=painted.resize(terrain.size,Image.Resampling.NEAREST)
    terrain.paste(overlay,(0,0),mask.resize(terrain.size,Image.Resampling.NEAREST).filter(ImageFilter.GaussianBlur(1.2)))
    # A soft, irregular trodden snow/gravel route, rather than rectangular
    # repeated patches or a paved ribbon. Geometry still follows the real route.
    paths=[[(0,24),(12,24),(20,25),(31,26),(44,25),(54,23)],
           [(14,24),(14,37),(21,37)],[(49,25),(49,37),(43,37)],[(31,26),(31,24)]]
    pathmask=Image.new('L',terrain.size);pd=ImageDraw.Draw(pathmask)
    for path in paths:pd.line([(x*16+8,y*16+8) for x,y in path],fill=255,width=44,joint='curve')
    pathmask=pathmask.filter(ImageFilter.GaussianBlur(9))
    rng=np.random.default_rng(750);yy,xx=np.indices((768,1024))
    coarse=Image.fromarray(rng.integers(0,255,(48,64),dtype=np.uint8)).resize((1024,768),Image.Resampling.BICUBIC)
    value=(np.asarray(coarse).astype(float)-128)*.065+rng.integers(-3,4,xx.shape)+np.sin(yy*.16+xx*.015)*2
    basecolor=np.array([191,206,239] if season in ['winter','spring'] else [161,166,142])
    material=Image.fromarray(np.clip(basecolor+value[:,:,None],0,255).astype('uint8'))
    terrain.paste(material,(0,0),pathmask)
    d=ImageDraw.Draw(terrain)
    import math
    for path in paths:
        pts=[(x*16+8,y*16+8) for x,y in path]
        for a,b in zip(pts,pts[1:]):
            length=math.dist(a,b);dx=(b[0]-a[0])/max(1,length);dy=(b[1]-a[1])/max(1,length)
            for i,step in enumerate(range(8,int(length),11)):
                side=3 if i%2 else -3
                px=int(a[0]+dx*step-dy*side);py=int(a[1]+dy*step+dx*side)
                d.ellipse((px-2,py-2,px+1,py+2),fill='#a7bbdf' if season in ['spring','winter'] else '#8c977f')
                d.line((px-1,py+2,px+2,py+2),fill='#dce6f7' if season in ['spring','winter'] else '#b3b7a2')
    if season=='winter':
        for cx in [19*16+8,44*16+8]:snow_dome(terrain,cx,33*16)
    # The red hut reuses the town's authored seasonal timber/corrugated metal
    # material, aligned to the new, independently authored research-station door.
    town=Image.open(ROOT/f'ContentPack/assets/maps/Town_{season}_scene.png').convert('RGB')
    hut=town.crop((186,190,378,352));alpha=Image.new('L',hut.size);ad=ImageDraw.Draw(alpha)
    # Polygon traces the shared building silhouette; don't import its old paths.
    ad.polygon([(9,54),(12,34),(88,16),(91,0),(109,0),(113,15),(157,25),(175,49),(180,123),(186,144),(123,161),(49,156),(13,143)],fill=255)
    terrain.paste(hut,(394,232),alpha)
    # Weather mast identifies this building independently of the town inn.
    d=ImageDraw.Draw(terrain);d.line((607,264,607,369),fill='#394c60',width=3)
    d.line((593,276,622,276),fill='#677f90',width=2)
    d.polygon([(608,261),(634,267),(608,272)],fill='#c58b62')
    return terrain.convert('RGBA')


def snow_dome(image,cx,cy):
    """Native-pixel snow courses: cool side shadow and warm-white upper face."""
    d=ImageDraw.Draw(image);rr=np.random.default_rng(cx)
    # Retain the already painted shadow, replace the flat dome and tunnel.
    for y in range(-86,19):
        ny=(y+34)/52
        for x in range(-68,69):
            nx=x/68
            if nx*nx+ny*ny>1:continue
            light=np.clip(.86-.12*nx-.10*ny,0,1)
            base=np.array([149,177,216])+(np.array([241,246,255])-np.array([149,177,216]))*light
            course=(y+86+6*nx*nx)/14
            row=int(course)
            mortar=course%1<.075 or ((x+78+(row%2)*13)%26<1.5 and course%1<.93)
            if mortar:base-=np.array([23,24,18])
            base+=rr.integers(-3,4)
            image.putpixel((cx+x,cy+y),tuple(np.clip(base,0,255).astype(int)))
    d=ImageDraw.Draw(image)
    d.ellipse((cx-19,cy-20,cx+31,cy+30),fill='#9db7d6',outline='#7898bc',width=2)
    d.arc((cx-16,cy-18,cx+27,cy+29),180,345,fill='#d4e3f5',width=5)
    d.rounded_rectangle((cx-10,cy-6,cx+20,cy+29),radius=13,fill='#314d68')
    d.rectangle((cx-10,cy+10,cx+20,cy+29),fill='#314d68')
    d.line((cx-10,cy+29,cx+20,cy+29),fill='#cbdcf0',width=2)
    d.ellipse((cx+14,cy-79,cx+18,cy-76),fill='#718cae')


def research_interior():
    # Shared local building craft, rather than a new oversized flat furniture
    # style. Keep this reuse explicit; research progression and staff are later.
    image=Image.open(ROOT/'ContentPack/assets/maps/Guesthouse_spring_scene.png').convert('RGB')
    a=np.asarray(image).copy()
    # Change the left bed's red wool to blue-green; retain its woven highlights.
    region=a[80:136,38:95];sel=(region[:,:,0]>region[:,:,1]*1.25)&(region[:,:,0]>region[:,:,2]*1.18)
    old=region[sel].astype(float);region[sel]=np.clip(old*np.array([.58,1.17,1.35]),0,255)
    image=Image.fromarray(a);d=ImageDraw.Draw(image)
    # Paper weather log and specimen trays on the existing right-hand desk.
    d.polygon([(281,77),(301,79),(300,91),(279,89)],fill='#ded9b8')
    d.line((283,84,286,81,291,86,296,82),fill='#597884')
    for x in [307,314,321]:
        d.rectangle((x,83,x+4,89),fill='#778d8b',outline='#c7bea0');d.point((x+2,85),fill='#e5ddbc')
    return image.convert('RGBA')
