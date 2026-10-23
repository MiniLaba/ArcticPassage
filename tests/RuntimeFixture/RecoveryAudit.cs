using System;
using System.Linq;
using System.Collections.Generic;
using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Objects;

public interface IArcticRecoveryApi { int RecoverNow(); }

public partial class ModEntry {
 const string RecoveryChestTag="WhiteBay.ArcticPassage.Runtime/RecoveryChest";
 const string RecoveryCaseTag="WhiteBay.QA/RecoveryCase";
 bool recoveryPending;
 string recoveryExpected="";

 void RegisterRecoveryAudit(IModHelper helper) {
  helper.Events.GameLoop.DayStarted+=(_,_)=>{
   if(!recoveryPending || Game1.GetSaveGameName(false)!="ArcticRecoveryQA")return;
   recoveryPending=false;
   var source=Game1.getLocationFromName(Prefix+"Icefjord");
   var expected=new List<Item>();
   foreach(var pot in source.objects.Values.OfType<CrabPot>().Where(p=>p.modData.ContainsKey(RecoveryCaseTag))) {
    expected.Add(ItemRegistry.Create("(O)710"));
    if(pot.heldObject.Value!=null)expected.Add(pot.heldObject.Value);
    else if(pot.bait.Value!=null)expected.Add(pot.bait.Value);
   }
   recoveryExpected=RecoverySnapshot(expected);
   Monitor.Log("AUDIT RECOVERY native pre-recovery attachment snapshot: "+recoveryExpected,LogLevel.Info);
   DelayedAction.functionAfterDelay(CheckRecoveryAfterTransition,4500);
  };
 }
 IArcticRecoveryApi RecoveryApi()=>Helper.ModRegistry.GetApi<IArcticRecoveryApi>("WhiteBay.ArcticPassage.Runtime")??throw new Exception("Production recovery API not loaded");
 static string RecoverySnapshot(IEnumerable<Item?> items)=>string.Join("|",items.Where(i=>i!=null).Select(i=>i!).GroupBy(i=>i.QualifiedItemId+";q="+i.Quality).Select(g=>g.Key+";n="+g.Sum(i=>i.Stack)).OrderBy(s=>s));
 Chest RecoveryChest()=>Game1.getLocationFromName(Prefix+"Fishery").objects.Values.OfType<Chest>().Single(c=>c.modData.ContainsKey(RecoveryChestTag));

 void PrepareRecoveryAudit() {
  if(Game1.player.Name!="ArcticQA" || Game1.GetSaveGameName(false)!="ArcticRecoveryQA")return;
  var f=Game1.player;var inventory=f.Items.ToArray();
  try {
   Check(Game1.currentSeason=="fall" && Game1.dayOfMonth==28,"recovery audit begins on actual autumn 28");
   Check(Helper.ModRegistry.IsLoaded("WhiteBay.ArcticPassage.Runtime"),"production runtime entry is actually loaded");
   var source=Game1.getLocationFromName(Prefix+"Icefjord");var positions=new List<Vector2>();
   for(int y=1;y<source.Map.Layers[0].LayerHeight-1 && positions.Count<3;y++)for(int x=1;x<source.Map.Layers[0].LayerWidth-1 && positions.Count<3;x++) {
    if(!CrabPot.IsValidCrabPotLocationTile(source,x,y))continue;
    if(!new[]{new Point(x-1,y),new Point(x+1,y),new Point(x,y-1),new Point(x,y+1)}.Any(p=>!source.isWaterTile(p.X,p.Y) && source.Map.GetLayer("Buildings").Tiles[p.X,p.Y]==null))continue;
    var tile=new Vector2(x,y);var item=(StardewValley.Object)ItemRegistry.Create("(O)710");
    Check(item.placementAction(source,x*64,y*64,f),"actual autumn native pot placement "+tile);
    var pot=(CrabPot)source.objects[tile];pot.modData[RecoveryCaseTag]=positions.Count.ToString();
    if(positions.Count<2) {
     var bait=ItemRegistry.Create(positions.Count==0?"(O)774":"(O)685",1);f.Items.Add(bait);
     Check(pot.performObjectDropInAction(bait,false,f,false),"autumn native bait insertion");
    }
    if(positions.Count==1) {
     // Deliberate QA fixture tests exact stack/quality preservation, not fishing.
     pot.heldObject.Value=(StardewValley.Object)ItemRegistry.Create("(O)"+Prefix+"SnowCrab",2,2);
     pot.readyForHarvest.Value=true;
    }
    positions.Add(tile);
   }
   Check(positions.Count==3,"three autumn fjord test states are available");
   var harbor=Game1.getLocationFromName(Prefix+"Harbor");
   // These twelve reachable winter coordinates were independently verified
   // by the previous live winter/save audit, not by the recovery algorithm.
   int controlCount=0;
   foreach(var open in new[]{new Point(28,13),new Point(32,13),new Point(33,13),new Point(41,13),new Point(42,13),new Point(53,21),new Point(54,22),new Point(54,23),new Point(37,27),new Point(37,28),new Point(29,38),new Point(30,38)}) {
    if(!CrabPot.IsValidCrabPotLocationTile(harbor,open.X,open.Y))continue;
    Check(((StardewValley.Object)ItemRegistry.Create("(O)710")).placementAction(harbor,open.X*64,open.Y*64,f),"open-water control pot placed "+open);
    var pot=(CrabPot)harbor.objects[new Vector2(open.X,open.Y)];pot.modData[RecoveryCaseTag]="open";
    var bait=ItemRegistry.Create("(O)685",1);f.Items.Add(bait);
    Check(pot.performObjectDropInAction(bait,false,f,false),"open-water control baited");
    controlCount++;
   }
   Check(controlCount>=3,"at least three control positions allow native placement in both autumn and winter");
   f.modData["WhiteBay.QA/RecoveryControlCount"]=controlCount.ToString();
   Check(RecoveryApi().RecoverNow()==0,"reachable autumn pots are not reclaimed prematurely");
   f.modData["WhiteBay.QA/RecoveryPositions"]=string.Join("|",positions.Select(p=>p.X+","+p.Y));
   Monitor.Log("AUDIT RECOVERY prepared three fjord pots (baited/ready-gold-stack/empty) plus "+controlCount+" baited open-water controls. F12 starts native autumn-to-winter sleep.",LogLevel.Info);
  }catch(Exception ex){Monitor.Log("AUDIT RECOVERY FAIL setup "+ex,LogLevel.Error);}
  finally{f.Items.Clear();foreach(var item in inventory)f.Items.Add(item);}
 }

