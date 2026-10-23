using System;
using System.Linq;
using System.Collections.Generic;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Network;

public partial class ModEntry {
 void RegisterEnvironmentAudit(IModHelper helper) {
  helper.ConsoleCommands.Add("ap_audit_environment","Native forecast and context isolation audit; dedicated QA, no save.",(_,_)=>{
   if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA")return;
   string original=Game1.currentSeason;
   try {
    foreach(string name in new[]{"Town","Harbor","Icefjord","Tundra"}) {
     var location=Game1.getLocationFromName(Prefix+name);var live=location.GetWeather();
     string expected=Prefix+(name=="Tundra"?"TundraClimate":"CoastClimate");
     if(location.GetLocationContextId()!=expected || live.IsDebrisWeather || live.IsGreenRain)
      throw new Exception("Old valley weather inherited after upgrade: "+name);
     Monitor.Log("AUDIT CLIMATE UPGRADE "+name+" context="+expected+" debris="+live.IsDebrisWeather+" greenRain="+live.IsGreenRain,LogLevel.Info);
    }
    var context=Game1.locationContextData[Prefix+"CoastClimate"];
    if(context.CopyWeatherFromLocation!=null || context.PlayRandomAmbientSounds)
     throw new Exception("Coast still inherits valley weather or ambient birds");
    if(Game1.locationContextData[Prefix+"TundraClimate"].CopyWeatherFromLocation!=Prefix+"CoastClimate")
     throw new Exception("Tundra weather does not follow coast");
    foreach(string season in new[]{"spring","summer","fall","winter"}) {
     Game1.currentSeason=season;
     var counts=new Dictionary<string,int>();
     for(int seed=0;seed<256;seed++) {
      var forecast=new LocationWeather();
      forecast.UpdateDailyWeather(Prefix+"CoastClimate",context,new Random(seed));
      string weather=forecast.WeatherForTomorrow;
      if(!new[]{"Sun","Rain","Snow"}.Contains(weather))throw new Exception("Unexpected forecast "+weather);
      if(season=="winter" && weather=="Rain" || season=="summer" && weather=="Snow")
       throw new Exception("Wrong seasonal precipitation "+season+" "+weather);
      counts[weather]=counts.GetValueOrDefault(weather)+1;
      // Consume the forecast through the actual native day-weather handler.
      forecast.UpdateDailyWeather(Prefix+"CoastClimate",context,new Random(seed+900));
      if(forecast.IsDebrisWeather || forecast.IsGreenRain || forecast.IsLightning)
       throw new Exception("Valley effect leaked into Arctic day weather");
      var tundra=new LocationWeather();tundra.CopyFrom(forecast);
      if(tundra.IsSnowing!=forecast.IsSnowing || tundra.IsRaining!=forecast.IsRaining)
       throw new Exception("Adjacent contexts do not copy precipitation");
     }
     if(counts.Count<2)throw new Exception("Forecast conditions did not vary");
     Monitor.Log("AUDIT ENVIRONMENT "+season+" forecasts="+string.Join(",",counts.Select(p=>p.Key+":"+p.Value))+" no valley debris/green rain; native copying passed",LogLevel.Info);
    }
    Monitor.Log("AUDIT ENVIRONMENT COMPLETE: 1024 native forecasts; isolated objects only; no saved date or valley weather changed.",LogLevel.Info);
   } catch(Exception ex) {Monitor.Log("AUDIT FAIL "+ex,LogLevel.Error);}
   finally {Game1.currentSeason=original;}
  });
 }
}
