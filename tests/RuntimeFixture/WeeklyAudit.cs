using System;
using System.Linq;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Menus;
using StardewValley.SpecialOrders;
using StardewValley.SpecialOrders.Objectives;

public partial class ModEntry {
 void PrepareWeeklyAudit() {
  if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA" || !ShipmentFlag("weekly-preview.enabled"))return;
  // Never permit this fixture to overwrite its source preview save or an ordinary character.
  Game1.SetSaveName("ArcticWeeklyQA");
  Monitor.Log("WEEKLY QA: isolated native API fixture, synthetic fish; NOT normal catching/play. No save requested.",LogLevel.Info);
  Game1.activeClickableMenu=null;Game1.eventUp=false;
  Game1.player.mailReceived.Add("ArcticPassage_Shed");
  foreach(var q in Game1.player.questLog.Where(q=>q.id.Value.StartsWith("ArcticPassage_")).ToArray())Game1.player.questLog.Remove(q);
  Game1.warpFarmer("ArcticPassage_CommunityHouse",3,6,false);
  DelayedAction.functionAfterDelay(AuditWeeklyContracts,1000);
 }
 void AuditWeeklyContracts() {
  try {
   const string type="ArcticPassage_Weekly";
   var f=Game1.player;var team=f.team;var here=Game1.currentLocation;
   foreach(var o in team.specialOrders.Where(o=>o.orderType.Value==type).ToArray())team.specialOrders.Remove(o);
   team.acceptedSpecialOrderTypes.Remove(type);
   team.acceptedSpecialOrderTypes.Add("ArcticQA_Unrelated");
   int money=f.Money;
   here.performAction("ArcticPassageWeekly",f,new xTile.Dimensions.Location(5,5));
   var board=Game1.activeClickableMenu as SpecialOrdersBoard ?? throw new Exception("No native weekly board");
   var left=Helper.Reflection.GetField<SpecialOrder>(board,"leftOrder").GetValue();
   var button=left.questKey.Value=="ArcticPassage_FreshCrates"?board.acceptLeftQuestButton:board.acceptRightQuestButton;
   board.receiveLeftClick(button.bounds.Center.X,button.bounds.Center.Y);
   var order=team.specialOrders.Single(o=>o.orderType.Value==type);
   Check(order.questKey.Value=="ArcticPassage_FreshCrates" && f.Money==money,"weekly native board accepted FreshCrates without payout");
   board.receiveLeftClick(button.bounds.Center.X,button.bounds.Center.Y);
   Check(team.specialOrders.Count(o=>o.orderType.Value==type)==1,"weekly repeated acceptance cannot duplicate the order");
   Game1.exitActiveMenu();order.Update();
   var objective=(DonateObjective)order.objectives.Single();
   Check(objective.GetCount()==0,"weekly donation starts at zero");
   here.performAction("ArcticPassageFishCrate",f,new xTile.Dimensions.Location(3,5));
   DelayedAction.functionAfterDelay(()=>AuditWeeklyBox(order,money),1000);
  }catch(Exception ex){Monitor.Log("WEEKLY QA FAILED: "+ex,LogLevel.Error);}
 }
 void AuditWeeklyBox(SpecialOrder order,int money) {
  try {
   var f=Game1.player;var team=f.team;var here=Game1.currentLocation;
   var objective=(DonateObjective)order.objectives.Single();
   var crate=Game1.activeClickableMenu as QuestContainerMenu ?? throw new Exception("No native dropbox after lock");
   var old=f.Items.ToArray();
   for(int i=0;i<f.Items.Count;i++)f.Items[i]=null;
   void Put(int slot,string id,int n,int quality=0) {
    f.Items[slot]=ItemRegistry.Create(id,n,quality);
    var b=crate.inventory.inventory[slot].bounds;crate.receiveLeftClick(b.Center.X,b.Center.Y);
   }
   Put(0,"(O)ArcticPassage_PolarCod",1);
   Check(objective.GetCount()==1 && f.Items[0]==null,"weekly native box accepts partial one-fish delivery");
   Put(1,"(O)388",4);
   Check(objective.GetCount()==1 && f.Items[1]?.Stack==4,"weekly box rejects wood without consuming it");
   Put(2,"(O)ArcticPassage_Shrimp",2);
   Check(objective.GetCount()==1 && f.Items[2]?.Stack==2,"weekly box rejects trap shrimp");
   crate.exitThisMenu();
   Check(objective.GetCount()==1 && !order.HasReward(),"weekly partial progress survives native box closing without reward");
   here.performAction("ArcticPassageFishCrate",f,new xTile.Dimensions.Location(3,5));
   DelayedAction.functionAfterDelay(()=> {
    try {
   crate=(QuestContainerMenu)Game1.activeClickableMenu;
   Put(3,"(O)ArcticPassage_Capelin",2,2);
   Put(4,"(O)ArcticPassage_AtlanticCod",5,1);
   Check(objective.GetCount()==6 && f.Items[4]?.Stack==2,"weekly mixed species/qualities cap at six and keep surplus two");
   crate.exitThisMenu();order.Update();order.CheckCompletion();
   Check(order.HasReward() && order.GetMoneyReward()==650 && f.Money==money,"weekly closing native box confirms completion; 650 pending, not automatically paid");
   var fishOrder=SpecialOrder.GetSpecialOrder("ArcticPassage_CoastalLog",42);
   fishOrder.Update();
   var fishGoal=fishOrder.objectives.Single();
   fishOrder.onFishCaught?.Invoke(f,ItemRegistry.Create("(O)388"));
   fishOrder.onFishCaught?.Invoke(f,ItemRegistry.Create("(O)ArcticPassage_Shrimp"));
   Check(fishGoal.GetCount()==0,"weekly native Fish objective rejects wood and trap catch");
   foreach(string id in new[]{"PolarCod","Capelin","AtlanticCod","ArcticChar","Wolffish","Halibut"})fishOrder.onFishCaught?.Invoke(f,ItemRegistry.Create("(O)ArcticPassage_"+id));
   Check(fishGoal.GetCount()==6,"weekly native Fish callback counts six tagged rod catches (API simulation only)");
   Check(team.acceptedSpecialOrderTypes.Contains("ArcticQA_Unrelated"),"weekly refresh preserves unrelated accepted board type");
   for(int i=0;i<old.Length;i++)f.Items[i]=old[i];
   Monitor.Log("WEEKLY QA DONATION COMPLETE: native board, partial/reopen, rejected items, mixed quality/species, surplus and pending reward passed. K/J then Enter may test native payout separately. No ordinary play or save claimed.",LogLevel.Info);
    }catch(Exception ex){Monitor.Log("WEEKLY QA FAILED: "+ex,LogLevel.Error);}
   },1000);
  }catch(Exception ex){Monitor.Log("WEEKLY QA FAILED: "+ex,LogLevel.Error);}
 }
}
