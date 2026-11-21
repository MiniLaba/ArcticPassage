using System;
using System.Linq;
using System.Collections.Generic;
using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Objects;

public partial class ModEntry {
 Vector2? winterPotApproach;
 int winterPotFacing;
 void PrepareWinterPot() {
  var f=Game1.player;var location=Game1.getLocationFromName(Prefix+"Harbor");
  var inventory=f.Items.ToArray();
  try {
   Check(Game1.currentSeason=="winter" && location.GetSeason()==Season.Winter,"winter pot audit uses actual loaded winter date");
   Check(location.GetData().FishAreas["Default"].CrabPotFishTypes.SequenceEqual(new[]{"ap_crab_winter"}),"CP actual winter harbor type resolves to snow crab");
   int successes=0;
   for(int y=1;y<location.Map.Layers[0].LayerHeight-1;y++)for(int x=1;x<location.Map.Layers[0].LayerWidth-1;x++) {
    var tile=new Vector2(x,y);
    if(location.objects.ContainsKey(tile) || !CrabPot.IsValidCrabPotLocationTile(location,x,y))continue;
    var adjacent=new[]{new Point(x,y+1),new Point(x-1,y),new Point(x,y-1),new Point(x+1,y)};
    int direction=Array.FindIndex(adjacent,p=>!location.isTileFishable(p.X,p.Y) && location.Map.GetLayer("Buildings").Tiles[p.X,p.Y]==null);
    if(direction<0)continue;
    var item=(StardewValley.Object)ItemRegistry.Create("(O)710");
    Check(item.placementAction(location,x*64,y*64,f),"native winter pot placement "+tile);
    var pot=location.objects[tile] as CrabPot ?? throw new Exception("Native object placement did not create a CrabPot at "+tile);
    pot.modData["WhiteBay.QA/WinterTrap"]="prepared";
    var bait=ItemRegistry.Create("(O)685",1);f.Items.Add(bait);
    Check(pot.performObjectDropInAction(bait,false,f,false) && pot.bait.Value!=null,"native winter bait insertion "+tile);
    pot.DayUpdate();
    // A native daily handler is an API test, not an actual overnight transition.
    if(pot.heldObject.Value?.ItemId!=Prefix+"SnowCrab") {
     location.objects.Remove(tile);pot.performRemoveAction();continue;
    }
    successes++;
    if(successes==1) {
     int before=CountItem("(O)"+Prefix+"SnowCrab");
     pot.checkForAction(f,false);
     Check(CountItem("(O)"+Prefix+"SnowCrab")==before+1 && pot.heldObject.Value==null,"native winter crab collection adds exactly one and clears trap");
     location.objects.Remove(tile);pot.performRemoveAction();
     Monitor.Log("AUDIT WINTER POT native placement/bait/daily-catch/collection passed "+tile,LogLevel.Info);
    }else {
     winterPotApproach=new Vector2(adjacent[direction].X,adjacent[direction].Y);
     winterPotFacing=new[]{0,1,2,3}[direction];
     Monitor.Log("AUDIT WINTER POT ready crab left at "+tile+"; approach="+winterPotApproach+" facing="+winterPotFacing+". F11 only positions; X must collect. No save.",LogLevel.Info);
     return;
    }
   }
   throw new Exception("Could not prepare two native-caught snow crabs on reachable winter water");
  }catch(Exception ex){Monitor.Log("AUDIT WINTER POT FAIL "+ex,LogLevel.Error);}
  finally {f.Items.Clear();foreach(var item in inventory)f.Items.Add(item);}
 }
}
