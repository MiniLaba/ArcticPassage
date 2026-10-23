using System;
using System.Linq;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Tools;

public partial class ModEntry {
 bool InteractiveQa=>Game1.GetSaveGameName(false) is "ArcticQA" or "ArcticFlowQA" or "ArcticShipmentQA";
 string lastRodObservation="";
 void RegisterCounterObservations(IModHelper helper) {
  helper.Events.Input.ButtonPressed+=(_,e)=>{
   if(!Context.IsWorldReady || !InteractiveQa)return;
   if((e.Button==SButton.C || e.Button==SButton.X) && Game1.player.CurrentTool is FishingRod rod)
    Monitor.Log("QA READ TOOL KEY "+e.Button+" active="+Game1.game1.IsActive+" pauseUnfocused="+Game1.options.pauseWhenOutOfFocus+" nibble="+rod.isNibbling+" remainingMs="+(rod.timeUntilFishingNibbleDone-rod.fishingNibbleAccumulator),LogLevel.Info);
   if(e.Button==SButton.F4 && Game1.activeClickableMenu==null) {
    Game1.warpFarmer(Prefix+"Harbor",16,22,false);Game1.player.CurrentToolIndex=11;
    DelayedAction.functionAfterDelay(()=>Game1.player.faceDirection(0),300);
    Monitor.Log("QA F4 supplies approach only; no purchase or inventory injection",LogLevel.Info);
   }
   if(e.Button==SButton.F5)Monitor.Log("QA READ CRITTERS "+Game1.currentLocation.Name+" "+string.Join(",",Game1.currentLocation.critters?.Select(c=>c.GetType().Name) ?? Enumerable.Empty<string>()),LogLevel.Info);
   if(e.Button==SButton.F5)Monitor.Log("QA READ GUIDE "+string.Join("|",Game1.player.modData.Pairs.Where(p=>p.Key.StartsWith("WhiteBay.ArcticPassage/FieldGuide/")).Select(p=>p.Key+"="+p.Value)),LogLevel.Info);
   if(e.Button==SButton.F5)Monitor.Log("QA READ LEDGER gold="+Game1.player.Money+" heldTool="+Game1.player.CurrentTool?.QualifiedItemId+" inventory="+string.Join("|",Game1.player.Items.Select((i,n)=>(i,n)).Where(p=>p.i!=null).Select(p=>p.n+":"+p.i.QualifiedItemId+"x"+p.i.Stack+"q"+p.i.Quality))+" recipes="+string.Join(",",Game1.player.cookingRecipes.Keys.Where(k=>k.StartsWith(Prefix))),LogLevel.Info);
  };
  helper.Events.Display.MenuChanged+=(_,e)=>{
   if(Context.IsWorldReady && InteractiveQa)Monitor.Log("QA READ MENU "+e.OldMenu?.GetType().Name+" -> "+e.NewMenu?.GetType().Name,LogLevel.Info);
  };
  helper.Events.Player.InventoryChanged+=(_,e)=>{
   if(!Context.IsWorldReady || !InteractiveQa)return;
   foreach(var i in e.Added)Monitor.Log("QA READ ADD "+i.QualifiedItemId+" x"+i.Stack+" q"+i.Quality,LogLevel.Info);
   foreach(var i in e.Removed)Monitor.Log("QA READ REMOVE "+i.QualifiedItemId+" x"+i.Stack+" q"+i.Quality,LogLevel.Info);
  };
  helper.Events.GameLoop.UpdateTicked+=(_,e)=>{
   if(!e.IsMultipleOf(6) || !Context.IsWorldReady || !InteractiveQa || Game1.player.CurrentTool is not FishingRod rod)return;
   string state=$"fishing={rod.isFishing} nibble={rod.isNibbling} hit={rod.hit} reeling={rod.isReeling} caught={rod.fishCaught} pull={rod.pullingOutOfWater}";
   if(state==lastRodObservation)return;lastRodObservation=state;
   Monitor.Log("QA READ ROD "+state,LogLevel.Info);
  };
 }
}
