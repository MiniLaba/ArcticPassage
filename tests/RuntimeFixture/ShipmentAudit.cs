using System;
using System.Linq;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Quests;

public interface IShipmentApi { bool CanChangeShipment(); string ChangeShipment(); }

public partial class ModEntry {
 bool ShipmentFlag(string name)=>System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,name));
 void PrepareShipmentPreview() {
  if(ShipmentFlag("shipment-reload.enabled")) {
   Monitor.Log("SHIPMENT RELOAD native saved arrival, no preparation or mutation",LogLevel.Info);return;
  }
  // Redirect the native save target BEFORE any fixture mutation. The original
  // winter save must never receive our prepared quest or optional UI changes.
  Game1.SetSaveName("ArcticShipmentQA");
  try { AuditShipment(); }
  catch(Exception ex) {Monitor.Log("AUDIT SHIPMENT FAIL "+ex,LogLevel.Error);return;}
  ClearShipmentProgress();
  Game1.player.addQuest(Prefix+"FirstCatch_summer");
  Game1.warpFarmer(Prefix+"Guesthouse",12,14,false);
  Game1.timeOfDay=1200;Game1.player.CurrentToolIndex=11;
  Game1.options!.desiredBaseZoomLevel=.75f;
  Monitor.Log("SHIPMENT UI FIXTURE: native winter 7, summer capelin order, no fish/money grants; save target="+Game1.GetSaveGameName(false)+". Not a normal new-character run.",LogLevel.Info);
 }
 void ClearShipmentProgress() {
  foreach(var q in Game1.player.questLog.Where(q=>q.id.Value.StartsWith(Prefix)).ToArray())Game1.player.questLog.Remove(q);
  foreach(var key in new[]{"WoodDelivered","IronDelivered","Shed","Boat"})Game1.player.mailReceived.Remove(Prefix+key);
 }
 string ShipmentItems()=>string.Join("|",Game1.player.Items.Select((i,n)=>i==null?n+":empty":n+":"+i.QualifiedItemId+":"+i.Stack+":"+i.Quality));
 void AuditShipment() {
  var f=Game1.player;var quests=f.questLog.ToArray();var mail=f.mailReceived.ToArray();
  var items=f.Items.Select(i=>{if(i==null)return null;var c=i.getOne();c.Stack=i.Stack;return c;}).ToArray();
  string season=Game1.currentSeason;var location=Game1.currentLocation;int money=f.Money;
  var api=Helper.ModRegistry.GetApi<IShipmentApi>("WhiteBay.ArcticPassage.Runtime")??throw new Exception("Missing runtime shipment API");
  try {
   Game1.currentLocation=Game1.getLocationFromName(Prefix+"Guesthouse");
   foreach(string from in new[]{"spring","summer","fall","winter"})
    foreach(string now in new[]{"spring","summer","fall","winter"}) {
     ClearShipmentProgress();Game1.currentSeason=now;
     var sentinel=new Quest();sentinel.id.Value="WhiteBayQA_Unrelated";f.questLog.Add(sentinel);
     f.addQuest(Prefix+"FirstCatch_"+from);
     var q=(ItemDeliveryQuest)FindQuest("FirstCatch_"+from);q.accepted.Value=true;q.dayQuestAccepted.Value=3;q.modData["WhiteBayQA/keep"]="kept";
     int slot=f.questLog.IndexOf(q);string before=ShipmentItems();int gold=f.Money;
     bool expected=from is "spring" or "summer" ? now is "fall" or "winter" : from=="fall" ? now is "spring" or "winter" : now is "summer" or "fall";
     Check(api.CanChangeShipment()==expected,"shipment availability "+from+" -> "+now);
     string result=api.ChangeShipment();
     Check(result==(expected?"changed":"changeUnavailable"),"shipment result "+from+" -> "+now);
     var current=(ItemDeliveryQuest)f.questLog[slot];
     Check(f.questLog.Contains(sentinel)&&ShipmentItems()==before&&f.Money==gold,"shipment preserves unrelated quest, every item and money");
     Check(current.number.Value==3&&current.moneyReward.Value==400&&current.nextQuests.Single()==Prefix+"Shed"&&current.accepted.Value&&current.dayQuestAccepted.Value==3&&current.modData["WhiteBayQA/keep"]=="kept","shipment preserves native contract and quest metadata");
     if(expected)Check(!api.CanChangeShipment()&&api.ChangeShipment()=="changeUnavailable","shipment repeat cannot reset order");
     f.questLog.Remove(sentinel);
    }
   ClearShipmentProgress();Game1.currentSeason="winter";f.addQuest(Prefix+"FirstCatch_summer");
   var completed=FindQuest("FirstCatch_summer");completed.completed.Value=true;
   Check(completed.HasReward()&&!api.CanChangeShipment()&&api.ChangeShipment()=="changeUnavailable"&&completed.GetMoneyReward()==400,"completed unclaimed 400 reward cannot be rebooked");
   ClearShipmentProgress();f.addQuest(Prefix+"FirstCatch_summer");f.addQuest(Prefix+"FirstCatch_spring");
   Check(!api.CanChangeShipment(),"duplicate pending orders fail closed");
   ClearShipmentProgress();f.addQuest(Prefix+"FirstCatch_summer");((ItemDeliveryQuest)FindQuest("FirstCatch_summer")).number.Value=4;
   Check(!api.CanChangeShipment(),"third-party modified amount is preserved");
   ClearShipmentProgress();f.addQuest(Prefix+"FirstCatch_summer");Game1.currentLocation=Game1.getLocationFromName("Beach");
   Check(!api.CanChangeShipment()&&api.ChangeShipment()=="changeUnavailable","vanilla location rejects rebooking");
   Game1.currentLocation=Game1.getLocationFromName(Prefix+"Guesthouse");
   Check(api.ChangeShipment()=="changed","native winter replacement created");
   var changed=FindQuest("FirstCatch_winter");var ada=Game1.getCharacterFromName(Prefix+"Ada");
   var wrong=ItemRegistry.Create("(O)"+Prefix+"Capelin",3);f.Items.Add(wrong);
   Check(!changed.OnItemOfferedToNpc(ada,wrong,false)&&wrong.Stack==3,"native rebooked order rejects old fish without consuming it");
   var right=ItemRegistry.Create("(O)"+Prefix+"PolarCod",5);f.Items.Add(right);
   Check(changed.OnItemOfferedToNpc(ada,right,false)&&right.Stack==2&&changed.completed.Value,"native rebooked order consumes exactly three new fish");
   Check(f.questLog.Count(q=>q.id.Value==Prefix+"Shed")==1&&changed.GetMoneyReward()==400&&!api.CanChangeShipment(),"native continuation and pending reward occur only once");
   DrainDialogue(ada);
   Monitor.Log("AUDIT SHIPMENT COMPLETE: 16 season pairs plus duplicate/completed/modified/vanilla/native-delivery guards; API fixture, not normal play",LogLevel.Info);
  } finally {
   Game1.currentSeason=season;Game1.currentLocation=location;f.Money=money;
   f.questLog.Clear();foreach(var q in quests)f.questLog.Add(q);
   f.mailReceived.Clear();foreach(var m in mail)f.mailReceived.Add(m);
   f.Items.Clear();foreach(var i in items)f.Items.Add(i);
   Game1.activeClickableMenu=null;Game1.dialogueUp=false;f.CanMove=true;
  }
 }
}
