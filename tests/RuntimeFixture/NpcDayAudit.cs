using System;
using System.Linq;
using System.Collections.Generic;
using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewValley;

public partial class ModEntry {
 bool npcDayStarted, npcDayFinished;
 readonly HashSet<string> npcArrivals=new();
 readonly HashSet<string> npcDeparturesChecked=new();
 readonly Dictionary<string,List<(int Time,string Location,Point Tile)>> npcTargets=new();
 void RegisterNpcDayAudit(IModHelper helper) {
  helper.Events.GameLoop.SaveLoaded+=(_,_)=>{
   if(Game1.GetSaveGameName(false)!="ArcticNPCQA" || !System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"npc-day.enabled")))return;
   npcDayStarted=true;npcDayFinished=false;
   Monitor.Log("NPC DAY BEGIN real native clock; isolated clone; no NPC warps, schedule calls or time acceleration",LogLevel.Info);
   foreach(string name in new[]{"Ada","Mira","Roan"}) {
    var npc=Game1.getCharacterFromName(Prefix+name);
    var targets=npc.Schedule.OrderBy(p=>p.Key).Select(p=>(p.Key,p.Value.targetLocationName,p.Value.targetTile)).ToList();
    npcTargets[name]=targets;
    Monitor.Log("NPC DAY PLAN "+name+" schedule="+npc.dayScheduleName.Value+" "+string.Join("|",targets.Select(t=>$"{t.Key}:{t.targetLocationName}@{t.targetTile}")),LogLevel.Info);
   }
  };
  helper.Events.GameLoop.UpdateTicked+=(_,e)=>{
   if(!npcDayStarted || npcDayFinished || !e.IsMultipleOf(30) || !Context.IsWorldReady || Game1.GetSaveGameName(false)!="ArcticNPCQA")return;
   foreach(var pair in npcTargets) {
    var npc=Game1.getCharacterFromName(Prefix+pair.Key);
    var target=pair.Value.LastOrDefault(t=>t.Time<=Game1.timeOfDay);
    if(target.Location==null)continue;
    string id=pair.Key+":"+target.Time;
    if(npc.currentLocation.Name==target.Location && npc.Tile==new Vector2(target.Tile.X,target.Tile.Y) && npcArrivals.Add(id))
     Monitor.Log($"NPC DAY ARRIVED {id} at {Game1.timeOfDay} {npc.currentLocation.Name} {npc.Tile}",LogLevel.Info);
   }
  };
  helper.Events.GameLoop.TimeChanged+=(_,e)=>{
   if(!npcDayStarted || npcDayFinished || Game1.GetSaveGameName(false)!="ArcticNPCQA")return;
   foreach(var pair in npcTargets) {
    var npc=Game1.getCharacterFromName(Prefix+pair.Key);
    if(e.NewTime%100==0)Monitor.Log($"NPC DAY POSITION {e.NewTime} {pair.Key} {npc.currentLocation.Name} {npc.Tile} path={npc.controller?.pathToEndPoint?.Count ?? 0}",LogLevel.Info);
    for(int i=0;i<pair.Value.Count-1;i++) {
     string id=pair.Key+":"+pair.Value[i].Time;
     if(e.NewTime>=pair.Value[i+1].Time && npcDeparturesChecked.Add(id) && !npcArrivals.Contains(id))
      Monitor.Log("NPC DAY MISSED destination before next departure: "+id,LogLevel.Error);
    }
   }
   if(e.NewTime<2200)return;
   npcDayFinished=true;
   foreach(var pair in npcTargets)foreach(var target in pair.Value) {
    string id=pair.Key+":"+target.Time;
    Monitor.Log("NPC DAY FINAL "+id+" reached="+npcArrivals.Contains(id),npcArrivals.Contains(id)?LogLevel.Info:LogLevel.Error);
   }
   Monitor.Log("NPC DAY COMPLETE at native 2200; freeze observer clock now to prevent unattended pass-out/save",LogLevel.Info);
  };
 }
}