 void BeginRecoveryTransition() {
  try {
   Check(Game1.player.Name=="ArcticQA" && Game1.GetSaveGameName(false)=="ArcticRecoveryQA" && Game1.currentSeason=="fall" && Game1.dayOfMonth==28,"transition saves only isolated autumn-28 recovery clone");
   recoveryPending=true;Game1.warpFarmer(Prefix+"Guesthouse",4,7,false);
   DelayedAction.functionAfterDelay(()=>{
    Game1.timeOfDay=2200;Game1.currentLocation.answerDialogueAction("Sleep_Yes",null);
    Monitor.Log("AUDIT RECOVERY normal autumn-28 sleep/new-season/save started",LogLevel.Info);
   },1500);
  }catch(Exception ex){recoveryPending=false;Monitor.Log("AUDIT RECOVERY FAIL transition "+ex,LogLevel.Error);}
 }

 void CheckRecoveryAfterTransition() {
  try {
   Check(Game1.currentSeason=="winter" && Game1.dayOfMonth==1,"native date changed autumn 28 to winter 1");
   var source=Game1.getLocationFromName(Prefix+"Icefjord");
   Check(!source.objects.Values.OfType<CrabPot>().Any(p=>p.modData.ContainsKey(RecoveryCaseTag)),"all three icebound test pots removed from fjord");
   var controls=Game1.getLocationFromName(Prefix+"Harbor").objects.Values.OfType<CrabPot>().Where(p=>p.modData.TryGetValue(RecoveryCaseTag,out string tag) && tag=="open").ToArray();
   Check(controls.Length==int.Parse(Game1.player.modData["WhiteBay.QA/RecoveryControlCount"]) && controls.All(p=>p.readyForHarvest.Value),"all open-water controls remain and complete overnight");
   string catches=string.Join(",",controls.GroupBy(p=>p.heldObject.Value?.ItemId??"none").Select(g=>g.Key+":"+g.Count()));
   Monitor.Log("AUDIT RECOVERY winter-1 control catches: "+catches,LogLevel.Info);
   Check(controls.All(p=>p.heldObject.Value?.ItemId==Prefix+"SnowCrab" || new[]{"168","169","170","171","172"}.Contains(p.heldObject.Value?.ItemId)),"first winter night excludes out-of-season shrimp");
   Check(controls.Any(p=>p.heldObject.Value?.ItemId==Prefix+"SnowCrab"),"first winter night produces snow crab");
   var chest=RecoveryChest();
   Check(RecoverySnapshot(chest.Items)==recoveryExpected,"recovery chest exactly matches pre-recovery gear and attachment quantities/qualities");
   Check(chest.Items.Where(i=>i?.ItemId==Prefix+"SnowCrab" && i.Quality==2).Sum(i=>i!.Stack)==2,"two gold-quality crabs survive recovery");
   Check(!chest.Items.Any(i=>i?.ItemId=="685"),"already-used bait is not refunded for a completed catch");
   TestRecoveryFullChest(chest,source);
   string snapshot=RecoverySnapshot(chest.Items);Check(RecoveryApi().RecoverNow()==0 && RecoverySnapshot(chest.Items)==snapshot,"repeat recovery does not duplicate gear");
   Game1.player.modData["WhiteBay.QA/RecoveryExpected"]=snapshot;
   Check(Game1.GetSaveGameName(false)=="ArcticRecoveryQA","post-recovery save target is isolated clone");
   auditSave=SaveGame.Save();
   Monitor.Log("AUDIT RECOVERY COMPLETE; native save started for recovered chest: "+snapshot,LogLevel.Info);
  }catch(Exception ex){Monitor.Log("AUDIT RECOVERY FAIL after transition "+ex,LogLevel.Error);}
 }

