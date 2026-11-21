using System;
using System.Linq;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Quests;
using StardewValley.Menus;
using Microsoft.Xna.Framework;
using System.Collections.Generic;

public partial class ModEntry {
 const string Prefix="ArcticPassage_";
 bool auditActive;
 bool awaitingSleep;
 IEnumerator<int>? auditSave;
 void RegisterIntegrationAudit(IModHelper helper) {
  RegisterCompatibilityAudit(helper);
  helper.ConsoleCommands.Add("ap_audit_delivery","Native engine integration audit; modifies only the dedicated ArcticQA test character in memory.",(_,_)=>{
   if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA")return;
   try { AuditDeliveries(); } catch(Exception ex) { Monitor.Log("AUDIT FAIL "+ex,LogLevel.Error); }
  });
  helper.ConsoleCommands.Add("ap_audit_sleep","Start a native overnight test from the guesthouse bed.",(_,_)=>{
   if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA")return;
   auditActive=true;awaitingSleep=true;
   Game1.activeClickableMenu=null;Game1.dialogueUp=false;Game1.player.CanMove=true;
   Game1.warpFarmer(Prefix+"Guesthouse",4,7,false);
   DelayedAction.functionAfterDelay(()=>{
    try {
     Check(Game1.currentLocation.Name==Prefix+"Guesthouse","sleep begins in guesthouse");
     Check(Game1.currentLocation.CanWakeUpHere(Game1.player,new Point(4,7)),"native bed is a valid wake-up point");
     Game1.player.modData["WhiteBay.QA/BeforeSleepDay"]=Game1.Date.TotalDays.ToString();
     // Advancing the displayed hour alone skips daytime machine processing.
     // Exercise the native ten-minute updates before the normal overnight path.
     for(int i=0;i<200 && Game1.timeOfDay<2200;i++) {
      int previous=Game1.timeOfDay;Game1.performTenMinuteClockUpdate();
      if(Game1.timeOfDay<=previous)throw new Exception("Native clock did not advance");
     }
     Game1.player.Stamina=10;Game1.player.health=10;
     Game1.currentLocation.answerDialogueAction("Sleep_Yes",null);
    } catch(Exception ex) { Monitor.Log("AUDIT FAIL "+ex,LogLevel.Error); }
   },1200);
  });
  helper.Events.GameLoop.DayStarted+=(_,_)=>{
   if(!auditActive || !awaitingSleep || Game1.player.Name!="ArcticQA")return;
   awaitingSleep=false;
   DelayedAction.functionAfterDelay(()=>{
    try {
     Check(Game1.currentLocation.Name==Prefix+"Guesthouse","woke in guesthouse after native overnight transition");
     Check(Game1.Date.TotalDays>int.Parse(Game1.player.modData["WhiteBay.QA/BeforeSleepDay"]),"calendar advanced overnight");
     Check(Game1.player.Stamina==Game1.player.MaxStamina && Game1.player.health==Game1.player.maxHealth,"guesthouse sleep restores stamina and health");
     Check(Game1.player.mailReceived.Contains(Prefix+"Shed") && Game1.player.mailReceived.Contains(Prefix+"Boat"),"day-start actions completed both repairs");
     Check(Game1.player.mailbox.Contains(Prefix+"Processing") && Game1.player.mailbox.Contains(Prefix+"Route"),"processing reward and route letters arrived");
     Monitor.Log("AUDIT OVERNIGHT COMPLETE day="+Game1.Date.TotalDays+" tile="+Game1.player.Tile,LogLevel.Info);
    } catch(Exception ex) { Monitor.Log("AUDIT FAIL "+ex,LogLevel.Error); }
   },1800);
  };
  helper.ConsoleCommands.Add("ap_audit_orders","Exercise native purchase logic and reopen stock; API audit, not UI clicks.",(_,_)=>{
   if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA")return;
   try { AuditOrders(); } catch(Exception ex) { Monitor.Log("AUDIT FAIL "+ex,LogLevel.Error); }
  });
  helper.ConsoleCommands.Add("ap_audit_stock","Assert the number of available daily offers: ap_audit_stock 0 or 3.",(_,args)=>{
   if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA" || args.Length!=1)return;
   try {
    var shop=OpenOrders();int available=shop.forSale.Count(i=>shop.itemPriceAndStock[i].Stock>0);
    Check(available==int.Parse(args[0]),"daily order available stock="+available+" expected="+args[0]);Game1.exitActiveMenu();
   } catch(Exception ex) { Monitor.Log("AUDIT FAIL "+ex,LogLevel.Error); }
  });
  helper.ConsoleCommands.Add("ap_audit_machine_data","Read the actual native machine definitions used for compatibility work.",(_,_)=>{
   var machines=helper.GameContent.Load<Dictionary<string,StardewValley.GameData.Machines.MachineData>>("Data/Machines");
   foreach(var id in new[]{"(BC)FishSmoker","(BC)BaitMaker","(BC)Dehydrator"})
    if(machines.TryGetValue(id,out var entry))Monitor.Log("NATIVE MACHINE "+id+" "+Newtonsoft.Json.JsonConvert.SerializeObject(entry),LogLevel.Info);
  });
  helper.ConsoleCommands.Add("ap_audit_processing","Native recipe/input/price/quality tests and persistent two-night racks.",(_,_)=>{
   if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA")return;
   try { AuditProcessing(); } catch(Exception ex) { Monitor.Log("AUDIT FAIL "+ex,LogLevel.Error); }
  });
  helper.Events.GameLoop.DayStarted+=(_,_)=>{
   if(Game1.player?.Name!="ArcticQA")return;
   DelayedAction.functionAfterDelay(()=>{
    try {
     var here=Game1.getLocationFromName(Prefix+"Fishery");
     foreach(var rack in here.objects.Values.Where(o=>o.modData.ContainsKey("WhiteBay.QA/DryStartDay") && o.heldObject.Value!=null)) {
      int days=Game1.Date.TotalDays-int.Parse(rack.modData["WhiteBay.QA/DryStartDay"]);
      Monitor.Log("AUDIT RACK day="+days+" ready="+rack.readyForHarvest.Value+" minutes="+rack.MinutesUntilReady+" output="+rack.heldObject.Value?.QualifiedItemId,LogLevel.Info);
      if(days>0)Check(rack.readyForHarvest.Value==(days>=2),"two-night drying deadline day="+days);
     }
    } catch(Exception ex) { Monitor.Log("AUDIT FAIL "+ex,LogLevel.Error); }
   },1800);
  };
  helper.ConsoleCommands.Add("ap_audit_fjord","Use repaired map action and then deliver the final fish via native quest handler.",(_,_)=>{
   if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA")return;
   Game1.activeClickableMenu=null;Game1.warpFarmer(Prefix+"Harbor",42,24,false);
   DelayedAction.functionAfterDelay(()=>{
    try {
     string action=Game1.currentLocation.doesTileHaveProperty(43,24,"Action","Buildings");
     Check(action=="Warp 35 34 "+Prefix+"Icefjord","repaired route action is active");
     Game1.currentLocation.performAction(action,Game1.player,new xTile.Dimensions.Location(43,24));
     DelayedAction.functionAfterDelay(()=>{
      try {
       Check(Game1.currentLocation.Name==Prefix+"Icefjord","actual route action reached fjord");
       Check(FindQuest("FjordVisit").completed.Value,"native location quest completed after route travel");
       Deliver("DeepCatch","Ada","(O)ArcticPassage_Halibut",1);
       Check(!Game1.player.questLog.Any(q=>q.id.Value.StartsWith(Prefix) && !q.completed.Value),"six-step delivery chain has no unfinished stage");
      } catch(Exception ex) { Monitor.Log("AUDIT FAIL "+ex,LogLevel.Error); }
     },1200);
    } catch(Exception ex) { Monitor.Log("AUDIT FAIL "+ex,LogLevel.Error); }
   },1500);
  });
  helper.ConsoleCommands.Add("ap_audit_save","Serialize only the dedicated QA character with the native SaveGame enumerator.",(_,_)=>{
   if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA" || auditSave!=null)return;
   Game1.activeClickableMenu=null;Game1.dialogueUp=false;
   auditSave=SaveGame.Save();
  });
  helper.Events.GameLoop.UpdateTicked+=(_,_)=>{
   if(auditSave==null)return;
   try {
    if(!auditSave.MoveNext()) { auditSave.Dispose();auditSave=null;Monitor.Log("AUDIT NATIVE SAVE COMPLETE",LogLevel.Info); }
   } catch(Exception ex) { auditSave=null;Monitor.Log("AUDIT FAIL save "+ex,LogLevel.Error); }
  };
  helper.Events.GameLoop.SaveLoaded+=(_,_)=>{
   if(Game1.player.Name!="ArcticQA")return;
   Monitor.Log("AUDIT LOAD SNAPSHOT location="+Game1.currentLocation?.Name+" lastSleep="+Game1.player.lastSleepLocation.Value+" tile="+Game1.player.Tile+" day="+Game1.Date.TotalDays+" money="+Game1.player.Money+" completed="+string.Join(",",Game1.player.questLog.Where(q=>q.id.Value.StartsWith(Prefix)).Select(q=>q.id.Value+":"+q.completed.Value))+" flags="+string.Join(",",Game1.player.mailReceived.Where(s=>s.StartsWith(Prefix))),LogLevel.Info);
  };
 }
 void Check(bool condition,string message) {
  if(!condition)throw new Exception(message);
  Monitor.Log("AUDIT PASS "+message,LogLevel.Info);
 }
 Quest FindQuest(string id)=>Game1.player.questLog.Single(q=>q.id.Value==Prefix+id);
 int CountItem(string id)=>Game1.player.Items.Where(i=>i?.QualifiedItemId==id).Sum(i=>i.Stack);
 void DrainDialogue(NPC npc) {
  if(npc.CurrentDialogue.Count==0)return;
  var dialogue=npc.CurrentDialogue.Peek();
  for(int i=0;i<20 && !dialogue.isDialogueFinished();i++) {
   dialogue.prepareCurrentDialogueForDisplay();
   dialogue.exitCurrentDialogue();
  }
  Check(dialogue.isDialogueFinished(),npc.Name+" delivery dialogue parsed to completion");
  npc.CurrentDialogue.Clear();
  Game1.activeClickableMenu=null;
  Game1.dialogueUp=false;
  Game1.player.CanMove=true;
 }
 void Deliver(string questId,string npcId,string itemId,int amount,string? flag=null) {
  var q=FindQuest(questId);var npc=Game1.getCharacterFromName(Prefix+npcId);
  var item=ItemRegistry.Create(itemId,amount+2);
  Game1.player.Items.Add(item);
  int before=CountItem(itemId);
  Check(q.OnItemOfferedToNpc(npc,item,false),questId+" accepted matching item");
  Check(q.completed.Value,questId+" completed through native delivery handler");
  Check(CountItem(itemId)==before-amount,questId+" consumed exactly "+amount);
  int after=CountItem(itemId);
  Check(!q.OnItemOfferedToNpc(npc,item,false) && CountItem(itemId)==after,questId+" cannot consume a second delivery");
  DrainDialogue(npc);
  if(flag!=null)Check(Game1.player.mailReceived.Contains(Prefix+flag),questId+" persisted its delivered-material flag");
  Monitor.Log("AUDIT REWARD "+questId+" pending journal gold="+q.GetMoneyReward(),LogLevel.Info);
 }
 void AuditDeliveries() {
  auditActive=true;
  var f=Game1.player;
  foreach(var q in f.questLog.Where(q=>q.id.Value.StartsWith(Prefix)).ToArray())f.questLog.Remove(q);
  foreach(var flag in new[]{"WoodDelivered","IronDelivered","Shed","Boat"})f.mailReceived.Remove(Prefix+flag);
  f.addQuest(Prefix+"Arrival");
  var arrival=FindQuest("Arrival");
  Check(!arrival.OnWarped(Game1.getLocationFromName(Prefix+"Harbor"),false) && !arrival.completed.Value,"arrival rejects the wrong location");
  Check(arrival.OnWarped(Game1.getLocationFromName(Prefix+"Guesthouse"),false) && arrival.completed.Value,"arrival completes at the guesthouse");
  string first="FirstCatch_"+Game1.currentSeason;
  var catchQuest=(ItemDeliveryQuest)FindQuest(first);
  var ada=Game1.getCharacterFromName(Prefix+"Ada");
  var insufficient=ItemRegistry.Create(catchQuest.ItemId.Value,2);f.Items.Add(insufficient);
  int before=CountItem(catchQuest.ItemId.Value);
  catchQuest.OnItemOfferedToNpc(ada,insufficient,false);
  Check(!catchQuest.completed.Value && before==CountItem(catchQuest.ItemId.Value),"insufficient fish are not consumed");
  DrainDialogue(ada);
  Deliver(first,"Ada",catchQuest.ItemId.Value,3);
  Deliver("Shed","Roan","(O)388",40,"WoodDelivered");
  Deliver("BoatRepair","Roan","(O)335",2,"IronDelivered");
  Check(!f.mailReceived.Contains(Prefix+"Boat") && !f.mailReceived.Contains(Prefix+"Shed"),"repairs do not unlock on the delivery day");
  Check(f.hasQuest(Prefix+"FjordVisit"),"fjord visit is the next active quest");
  Monitor.Log("AUDIT DELIVERY COMPLETE: engine checks only; journal payout, overnight transitions and physical catching remain separate tests.",LogLevel.Info);
 }
 ShopMenu OpenOrders() {
  Game1.activeClickableMenu=null;Game1.dialogueUp=false;
  Game1.currentLocation.performAction("OpenShop "+Prefix+"Orders",Game1.player,new xTile.Dimensions.Location(8,21));
  return Game1.activeClickableMenu as ShopMenu ?? throw new Exception("Orders did not open native shop");
 }
 void AuditOrders() {
  var shop=OpenOrders();
  Check(shop.forSale.Count==3,"exactly three daily orders are available");
  foreach(var item in shop.forSale.ToArray()) {
   var stock=shop.itemPriceAndStock[item];
   Check(stock.TradeItem!=null && stock.TradeItemCount>0 && stock.Stock==1,"order requires fish and has one stock");
   var fish=ItemRegistry.Create(stock.TradeItem!,stock.TradeItemCount!.Value+1);
   Game1.player.Items.Add(fish);
   int count=CountItem(fish.QualifiedItemId),money=Game1.player.Money;
   int expected=int.Parse(stock.ActionsOnPurchase.First(s=>s.StartsWith("AddMoney ")).Split(' ').Last());
   Helper.Reflection.GetMethod(shop,"tryToPurchaseItem").Invoke<bool>(item,null,1,0,0);
   Check(CountItem(fish.QualifiedItemId)==count-stock.TradeItemCount.Value,"native purchase consumed requested fish");
   Check(Game1.player.Money==money+expected,"native order paid exactly "+expected+" gold");
   foreach(var action in stock.ActionsOnPurchase.Where(s=>s.StartsWith("AddMail ")))
    Check(Game1.player.mailReceived.Contains(action.Split(' ')[2]),"dated order receipt flag was saved on farmer");
   if(shop.heldItem is Item receipt)Game1.player.addItemToInventoryBool(receipt);
   shop.heldItem=null;
  }
  Game1.exitActiveMenu();
  shop=OpenOrders();
  Check(shop.forSale.All(i=>shop.itemPriceAndStock[i].Stock<=0),"reopening same-day shop cannot restore order stock");
  Game1.exitActiveMenu();
  Monitor.Log("AUDIT ORDERS COMPLETE: native purchase handler checked; mouse purchase, next-day reset and save/reload remain separate tests.",LogLevel.Info);
 }
 void AuditProcessing() {
  var f=Game1.player;
  var recipe=new CraftingRecipe(Prefix+"DryingRack",false);
  var materials=new[]{("(O)388",40),("(O)771",15),("(O)335",1)};
  foreach(var (id,n) in materials)f.Items.Add(ItemRegistry.Create(id,n));
  var before=materials.ToDictionary(v=>v.Item1,v=>CountItem(v.Item1));
  recipe.consumeIngredients(null);
  foreach(var (id,n) in materials)Check(CountItem(id)==before[id]-n,"native crafting consumed "+n+" "+id);
  Check(recipe.createItem().QualifiedItemId=="(BC)"+Prefix+"DryingRack","recipe creates the registered big craftable");
  var here=Game1.getLocationFromName(Prefix+"Fishery");
  foreach(var (fish,index,price) in new[]{("AtlanticCod",0,168),("Capelin",1,91),("PolarCod",2,119)}) {
   foreach(int quality in new[]{0,1,2,4}) {
    var rack=(StardewValley.Object)ItemRegistry.Create("(BC)"+Prefix+"DryingRack");
    rack.Location=here;rack.TileLocation=new Vector2(14+index,12);
    var input=ItemRegistry.Create("(O)"+Prefix+fish,2,quality);f.Items.Add(input);
    int count=CountItem(input.QualifiedItemId),coal=CountItem("(O)382");
    Check(rack.performObjectDropInAction(input,false,f,false),"rack accepted "+fish+" quality="+quality);
    Check(CountItem(input.QualifiedItemId)==count-1 && CountItem("(O)382")==coal,"rack consumes one fish and no coal");
    var output=rack.heldObject.Value;
    Check(output?.QualifiedItemId=="(O)"+Prefix+"Dried"+fish && output.Quality==quality,"rack keeps fish identity and quality="+quality);
    Check(output!.Price==price,"rack base output price="+price);
    Check(!rack.readyForHarvest.Value && rack.MinutesUntilReady>0,"output is not immediately harvestable");
    if(quality==0) {
     rack.modData["WhiteBay.QA/DryStartDay"]=Game1.Date.TotalDays.ToString();
     here.objects[rack.TileLocation]=rack;
    }
    f.Items.Remove(input);
   }
  }
  foreach(var id in new[]{"(O)388","(O)"+Prefix+"Halibut","(O)"+Prefix+"ArcticChar"}) {
   var rack=(StardewValley.Object)ItemRegistry.Create("(BC)"+Prefix+"DryingRack");rack.Location=here;
   var input=ItemRegistry.Create(id,2);f.Items.Add(input);int count=CountItem(id);
   Check(!rack.performObjectDropInAction(input,false,f,false) && rack.heldObject.Value==null && CountItem(id)==count,"rack rejects unsupported input "+id);
   f.Items.Remove(input);
  }
  Monitor.Log("AUDIT PROCESSING INPUT COMPLETE: three racks remain in Fishery at 14..16,12 for real overnight/save tests.",LogLevel.Info);
 }
}
