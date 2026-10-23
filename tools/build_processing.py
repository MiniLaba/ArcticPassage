"""Native fuel-free air drying, with retained original pixel sprite masters."""
from PIL import Image, ImageOps

def build_processing(root,pack,patch,tr,loc,obj,objects):
    # Technical sprite packing: alpha-crop each generated frame, preserve its
    # aspect ratio, and align both states to the same ground baseline.
    source=Image.open(root/'art/source/drying-rack-master.png').convert('RGBA')
    sheet=Image.new('RGBA',(32,32))
    for frame in range(2):
        cell=source.crop((frame*source.width//2,0,(frame+1)*source.width//2,source.height))
        bounds=cell.getchannel('A').point(lambda a:255 if a>128 else 0).getbbox()
        sprite=ImageOps.contain(cell.crop(bounds),(14,30),Image.Resampling.NEAREST)
        sheet.paste(sprite,(frame*16+(16-sprite.width)//2,32-sprite.height))
    path=pack/'assets/machines/DryingRack.png';path.parent.mkdir(parents=True,exist_ok=True);sheet.save(path)
    Image.open(root/'art/source/dried-fish-products-master.png').convert('RGBA').resize((48,16),Image.Resampling.NEAREST).save(pack/'assets/items/processed-fish.png')
    rack=loc('DryingRack')
    rack_name=tr('machine.drying.name','Fish drying rack','晾鱼架')
    rack_desc=tr('machine.drying.description','Air-dries one cod or capelin over two nights. No fuel needed. Keeps the fish quality.','将一条鳕鱼或毛鳞鱼风干，需两个夜晚，不耗燃料。保留鱼的品质。')
    patch('Load','Mods/WhiteBay.ArcticPassage/DryingRack',FromFile='assets/machines/DryingRack.png')
    patch('Load','Mods/WhiteBay.ArcticPassage/ProcessedFish',FromFile='assets/items/processed-fish.png')
    patch('EditData','Data/BigCraftables',Entries={rack:{'Name':'Lumenhaven fish drying rack','DisplayName':rack_name,'Description':rack_desc,'Price':300,'Fragility':0,'CanBePlacedOutdoors':True,'CanBePlacedIndoors':True,'Texture':'Mods/WhiteBay.ArcticPassage/DryingRack','SpriteIndex':0}})
    patch('EditData','Data/CraftingRecipes',Entries={rack:'388 40 771 15 335 1/Home/'+rack+'/true/null/'+rack_name})
    rules=[]
    for index,(fish,en,zh,price) in enumerate([
        ('AtlanticCod','Air-dried Atlantic cod','风干大西洋鳕鱼',168),
        ('Capelin','Air-dried capelin','风干毛鳞鱼',91),
        ('PolarCod','Air-dried polar cod','风干北极鳕',119),
    ]):
        product=obj('Dried'+fish)
        objects[product]={'Name':en,'DisplayName':tr('product.'+fish+'.name',en,zh),'Description':tr('product.'+fish+'.description','Carefully air-dried at the harbor. A compact, savory fish product.','在港口细心风干的鱼货，紧实鲜香，便于储存。'),'Type':'Basic','Category':-26,'Price':price,'Texture':'Mods/WhiteBay.ArcticPassage/ProcessedFish','SpriteIndex':index,'Edibility':15,'ExcludeFromRandomSale':True,'ContextTags':['arcticpassage_fish_product']}
        rules.append({'Id':loc('Dry'+fish),'Triggers':[{'Id':'Input','Trigger':'ItemPlacedInMachine','RequiredItemId':'(O)'+obj(fish),'RequiredCount':1}],
            'OutputItem':[{'Id':'Product','ItemId':'(O)'+product,'CopyPrice':True,'CopyQuality':True,'PriceModifiers':[{'Id':'DryingValue','Modification':'Multiply','Amount':1.4}]}],
            'DaysUntilReady':2})
    patch('EditData','Data/Machines',Entries={'(BC)'+rack:{'OutputRules':rules,'AdditionalConsumedItems':[],'WobbleWhileWorking':False,'ShowNextIndexWhileWorking':True,'ShowNextIndexWhenReady':True,'AllowFairyDust':False,'OnlyCompleteOvernight':True,
        'InvalidItemMessage':tr('machine.drying.invalid','Use one Atlantic cod, polar cod or capelin.','这里可以风干大西洋鳕鱼、北极鳕或毛鳞鱼。')}})
    letter=tr('mail.drying','The shed is ready for slow work, too.^Here is the plan for a fish drying rack. Use 40 wood, 15 fiber and one iron bar. One cod or capelin takes two nights without coal. It keeps the quality of your catch.^-Roan %item craftingRecipe '+rack+' %%[#]A place to hang the catch',
        '加工棚也能做些慢工了。^附上晾鱼架的做法：40份木材、15份纤维和1块铁锭。放入一条鳕鱼或毛鳞鱼，等两个夜晚，不用烧煤，也能保留渔获的品质。^-罗安 %item craftingRecipe '+rack+' %%[#]挂起鱼货的地方')
    patch('EditData','Data/mail',Entries={loc('DryingPlan'):letter})
    # Separate one-time trigger also upgrades saves which repaired the shed in 0.4.
    patch('EditData','Data/TriggerActions',Entries={loc('DryingPlan'):{'Id':loc('DryingPlan'),'Trigger':'DayStarted','Condition':'PLAYER_HAS_MAIL Current '+loc('Shed'),'Actions':['AddMail Current '+loc('DryingPlan')+' now']}})
