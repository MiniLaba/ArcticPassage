using System;
using System.Linq;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Menus;

public partial class ModEntry {
 void PrepareDailyOrderAudit() {
  if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA" || !ShipmentFlag("daily-preview.enabled"))return;
  Game1.SetSaveName("ArcticDailyQA");
  Game1.activeClickableMenu=null; Game1.eventUp=false;
  Game1.warpFarmer("ArcticPassage_Harbor",8,22,false);
  DelayedAction.functionAfterDelay(AuditDailyOrders,1000);
 }
 void AuditDailyOrders() {
  var f=Game1.player; var items=f.Items.ToArray(); int gold=f.Money; int day=Game1.dayOfMonth;
  var mail=f.mailReceived.ToArray(); var data=f.modData.Pairs.ToArray();
  bool knewMira=f.friendshipData.ContainsKey("ArcticPassage_Mira");
  int friendship=knewMira?f.friendshipData["ArcticPassage_Mira"].Points:0;
  string Flag(string type)=>$"ArcticPassage_Order_{type}_{Game1.year}_{Game1.currentSeason}_{Game1.dayOfMonth}";
  int Friendship()=>f.friendshipData.TryGetValue("ArcticPassage_Mira",out var v)?v.Points:0;
  void Clear(){for(int i=0;i<f.Items.Count;i++)f.Items[i]=null;}
  void Put(int slot,string fish,int count,int quality=0){var item=ItemRegistry.Create(fish,count);item.Quality=quality;f.Items[slot]=item;}
  ShopMenu Open(){Game1.activeClickableMenu=null;Game1.currentLocation.performAction("OpenShop ArcticPassage_Orders",f,new xTile.Dimensions.Location(8,21));return Game1.activeClickableMenu as ShopMenu ?? throw new Exception("daily native counter missing");}
  void Buy(ShopMenu shop,ISalable item)=>Helper.Reflection.GetMethod(shop,"tryToPurchaseItem").Invoke<bool>(item,null,1,0,0);
  try {
   Monitor.Log("DAILY QA isolated synthetic inventory and native ShopMenu calls; no ordinary catch/interaction/save claim.",LogLevel.Info);
   foreach(string kind in new[]{"Regular","Restaurant","Research"})f.mailReceived.Remove(Flag(kind));
   f.Money=1000;Clear();
   var shop=Open();var restaurant=shop.forSale.Single(i=>i.QualifiedItemId=="(O)ArcticPassage_RestaurantReceipt");
   string fish=shop.itemPriceAndStock[restaurant].TradeItem;
   int payment=int.Parse(shop.itemPriceAndStock[restaurant].ActionsOnPurchase.Single(a=>a.StartsWith("AddMoney ")).Split(' ')[1]);
   int startFriendship=Friendship();
   Buy(shop,restaurant);
   Check(shop.heldItem==null && f.Money==1000 && !f.mailReceived.Contains(Flag("Restaurant")),"daily empty delivery has no payment or receipt");
   Put(0,fish,10);Buy(shop,restaurant);
   Check(f.Items[0].Stack==10 && shop.heldItem==null && f.Money==1000,"daily normal fish rejected without deduction");
   Put(1,fish,1,1);Buy(shop,restaurant);
   Check(f.Items[0].Stack==10 && f.Items[1].Stack==1 && Friendship()==startFriendship,"daily insufficient silver has no partial deduction or friendship");
   Clear();Put(0,"(O)145",2,4);Buy(shop,restaurant);
   Check(f.Items[0].Stack==2 && shop.heldItem==null,"daily wrong species rejected at iridium quality");
   Clear();Put(0,fish,3);Put(1,fish,1,4);Put(2,fish,2,1);Put(3,fish,2,2);
   Buy(shop,restaurant);
   Check(f.Items[0].Stack==3 && f.Items[1].Stack==1 && f.Items[2]==null && f.Items[3].Stack==2,"daily native purchase consumes exactly silver fish and preserves normal gold iridium");
   Check(f.Money==1000+payment && shop.heldItem?.QualifiedItemId=="(O)ArcticPassage_RestaurantReceipt" && f.mailReceived.Contains(Flag("Restaurant")),"daily native price reward receipt and dated mail committed");
   Check(Friendship()==startFriendship+25,"daily restaurant adds exactly 25 Mira friendship");
   shop.heldItem=null;shop.itemPriceAndStock[restaurant].Stock=1;Buy(shop,restaurant);
   Check(f.Money==1000+payment && Friendship()==startFriendship+25 && f.Items[3].Stack==2 && shop.heldItem==null,"daily stale native stock cannot pay consume or award twice");
   shop=Open();Check(!shop.forSale.Any(i=>i.QualifiedItemId==restaurant.QualifiedItemId),"daily native reopened menu hides paid restaurant order");
   Clear();Put(0,fish,3);
   Check(Helper.Reflection.GetMethod(shop,"HasTradeItem").Invoke<bool>(fish,3),"daily quality context is cleared after purchase for ordinary native checks");
   var regular=shop.forSale.Single(i=>i.QualifiedItemId=="(O)ArcticPassage_RegularReceipt");
   int before=f.Money;Buy(shop,regular);
   Check(f.Items[0]==null && f.Money>before && f.mailReceived.Contains(Flag("Regular")) && Friendship()==startFriendship+25,"daily ordinary order still accepts three normal fish without restaurant friendship");
   shop=Open();Clear();Put(0,fish,2);
   string sample="WhiteBay.ArcticPassage/ResearchSample/"+fish;f.modData.Remove(sample);
   var research=shop.forSale.Single(i=>i.QualifiedItemId=="(O)ArcticPassage_ResearchReceipt");Buy(shop,research);
   Check(f.Items[0].Stack==1 && f.modData.ContainsKey(sample) && f.mailReceived.Contains(Flag("Research")),"daily research consumes one real trade sample and records its first delivery");
   string recorded=f.modData[sample];before=f.Money;shop.heldItem=null;shop.itemPriceAndStock[research].Stock=1;Buy(shop,research);
   Check(f.Money==before && f.Items[0].Stack==1 && f.modData[sample]==recorded,"daily research duplicate cannot pay or rewrite first sample");
   // The menu still contains a paid offer. Changing the real date must not
   // allow its old actions/receipt token to be redeemed for tomorrow.
   Game1.dayOfMonth=day+1;Buy(shop,research);
   Check(f.Money==before && f.Items[0].Stack==1 && !f.mailReceived.Contains(Flag("Research")),"daily date-stale menu is rejected without tomorrow reward");
   Monitor.Log("DAILY QA COMPLETE: native quality rejection/selective deduction, normal order isolation, gold/receipt/friendship, duplicate/date/reopen and first sample passed. Synthetic fixture only; no save.",LogLevel.Info);
  } catch(Exception ex){Monitor.Log("DAILY QA FAILED: "+ex,LogLevel.Error);}
  finally {
   Game1.dayOfMonth=day;f.Money=gold;f.Items.Clear();foreach(var item in items)f.Items.Add(item);
   f.mailReceived.Clear();foreach(string flag in mail)f.mailReceived.Add(flag);
   f.modData.Clear();foreach(var pair in data)f.modData[pair.Key]=pair.Value;
   if(knewMira)f.friendshipData["ArcticPassage_Mira"].Points=friendship;else f.friendshipData.Remove("ArcticPassage_Mira");
   Game1.activeClickableMenu=null;
   Monitor.Log("DAILY QA temporary inventory/gold/date/mail/modData/friendship restored; no save requested.",LogLevel.Info);
  }
 }
}
