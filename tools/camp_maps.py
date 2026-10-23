"""Code-drawn seasonal field camp. Coordinates and collision share tile geometry."""
from pathlib import Path
import math
import random
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def configure_camp(m):
    indoor = m.name == 'ResearchStation'
    m.layers = {n: [[0]*m.w for _ in range(m.h)] for n in m.layers}
    m.over = {}; m.warps = []; m.scene_water = set(); m.scene_roofs = []
    m.scene_wood = set()
    if indoor:
        station(m)
    else:
        landscape(m)
    m.scene_file = f'{m.name}_{m.season}_scene.png'
    m.scene_image.save(ROOT/'ContentPack/assets/maps'/m.scene_file)
    for y in range(m.h):
        for x in range(m.w):
            m.tile('floor' if indoor else 'ground', x, y)
            if (x, y) not in m.scene_walk:
                m.tile('collision', x, y, 'Buildings')
    if indoor:
        for x in [3, 4, 5]:
            m.prop(x, 7, 'Bed', 'T', 'Back')
            m.prop(x, 7, 'TouchAction', 'Sleep', 'Back')
        m.action('collision', 17, 7, 'Message ArcticPassage_CampDesk')
        m.warp(12, 17, 'WinterCamp', 31, 25)
        m.points = {'spawn': [12, 14], 'bed_approach': [4, 9], 'desk_approach': [17, 8]}
    else:
        for y in [23, 24]:
            m.warp(0, y, 'Tundra', 53, 23)
        m.action('collision', 31, 24, 'Warp 12 14 ArcticPassage_ResearchStation')
        m.action('collision', 13, 23, 'Message ArcticPassage_CampRoute')
        m.action('collision', 20, 35, 'Message ArcticPassage_SnowShelter')
        m.points = {'spawn': [2, 24], 'station_approach': [31, 25], 'shelter_approach': [19, 37]}
        m.scene_roofs = [(24, 14, 36, 19)]
    debug = m.scene_image.copy(); d = ImageDraw.Draw(debug, 'RGBA')
    for x, y in m.scene_walk:
        d.rectangle((x*16, y*16, x*16+15, y*16+15), fill=(60, 240, 140, 70))
    debug.save(ROOT/f'previews/{m.name}_{m.season}_navigation.png')


