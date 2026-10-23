using System;
using System.Linq;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Menus;

public partial class ModEntry {
 void PrepareRepairAudit() {
  if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA" || !ShipmentFlag("repair-preview.enabled"))return;
  Game1.SetSaveName("ArcticRepairQA");
  Monitor.Log("REPAIR QA isolated native shop API fixture; synthetic inputs, no normal catching or save claim.",LogLevel.Info);
  Game1.activeClickableMenu=null;Game1.eventUp=false;
  Game1.warpFarmer("ArcticPassage_Harbor",16,22,false);
  DelayedAction.functionAfterDelay(AuditRepairBarter,1000);
 }
 void AuditRepairBarter() {
  try {
   var f=Game1.player;
   f.mailReceived.Add("ArcticPassage_Shed");
   f.mailReceived.Remove("ArcticPassage_IronDelivered");f.mailReceived.Remove("ArcticPassage_Boat");
   foreach(var season in new[]{"spring","summer","fall","winter"}) {
    Game1.currentSeason=season;
    foreach(int n in new[]{1,2})f.mailReceived.Remove("ArcticPassage_LocalRepairIron_"+n);
    for(int i=0;i<f.Items.Count;i++)f.Items[i]=null;
    string fish="(O)ArcticPassage_"+(season is "spring" or "summer"?"Capelin":season=="fall"?"AtlanticCod":"PolarCod");
    ShopMenu Open() {
     Game1.currentLocation.performAction("OpenShop ArcticPassage_Supplies",f,new xTile.Dimensions.Location(16,21));
     return Game1.activeClickableMenu as ShopMenu ?? throw new Exception("No supplies shop");
    }
    var shop=Open();
    var offers=shop.forSale.Where(i=>shop.itemPriceAndStock[i].TradeItem==fish).ToArray();
    Check(offers.Length==2,"repair "+season+" has exactly two native seasonal barter offers");
    int money=f.Money;
    Helper.Reflection.GetMethod(shop,"tryToPurchaseItem").Invoke<bool>(offers[0],null,1,0,0);
    Check(shop.heldItem==null && !f.mailReceived.Contains("ArcticPassage_LocalRepairIron_1") && f.Money==money,"repair empty fish inventory cannot obtain iron or consume receipt");
    f.Items[0]=ItemRegistry.Create(fish,7);
    foreach(var item in offers) {
     Helper.Reflection.GetMethod(shop,"tryToPurchaseItem").Invoke<bool>(item,null,1,0,0);
     Check(shop.heldItem?.QualifiedItemId=="(O)335","repair native trade produces an ordinary iron bar");
     f.addItemToInventoryBool((Item)shop.heldItem);shop.heldItem=null;
    }
    Check(CountItem(fish)==1 && CountItem("(O)335")==2 && f.Money==money,"repair native two trades consume six fish, keep one and do not spend gold");
    Check(f.mailReceived.Contains("ArcticPassage_LocalRepairIron_1") && f.mailReceived.Contains("ArcticPassage_LocalRepairIron_2"),"repair two persistent receipts recorded");
    Game1.exitActiveMenu();shop=Open();
    Check(!shop.forSale.Any(i=>shop.itemPriceAndStock[i].TradeItem==fish),"repair reopening cannot restore the redeemed offers");
    Game1.exitActiveMenu();
   }
   Game1.currentSeason="spring";
   Game1.currentLocation.performAction("OpenShop ArcticPassage_Supplies",f,new xTile.Dimensions.Location(16,21));
   var closed=(ShopMenu)Game1.activeClickableMenu;
   Check(!closed.forSale.Any(i=>closed.itemPriceAndStock[i].TradeItem!=null),"repair season change does not reset the two shared receipts");
   Monitor.Log("REPAIR QA COMPLETE: four seasons, native purchase/rejection/consumption/persistent receipt/reopen and cross-season limit passed. API fixture only, no save.",LogLevel.Info);
  }catch(Exception ex){Monitor.Log("REPAIR QA FAILED: "+ex,LogLevel.Error);}
 }
}
