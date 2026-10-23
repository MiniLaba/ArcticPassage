"""Native seafood, trap pools and kitchen recipes; generated art only packed here."""
from PIL import Image, ImageOps

MEALS = [
    ('CharSoup', 'Arctic char soup', '北极红点鲑汤', 'ArcticPassage_ArcticChar 1 192 1 20 1', 360, 80, {'FishingLevel':1}),
    ('PanCod', 'Pan-fried cod', '香煎鳕鱼', 'ArcticPassage_AtlanticCod 1 247 1', 260, 70, {'FishingLevel':1}),
    ('ShrimpChowder', 'Cream northern shrimp soup', '奶油北方虾汤', 'ArcticPassage_NorthernShrimp 1 184 1 246 1', 330, 90, {'FishingLevel':2}),
    ('FishPotatoStew', 'Fish and potato stew', '炖鱼配土豆', 'ArcticPassage_PolarCod 1 192 1 78 1', 230, 85, {'Defense':1}),
]


def pack_icons(root, pack, filename, columns, rows, count, output):
    master=Image.open(root/'art/source'/filename).convert('RGBA')
    sheet=Image.new('RGBA',(16*count,16))
    for index in range(count):
        x,y=index%columns,index//columns
        cell=master.crop((x*master.width//columns,y*master.height//rows,
                          (x+1)*master.width//columns,(y+1)*master.height//rows))
        # Technical alpha quantization removes sub-pixel export haze, preserving
        # the generated opaque silhouette rather than painting new content.
        cell.putalpha(cell.getchannel('A').point(lambda a:255 if a>=128 else 0))
        bounds=cell.getchannel('A').getbbox()
        if not bounds:raise ValueError('Empty generated sprite '+str(index))
        sprite=ImageOps.contain(cell.crop(bounds),(14,14),Image.Resampling.NEAREST)
        sheet.paste(sprite,(index*16+(16-sprite.width)//2,(16-sprite.height)//2))
    sheet.save(pack/'assets/items'/output)


def build_seafood(root,pack,patch,tr,loc,obj,objects,fish,locations,shops):
    pack_icons(root,pack,'seafood-icons-063-v2-master.png',3,3,9,'seafood.png')
    pack_icons(root,pack,'harbor-cuisine-063-master.png',2,2,4,'cuisine.png')
    texture='Mods/WhiteBay.ArcticPassage/Seafood'
    patch('Load',texture,FromFile='assets/items/seafood.png')
    patch('Load','Mods/WhiteBay.ArcticPassage/Cuisine',FromFile='assets/items/cuisine.png')
    for key in ['PolarCod','AtlanticCod','Capelin','ArcticChar','Halibut','Wolffish','GoldenRedfish']:
        objects[obj(key)]['Texture']=texture
    for index,key,en,zh,price,tags,description,description_zh in [
        (7,'NorthernShrimp','Northern shrimp','北方长额虾',110,
         'ap_shrimp_spring ap_shrimp_summer ap_shrimp_fall',
         'Pandalus borealis. Lives over cold, soft seabeds; commercial fisheries mainly use deep-water trawls. Shore pots are a gameplay simplification.',
         'Pandalus borealis。栖息于寒冷软质海底；现实渔业主要采用深水拖网，岸边蟹笼为玩法简化。'),
        (8,'SnowCrab','Snow crab','雪蟹',235,'ap_crab_fall ap_crab_winter',
         'Chionoecetes opilio. A long-legged cold-water crab. Distribution varies between northern seas; this bay uses a composite geography.',
         'Chionoecetes opilio。长足的冷水蟹；分布因海区而异，栖光湾采用复合地理设计。')]:
        id=obj(key)
        objects[id]={'Name':en,'DisplayName':tr('fish.'+key+'.name',en,zh),
            'Description':tr('fish.'+key+'.description',description,description_zh),
            'Type':'Fish','Category':-4,'Price':price,'Texture':texture,'SpriteIndex':index,
            'Edibility':10,'ExcludeFromRandomSale':True,'ContextTags':['fish_arcticpassage','fish_ocean','fish_trap']}
        fish[id]=f'{en}/trap/0.45/0/{tags}/2/12'
    # Unique seasonal type strings are not added to vanilla locations. The
    # location's default area excludes ordinary warm-water vanilla catches.
    for name in ['Harbor','Icefjord']:
        locations[loc(name)]['FishAreas']={'Default':{'CrabPotFishTypes':[
            ('ap_{{HarborTrapType}}_' if name=='Harbor' else 'ap_crab_')+'{{Season}}'],
            'CrabPotJunkChance':0.2}}
    recipes={}
    for index,(key,en,zh,ingredients,price,energy,buff) in enumerate(MEALS):
        id=obj(key)
        # Native shop LearnRecipe keys by BaseName, so keep the internal name
        # equal to the recipe ID; DisplayName supplies readable translations.
        objects[id]={'Name':id,'DisplayName':tr('meal.'+key+'.name',en,zh),
            'Description':tr('meal.'+key+'.description','A warm harbor meal made with a carefully handled local catch.',
                             '用细心保存的本地渔获做成的热食，适合收工后慢慢享用。'),
            'Type':'Cooking','Category':-7,'Price':price,'Edibility':energy,
            'Texture':'Mods/WhiteBay.ArcticPassage/Cuisine','SpriteIndex':index,
            'ExcludeFromRandomSale':True,'Buffs':[{'Id':'Meal','Duration':240,'CustomAttributes':buff}]}
        recipes[id]=ingredients+'/10 10/'+id+'/null/'+objects[id]['DisplayName']
        shops[loc('Supplies')]['Items'].append({'Id':id+'Recipe','ItemId':'(O)'+id,
            'IsRecipe':True,'Price':450,'AvailableStock':1})
    # Supplied staples keep the remote kitchen usable without local agriculture.
    for id,price in [('192',120),('20',100),('247',240),('184',150),('246',120),('78',100)]:
        shops[loc('Supplies')]['Items'].append({'Id':'Kitchen_'+id,'ItemId':'(O)'+id,
            'Price':price,'AvailableStock':5})
    shops[loc('Supplies')]['Items'].append({'Id':'CrabPot','ItemId':'(O)710',
        'Price':1500,'AvailableStock':3,'Condition':'PLAYER_FISHING_LEVEL Current 3'})
    patch('EditData','Data/CookingRecipes',Entries=recipes)
