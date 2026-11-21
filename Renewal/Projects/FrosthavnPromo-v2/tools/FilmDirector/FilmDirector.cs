using System;
using System.IO;
using System.Linq;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Tools;
using Microsoft.Xna.Framework;
public class FilmDirector:Mod {
 int ticks;bool started;string last="";int faceAfterWarp=2;
 public class Command {public string Id="",Kind="",Location="Harbor",Item="",Npc="";public int X=24,Y=24,Time=1200,Facing=2,Count=1,Day=7;public float Zoom=.75f;}
 public override void Entry(IModHelper h) {
 h.Events.GameLoop.UpdateTicked+=(_,_)=>{
  if(Game1.options!=null)Game1.options.pauseWhenOutOfFocus=false;
  if(!started && ++ticks>180 && !Context.IsWorldReady){started=true;SaveGame.Load("FilmHarbor_827103002");Game1.activeClickableMenu=null;Monitor.Log("FILM loading disposable FilmHarbor only",LogLevel.Info);}
  if(!Context.IsWorldReady||Game1.player.Name!="FilmHarbor")return;
  Game1.gameTimeInterval=0;
  if(Game1.ticks%15==0){try{var c=h.Data.ReadJsonFile<Command>("command.json");if(c!=null&&c.Id!=last){last=c.Id;Apply(c);}}catch(Exception e){Monitor.Log(e.ToString(),LogLevel.Warn);}}
  if(Game1.ticks%30==0){
   var rod=Game1.player.CurrentTool as FishingRod;
   h.Data.WriteJsonFile("state.json",new{utc=DateTime.UtcNow,player=Game1.player.Name,location=Game1.currentLocation.Name,x=Game1.player.Tile.X,y=Game1.player.Tile.Y,time=Game1.timeOfDay,season=Game1.currentSeason,day=Game1.dayOfMonth,menu=Game1.activeClickableMenu?.GetType().FullName,facing=Game1.player.FacingDirection,freeze=Game1.freezeControls,dialogue=Game1.dialogueUp,eventUp=Game1.eventUp,frontAction=Game1.currentLocation.doesTileHaveProperty(Game1.player.TilePoint.X,Game1.player.TilePoint.Y-1,"Action","Buildings"),canMove=Game1.player.CanMove,usingTool=Game1.player.UsingTool,nibbling=rod?.isNibbling,caught=Game1.player.fishCaught.Count(),items=Game1.player.Items.Where(i=>i!=null).Select(i=>new{id=i.QualifiedItemId,n=i.Stack}).ToArray(),lastCommand=last});
  }
 };
 h.Events.Player.Warped+=(_,e)=>{if(e.IsLocalPlayer)DelayedAction.functionAfterDelay(()=>{Game1.freezeControls=false;Game1.dialogueUp=false;Game1.player.CanMove=true;Game1.player.faceDirection(faceAfterWarp);},700);};
 h.Events.GameLoop.SaveLoaded+=(_,_)=>{Monitor.Log("FILM WORLD LOADED "+Game1.player.Name,LogLevel.Info);DelayedAction.functionAfterDelay(()=>Scene("Harbor",24,24,1200,.75f),1500);};
 h.ConsoleCommands.Add("film_scene","Stage real location in disposable film save",(_,a)=>{if(Context.IsWorldReady&&Game1.player.Name=="FilmHarbor"&&a.Length>=3)Scene(a[0],int.Parse(a[1]),int.Parse(a[2]),a.Length>3?int.Parse(a[3]):1200,.75f);});
 }
 void Apply(Command c){
  if(c.Kind=="scene"){faceAfterWarp=c.Facing;Scene(c.Location,c.X,c.Y,c.Time,c.Zoom);DelayedAction.functionAfterDelay(()=>Game1.player.faceDirection(c.Facing),400);}
  else if(c.Kind=="prep"){Game1.player.mailReceived.Add("ArcticPassage_Shed");Game1.player.modData["WhiteBay.ArcticPassage/SledStage"]="5";Game1.dayOfMonth=c.Day;Game1.player.Stamina=Game1.player.MaxStamina;Game1.player.health=Game1.player.maxHealth;Monitor.Log("FILM staged unlocked sled and filming date only; no saves",LogLevel.Info);}
  else if(c.Kind=="item"){var item=ItemRegistry.Create(c.Item,c.Count);Game1.player.Items[0]=item;Game1.player.CurrentToolIndex=0;Monitor.Log("FILM preseed prop "+c.Item+" x"+c.Count,LogLevel.Info);}
  else if(c.Kind=="face")Game1.player.faceDirection(c.Facing);
  else if(c.Kind=="npc"){var npc=Game1.getCharacterFromName(c.Npc);if(npc!=null)Game1.warpCharacter(npc,Game1.currentLocation.Name,new Vector2(c.X,c.Y));}
  else if(c.Kind=="hud")Game1.displayHUD=true;
  Monitor.Log("FILM command "+c.Id+" "+c.Kind,LogLevel.Info);
 }
 void Scene(string name,int x,int y,int time,float zoom){
  Game1.activeClickableMenu=null;Game1.eventUp=false;Game1.player.CanMove=true;Game1.player.Halt();Game1.player.UsingTool=false;
  Game1.timeOfDay=time;Game1.displayHUD=false;Game1.options.desiredBaseZoomLevel=zoom;
  Game1.warpFarmer(name=="BusStop"?name:"ArcticPassage_"+name,x,y,false);
  Monitor.Log("FILM staged "+name+" at "+x+","+y+"; actual engine footage, not progression validation",LogLevel.Info);
 }
}
