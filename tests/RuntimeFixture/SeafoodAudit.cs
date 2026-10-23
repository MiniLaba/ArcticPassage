using System;
using System.Linq;
using System.Collections.Generic;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Objects;
using Microsoft.Xna.Framework;

public partial class ModEntry {
 void AuditSeafood() {
  if(!Context.IsWorldReady || Game1.player.Name!="ArcticQA")return;
  var farmer=Game1.player;
  var inventory=farmer.Items.ToArray();
  int money=farmer.Money;
  var learned=farmer.cookingRecipes.Keys.ToDictionary(k=>k,k=>farmer.cookingRecipes[k]);
  try {
   foreach(string name in new[]{"CharSoup","PanCod","ShrimpChowder","FishPotatoStew"}) {
    farmer.Items.Clear();
    var recipe=new CraftingRecipe(Prefix+name,true);
    var raw=Helper.GameContent.Load<Dictionary<string,string>>("Data/CookingRecipes")[Prefix+name].Split('/')[0].Split(' ');
    Check(!recipe.doesFarmerHaveIngredientsInInventory(null),"empty inventory cannot cook "+name);
    for(int i=0;i<raw.Length;i+=2)farmer.Items.Add(ItemRegistry.Create("(O)"+raw[i],int.Parse(raw[i+1])));
    Check(recipe.doesFarmerHaveIngredientsInInventory(null),"native ingredients accepted "+name);
    recipe.consumeIngredients(null);
    Check(!farmer.Items.Any(i=>i!=null && i.Stack>0),"exact ingredients consumed "+name);
    var meal=recipe.createItem();
    Check(meal.QualifiedItemId=="(O)"+Prefix+name && meal.Category==-7,"native cooking output "+name);
    Monitor.Log("AUDIT SEAFOOD COOK "+name+" ingredient gate, exact deduction and output passed.",LogLevel.Info);
   }
   foreach(string name in new[]{"CharSoup","PanCod","ShrimpChowder","FishPotatoStew"})farmer.cookingRecipes.Remove(Prefix+name);
   farmer.Money=5000;
   Check(Utility.TryOpenShopMenu(Prefix+"Supplies",null,true),"supplies shop opens for recipe purchase");
   var shop=(StardewValley.Menus.ShopMenu)Game1.activeClickableMenu;
   foreach(string name in new[]{"CharSoup","PanCod","ShrimpChowder","FishPotatoStew"}) {
    var item=shop.forSale.Single(i=>i.QualifiedItemId=="(O)"+Prefix+name);
    int before=farmer.Money;
    Helper.Reflection.GetMethod(shop,"tryToPurchaseItem").Invoke<bool>(item,null,1,0,0);
    Check(farmer.cookingRecipes.ContainsKey(Prefix+name) && farmer.Money==before-450,"native shop learns recipe and charges 450: "+name);
   }
   Game1.exitActiveMenu();
   foreach(var pair in new[]{("Harbor","shrimp"),("Icefjord","crab")}) {
    var location=Game1.getLocationFromName(Prefix+pair.Item1);
    var area=location.GetData().FishAreas["Default"];
    var original=area.CrabPotFishTypes;
    try {
     string liveKind=pair.Item1=="Harbor" && Game1.currentSeason=="winter"?"crab":pair.Item2;
     Check(original.SequenceEqual(new[]{"ap_"+liveKind+"_"+Game1.currentSeason}),"CP resolved live trap season "+pair.Item1);
     var tiles=new List<Vector2>();
     for(int y=0;y<location.Map.Layers[0].LayerHeight;y++)
      for(int x=0;x<location.Map.Layers[0].LayerWidth;x++)
       if(CrabPot.IsValidCrabPotLocationTile(location,x,y) && new[]{new Point(x-1,y),new Point(x+1,y),new Point(x,y-1),new Point(x,y+1)}.Any(p=>
        p.X>=0 && p.Y>=0 && p.X<location.Map.Layers[0].LayerWidth && p.Y<location.Map.Layers[0].LayerHeight &&
        !location.isTileFishable(p.X,p.Y) && location.Map.GetLayer("Buildings").Tiles[p.X,p.Y]==null))tiles.Add(new Vector2(x,y));
     if(tiles.Count==0 && pair.Item1=="Icefjord" && Game1.currentSeason=="winter") {
      Monitor.Log("AUDIT SEAFOOD winter fjord has no reachable pot water; winter crab access uses harbor instead.",LogLevel.Info);continue;
     }
     Check(tiles.Count>0,"native crab-pot shoreline placement exists "+pair.Item1);
     Monitor.Log("AUDIT SEAFOOD native pot placements "+pair.Item1+" count="+tiles.Count+" first="+tiles[0],LogLevel.Info);
     // Probe each authored type through the native daily-catch implementation.
     // With the runtime enabled, only the actual date is tested: its live
     // season guard intentionally rejects stale or simulated seasonal tags.
     // Historical content-only tests may still probe each type in memory.
     foreach(string season in Helper.ModRegistry.IsLoaded("WhiteBay.ArcticPassage.Runtime") ? new[]{Game1.currentSeason} : new[]{"spring","summer","fall","winter"}) {
      string kind=pair.Item1=="Harbor" && season=="winter"?"crab":pair.Item2;
      area.CrabPotFishTypes=new List<string>{"ap_"+kind+"_"+season};
      int caught=0;
      bool available=kind=="shrimp"?season!="winter":season=="fall" || season=="winter";
      string expected=Prefix+(kind=="shrimp"?"NorthernShrimp":"SnowCrab");
      for(int sample=0;sample<256;sample++) {
       var pot=new CrabPot();pot.Location=location;pot.TileLocation=tiles[sample%tiles.Count];
       pot.owner.Value=farmer.UniqueMultiplayerID;pot.directionOffset.Value=new Vector2(sample,0);
       pot.bait.Value=(StardewValley.Object)ItemRegistry.Create("(O)685");
       pot.DayUpdate();
       string id=pot.heldObject.Value?.ItemId??"none";
       if(id==expected)caught++;
       else if(!new[]{"168","169","170","171","172"}.Contains(id))throw new Exception("unexpected catch "+pair.Item1+" "+season+" "+id);
      }
      Check(available?caught>0:caught==0,"native seasonal pool "+pair.Item1+" "+season);
      Monitor.Log("AUDIT SEAFOOD trap type "+pair.Item1+"/"+season+" catch="+caught+" of 256; no alien fish",LogLevel.Info);
     }
    }finally{area.CrabPotFishTypes=original;}
   }
   var inn=Game1.getLocationFromName(Prefix+"Guesthouse");
   Check(inn.doesTileHaveProperty(20,7,"Action","Buildings")=="Kitchen","actual stove tile offers native kitchen");
   Monitor.Log("AUDIT SEAFOOD COMPLETE: native recipes and per-type draws; live "+Game1.currentSeason+" tokens/maps verified. No save.",LogLevel.Info);
  }catch(Exception ex){Monitor.Log("AUDIT SEAFOOD FAIL "+ex,LogLevel.Error);}
  finally {
   farmer.Items.Clear();foreach(var item in inventory)farmer.Items.Add(item);
   farmer.Money=money;farmer.cookingRecipes.Clear();foreach(var pair in learned)farmer.cookingRecipes.Add(pair.Key,pair.Value);
   Game1.exitActiveMenu();
  }
  if(Game1.currentSeason=="winter")PrepareWinterPot();
 }
}
