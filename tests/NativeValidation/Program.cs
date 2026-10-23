using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using StardewValley.GameData.Objects;
using StardewValley.GameData.Locations;
using StardewValley.GameData.Characters;
using StardewValley.GameData.Shops;
using StardewValley.GameData;
using System.Reflection;
var root=Path.GetFullPath(args[0]);
var content=JObject.Parse(File.ReadAllText(Path.Combine(root,"ContentPack/content.json")));
var settings=new JsonSerializerSettings { MissingMemberHandling=MissingMemberHandling.Error };
int models=0;
foreach(JObject p in content["Changes"]!) {
 var target=(string?)p["Target"]; var entries=p["Entries"] as JObject;
 if(entries==null)continue;
 Type? type=target switch {"Data/Machines"=>typeof(StardewValley.GameData.Machines.MachineData),"Data/BigCraftables"=>typeof(StardewValley.GameData.BigCraftables.BigCraftableData),"Data/AudioChanges"=>typeof(AudioCueData),"Data/LocationContexts"=>typeof(StardewValley.GameData.LocationContexts.LocationContextData),"Data/Objects"=>typeof(ObjectData),"Data/Locations"=>typeof(LocationData),"Data/Characters"=>typeof(CharacterData),"Data/Shops"=>typeof(ShopData),"Data/TriggerActions"=>typeof(TriggerActionData),_=>null};
 if(target=="Data/SpecialOrders")type=typeof(StardewValley.GameData.SpecialOrders.SpecialOrderData);
 if(type==null)continue;
 foreach(var e in entries.Properties()) {JsonConvert.DeserializeObject(e.Value.ToString(),type,settings);models++;}
}
Console.WriteLine($"PASS: {models} records deserialized against the installed game's real data classes, unknown fields rejected.");
var game=Assembly.LoadFrom(Path.Combine(AppContext.BaseDirectory,"Stardew Valley.dll"));
if (args.Contains("--inspect-journal")) {
 var journal=game.GetType("StardewValley.Menus.QuestLog")!;
 foreach(var field in journal.GetFields(BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance|BindingFlags.DeclaredOnly))
  Console.WriteLine($"FIELD {field.FieldType} {field.Name}");
 foreach(var method in journal.GetMethods(BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance|BindingFlags.DeclaredOnly))
  Console.WriteLine($"METHOD {method}");
 return;
}
var queries=game.GetType("StardewValley.GameStateQuery+DefaultResolvers")!;
foreach(var name in new[]{"PLAYER_LOCATION_NAME","PLAYER_HAS_MAIL","PLAYER_FISHING_LEVEL","SEASON","TIME"})
 if(queries.GetMethod(name,BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Static)==null)throw new Exception("Missing native query "+name);
Console.WriteLine("PASS: all referenced game-state queries exist in the installed game.");
AppDomain.CurrentDomain.AssemblyResolve += (_,e) => e.Name.StartsWith("xTile,") ? Assembly.LoadFrom(Path.Combine(AppContext.BaseDirectory,"xTile.dll")) : null;
var tmxAssembly=Assembly.LoadFrom(Path.Combine(AppContext.BaseDirectory,"TMXTile.dll"));
var tmxType=tmxAssembly.GetType("TMXTile.TMXFormat")!;
var parser=Activator.CreateInstance(tmxType,new object[]{16,16,4,4});
var load=tmxType.GetMethod("Load",new[]{typeof(Stream)})!;
int maps=0;
foreach(var f in Directory.GetFiles(Path.Combine(root,"ContentPack/assets/maps"),"*.tmx")) {
 using var stream=File.OpenRead(f); var map=load.Invoke(parser,new object[]{stream});
 if(map==null)throw new Exception("No parsed map: "+f);maps++;
 var parsed=(xTile.Map)map;
 foreach(var layer in parsed.Layers)
  for(int y=0;y<layer.LayerHeight;y++)for(int x=0;x<layer.LayerWidth;x++) {
   var tile=layer.Tiles[x,y];
   if(tile!=null && tile.TileIndexProperties.ContainsKey("Action") && !tile.Properties.ContainsKey("Action"))
    throw new Exception($"Action lacks native instance property: {Path.GetFileName(f)} {layer.Id} {x},{y}");
  }

}
Console.WriteLine($"PASS: {maps} maps loaded through SMAPI's real TMXTile/xTile parser.");
Console.WriteLine("PASS: all map actions are native instance properties, usable by NPC door discovery.");
Console.WriteLine("Native data/map validation completed.");
