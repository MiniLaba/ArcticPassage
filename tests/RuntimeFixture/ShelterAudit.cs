using System;
using System.Linq;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Input;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Menus;
using System.Reflection;

public partial class ModEntry {
 const string ShelterRecord="WhiteBay.ArcticPassage/SnowShelterLesson";
 void ShelterKey(IClickableMenu menu,Keys key)=>menu.GetType().GetMethod("Control",BindingFlags.Instance|BindingFlags.NonPublic)!.Invoke(menu,new object[]{key});
 void ShelterClose(){Game1.activeClickableMenu=null;Game1.dialogueUp=false;}
 void ShelterOpen(){
  ShelterClose();var l=Game1.currentLocation;var action=l.doesTileHaveProperty(20,35,"Action","Buildings");
  Check(action=="ArcticPassageSnowShelter","shelter existing exhibit has actual native map action");
  l.performAction(action,Game1.player,new xTile.Dimensions.Location(20,35));
 }
 void PrepareShelterAudit(){
  if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA" || !ShipmentFlag("shelter-preview.enabled"))return;
  Game1.SetSaveName("ArcticShelterQA");
  Monitor.Log("SHELTER QA isolated winter API fixture; synthetic location/date, no normal unlock or save claim.",LogLevel.Info);
  Game1.player.modData.Remove(ShelterRecord);Game1.eventUp=false;
  Game1.warpFarmer("ArcticPassage_WinterCamp",20,36,false);
  DelayedAction.functionAfterDelay(AuditShelter,1000);
 }
 void AuditShelter(){try{
  var f=Game1.player;int money=f.Money;
  string Inventory()=>string.Join("|",f.Items.Select(i=>i==null?"empty":i.QualifiedItemId+":"+i.Stack));
  string inventory=Inventory();
  Check(!Game1.currentLocation.isCollidingPosition(f.GetBoundingBox(),Game1.viewport,f),"shelter exhibit approach is actually walkable");
  Game1.currentSeason="summer";ShelterOpen();
  Check(Game1.activeClickableMenu?.GetType().Name!="LessonMenu" && !f.modData.ContainsKey(ShelterRecord),"shelter nonwinter opens only a notice and grants no record");
  Game1.currentSeason="winter";ShelterOpen();
  Check(Game1.activeClickableMenu?.GetType().Name=="LessonMenu","shelter native winter action opens actual game menu");
  var menu=Game1.activeClickableMenu!;
  ShelterKey(menu,Keys.Enter);Check(!f.modData.ContainsKey(ShelterRecord),"shelter wrong seam arrangement grants no completion");
  ShelterKey(menu,Keys.Right);ShelterKey(menu,Keys.Enter);ShelterKey(menu,Keys.Escape);
  Check(Game1.activeClickableMenu==null && !f.modData.ContainsKey(ShelterRecord),"shelter cancelling a partially arranged model grants no record");
  ShelterOpen();menu=Game1.activeClickableMenu!;
  for(int i=0;i<3;i++){ShelterKey(menu,Keys.Left);ShelterKey(menu,Keys.Enter);}
  Check(f.modData.ContainsKey(ShelterRecord),"shelter three real menu placements write personal completion");
  string stamp=f.modData[ShelterRecord];ShelterKey(menu,Keys.Enter);
  ShelterOpen();menu=Game1.activeClickableMenu!;
  for(int i=0;i<3;i++){ShelterKey(menu,Keys.Right);ShelterKey(menu,Keys.Enter);}
  Check(f.modData[ShelterRecord]==stamp && f.Money==money && Inventory()==inventory,"shelter replay preserves first date and cannot duplicate rewards or consume inventory");
  ShelterClose();f.modData.Remove(ShelterRecord);ShelterOpen();menu=Game1.activeClickableMenu!;
  ShelterKey(menu,Keys.Right);ShelterKey(menu,Keys.Enter);Game1.dayOfMonth++;
  ShelterKey(menu,Keys.Left);ShelterKey(menu,Keys.Enter);Game1.dayOfMonth--;
  Check(Game1.activeClickableMenu==null && !f.modData.ContainsKey(ShelterRecord),"shelter stale next-day model closes without recording");
  ShelterOpen();menu=Game1.activeClickableMenu!;Game1.currentSeason="spring";
  ShelterKey(menu,Keys.Right);ShelterKey(menu,Keys.Enter);Game1.currentSeason="winter";
  Check(Game1.activeClickableMenu==null && !f.modData.ContainsKey(ShelterRecord),"shelter season change closes a stale model without recording");
  ShelterClose();f.faceDirection(0);f.CanMove=true;f.freezePause=0;
  Monitor.Log("SHELTER QA COMPLETE: native map/menu, winter gate, wrong placement, cancellation, three courses, replay and stale day/season passed. No save; API fixture only. Ready for actual keyboard exhibit at 20,36 facing north.",LogLevel.Info);
 }catch(Exception ex){Monitor.Log("SHELTER QA FAILED: "+ex,LogLevel.Error);}}
}
