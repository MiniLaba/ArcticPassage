using System;
using System.Linq;
using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Objects;

public partial class ModEntry {
 const string WinterTrapTag="WhiteBay.QA/WinterTrap";
 bool winterOvernightPending;
 void RegisterWinterOvernightAudit(IModHelper helper) {
  helper.Events.GameLoop.DayStarted+=(_,_)=>{
   if(!winterOvernightPending)return;
   winterOvernightPending=false;
   DelayedAction.functionAfterDelay(AuditWinterReload,2500);
  };
 }
 void BeginWinterOvernight() {
  var f=Game1.player;
  try {
   // This operation must never write to the original spring QA or a player save.
   Check(f.Name=="ArcticQA" && Game1.GetSaveGameName(false)=="ArcticWinterQA" && Game1.currentSeason=="winter","overnight writes only the dedicated winter clone");
   var location=Game1.getLocationFromName(Prefix+"Harbor");
   var inventory=f.Items.ToArray();int placed=0;
   try {
    foreach(var pair in location.objects.Pairs.Where(p=>p.Value.modData.ContainsKey(WinterTrapTag)).ToArray()) {
     pair.Value.performRemoveAction();location.objects.Remove(pair.Key);
    }
    for(int y=1;y<location.Map.Layers[0].LayerHeight-1;y++)for(int x=1;x<location.Map.Layers[0].LayerWidth-1;x++) {
     var tile=new Vector2(x,y);
     if(location.objects.ContainsKey(tile) || !CrabPot.IsValidCrabPotLocationTile(location,x,y))continue;
     if(!new[]{new Point(x-1,y),new Point(x+1,y),new Point(x,y-1),new Point(x,y+1)}.Any(p=>!location.isTileFishable(p.X,p.Y) && location.Map.GetLayer("Buildings").Tiles[p.X,p.Y]==null))continue;
     var item=(StardewValley.Object)ItemRegistry.Create("(O)710");
     Check(item.placementAction(location,x*64,y*64,f),"overnight native trap placement "+tile);
     var pot=location.objects[tile] as CrabPot ?? throw new Exception("Not a native trap");
     pot.modData[WinterTrapTag]="overnight";
     var bait=ItemRegistry.Create("(O)685",1);f.Items.Add(bait);
     Check(pot.performObjectDropInAction(bait,false,f,false) && !pot.readyForHarvest.Value && pot.heldObject.Value==null,"overnight trap starts baited and empty "+tile);
     placed++;
    }
   }finally{f.Items.Clear();foreach(var item in inventory)f.Items.Add(item);}
   Check(placed>0,"winter overnight has reachable baited traps");
   f.modData["WhiteBay.QA/WinterBeforeDay"]=Game1.Date.TotalDays.ToString();
   f.modData["WhiteBay.QA/WinterTrapCount"]=placed.ToString();
   winterOvernightPending=true;
   Game1.warpFarmer(Prefix+"Guesthouse",4,7,false);
   DelayedAction.functionAfterDelay(()=>{
    Game1.timeOfDay=2200;
    Game1.currentLocation.answerDialogueAction("Sleep_Yes",null);
    Monitor.Log("AUDIT WINTER OVERNIGHT started normal sleep/new-day/save; native target="+Game1.GetSaveGameName(false)+" traps="+placed,LogLevel.Info);
   },1500);
  }catch(Exception ex){winterOvernightPending=false;Monitor.Log("AUDIT WINTER OVERNIGHT FAIL "+ex,LogLevel.Error);}
 }
 void AuditWinterReload() {
  try {
   var f=Game1.player;
   Check(f.Name=="ArcticQA" && Game1.GetSaveGameName(false)=="ArcticWinterQA","winter state belongs to isolated save");
   Check(f.modData.TryGetValue("WhiteBay.QA/WinterBeforeDay",out string before) && Game1.Date.TotalDays==int.Parse(before)+1,"winter overnight advanced exactly one day");
   var location=Game1.getLocationFromName(Prefix+"Harbor");
   Check(location.GetData().FishAreas["Default"].CrabPotFishTypes.SequenceEqual(new[]{"ap_crab_winter"}),"winter crab type survived new-day or load");
   var traps=location.objects.Values.OfType<CrabPot>().Where(p=>p.modData.ContainsKey(WinterTrapTag)).ToArray();
   Check(traps.Length==int.Parse(f.modData["WhiteBay.QA/WinterTrapCount"]),"all winter traps retained across native transition");
   Check(traps.All(p=>p.readyForHarvest.Value && p.heldObject.Value!=null),"all baited traps completed through actual new-day processing");
   Check(traps.All(p=>p.heldObject.Value!.ItemId==Prefix+"SnowCrab" || new[]{"168","169","170","171","172"}.Contains(p.heldObject.Value!.ItemId)),"winter overnight has only snow crab or native junk");
   int crabs=traps.Count(p=>p.heldObject.Value?.ItemId==Prefix+"SnowCrab");
   Check(crabs>0,"actual overnight produced snow crab");
   Monitor.Log("AUDIT WINTER OVERNIGHT/RELOAD COMPLETE day="+Game1.Date.TotalDays+" traps="+traps.Length+" crab="+crabs+" target="+Game1.GetSaveGameName(false),LogLevel.Info);
  }catch(Exception ex){Monitor.Log("AUDIT WINTER OVERNIGHT/RELOAD FAIL "+ex,LogLevel.Error);}
 }
}
