using System;
using StardewModdingAPI;
using StardewValley;

public partial class ModEntry {
 void AuditMusic() {
  if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA")return;
  int time=Game1.timeOfDay;
  try {
   foreach(string name in new[]{"LumenhavenTheme","IcefjordTheme","PolarNightTheme"}) {
    var cue=Game1.soundBank.GetCue("ArcticPassage_"+name);
    cue.Play();
    if(!cue.IsPlaying)throw new Exception("Cue did not start: "+name);
    cue.Stop(Microsoft.Xna.Framework.Audio.AudioStopOptions.Immediate);
    Monitor.Log("AUDIT MUSIC native streaming cue started/stopped: "+name,LogLevel.Info);
   }
   foreach(string name in new[]{"Town","Harbor","Icefjord","Tundra","Guesthouse","Fishery"}) {
    var location=Game1.getLocationFromName("ArcticPassage_"+name);
    foreach(int hour in new[]{600,1200,1750,1800,2300,2600}) {
     Game1.timeOfDay=hour;
     string expected="ArcticPassage_"+(hour>=1800?"PolarNightTheme":name=="Icefjord" || name=="Tundra"?"IcefjordTheme":"LumenhavenTheme");
     string actual=location.GetLocationSpecificMusic();
     if(actual!=expected)throw new Exception(name+" at "+hour+": "+actual+" != "+expected);
    }
    Monitor.Log("AUDIT MUSIC six time boundaries passed: "+name,LogLevel.Info);
   }
   Monitor.Log("AUDIT MUSIC COMPLETE: 3 real native Vorbis cue starts, 36 location/time selections. Not a listening review.",LogLevel.Info);
  }catch(Exception ex){Monitor.Log("AUDIT MUSIC FAIL "+ex,LogLevel.Error);}
  finally {Game1.timeOfDay=time;}
 }
}
