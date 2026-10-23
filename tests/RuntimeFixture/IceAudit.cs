using System;
using System.Linq;
using System.Collections.Generic;
using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Tools;

public partial class ModEntry {
 const string IceDayKey="WhiteBay.ArcticPassage/IceFishingDay";
 bool[]? iceBefore;
 bool[]? iceCollisionBefore;
 void PrepareIceAudit() {
  if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA" || !ShipmentFlag("ice-preview.enabled"))return;
  Game1.SetSaveName("ArcticIceQA");
  Monitor.Log("ICE QA isolated native API fixture, synthetic tools/skills and preview position; NOT normal play, no save requested.",LogLevel.Info);
  Game1.MasterPlayer.modData.Remove(IceDayKey);
  Game1.player.mailReceived.Add("ArcticPassage_Boat");
  for(int i=0;i<Game1.player.Items.Count;i++)Game1.player.Items[i]=null;
  Game1.player.Items[0]=ItemRegistry.Create("(T)BambooPole");Game1.player.Items[1]=new Pickaxe();Game1.player.CurrentToolIndex=0;
  Game1.activeClickableMenu=null;Game1.eventUp=false;
  Game1.warpFarmer("ArcticPassage_Icefjord",40,34,false);
  DelayedAction.functionAfterDelay(AuditIceClosed,1000);
 }
 bool[] IceFishableSnapshot(GameLocation l)=>Enumerable.Range(0,72*56).Select(i=>l.isTileFishable(i%72,i/72)).ToArray();
 bool[] IceCollisionSnapshot(GameLocation l)=>Enumerable.Range(0,6).Select(i=>l.isCollidingPosition(new Rectangle((41+i%3)*64+16,(34+i/3)*64+16,32,32),Game1.viewport,Game1.player)).ToArray();
 void IceAction() {
  string action=Game1.currentLocation.doesTileHaveProperty(40,35,"Action","Buildings");
  Check(action=="ArcticPassageIceFishing","ice actual patched map marker carries the registered action");
  Game1.currentLocation.performAction(action,Game1.player,new xTile.Dimensions.Location(40,35));
 }
 void AuditIceClosed() {
  try {
   var l=Game1.currentLocation;
   Check(Game1.currentSeason=="winter","ice fixture loaded a real winter save");
   iceBefore=IceFishableSnapshot(l);iceCollisionBefore=IceCollisionSnapshot(l);
   Check(Enumerable.Range(0,6).All(i=>!l.isTileFishable(41+i%3,34+i/3)),"ice sealed opening rejects all six target tiles");
   Check(iceCollisionBefore.All(x=>x),"ice opening footprint is impassable before clearing");
   IceAction();
   Check(!Game1.MasterPlayer.modData.ContainsKey(IceDayKey),"ice wrong tool cannot open the site");
   Game1.activeClickableMenu?.exitThisMenu(false);
   Game1.player.CurrentToolIndex=1;IceAction();
   Check(!Game1.MasterPlayer.modData.ContainsKey(IceDayKey),"ice opening is not granted before the clearing animation");
   DelayedAction.functionAfterDelay(AuditIceOpen,2200);
  }catch(Exception ex){Monitor.Log("ICE QA FAILED: "+ex,LogLevel.Error);}
 }
 void AuditIceOpen() {
  try {
   var f=Game1.player;var l=Game1.currentLocation;
   Check(Game1.MasterPlayer.modData.TryGetValue(IceDayKey,out var day) && day==Game1.Date.TotalDays.ToString(),"ice clearing persisted the exact current day on host farmer");
   var after=IceFishableSnapshot(l);
   var changed=Enumerable.Range(0,after.Length).Where(i=>after[i]!=iceBefore![i]).ToArray();
   Check(changed.Length==6 && changed.All(i=>i%72>=41 && i%72<=43 && i/72>=34 && i/72<=35),"ice exactly six tiles became fishable; all other fjord water unchanged");
   Check(IceCollisionSnapshot(l).SequenceEqual(iceCollisionBefore!) && iceCollisionBefore!.All(x=>x),"ice all six tiles remain impassable after opening");
   Check(f.freezePause<=0,"ice native movement freeze ends after animation");
   f.Items[0]=ItemRegistry.Create("(T)BambooPole");f.CurrentToolIndex=0;
   if(!f.fishCaught.ContainsKey("129"))f.fishCaught["129"]=new[]{1,12};
   foreach(var scenario in new[]{(Level:0,Training:false),(Level:4,Training:false),(Level:4,Training:true)}) {
    int level=scenario.Level;
    f.Items[0]=ItemRegistry.Create(scenario.Training?"(T)TrainingRod":"(T)BambooPole");
    f.fishingLevel.Value=level;var counts=new Dictionary<string,int>();
    for(int i=0;i<500;i++) {
     string id=l.getFish(0,null,3,f,0,new Vector2(42,34),null)?.QualifiedItemId??"none";
     counts[id]=counts.GetValueOrDefault(id)+1;
    }
    Monitor.Log("ICE QA native fish selection rod="+f.CurrentTool.ItemId+" level="+level+": "+string.Join(",",counts.Select(x=>x.Key+"="+x.Value)),LogLevel.Info);
    Check(counts.ContainsKey("(O)ArcticPassage_PolarCod"),"ice winter pool includes native polar cod at level "+level);
    Check(!counts.Keys.Any(x=>x.StartsWith("(O)ArcticPassage_") && x!="(O)ArcticPassage_PolarCod" && x!="(O)ArcticPassage_Halibut"),"ice excludes warm-season local rod species");
    Check((level==0 || scenario.Training)?!counts.ContainsKey("(O)ArcticPassage_Halibut"):counts.ContainsKey("(O)ArcticPassage_Halibut"),"ice native halibut level-four gate enforced");
   }
   int originalDay=Game1.dayOfMonth;Game1.dayOfMonth++;
   Check(!l.isTileFishable(42,34),"ice next date seals the hole without changing collision or mail");
   Game1.dayOfMonth=originalDay;Game1.MasterPlayer.modData.Remove(IceDayKey);
   f.CurrentToolIndex=1;f.faceDirection(2);f.freezePause=0;f.CanMove=true;
   Game1.dialogueUp=false;Game1.eventUp=false;Game1.activeClickableMenu=null;
   Monitor.Log("ICE QA COMPLETE: native target isolation, collision, pickaxe, timed activation, winter fish/level and next-day boundary passed. Reset closed for desktop interaction; no save/normal catch claim.",LogLevel.Info);
  }catch(Exception ex){Monitor.Log("ICE QA FAILED: "+ex,LogLevel.Error);}
 }
}
