using Mono.Cecil;
var a=AssemblyDefinition.ReadAssembly(args[0]);
var t=a.MainModule.Types.First(x=>x.FullName=="StardewValley.Tools.FishingRod");
foreach(var m in t.Methods.Where(m=>m.HasBody && (m.Name.Contains("BobberTile") || m.Name=="doneFishing" || m.Name=="DoFunction"))) { Console.WriteLine("METHOD "+m.FullName); foreach(var i in m.Body.Instructions) Console.WriteLine(i); }