def landscape(m):
    winter = m.season == 'winter'; spring = m.season == 'spring'
    snow = winter or spring
    rr = random.Random(750)
    # Draw at a consistent two-screen-pixel grain, then export native 16px tiles.
    im = Image.new('RGB', (512, 384), '#c3d4e8' if snow else '#89938b')
    d = ImageDraw.Draw(im)
    surface = ['#d5e2f2', '#b8cbe4', '#cbd9ec', '#e6edf4'] if snow else ['#89938b', '#a1a593', '#727f7d', '#bac0ab']
    for _ in range(10500):
        x, y = rr.randrange(512), rr.randrange(384)
        d.line((x, y, x+rr.randrange(1, 5), y), fill=rr.choice(surface))
    # Layered bedrock bluffs form an enclosed, treeless basin, rather than a
    # flat white field. Low vegetation appears only between the stone seams.
    for y in range(-25, 420, 58):
        for x in range(-65, 590, 98):
            xx = x+rr.randrange(-22, 23); yy = y+rr.randrange(-15, 16)
            w = rr.randrange(56, 104); h = rr.randrange(17, 29)
            d.ellipse((xx-3, yy+8, xx+w+6, yy+h+16), fill='#9eafca' if snow else '#647579')
            outline = [(xx, yy+h), (xx+5, yy+7), (xx+w//3, yy-2), (xx+w*3//4, yy+2), (xx+w, yy+h), (xx+w-5, yy+h+11), (xx+8, yy+h+10)]
            d.polygon(outline, fill='#47566c', outline='#344658')
            for sx in range(xx+7, xx+w-6, 4):
                sy = yy+h+rr.randrange(-3, 5)
                d.line((sx, sy-8, sx-2, sy+5), fill=rr.choice(['#8295ad', '#61758b', '#a5b4c7']))
                d.point((sx-1, sy+6), fill='#253a50')
            cap = [(xx+1, yy+h-2), (xx+7, yy+5), (xx+w//3, yy-4), (xx+w*3//4, yy), (xx+w-2, yy+h-4), (xx+w-19, yy+h-6), (xx+w//2, yy+h-8), (xx+15, yy+h-5)]
            d.polygon(cap, fill='#dfebfa' if snow else '#abb39c')
            d.line(cap[:4], fill='#f1f5fc' if snow else '#c7cab1', width=2)
            if not winter:
                for _ in range(34):
                    px = rr.randrange(xx+7, xx+w-7); py = rr.randrange(yy+3, yy+h-4)
                    d.rectangle((px, py, px+2, py+1), fill=rr.choice(['#c5b87d', '#777f69', '#b49466'] if m.season == 'fall' else ['#a8af87', '#7b8b70', '#b7bf95']))
    bare_terrain=im.copy()
    routes = [[(0, 24), (12, 24), (20, 25), (31, 26), (44, 25), (54, 23)],
              [(14, 24), (14, 37), (21, 37)], [(49, 25), (49, 37), (43, 37)], [(31, 26), (31, 24)]]
    mask = Image.new('L', (m.w, m.h)); md = ImageDraw.Draw(mask)
    for route in routes:
        md.line(route, fill=255, width=3)
        pts = [(x*8+4, y*8+4) for x, y in route]
        d.line(pts, fill='#97accb' if snow else '#65777b', width=32, joint='curve')
        d.line(pts, fill='#c4d7ed' if snow else '#b6b9a6', width=26, joint='curve')
        d.line(pts, fill='#dce8f4' if snow else '#c4c6b1', width=17, joint='curve')
        for a, b in zip(pts, pts[1:]):
            length = math.dist(a, b)
            for step in range(4, int(length), 7):
                t = step/max(1, length); px = int(a[0]+(b[0]-a[0])*t); py = int(a[1]+(b[1]-a[1])*t)
                d.line((px-2, py, px, py+1), fill='#acbfda' if snow else '#8b998f')
                d.line((px+3, py+3, px+5, py+4), fill='#bdcfe6' if snow else '#a4ab99')
    md.rectangle((27, 24, 35, 27), fill=255)
    md.rectangle((16, 36, 22, 38), fill=255); md.rectangle((41, 36, 47, 38), fill=255)
    # Two seasonal shelters. Snow blocks are curved horizontal courses with
    # staggered joints, ventilation detail and low entrance tunnel.
    for cx, cy in [(19*8+4, 33*8), (44*8+4, 33*8)]:
        d.ellipse((cx-39,cy-5,cx+42,cy+21), fill='#a0b6d4' if snow else '#71827f')
        if winter:
            d.ellipse((cx-34,cy-43,cx+34,cy+9), fill='#a9c6e6', outline='#7f9fbe')
            d.ellipse((cx-32,cy-43,cx+29,cy+3), fill='#dfedf7')
            for j, sy in enumerate(range(cy-34,cy+4,7)):
                dy=(sy-(cy-17))/26; half=int(32*math.sqrt(max(0,1-dy*dy)))
                d.line((cx-half,sy,cx+half,sy), fill='#9ebbd6')
                for sx in range(cx-half+5+(j%2)*6,cx+half-3,13):
                    d.line((sx,sy,sx+1,sy+6), fill='#afc9dd')
            d.ellipse((cx-10,cy-10,cx+17,cy+16), fill='#b5cde4', outline='#93b1cd')
            d.rectangle((cx-6,cy+2,cx+10,cy+15), fill='#334e67')
            d.arc((cx-6,cy-5,cx+10,cy+8),180,360,fill='#334e67',width=5)
            d.line((cx-5,cy+16,cx+11,cy+16), fill='#eff6fc', width=2)
            d.point((cx+9,cy-38), fill='#6587a5')
        else:
            d.polygon([(cx-35,cy+8),(cx-8,cy-36),(cx+32,cy+7)], fill='#b49a64', outline='#4e6266')
            d.polygon([(cx-8,cy-36),(cx+3,cy+8),(cx+32,cy+7)], fill='#718584')
            d.polygon([(cx-8,cy-28),(cx-17,cy+8),(cx+1,cy+8)], fill='#344b56')
            d.line((cx-8,cy-36,cx-35,cy+8), fill='#e2c68d', width=2)
            for sx in [cx-45,cx+40]:
                d.line((cx-8,cy-30,sx,cy+14), fill='#c4c9b8'); d.line((sx,cy+12,sx,cy+17), fill='#3e5362')
    # Trail posts and the sign/observation positions are readable at player zoom.
    for tx,ty in [(8,22),(15,26),(25,24),(38,26),(50,24)]:
        px,py=tx*8+4,ty*8+4
        d.line((px,py-14,px,py+2), fill='#5e5c58', width=2)
        d.rectangle((px-2,py-12,px+2,py-8), fill='#c37b56')
        if snow:d.line((px-3,py-14,px+3,py-14),fill='#eff5fa',width=2)
    for tx,ty in [(13,23),(20,35)]:
        px,py=tx*8,ty*8
        d.rectangle((px+3,py+5,px+4,py+14),fill='#645a4a')
        d.rectangle((px-2,py-1,px+10,py+7),fill='#3d5362',outline='#a5b8c4')
        d.line((px,py+2,px+7,py+2),fill='#e6c88f')
    for px,py in [(26*8+6,24*8),(36*8+6,24*8),(13*8+3,22*8)]:
        d.line((px,py-12,px,py+5),fill='#3b4c5a',width=2)
        d.rectangle((px-3,py-18,px+3,py-11),fill='#314b60')
        d.rectangle((px-2,py-17,px+2,py-13),fill='#f4cf83')
    m.scene_walk={(x,y) for y in range(m.h) for x in range(m.w) if mask.getpixel((x,y))}
    from camp_materials import finish_camp
    m.scene_image=finish_camp(m.season,bare_terrain,im)


def station(m):
    m.properties={'PassOutSafe':'T','AmbientLight':'0 0 0','AmbientNightLight':'24 18 10'}
    # Clear central circulation and exit apron, furniture excluded explicitly.
    mask=Image.new('L',(24,18));md=ImageDraw.Draw(mask)
    md.rectangle((2,4,21,15),fill=255);md.rectangle((10,15,13,17),fill=255)
    for box in [(2,3,6,8),(8,5,11,8),(12,3,15,5),(17,4,21,7),(18,8,19,8),(1,10,5,13)]:md.rectangle(box,fill=0)
    md.rectangle((3,6,5,8),fill=255)
    m.scene_walk={(x,y) for y in range(18) for x in range(24) if mask.getpixel((x,y))}
    from camp_materials import research_interior
    m.scene_wood=set(m.scene_walk);m.scene_image=research_interior()