 void TestRecoveryFullChest(Chest chest,GameLocation source) {
  var stored=chest.Items.ToArray();
  var text=Game1.player.modData["WhiteBay.QA/RecoveryPositions"].Split('|')[0].Split(',');var tile=new Vector2(float.Parse(text[0]),float.Parse(text[1]));
  var legacy=new CrabPot{Location=source,TileLocation=tile};legacy.bait.Value=(StardewValley.Object)ItemRegistry.Create("(O)DeluxeBait",1);
  source.objects.Add(tile,legacy); // Simulated old-save object under new ice.
  var beach=Game1.getLocationFromName("Beach");var control=new Vector2(1,1);
  Check(!beach.objects.ContainsKey(control),"vanilla-location control slot is free");
  var beachPot=new CrabPot{Location=beach,TileLocation=control};beach.objects.Add(control,beachPot);
  try {
   chest.Items.Clear();for(int i=0;i<chest.GetActualCapacity();i++)chest.Items.Add(ItemRegistry.Create("(T)Axe"));
   Check(RecoveryApi().RecoverNow()==0 && ReferenceEquals(source.objects[tile],legacy) && legacy.bait.Value?.ItemId=="DeluxeBait","full chest retains stranded source and unused bait");
  }finally{chest.Items.Clear();foreach(var item in stored)chest.Items.Add(item);}
  try {
   Check(RecoveryApi().RecoverNow()==1 && !source.objects.ContainsKey(tile),"clearing chest allows deferred gear recovery exactly once");
   Check(chest.Items.Where(i=>i?.ItemId=="DeluxeBait").Sum(i=>i!.Stack)==1,"unused deluxe bait is refunded once");
   Check(ReferenceEquals(beach.objects[control],beachPot),"vanilla-location crab pot is untouched");
  }finally{beach.objects.Remove(control);}
 }

 void AuditRecoveryReload() {
  try {
   Check(Game1.GetSaveGameName(false)=="ArcticRecoveryQA" && Game1.currentSeason=="winter" && Game1.dayOfMonth==1,"reload reads isolated winter-1 recovery save");
   var chest=RecoveryChest();string expected=Game1.player.modData["WhiteBay.QA/RecoveryExpected"];
   Check(RecoverySnapshot(chest.Items)==expected,"saved chest quantities and qualities survived process restart");
   Check(RecoveryApi().RecoverNow()==0 && RecoverySnapshot(chest.Items)==expected,"load and repeat recovery do not duplicate items");
   Check(Game1.getLocationFromName(Prefix+"Harbor").objects.Values.OfType<CrabPot>().Count(p=>p.modData.TryGetValue(RecoveryCaseTag,out string tag) && tag=="open")==int.Parse(Game1.player.modData["WhiteBay.QA/RecoveryControlCount"]),"all open-water controls survive reload");
   Monitor.Log("AUDIT RECOVERY RELOAD COMPLETE "+expected,LogLevel.Info);
  }catch(Exception ex){Monitor.Log("AUDIT RECOVERY RELOAD FAIL "+ex,LogLevel.Error);}
 }

 void LocateRecoveryChest() {
  try {
   var chest=RecoveryChest();var p=chest.TileLocation;
   Game1.warpFarmer(Prefix+"Fishery",(int)p.X,(int)p.Y+1,false);Game1.player.CurrentToolIndex=11;
   DelayedAction.functionAfterDelay(()=>Game1.player.faceDirection(0),300);
   Monitor.Log("Preview F11: recovery chest approach only at "+p,LogLevel.Info);
  }catch(Exception ex){Monitor.Log("AUDIT RECOVERY locate "+ex.Message,LogLevel.Error);}
 }
}
