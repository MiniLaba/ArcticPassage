"""R02's two missing outdoor regions and fourth main interior, drawn in code.

The town, original routes and location IDs are retained. New connections are
added to existing reachable aprons, with all ice/cliffs physically blocked.
"""
from pathlib import Path
import copy, json, math, random
import xml.etree.ElementTree as E
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[1]; P = R/'ContentPack'; M = P/'assets/maps'
SEASONS = ('spring','summer','fall','winter'); TAG = 'R02 frontier: '


def dump(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def rock(d, rr, x, y, w, h, snow):
    d.ellipse((x-4,y+h-2,x+w+8,y+h+13),fill='#8fabc1' if snow else '#61777c')
    contour=[(x,y+h),(x+5,y+9),(x+w//3,y),(x+w*3//4,y+3),(x+w,y+h-1),(x+w-5,y+h+9),(x+8,y+h+10)]
    d.polygon(contour,fill='#475765',outline='#304455')
    for sx in range(x+7,x+w-4,4):
        sy=y+h+rr.randrange(-4,4)
        d.line((sx,sy-10,sx-3,sy+5),fill=rr.choice(('#6b8191','#9ba9ac','#566b7d')))
        d.point((sx-2,sy+5),fill='#2c4053')
    top=[(x+1,y+h-3),(x+7,y+6),(x+w//3,y-2),(x+w*3//4,y+1),(x+w-3,y+h-4),(x+w//2,y+h-7),(x+13,y+h-5)]
    d.polygon(top,fill='#dfebef' if snow else '#a0a78d')
    d.line(top[:4],fill='#f3f4e7' if snow else '#c0bba0',width=2)
    if not snow:
        for _ in range(w//2):
            sx=rr.randrange(x+8,x+w-5);sy=rr.randrange(y+5,y+h-5)
            d.line((sx,sy,sx+2,sy),fill=rr.choice(('#a5a47b','#798576','#c3b68d')))


def trail(im, mask, points, season, width=3):
    d=ImageDraw.Draw(im);md=ImageDraw.Draw(mask);snow=season in ('winter','spring')
    md.line(points,fill=255,width=width)
    pts=[(x*8+4,y*8+4) for x,y in points]
    for thick,col in [(width*8+6,'#8da5ba' if snow else '#607776'),(width*8,'#c1d5e1' if snow else '#a6aa92'),(width*8-8,'#e2e9e6' if snow else '#c2bda2')]:
        d.line(pts,fill=col,width=thick,joint='curve')
    for a,b in zip(pts,pts[1:]):
        length=math.dist(a,b)
        for n in range(3,int(length),6):
            t=n/length;x=round(a[0]+(b[0]-a[0])*t);y=round(a[1]+(b[1]-a[1])*t)
            if season=='winter':
                d.line((x-4,y,x-3,y+2),fill='#a7bccb');d.line((x+4,y,x+5,y+2),fill='#a7bccb')
            else:d.line((x-2,y,x+1,y),fill='#a4aca0' if snow else '#8c9685')


def marker(d,x,y,kind='sign',snow=False):
    x*=8;y*=8
    if kind=='sign':
        d.rectangle((x+3,y+4,x+5,y+15),fill='#665b4d')
        d.rectangle((x-3,y-2,x+12,y+7),fill='#304c5e',outline='#b7bca5')
        d.line((x,y+1,x+8,y+1),fill='#e1cca0');d.line((x,y+4,x+5,y+4),fill='#9eaeac')
    else:
        d.rectangle((x+3,y-11,x+5,y+7),fill='#5b6263')
        d.rectangle((x+1,y-9,x+7,y-3),fill='#bb6c4c' if kind=='post' else '#e8c481')
        d.line((x,y-11,x+8,y-11),fill='#edf3ed' if snow else '#364e60',width=2)


def outdoor(name, season):
    rr=random.Random(21079 if name=='SledTrail' else 21080);snow=season in ('spring','winter')
    im=Image.new('RGB',(512,384),'#cedfe8' if snow else '#8f998e' if season=='summer' else '#948f7e');d=ImageDraw.Draw(im)
    palette=('#e4eeeb','#bfd0df','#a7bdd0','#d4e1e8') if snow else ('#a4aa91','#7d8a7c','#b7b399','#6f827b') if season=='summer' else ('#9e947a','#b3a58a','#827f72','#687b79')
    for _ in range(16000):
        x,y=rr.randrange(512),rr.randrange(384);d.line((x,y,x+rr.randrange(1,5),y),fill=rr.choice(palette))
    # Exposed gneiss ridges, not an evenly spaced field of generic boulders.
    for ridge in range(5):
        for n in range(5):
            x=-40+n*120+rr.randrange(-25,25);y=25+ridge*76+rr.randrange(-15,15)
            rock(d,rr,x,y,rr.randrange(70,116),rr.randrange(22,34),snow)
    mask=Image.new('L',(64,48));water=set();actions={};roofs=[]
    if name=='SledTrail':
        # A broad, marked switchback and a quiet work yard beneath the ridge.
        trail(im,mask,[(12,47),(12,41),(19,35),(24,29),(25,24),(32,18),(32,0)],season)
        trail(im,mask,[(25,24),(40,24),(52,24),(63,24)],season)
        md=ImageDraw.Draw(mask);md.rectangle((20,24,30,29),fill=255)
        d=ImageDraw.Draw(im)
        d.rounded_rectangle((156,185,250,243),radius=9,fill='#bed0da' if snow else '#a8ad95',outline='#849da8')
        # Low wind shelter, timber lashing and covered supply cases.
        d.rectangle((170,169,214,196),fill='#a75549',outline='#364d5a')
        for y in range(173,195,4):d.line((171,y,213,y),fill='#bd7560')
        d.polygon([(165,169),(191,151),(219,169),(215,172),(168,172)],fill='#e2ece9' if snow else '#576b75',outline='#3c5360')
        d.rectangle((186,177,197,196),fill='#485665',outline='#bdad87')
        d.rectangle((176,177,181,184),fill='#ecc985')
        for x in (165,216,235):
            d.rectangle((x,227,x+13,237),fill='#668286',outline='#354e5c');d.line((x+2,229,x+11,229),fill='#aabdb8')
        # Parked sled: curved runners, cross slats and lashings at native scale.
        for y in (210,220):
            d.line((216,y,248,y,252,y-4),fill='#6d5744',width=2)
            d.line((217,y-1,247,y-1,251,y-5),fill='#c5a274')
        for x in range(221,246,4):d.line((x,209,x,220),fill='#a58860',width=2)
        d.line((217,207,216,221),fill='#554f43',width=2)
        # Markers are outside the clear two-person walking lane.
        for x,y in [(11,43),(17,37),(25,31),(27,22),(33,15),(33,7),(41,22),(54,22)]:marker(d,x,y,'post',snow)
        actions={(23,24):'Message ArcticPassage_SledRoute',(29,27):'Message ArcticPassage_SledPending'}
        for x,y in actions:marker(d,x,y,snow=snow)
        warps=[(12,47,'Tundra',26,4),(32,0,'Glacier',32,44),(63,24,'WinterCamp',49,24)]
        points={'spawn':[12,42],'junction':[25,24],'station_approach':[28,27],'glacier_departure':[32,2],'camp_departure':[61,24]}
        # Shelter bases are blocked separately from the upper facade.
        roofs=[(20,18,27,23)]
    else:
        # Valley ice tongue: plateau snow, blue fractured front, basal moraine.
        d=ImageDraw.Draw(im)
        outline=[(75,0),(438,0),(443,67),(421,93),(451,126),(426,153),(431,174),(391,189),(349,179),(314,197),(268,181),(225,196),(179,182),(139,193),(97,176),(108,151),(81,129),(98,96),(78,64)]
        d.polygon([(x+7,y+13) for x,y in outline],fill='#536f7e')
        d.polygon(outline,fill='#93b9cb',outline='#527d99')
        for x in range(98,428,11):
            base=179+int(8*math.sin(x/19));top=121+rr.randrange(-15,15)
            d.polygon([(x,top),(x+9,top-6),(x+12,base),(x+2,base+6)],fill=rr.choice(('#8fb5ca','#c8e0e5','#a9d0dc','#6f9bb6')))
            d.line((x+3,top+3,x+6,base),fill='#e2f0eb')
            if x%3==0:d.line((x+9,top+6,x+11,base-2),fill='#4d7d9e',width=2)
        top=[(75,0),(438,0),(443,67),(421,93),(451,126),(426,139),(384,131),(343,147),(311,137),(268,151),(223,139),(187,150),(145,137),(109,144),(81,129),(98,96),(78,64)]
        d.polygon(top,fill='#dfeeed',outline='#b5d1da')
        for j in range(16):
            x=98+j*21;y=40+rr.randrange(-20,36)
            d.line((x,y,x+13,y+28,x+9,y+53,x+22,y+76),fill='#8db6cc',width=2)
            d.line((x+3,y,x+16,y+28),fill='#f0f4e9')
        # Meltwater is scenic and never a source of invented marine fish.
        stream=[(35,25),(39,29),(43,34),(46,40),(52,47)]
        d.line([(x*8+4,y*8+4) for x,y in stream],fill='#354f65',width=22,joint='curve')
        d.line([(x*8+4,y*8+4) for x,y in stream],fill='#91b8c1' if not snow else '#bad4df',width=16,joint='curve')
        for n in range(44):
            y=207+n*4;x=285+int(n*2.6)
            d.line((x,y,x+8,y+1),fill='#d1e1da' if not snow else '#e9f0eb')
        trail(im,mask,[(32,47),(32,40),(28,35),(27,29),(31,27),(33,27)],season)
        trail(im,mask,[(28,35),(18,34),(13,31),(11,28)],season)
        ImageDraw.Draw(mask).rectangle((28,26,34,28),fill=255)
        d=ImageDraw.Draw(im)
        # Observation decking: a fixed distance from the calving/rockfall face.
        d.rectangle((223,207,279,228),fill='#8c7b60',outline='#4d5a5d')
        for y in range(209,228,4):d.line((224,y,278,y),fill='#c0aa81')
        d.line((224,207,278,207),fill='#526573',width=2)
        for x in range(225,279,13):d.line((x,201,x,213),fill='#435968',width=2)
        d.line((225,202,278,202),fill='#a7b8b7')
        for x,y in [(31,42),(27,36),(26,30),(18,33),(12,29)]:marker(d,x,y,'post',snow)
        # Survey stakes are datum marks, not collectible ice crystals.
        for x,y in [(21,25),(40,25),(44,33)]:
            px,py=x*8,y*8;d.line((px,py-23,px,py+5),fill='#d1b084',width=2)
            for yy in range(py-22,py+3,6):d.line((px-1,yy,px+1,yy),fill='#ad5948',width=2)
        actions={(30,25):'Message ArcticPassage_GlacierSafety',(10,28):'Message ArcticPassage_Geology'}
        for x,y in actions:marker(d,x,y,snow=snow)
        warps=[(32,47,'SledTrail',32,2)]
        points={'spawn':[32,44],'lookout':[31,27],'sample_approach':[11,28]}
    walk={(x,y) for y in range(48) for x in range(64) if mask.getpixel((x,y))}
    for point in actions:walk.discard(point)
    exits={(x,y) for x,y,*_ in warps}
    walk={p for p in walk if (p[0] not in (0,63) and p[1] not in (0,47)) or p in exits}
    # Native terrain at 16px/tile, two-pixel drawing grain, no photographic filter.
    return im.resize((1024,768),Image.Resampling.NEAREST),walk,actions,warps,points,roofs


def community():
    rr=random.Random(21081);im=Image.new('RGB',(384,288),'#263c4b');d=ImageDraw.Draw(im)
    d.rectangle((16,16,367,254),fill='#a47c53',outline='#544938')
    for y in range(20,69,6):
        d.rectangle((18,y,365,y+4),fill=rr.choice(('#775c44','#87684a','#987653')))
        d.line((18,y,365,y),fill='#af8a5d')
    d.rectangle((17,66,366,75),fill='#554a3c')
    for y in range(76,254,12):
        d.line((18,y,365,y),fill='#6d5944')
        for x in range(18+(y%24)*4,367,68):d.line((x,y,x,y+11),fill='#826a4d')
        for _ in range(14):
            x=rr.randrange(21,361);d.line((x,y+5,x+rr.randrange(2,15),y+5),fill='#b58d5d')
    # Deep window reveals and warm trims; no out-of-place painted summer trees.
    for x in (70,271):
        d.rectangle((x-5,22,x+39,64),fill='#514938',outline='#c2a877')
        d.rectangle((x,25,x+34,59),fill='#7897a5')
        d.polygon([(x,48),(x+10,38),(x+17,44),(x+26,35),(x+34,44),(x+34,59),(x,59)],fill='#bdcfd0')
        d.rectangle((x+15,24,x+18,60),fill='#d5b17a');d.line((x,42,x+34,42),fill='#d5b17a',width=2)
        d.rectangle((x-6,61,x+40,66),fill='#bd9664')
    # Public noticeboard, labelled shelves, thermos and soup counter.
    d.rectangle((34,47,116,89),fill='#624e39',outline='#d2ad70')
    for x,y in [(40,53),(65,52),(90,57)]:
        d.rectangle((x,y,x+17,y+23),fill='#e0d2ae',outline='#968467')
        d.line((x+3,y+7,x+13,y+7),fill='#7d8372');d.line((x+3,y+11,x+11,y+11),fill='#96947d')
        d.point((x+8,y+2),fill='#a45a4d')
    d.rectangle((273,72,350,122),fill='#806248',outline='#4b4539')
    for y in (78,103,121):d.line((275,y,349,y),fill='#bd9a68',width=2)
    for x in range(279,344,12):d.rectangle((x,82,x+6,98),fill=rr.choice(('#b5bdab','#bb7757','#d0b77c','#627e7f')))
    d.rectangle((275,108,286,119),fill='#465d67');d.rectangle((277,106,284,109),fill='#c8d1bc')
    d.ellipse((318,106,339,118),fill='#c9c2a6',outline='#5e5e51');d.ellipse((321,109,336,115),fill='#c8a169')
    # A small insulated fish crate beneath the noticeboard; action is added by weekly orders.
    d.rectangle((46,79,64,94),fill='#354f59',outline='#b3c0b7')
    d.rectangle((47,77,63,81),fill='#9ba99f',outline='#4d6668')
    d.line((49,85,60,85),fill='#cfb888',width=2)
    d.rectangle((51,87,58,90),fill='#273d46')
    # Communal table and four chairs, clearly excluded from collision paths.
    d.rectangle((126,128,235,179),fill='#544b3c')
    d.rectangle((121,120,240,165),fill='#c5a16f',outline='#68513c')
    for y in range(125,165,7):d.line((125,y,237,y),fill='#ab875a')
    d.rectangle((160,122,198,164),fill='#a95e4f');d.line((166,124,166,161),fill='#d2b079');d.line((192,124,192,161),fill='#d2b079')
    for x,y in [(130,130),(212,143)]:d.ellipse((x,y,x+15,y+9),fill='#e3d3ae',outline='#988263')
    d.rectangle((174,130,184,148),fill='#405d6a',outline='#d0bb8e');d.rectangle((178,126,181,130),fill='#c0c3ac')
    for x,y in [(135,102),(215,102),(135,172),(215,172)]:
        d.rectangle((x,y,x+12,y+21),fill='#6e5842',outline='#433f35');d.rectangle((x+2,y+3,x+10,y+15),fill='#bc9865')
    # Woven rugs: a restrained repeated textile geometry, not invented symbols.
    for x,y,w,h in [(42,174,59,48),(266,178,64,43)]:
        d.rectangle((x,y,x+w,y+h),fill='#4e6871',outline='#d0b58a')
        for row in range(y+4,y+h-3,6):
            d.line((x+3,row,x+w-3,row),fill='#a97356' if row%12 else '#b9c4ad',width=2)
        for xx in range(x+5,x+w,8):d.line((xx,y-2,xx,y),fill='#d0c5a4');d.line((xx,y+h,xx,y+h+2),fill='#d0c5a4')
    d.rectangle((165,252,218,287),fill='#a0815a')
    for y in range(255,288,6):d.line((166,y,217,y),fill='#695c49')
    mask=Image.new('L',(24,18));md=ImageDraw.Draw(mask);md.rectangle((2,5,21,15),fill=255);md.rectangle((10,15,13,17),fill=255)
    for box in [(2,5,7,5),(17,5,21,7),(7,6,15,11)]:md.rectangle(box,fill=0)
    walk={(x,y) for y in range(18) for x in range(24) if mask.getpixel((x,y)) and (y!=17 or x==12)}
    actions={(5,5):'Message ArcticPassage_Community',(20,7):'Kitchen'}
    return im,walk,actions,[(12,17,'Town',20,9)],{'spawn':[12,14],'board_approach':[5,6],'kitchen_approach':[20,8]},[]


def export(name,season,scene,walk,actions,warps,points,roofs):
    w,h=scene.width//16,scene.height//16
    scene.save(M/f'{name}_{season}_scene.png')
    root=E.Element('map',version='1.10',tiledversion='1.10.2',orientation='orthogonal',renderorder='right-down',width=str(w),height=str(h),tilewidth='16',tileheight='16',infinite='0')
    props={'PassOutSafe':'T','LocationContext':'ArcticPassage_TundraClimate' if name!='CommunityHouse' else 'ArcticPassage_CoastClimate','Warp':' '.join(str(v) for rec in warps for v in (rec[0],rec[1],'ArcticPassage_'+rec[2],rec[3],rec[4]))}
    if name!='CommunityHouse':props['Outdoors']='T'
    else:props.update(AmbientLight='0 0 0',AmbientNightLight='24 18 10')
    pr=E.SubElement(root,'properties')
    for k,v in props.items():E.SubElement(pr,'property',name=k,value=v)
    ts=E.SubElement(root,'tileset',firstgid='1',name='z_'+name+'Scene',tilewidth='16',tileheight='16',tilecount=str(w*h),columns=str(w))
    E.SubElement(ts,'image',source=f'{name}_{season}_scene.png',width=str(w*16),height=str(h*16))
    for y in range(h):
        for x in range(w):
            t=E.SubElement(ts,'tile',id=str(y*w+x));pr=E.SubElement(t,'properties')
            E.SubElement(pr,'property',name='NoSpawn',value='All')
            E.SubElement(pr,'property',name='Type',value='Wood' if name=='CommunityHouse' else 'Grass' if season=='winter' else 'Stone')
    collision=w*h+1
    Image.new('RGBA',(16,16)).save(M/'Frontier_collision.png')
    gids={pos:collision+1+i for i,pos in enumerate(actions)}
    for gid,act in [(collision,None)]+[(gids[pos],act) for pos,act in actions.items()]:
        ts=E.SubElement(root,'tileset',firstgid=str(gid),name=f'z_{name}Action{gid}',tilewidth='16',tileheight='16',tilecount='1',columns='1');E.SubElement(ts,'image',source='Frontier_collision.png',width='16',height='16')
        if act:
            t=E.SubElement(ts,'tile',id='0');pr=E.SubElement(t,'properties');E.SubElement(pr,'property',name='Action',value=act)
    for i,layer in enumerate(('Back','Buildings','Front','AlwaysFront')):
        ly=E.SubElement(root,'layer',id=str(i+1),name=layer,width=str(w),height=str(h));grid=[]
        for y in range(h):
            row=[]
            for x in range(w):
                gid=y*w+x+1 if layer=='Back' else gids.get((x,y),collision if (x,y) not in walk else 0) if layer=='Buildings' else 0
                if layer=='Front' and any(x1<=x<=x2 and y1<=y<=y2 for x1,y1,x2,y2 in roofs):gid=y*w+x+1
                row.append(gid)
            grid.append(','.join(map(str,row)))
        E.SubElement(ly,'data',encoding='csv').text='\n'+',\n'.join(grid)+'\n'
    group=E.SubElement(root,'objectgroup',name='Buildings',visible='0')
    for (x,y),act in actions.items():
        ob=E.SubElement(group,'object',name='TileData',x=str(x*16),y=str(y*16),width='16',height='16');pr=E.SubElement(ob,'properties');E.SubElement(pr,'property',name='Action',type='string',value=act)
    E.indent(root);E.ElementTree(root).write(M/f'{name}_{season}.tmx',encoding='utf-8',xml_declaration=True)
    debug=scene.convert('RGBA');dd=ImageDraw.Draw(debug,'RGBA')
    for x,y in walk:dd.rectangle((x*16,y*16,x*16+15,y*16+15),fill=(60,240,140,60))
    debug.save(R/f'previews/{name}_{season}_navigation.png');scene.save(R/f'previews/{name}_{season}.png')
    return {'size':[w,h],'points':points}


def main():
    content=json.loads((P/'content.json').read_text());content['Changes']=[p for p in content['Changes'] if not p.get('LogName','').startswith(TAG)]
    texts={l:json.loads((P/f'i18n/{l}.json').read_text()) for l in ('default','zh')};index=json.loads((R/'docs/build-index.json').read_text())
    def patch(action,target,**kwargs):content['Changes'].append(dict(Action=action,Target=target,LogName=TAG+target,**kwargs))
    def tr(key,en,zh):texts['default'][key]=en;texts['zh'][key]=zh;return '{{i18n:'+key+'}}'
    locations={}
    for name,en,zh in [('SledTrail','Marked sled trail','雪橇山路'),('Glacier','Glacier observation area','冰川观测区'),('CommunityHouse','Frosthavn community house','霜灯港社区屋')]:
        for s in SEASONS:index['maps'][name]=export(name,s,*(community() if name=='CommunityHouse' else outdoor(name,s)))
        patch('Load','Maps/ArcticPassage_'+name,FromFile='assets/maps/'+name+'_{{MapSeason}}.tmx')
        base=next(p['Entries']['ArcticPassage_'+('Guesthouse' if name=='CommunityHouse' else 'WinterCamp')] for p in content['Changes'] if p.get('Target')=='Data/Locations' and 'ArcticPassage_'+('Guesthouse' if name=='CommunityHouse' else 'WinterCamp') in p.get('Entries',{}))
        locations['ArcticPassage_'+name]={**copy.deepcopy(base),'DisplayName':tr('location.'+name,en,zh),'CreateOnLoad':{'MapPath':'Maps/ArcticPassage_'+name},'DefaultArrivalTile':dict(zip(('X','Y'),index['maps'][name]['points']['spawn'])),'Fish':[]}
    patch('EditData','Data/Locations',Entries=locations)
    patch('EditMap','Maps/ArcticPassage_Town',MapTiles=[{'Position':{'X':20,'Y':8},'Layer':'Buildings','SetProperties':{'Action':'Warp 12 14 ArcticPassage_CommunityHouse'}}])
    patch('EditMap','Maps/ArcticPassage_Tundra',AddWarps=['26 3 ArcticPassage_SledTrail 12 42'])
    # Existing bridge/camp return remains intact. This marked junction is an
    # additional route, never a season-dependent replacement of an old exit.
    # Real transparent action tiles, including TileData for the native reader.
    # A property-only CP patch on a null Buildings cell cannot create a tile.
    for season in SEASONS:
        path=M/f'WinterCamp_{season}.tmx';tree=E.parse(path);root=tree.getroot()
        ts=next((ts for ts in root.findall('tileset') if ts.get('name')=='z_FrontierCampLink'),None)
        if ts is None:
            gid=max(int(ts.get('firstgid'))+int(ts.get('tilecount')) for ts in root.findall('tileset'))
            ts=E.Element('tileset',firstgid=str(gid),name='z_FrontierCampLink',tilewidth='16',tileheight='16',tilecount='1',columns='1')
            E.SubElement(ts,'image',source='Frontier_collision.png',width='16',height='16')
            t=E.SubElement(ts,'tile',id='0');pr=E.SubElement(t,'properties');E.SubElement(pr,'property',name='Action',value='Warp 60 24 ArcticPassage_SledTrail')
            root.insert(len(root.findall('tileset'))+1,ts)
        gid=int(ts.get('firstgid'));w=int(root.get('width'))
        layer=root.find("layer[@name='Buildings']/data");cells=[int(v) for v in layer.text.strip().split(',')];cells[23*w+50]=gid
        layer.text='\n'+',\n'.join(','.join(map(str,cells[y*w:(y+1)*w])) for y in range(int(root.get('height'))))+'\n'
        group=root.find("objectgroup[@name='Buildings']")
        if group is None:group=E.SubElement(root,'objectgroup',name='Buildings',visible='0')
        for ob in list(group):
            if ob.get('x')=='800' and ob.get('y')=='368':group.remove(ob)
        ob=E.SubElement(group,'object',name='TileData',x='800',y='368',width='16',height='16');pr=E.SubElement(ob,'properties');E.SubElement(pr,'property',name='Action',type='string',value='Warp 60 24 ArcticPassage_SledTrail')
        E.indent(root);tree.write(path,encoding='utf-8',xml_declaration=True)
    index['maps']['WinterCamp']['points']['mountain_link_approach']=[49,23]
    sign_data={
        'SledRoute':tr('frontier.sled','Marked mountain trail. South: tundra lookout. North: glacier observation deck. East: field camp. In summer use the gravel walking route. Winter dog-team services operate from the marked station. Never leave the trail to cross sea ice.','山路标记线：向南回苔原观景处，向北去冰川观测台，向东到营地。夏季沿砾石步道步行；冬季在标记站点搭乘犬队雪橇。不要离开步道横穿海冰。'),
        'GlacierSafety':tr('frontier.glacier','Observe from this fixed deck. The ice front, crevasses and meltwater channel are out of bounds. Survey stakes measure positions; they do not indicate safe ice. Return south along the marked moraine path.','请在固定观测台观看。冰川前缘、裂隙和融水河道均不开放进入。测量标杆用于定位，不代表冰面安全。返程沿标记的冰碛步道向南走。'),
        'Geology':tr('frontier.geology','The mixed stones at this moraine were carried by moving ice. Survey from the path; never hammer the glacier.','冰碛里的混杂石块，是移动的冰川携带而来。请从步道观察，不要敲凿冰川。'),
        'SledPending':tr('frontier.sled.pending','The dog-team station is being prepared. Follow the marked walking trail for now.','犬队站点正在筹备。当前请沿标记步道步行往返。'),
        'Community':tr('frontier.community','Frosthavn community house. Shared tables, local notices and a kitchen on the right. The south door returns to the upper town lane.','霜灯港社区屋。这里有共用长桌、地方公告和右侧料理台。南门返回小镇上街。')}
    patch('EditData','Strings/StringsFromMaps',Entries={'ArcticPassage_'+k:v for k,v in sign_data.items()})
    # Readable sign on the new camp junction; code drawing only.
    for s in SEASONS:
        path=M/f'WinterCamp_{s}_scene.png';im=Image.open(path).convert('RGBA');d=ImageDraw.Draw(im)
        d.rectangle((803,370,807,385),fill='#665b4d');d.rectangle((793,359,818,373),fill='#385469',outline='#c0b797');d.line((797,364,811,364),fill='#e7c990');d.line((797,368,806,368),fill='#bcc7b9');im.save(path)
    for l,t in texts.items():dump(P/f'i18n/{l}.json',t)
    dump(P/'content.json',content);dump(R/'docs/build-index.json',index)
    print('Built R02 twelve seasonal TMX sources: mountain trail, glacier moraine/deck, community house. Existing paths preserved.')


if __name__=='__main__':main()
