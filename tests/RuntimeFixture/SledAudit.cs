using System;
using System.Linq;
using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Menus;
public partial class ModEntry {
 const string SledKey="WhiteBay.ArcticPassage/SledStage";
 int SledStep=>Game1.player.modData.TryGetValue(SledKey,out var s)?int.Parse(s):0;
 void SledClose(){Game1.activeClickableMenu=null;Game1.dialogueUp=false;Game1.eventUp=false;}
 void SledAt(string name,int x,int y,Action next){SledClose();Game1.warpFarmer("ArcticPassage_"+name,x,y,false);DelayedAction.functionAfterDelay(()=>{try{next();}catch(Exception ex){Monitor.Log("SLED QA FAILED: "+ex,LogLevel.Error);}},1000);}
 void SledAction(int x,int y){SledClose();var l=Game1.currentLocation;string a=l.doesTileHaveProperty(x,y,"Action","Buildings");Check(a=="ArcticPassageSled","sled actual map action "+l.Name+" "+x+","+y);l.performAction(a,Game1.player,new xTile.Dimensions.Location(x,y));}
 void SledAnswer(string answer){Game1.currentLocation.answerDialogue(new Response(answer,answer));}
 void PrepareSledAudit(){
  if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA" || !ShipmentFlag("sled-preview.enabled"))return;
  Game1.SetSaveName("ArcticSledQA");
  Monitor.Log("SLED QA isolated synthetic inputs and native map/quest/inventory/answer/warp checks, NOT normal play; no save requested.",LogLevel.Info);
  Game1.player.modData.Remove(SledKey);for(int i=0;i<Game1.player.Items.Count;i++)Game1.player.Items[i]=null;
  foreach(var q in Game1.player.questLog.Where(q=>q.id.Value.StartsWith("ArcticPassage_Sled")).ToArray())Game1.player.questLog.Remove(q);
  Game1.player.mailReceived.Remove("ArcticPassage_Shed");
  SledAt("Tundra",28,39,()=>{
   SledAction(28,38);Check(SledStep==0,"sled shed prerequisite blocks winter start");
   Game1.player.mailReceived.Add("ArcticPassage_Shed");Game1.currentSeason="summer";
   SledAction(28,38);Check(SledStep==0,"sled nonwinter cannot start or spend anything");Game1.currentSeason="winter";
   SledAction(28,38);Check(SledStep==1 && Game1.player.hasQuest("ArcticPassage_SledTools"),"sled starts a real native tools quest");
   SledAt("SledTrail",28,27,()=>{
    for(int i=0;i<Game1.player.Items.Count;i++)Game1.player.Items[i]=ItemRegistry.Create("(O)390",999);
    SledAction(29,27);Check(CountItem("(O)ArcticPassage_SledTool")==0 && SledStep==1,"sled full bag cannot lose or advance tool pickup");
    Game1.player.Items[0]=null;SledAction(29,27);SledAction(29,27);
    Check(CountItem("(O)ArcticPassage_SledTool")==1,"sled native quest tool pickup cannot duplicate in inventory");
    Check(((StardewValley.Object)Game1.player.Items.First(i=>i?.ItemId=="ArcticPassage_SledTool")).questItem.Value,"sled item is native quest equipment");
    for(int i=0;i<Game1.player.Items.Count;i++)if(Game1.player.Items[i]?.ItemId=="390")Game1.player.Items[i]=null;
    SledAt("Tundra",28,39,()=>{
     SledAction(28,38);Check(SledStep==2 && CountItem("(O)ArcticPassage_SledTool")==0 && Game1.player.hasQuest("ArcticPassage_SledSupplies"),"sled return consumes tool and advances native quest");
     SledAt("WinterCamp",13,24,()=>{
      SledAction(13,23);SledAction(13,23);Check(CountItem("(O)ArcticPassage_SledSupply")==1,"sled camp supplies pickup is unique");
      SledAt("Tundra",28,39,()=>{
       SledAction(28,38);Check(SledStep==3 && CountItem("(O)ArcticPassage_SledSupply")==0,"sled supplies delivery consumes one crate");
       SledAction(28,38);Check(SledStep==3,"sled repair cannot bypass missing materials");
       Game1.player.Items[0]=ItemRegistry.Create("(O)388",21);Game1.player.Items[1]=ItemRegistry.Create("(O)771",6);int money=Game1.player.Money;
       SledAction(28,38);SledAnswer("No");Check(SledStep==3 && CountItem("(O)388")==21 && CountItem("(O)771")==6,"sled cancelling native repair question keeps materials");
       SledAction(28,38);SledAnswer("Yes");Check(SledStep==4 && CountItem("(O)388")==1 && CountItem("(O)771")==1 && Game1.player.Money==money,"sled confirmed repair consumes exactly twenty wood and five fiber, no fare");
       SledAction(28,38);SledAnswer("1");Check(Game1.activeClickableMenu?.GetType().Name=="Trip" && SledStep==4,"sled trial starts scene without premature unlock");
       DelayedAction.functionAfterDelay(AuditSledArrived,11500);
      });
     });
    });
   });
  });
 }
 void AuditSledArrived(){try{
  Check(Game1.currentLocation.Name=="ArcticPassage_WinterCamp" && Game1.player.TilePoint==new Point(13,24) && SledStep==5,"sled full trial scene arrives natively and then unlocks");
  Check(!Game1.currentLocation.isCollidingPosition(Game1.player.GetBoundingBox(),Game1.viewport,Game1.player),"sled camp landing is walkable with full native farmer bounds");
  SledAction(13,23);SledAnswer("2");DelayedAction.functionAfterDelay(()=>{
   try{
    Check(Game1.currentLocation.Name=="ArcticPassage_Glacier" && Game1.player.TilePoint==new Point(30,26),"sled unlocked camp to glacier native arrival");
    Check(!Game1.currentLocation.isCollidingPosition(Game1.player.GetBoundingBox(),Game1.viewport,Game1.player),"sled glacier landing is walkable");
    SledAction(30,25);SledAnswer("0");DelayedAction.functionAfterDelay(()=>{
     try{
      Check(Game1.currentLocation.Name=="ArcticPassage_Tundra" && Game1.player.TilePoint==new Point(28,39),"sled glacier return to tundra natively");
      Check(!Game1.currentLocation.isCollidingPosition(Game1.player.GetBoundingBox(),Game1.viewport,Game1.player),"sled tundra landing is walkable");
      Game1.currentSeason="spring";SledAction(28,38);Check(SledStep==5 && Game1.activeClickableMenu?.GetType().Name!="Trip","sled season transition retains unlock without starting a trip");Game1.currentSeason="winter";
      SledClose();Game1.player.faceDirection(0);Game1.player.CanMove=true;Game1.player.freezePause=0;
      Monitor.Log("SLED QA COMPLETE: four-step native quests/inventory/cancel/exact cost, full nine-second scenes, three real safe landings/return and nonwinter closure passed. No save, synthetic inputs, NOT ordinary progression. Ready for actual keyboard trip.",LogLevel.Info);
     }catch(Exception ex){Monitor.Log("SLED QA FAILED: "+ex,LogLevel.Error);}
    },11500);
   }catch(Exception ex){Monitor.Log("SLED QA FAILED: "+ex,LogLevel.Error);}
  },11500);
 }catch(Exception ex){Monitor.Log("SLED QA FAILED: "+ex,LogLevel.Error);}}
}
