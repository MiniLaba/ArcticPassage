using System;
using System.Linq;
using Mono.Cecil;
var game=AssemblyDefinition.ReadAssembly(args[0]);
if(args[1]=="--find-string") {
 foreach(var t in game.MainModule.GetTypes())foreach(var m in t.Methods.Where(m=>m.HasBody && m.Body.Instructions.Any(i=>i.Operand is string s && s.Contains(args[2])))) {
  Console.WriteLine(m.FullName);foreach(var i in m.Body.Instructions)Console.WriteLine(i);
 }
 return;
}
foreach(var t in game.MainModule.Types.Where(t=>t.FullName==args[1])) {
 if(args.Contains("--signatures")) { foreach(var m in t.Methods)Console.WriteLine(m.FullName); continue; }
 foreach(var m in t.Methods.Where(m=>m.HasBody && (args.Skip(2).Contains(m.Name) || m.Body.Instructions.Any(i=>i.Operand is string s && args.Skip(2).Any(a=>s.Contains(a)))))) {
  Console.WriteLine(m.FullName);foreach(var i in m.Body.Instructions)Console.WriteLine(i);
 }
 foreach(var t2 in t.NestedTypes)Console.WriteLine("Nested type: "+t2.FullName);
 foreach(var f in t.Fields)Console.WriteLine("FIELD: "+f.FullName);
}
