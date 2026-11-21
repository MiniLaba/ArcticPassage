using System;
using System.Linq;
using System.Collections.Generic;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Menus;

public partial class ModEntry {
 void RegisterCompatibilityAudit(IModHelper helper) {
  helper.ConsoleCommands.Add("ap_audit_collect","Collect two ready racks through native machine handlers; leave the middle rack for desktop input.",(_,_)=>{
   if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA")return;
   try {
    var here=Game1.getLocationFromName(Prefix+"Fishery");
    foreach(var rack in here.objects.Values.Where(o=>o.ItemId==Prefix+"DryingRack" && o.TileLocation.X!=15).ToArray()) {
     Check(rack.readyForHarvest.Value && rack.heldObject.Value!=null,"rack is ready before collection");
     string id=rack.heldObject.Value!.QualifiedItemId;int before=CountItem(id);
     rack.checkForAction(Game1.player,false);
     Check(CountItem(id)==before+1 && rack.heldObject.Value==null && !rack.readyForHarvest.Value,"native harvest adds exactly one product and empties rack");
    }
   } catch(Exception ex) { Monitor.Log("AUDIT FAIL "+ex,LogLevel.Error); }
  });
  helper.ConsoleCommands.Add("ap_audit_compatibility","Check native fish machines, fishery sale filters and recipe-mail parsing.",(_,_)=>{
   if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA")return;
   try { AuditCompatibility(); } catch(Exception ex) { Monitor.Log("AUDIT FAIL "+ex,LogLevel.Error); }
  });
  helper.ConsoleCommands.Add("ap_audit_cleanup","Keep test tools and a few processed goods in the dedicated preview inventory.",(_,_)=>{
   if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA")return;
   var f=Game1.player;
   var keep=f.Items.Where(i=>i is Tool || i?.ItemId.StartsWith(Prefix+"Dried")==true).Take(24).ToArray();
   f.Items.Clear();foreach(var item in keep)f.Items.Add(item);
   Monitor.Log("AUDIT cleaned preview inventory; no other character touched.",LogLevel.Info);
  });
 }
 void AuditCompatibility() {
  var f=Game1.player;var here=Game1.currentLocation;
  Game1.activeClickableMenu=null;
  here.performAction("OpenShop "+Prefix+"Market",f,new xTile.Dimensions.Location(8,6));
  var market=Game1.activeClickableMenu as ShopMenu ?? throw new Exception("Fishery market did not open");
  foreach(string fish in new[]{"PolarCod","AtlanticCod","Capelin","ArcticChar","Halibut","Wolffish"}) {
   var input=ItemRegistry.Create("(O)"+Prefix+fish,2,2);
   Check(market.highlightItemToSell(input),"fishery accepts "+fish+" for sale");
   foreach(string machineId in new[]{"FishSmoker","BaitMaker"}) {
    var machine=(StardewValley.Object)ItemRegistry.Create("(BC)"+machineId);machine.Location=here;
    f.Items.Add(input);int count=CountItem(input.QualifiedItemId);
    f.Items.Add(ItemRegistry.Create("(O)382",1));int coal=CountItem("(O)382");
    Check(machine.performObjectDropInAction(input,false,f,false),machineId+" accepts "+fish);
    Check(CountItem(input.QualifiedItemId)==count-1,machineId+" consumes one fish");
    var output=machine.heldObject.Value;
    Check(output!=null && output.preservedParentSheetIndex.Value==input.ItemId,machineId+" preserves custom fish identity "+fish);
    if(machineId=="FishSmoker")Check(CountItem("(O)382")==coal-1 && output!.Quality==2,"smoker consumes coal and keeps quality");
    else Check(CountItem("(O)382")==coal && output!.Stack>=5 && output.Stack<=10,"bait maker produces 5..10 targeted bait without fuel");
    f.Items.Remove(input);
   }
  }
  foreach(string product in new[]{"DriedAtlanticCod","DriedCapelin","DriedPolarCod"})
   Check(market.highlightItemToSell(ItemRegistry.Create("(O)"+Prefix+product)),"fishery accepts "+product+" for sale");
  Game1.exitActiveMenu();
  string key=Prefix+"DryingPlan";
  var mail=Helper.GameContent.Load<Dictionary<string,string>>("Data/mail")[key];
  var letter=new LetterViewerMenu(mail,key,false);
  Check(f.craftingRecipes.ContainsKey(Prefix+"DryingRack"),"native letter parser teaches drying-rack recipe");
  Monitor.Log("AUDIT COMPATIBILITY COMPLETE: engine methods, not a claim of mouse-driven crafting or sale.",LogLevel.Info);
 }
}
