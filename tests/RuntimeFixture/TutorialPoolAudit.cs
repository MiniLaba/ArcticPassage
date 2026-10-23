using System;
using System.Linq;
using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewValley;

public partial class ModEntry {
 void RegisterTutorialPoolAudit(IModHelper helper) {
  helper.Events.GameLoop.SaveLoaded+=(_,_)=>{
   if(Game1.GetSaveGameName(false)!="ArcticFlowQA" || !System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"wildlife-pool.enabled")))return;
   DelayedAction.functionAfterDelay(()=>{
    try {
     string[] methods={"addButterflies","addBirdies","addBunnies","addSquirrels","addWoodpecker","addOpossums","addOwl"};
     foreach(string scene in new[]{"Town","Harbor","Icefjord","Tundra"}) {
      var location=Game1.getLocationFromName(Prefix+scene);
      int before=location.critters?.Count ?? 0;
      foreach(string method in methods)for(int attempt=0;attempt<8;attempt++)
       typeof(GameLocation).GetMethod(method)!.Invoke(location,method=="addOwl"?Array.Empty<object>():new object[]{0.8,false});
      Check((location.critters?.Count ?? 0)==before,"native valley critter entry points add none in "+scene+" (56 calls)");
     }
     Monitor.Log("CRITTER API COMPLETE 224 native spawn calls; four scoped Arctic outdoors, no persistent data changed",LogLevel.Info);
    } catch(Exception ex) {Monitor.Log("CRITTER API FAIL "+ex,LogLevel.Error);}
   },8000);
  };
  helper.Events.GameLoop.SaveLoaded+=(_,_)=>{
   if(Game1.GetSaveGameName(false)!="ArcticFlowQA" || !System.IO.File.Exists(System.IO.Path.Combine(Helper.DirectoryPath,"tutorial-pool.enabled")))return;
   DelayedAction.functionAfterDelay(()=>{
    try {
     var player=Game1.player;
     string Before()=>player.Money+"/"+player.fishCaught.Length+"/"+string.Join("|",player.Items.Select(i=>i?.QualifiedItemId+":"+i?.Stack));
     string before=Before();
     Check(player.fishCaught.Length==0,"tutorial audit starts with no recorded fish");
     foreach(string name in new[]{"Harbor","Icefjord"}) {
      var location=Game1.getLocationFromName(Prefix+name);
      int native=0;
      for(int i=0;i<256;i++) {
       var item=location.getFish(1000f,null,4,player,0,new Vector2(31,20),null);
       Check(item!=null && item.ItemId.StartsWith(Prefix),"tutorial sea pool contains only own fish: "+item?.QualifiedItemId);
       native++;
      }
      Monitor.Log("TUTORIAL POOL API "+name+" draws="+native+"; no catches awarded, no minigame claimed",LogLevel.Info);
     }
     Check(before==Before(),"tutorial selection audit leaves wallet, inventory and fishing record unchanged");
    } catch(Exception ex) {Monitor.Log("TUTORIAL POOL FAIL "+ex,LogLevel.Error);}
   },8000);
  };
 }
}
