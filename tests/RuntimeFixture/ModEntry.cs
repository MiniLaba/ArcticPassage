using System;
using System.Linq;
using System.Collections.Generic;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using Microsoft.Xna.Framework;
using xTile;
public partial class ModEntry: Mod {
 int ticks; bool started; bool loaded; int stage;
 int previewScene;
 readonly (string Name,int X,int Y)[] previewScenes={
  ("Town",36,23),("Harbor",24,23),("Icefjord",35,34),
  ("Tundra",29,43),("Guesthouse",12,14),("Fishery",12,14)
 };
 public override void Entry(IModHelper helper) {
  RegisterIntegrationAudit(helper);
  RegisterCounterObservations(helper);
  RegisterNpcDayAudit(helper);
  RegisterTutorialPoolAudit(helper);
  RegisterEnvironmentAudit(helper);
  RegisterWinterOvernightAudit(helper);
  RegisterRecoveryAudit(helper);
  helper.Events.GameLoop.GameLaunched += (_,_)=>LocalizedContentManager.CurrentLanguageCode=LocalizedContentManager.LanguageCode.zh;
  helper.Events.GameLoop.UpdateTicked += OnTick;
  helper.Events.Player.Warped += (_,e)=>{
   if(e.Player.Name=="ArcticQA" && e.NewLocation.Name.StartsWith("ArcticPassage_"))
    DelayedAction.functionAfterDelay(LogAudio,2500);
  };
  helper.Events.Input.ButtonPressed += (_,e)=>{
   if(e.Button==SButton.F3 && Context.IsWorldReady && System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"night-preview.enabled"))) {
    Game1.timeOfDay=Game1.timeOfDay==2200?1200:2200;
    Monitor.Log("QA LIGHT PREVIEW time="+Game1.timeOfDay+" (temporary, not saved)",LogLevel.Info);return;
   }
   if(e.Button==SButton.F11 && Context.IsWorldReady && Game1.GetSaveGameName(false)=="ArcticRecoveryQA" && Game1.activeClickableMenu==null) {
    LocateRecoveryChest();return;
   }
   if(e.Button==SButton.F12 && Context.IsWorldReady && Game1.GetSaveGameName(false)=="ArcticRecoveryQA" && Game1.activeClickableMenu==null) {
    BeginRecoveryTransition();return;
   }
   if(e.Button==SButton.F5 && Context.IsWorldReady && Game1.player.Name=="ArcticQA") {
    Monitor.Log("QA READ STATE location="+Game1.currentLocation.Name+" tile="+Game1.player.Tile+" facing="+Game1.player.FacingDirection+" canMove="+Game1.player.CanMove+" mouse="+e.Cursor.ScreenPixels,LogLevel.Info);return;
   }
   if(e.Button==SButton.MouseLeft && Context.IsWorldReady && Game1.player.Name=="ArcticQA")
    Monitor.Log("QA READ MOUSE left event screen="+e.Cursor.ScreenPixels+" tile="+e.Cursor.Tile+" menu="+Game1.activeClickableMenu?.GetType().Name,LogLevel.Info);
   if(e.Button==SButton.F12 && Context.IsWorldReady && Game1.player.Name=="ArcticQA" && Game1.activeClickableMenu==null && Game1.currentSeason=="winter") {
    BeginWinterOvernight();return;
   }
   if(e.Button==SButton.F11 && Context.IsWorldReady && Game1.player.Name=="ArcticQA" && winterPotApproach.HasValue && Game1.activeClickableMenu==null) {
    var p=winterPotApproach.Value;
    Game1.warpFarmer(Prefix+"Harbor",(int)p.X,(int)p.Y,false);
    Game1.player.CurrentToolIndex=11;
    DelayedAction.functionAfterDelay(()=>Game1.player.faceDirection(winterPotFacing),300);
    Monitor.Log("Preview F11: ready winter crab pot approach only at "+p,LogLevel.Info);return;
   }
   if(e.Button==SButton.F10 && Context.IsWorldReady && Game1.player.Name=="ArcticQA" && Game1.activeClickableMenu==null) {
    Game1.warpFarmer("ArcticPassage_Guesthouse",20,8,false);
    Game1.player.CurrentToolIndex=11;
    DelayedAction.functionAfterDelay(()=>Game1.player.faceDirection(0),300);
    Monitor.Log("Preview F10: kitchen approach at 20,8; location only.",LogLevel.Info);return;
   }
   if((e.Button==SButton.F8 || e.Button==SButton.F9) && Context.IsWorldReady && Game1.player.Name=="ArcticQA" && Game1.activeClickableMenu==null) {
    bool harvest=e.Button==SButton.F8;
    Game1.warpFarmer("ArcticPassage_Fishery",harvest?15:8,harvest?13:7,false);
    while(Game1.player.Items.Count<12)Game1.player.Items.Add(null);
    Game1.player.CurrentToolIndex=11;
    DelayedAction.functionAfterDelay(()=>Game1.player.faceDirection(0),300);
    Monitor.Log(harvest?"Preview F8: ready rack approach at 15,13.":"Preview F9: market approach at 8,7.",LogLevel.Info);return;
   }
   if(e.Button==SButton.F7 && Context.IsWorldReady && Game1.player.Name=="ArcticQA" && Game1.activeClickableMenu==null) {
    Game1.warpFarmer("ArcticPassage_Guesthouse",10,13,false);
    DelayedAction.functionAfterDelay(()=>Game1.player.faceDirection(0),300);
    Monitor.Log("Preview F7: Mira dialogue approach at 10,13.",LogLevel.Info);return;
   }
   if(e.Button!=SButton.F6 || !Context.IsWorldReady || Game1.player.Name!="ArcticQA" || Game1.activeClickableMenu!=null)return;
   previewScene=(previewScene+1)%previewScenes.Length;
   var scene=previewScenes[previewScene];
   Game1.warpFarmer("ArcticPassage_"+scene.Name,scene.X,scene.Y,false);
   Monitor.Log("Preview F6: "+scene.Name+" at "+scene.X+","+scene.Y,LogLevel.Info);
  };
  helper.Events.GameLoop.SaveLoaded += (_,_)=>{
   if(Game1.player.Name!="ArcticQA") return;
   loaded=true; ticks=0; Game1.options.pauseWhenOutOfFocus=System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"interactive-fishing.enabled"));
   if(ShipmentFlag("daily-preview.enabled") || ShipmentFlag("weekly-preview.enabled") || ShipmentFlag("repair-preview.enabled") || ShipmentFlag("ice-preview.enabled") || ShipmentFlag("sled-preview.enabled") || ShipmentFlag("shelter-preview.enabled"))return;
   if(Game1.GetSaveGameName(false)!="ArcticFlowQA")Game1.player.eventsSeen.Add("ArcticPassage_Welcome");
   Monitor.Log("Existing dedicated preview save loaded through native SaveGame.Load; native save target="+Game1.GetSaveGameName(false),LogLevel.Info);
   if(ShipmentFlag("shipment-preview.enabled"))return;
   if(System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"camp-preview.enabled")))return;
   if(Game1.GetSaveGameName(false)=="ArcticNPCQA" || Game1.GetSaveGameName(false)=="ArcticFlowQA")return;
   if(Game1.GetSaveGameName(false)=="ArcticRecoveryQA") {
    bool reload=System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"recovery-reload.enabled"));
    DelayedAction.functionAfterDelay(reload?AuditRecoveryReload:PrepareRecoveryAudit,8000);return;
   }
   if(System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"winter-reload.enabled"))) {
    DelayedAction.functionAfterDelay(AuditWinterReload,8000);return;
   }
   DelayedAction.functionAfterDelay(AuditMusic,10000);
   DelayedAction.functionAfterDelay(AuditSeafood,18000);
  };
  helper.Events.Player.InventoryChanged+=(_,e)=>{
   if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA")return;
   foreach(var item in e.Added.Where(i=>i.ItemId.StartsWith("ArcticPassage_Dried") || i.ItemId==Prefix+"SnowCrab"))
    Monitor.Log("QA INVENTORY added "+item.QualifiedItemId+" stack="+item.Stack,LogLevel.Info);
  };
  helper.ConsoleCommands.Add("ap_native_interact","Run the actual map tile action (dedicated preview only).",(_,args)=>{
   if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA" || args.Length<2)return;
   int x=int.Parse(args[0]),y=int.Parse(args[1]);
   string action=Game1.currentLocation.doesTileHaveProperty(x,y,"Action","Buildings");
   Monitor.Log("Native action "+x+","+y+": "+action,LogLevel.Info);
   if(action!=null)Game1.currentLocation.performAction(action,Game1.player,new xTile.Dimensions.Location(x,y));
   DelayedAction.functionAfterDelay(()=>Monitor.Log("After native action: "+Game1.currentLocation.Name+" quests="+string.Join(",",Game1.player.questLog.Select(q=>q.id.Value+":"+q.completed.Value)),LogLevel.Info),1000);
  });
  helper.ConsoleCommands.Add("ap_native_fish","Sample the real game fish selection API; no minigame claim.",(_,args)=>{
   if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA")return;
   var sample=new Dictionary<string,int>();var here=Game1.currentLocation;
   Game1.player.fishingLevel.Value=10;
   if(!Game1.player.fishCaught.ContainsKey("129"))Game1.player.fishCaught["129"]=new int[]{1,12};
   for(int i=0;i<250;i++) {
    var fish=here.getFish(0f,null,5,Game1.player,0,new Vector2(43,20),null);
    string id=fish?.QualifiedItemId??"none";sample[id]=sample.GetValueOrDefault(id)+1;
   }
   Monitor.Log("Native fish selection @ "+here.Name+" / "+Game1.currentSeason+": "+string.Join(", ",sample.Select(p=>p.Key+"="+p.Value)),LogLevel.Info);
  });
  helper.ConsoleCommands.Add("ap_preview_state","Inspect actual player state.",(_,_)=>Monitor.Log("location="+Game1.currentLocation.Name+" tile="+Game1.player.Tile+" canMove="+Game1.player.CanMove+" ready="+Context.IsWorldReady,LogLevel.Info));
  helper.ConsoleCommands.Add("ap_qa_maps","Inspect real map assets.",(_,_)=>Inspect());
  helper.ConsoleCommands.Add("ap_preview_season","Temporary QA season; immediately follow with patch update. Does not save.",(_,a)=>{
   if(a.Length==1)PreviewSeason(a[0]);
  });
 }
 void PreviewSeason(string season) {
  if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA" || !new[]{"spring","summer","fall","winter"}.Contains(season))return;
  Game1.currentSeason=season;
  Monitor.Log("QA: run 'patch update' now to refresh CP season tokens. No F10 shortcut is exposed.",LogLevel.Info);
  // The next console command is CP's public 'patch update'. No SMAPI internals
  // are accessed. A bare date mutation doesn't raise DayStarted automatically.
  DelayedAction.functionAfterDelay(()=>{
   Helper.GameContent.InvalidateCache(a=>a.Name.StartsWith("Maps/ArcticPassage_"));
   foreach(var scene in previewScenes)Game1.getLocationFromName("ArcticPassage_"+scene.Name)?.reloadMap();
   Game1.currentLocation.resetForPlayerEntry();
   Monitor.Log("QA SEASON PREVIEW "+season+" (temporary; not saved)",LogLevel.Info);
   Inspect();
  },5000);
 }
 void OnTick(object? sender,UpdateTickedEventArgs e) {
  ticks++;
  if(Game1.options!=null)Game1.options.pauseWhenOutOfFocus=System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"interactive-fishing.enabled"));
  if(!started && !Context.IsWorldReady && ticks>180) {
   started=true;
   string folder=System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"flow-preview.enabled"))?"ArcticFlowQA_451755789":(System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"npc-day.enabled")) || System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"night-preview.enabled")))?"ArcticNPCQA_451755789":System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"recovery-preview.enabled"))?"ArcticRecoveryQA_451755789":System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"winter-preview.enabled"))?"ArcticWinterQA_451755789":"ArcticQA_451755789";
   if(System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"camp-winter.enabled")))folder="ArcticWinterQA_451755789";
   if(ShipmentFlag("ice-preview.enabled") || ShipmentFlag("sled-preview.enabled") || ShipmentFlag("shelter-preview.enabled"))folder="ArcticWinterQA_451755789";
   if(ShipmentFlag("shipment-preview.enabled"))folder=ShipmentFlag("shipment-reload.enabled")?"ArcticShipmentQA_451755789":"ArcticWinterQA_451755789";
   if(!System.IO.File.Exists(System.IO.Path.Combine(Constants.SavesPath,folder,folder))){Monitor.Log("Preview save missing; use the normal load/new game menu.",LogLevel.Warn);return;}
   try { SaveGame.Load(folder); Game1.activeClickableMenu=null; Monitor.Log("Loading dedicated preview save: "+folder,LogLevel.Info); }
   catch(Exception ex){Monitor.Log(ex.ToString(),LogLevel.Error);}
  }
  if(loaded && Context.IsWorldReady && Game1.player.Name=="ArcticQA" && Game1.GetSaveGameName(false)!="ArcticFlowQA" && Game1.GetSaveGameName(false)!="ArcticShipmentQA" && (Game1.GetSaveGameName(false)!="ArcticNPCQA" || npcDayFinished || System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"night-preview.enabled"))))Game1.gameTimeInterval=0;
  if(loaded && Context.IsWorldReady && ticks>180 && stage==0) {
   stage=1;
   if(ShipmentFlag("daily-preview.enabled")) {PrepareDailyOrderAudit();return;}
   if(ShipmentFlag("shelter-preview.enabled")) {PrepareShelterAudit();return;}
   if(ShipmentFlag("sled-preview.enabled")) {PrepareSledAudit();return;}
   if(ShipmentFlag("ice-preview.enabled")) {PrepareIceAudit();return;}
   if(ShipmentFlag("repair-preview.enabled")) {PrepareRepairAudit();return;}
   if(ShipmentFlag("weekly-preview.enabled")) {PrepareWeeklyAudit();return;}
   if(ShipmentFlag("shipment-preview.enabled")) {PrepareShipmentPreview();return;}
   if(System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"camp-preview.enabled"))) {
    Game1.options!.desiredBaseZoomLevel=0.75f;
    Game1.warpFarmer("ArcticPassage_Tundra",50,23,false);
    Game1.timeOfDay=1200;Game1.player.CurrentToolIndex=11;
    Monitor.Log("CAMP QA arrival only: Tundra 50,23; native date="+Game1.currentSeason+" "+Game1.dayOfMonth+"; no grants, no automatic interactions or save",LogLevel.Info);return;
   }
   if(Game1.GetSaveGameName(false)=="ArcticFlowQA") {
    Game1.options!.desiredBaseZoomLevel=0.75f;
    Monitor.Log("FLOW ready at native saved arrival and date; real clock, no fixture grants/audits",LogLevel.Info);return;
   }
   Game1.activeClickableMenu=null;Game1.eventUp=false;
   Game1.warpFarmer("ArcticPassage_Town",31,23,false);if(System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"night-preview.enabled")))Game1.timeOfDay=2200;else if(Game1.GetSaveGameName(false)!="ArcticNPCQA")Game1.timeOfDay=1200;
   Game1.player.CanMove=true;Game1.options!.desiredBaseZoomLevel=0.75f;Inspect();
   if(!Game1.player.Items.Any(i=>i is StardewValley.Tools.FishingRod))
    Game1.player.addItemToInventoryBool(new StardewValley.Tools.FishingRod(0));
   Monitor.Log("Preview ready in Town at 36,23.",LogLevel.Info);
  }
 }
 void LogAudio() {
  if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA")return;
  var l=Game1.currentLocation;
  Monitor.Log("AUDIO "+l.Name+" context="+l.GetLocationContextId()+" randomAmbience="+l.GetLocationContext().PlayRandomAmbientSounds+" track="+Game1.getMusicTrackName(StardewValley.GameData.MusicContext.Default),LogLevel.Info);
 }
 void Inspect() {
  try {
   foreach(var n in new[]{"Town","Harbor","Icefjord","Tundra","Guesthouse","Fishery"}) {
    var m=Helper.GameContent.Load<Map>("Maps/ArcticPassage_"+n);
    var l=Game1.getLocationFromName("ArcticPassage_"+n);
    if(!m.TileSheets.Any(t=>t.ImageSource.Contains(n+"_"+Game1.currentSeason+"_scene")))
     throw new Exception("Season texture mismatch: "+n+" expected "+Game1.currentSeason);
    Monitor.Log(n+": layers="+m.Layers.Count+", sheets="+m.TileSheets.Count+", location="+(l!=null)+", NPCs="+(l?.characters.Count??0)+", doors="+(l?.doors.Count()??0)+", scene="+string.Join(",",m.TileSheets.Where(t=>t.Id.Contains("Scene")).Select(t=>t.ImageSource)),LogLevel.Info);
    if(l!=null && (n=="Harbor" || n=="Icefjord" || n=="Tundra")) {
     // Winter shore ice closes the former east casts. These open-water probes
     // are still within casting distance of the authored west/south approaches.
     var p=n=="Harbor"?new Point(33,20):n=="Icefjord"?new Point(39,37):new Point(41,20);
     Monitor.Log(n+" native isTileFishable "+p+"="+l.isTileFishable(p.X,p.Y),LogLevel.Info);
     var a=n=="Harbor"?new Point(24,23):n=="Icefjord"?new Point(35,34):new Point(29,43);
     bool waterBlocked=l.isCollidingPosition(new Rectangle(p.X*64+16,p.Y*64+16,32,32),Game1.viewport,Game1.player);
     bool pathBlocked=l.isCollidingPosition(new Rectangle(a.X*64+16,a.Y*64+16,32,32),Game1.viewport,Game1.player);
     Monitor.Log(n+" native collision water="+waterBlocked+" arrival="+pathBlocked,LogLevel.Info);
     if(!l.isTileFishable(p.X,p.Y) || !waterBlocked || pathBlocked)
      throw new Exception("Fishing / shoreline geometry failed for "+n);
     if(Game1.currentSeason=="winter" && n!="Tundra") {
      var ice=n=="Harbor"?new Point(43,20):new Point(43,34);
      if(l.isTileFishable(ice.X,ice.Y))throw new Exception("Winter ice was marked fishable: "+n);
      Monitor.Log(n+" winter shore ice correctly rejects fishing at "+ice,LogLevel.Info);
     }
    }
   }
   foreach(var n in new[]{"Ada","Mira","Roan"}) {var c=Game1.getCharacterFromName("ArcticPassage_"+n);Monitor.Log(n+": "+c?.currentLocation?.Name+" schedule="+(c?.Schedule?.Count??0),LogLevel.Info);}
  } catch(Exception ex){Monitor.Log(ex.ToString(),LogLevel.Error);}
 }
}
