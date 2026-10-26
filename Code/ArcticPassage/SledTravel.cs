using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Menus;

namespace ArcticPassage.Runtime;

/// <summary>Personal four-step winter route, with fixed inland landings and no free driving.</summary>
internal sealed class SledTravel
{
    private const string Key = "WhiteBay.ArcticPassage/SledStage";
    private const string Tool = "(O)ArcticPassage_SledTool", Supply = "(O)ArcticPassage_SledSupply";
    private readonly IModHelper helper;
    private readonly IMonitor monitor;
    private readonly record struct Stop(string Name, Point Sign, Point Landing);
    private static readonly Stop[] Stops = [new("Tundra", new(28,38), new(28,39)), new("WinterCamp", new(13,23), new(13,24)), new("Glacier", new(30,25), new(30,26))];
    private string T(string key) => helper.Translation.Get("sled." + key);
    private static int Stage(Farmer f) => f.modData.TryGetValue(Key,out string? s) && int.TryParse(s,out int n) ? Math.Clamp(n,0,5) : 0;
    private static int Count(Farmer f,string id) => f.Items.Where(i=>i?.QualifiedItemId==id).Sum(i=>i.Stack);
    private static void Consume(Farmer f,string id,int count)
    {
        for(int i=0;i<f.Items.Count && count>0;i++)
        { var item=f.Items[i];if(item?.QualifiedItemId!=id)continue;int n=Math.Min(item.Stack,count);item.Stack-=n;count-=n;if(item.Stack==0)f.Items[i]=null; }
    }
    internal SledTravel(IModHelper helper, IMonitor monitor)
    {
        this.helper=helper;this.monitor=monitor;
        GameLocation.RegisterTileAction("ArcticPassageSled",Interact);
        helper.Events.Input.ButtonPressed += (_,e)=>
        {
            if(e.Button!=SButton.X || e.IsSuppressed() || !Context.IsWorldReady || Game1.activeClickableMenu!=null
                || Game1.eventUp || Game1.dialogueUp || !Game1.player.CanMove || Game1.player.UsingTool) return;
            Point p=Game1.player.TilePoint;Point sign=p + (Game1.player.FacingDirection switch { 0=>new Point(0,-1),1=>new Point(1,0),2=>new Point(0,1),_=>new Point(-1,0) });
            string action=Game1.currentLocation.doesTileHaveProperty(sign.X,sign.Y,"Action","Buildings");
            if(action!="ArcticPassageSled")return;
            helper.Input.Suppress(e.Button);Game1.currentLocation.performAction(action,Game1.player,new xTile.Dimensions.Location(sign.X,sign.Y));
        };
        helper.Events.Player.Warped += (_,e)=>
        {
            if(!e.IsLocalPlayer || awaitingStop<0)return;
            int target=awaitingStop;bool trial=awaitingTrial;awaitingStop=-1;awaitingTrial=false;
            if(e.NewLocation.Name!="ArcticPassage_"+Stops[target].Name)return;
            monitor.Log("SLED native arrival "+Stops[target].Name+" tile="+Game1.player.Tile,LogLevel.Info);
            if(trial && Game1.currentSeason=="winter" && Stage(Game1.player)==4)
            {Advance(Game1.player,5);Game1.addHUDMessage(new HUDMessage(T("unlocked"),HUDMessage.newQuest_type));}
        };
        helper.Events.GameLoop.ReturnedToTitle += (_,_)=>{awaitingStop=-1;awaitingTrial=false;};
        helper.Events.Display.RenderedWorld += DrawParked;
    }
    private void Say(string key)=>Game1.drawObjectDialogue(T(key));
    private void Advance(Farmer f,int stage)
    {
        if(stage>1)f.completeQuest("ArcticPassage_Sled"+new[]{"","","Tools","Supplies","Repair","Trial"}[stage]);
        f.modData[Key]=stage.ToString(System.Globalization.CultureInfo.InvariantCulture);
        if(stage<5)f.addQuest("ArcticPassage_Sled"+new[]{"","Tools","Supplies","Repair","Trial"}[stage]);
        monitor.Log($"SLED personal stage={stage}; native inventory and quest log",LogLevel.Info);
    }
    private bool Give(Farmer f,string id)
    {
        if(Count(f,id)>0)return true;
        var item=(StardewValley.Object)ItemRegistry.Create(id);item.questItem.Value=true;
        if(!f.addItemToInventoryBool(item)){Say("full");return false;}
        return true;
    }
    private bool Interact(GameLocation l,string[] args,Farmer who,Point tile)
    {
        if(who!=Game1.player)return false;
        int stop=Array.FindIndex(Stops,s=>l.Name=="ArcticPassage_"+s.Name && tile==s.Sign);
        bool toolSite=l.Name=="ArcticPassage_SledTrail" && tile==new Point(29,27);
        if(stop<0 && !toolSite)return false;
        if(Game1.currentSeason!="winter"){Say("season");return true;}
        if(Context.IsMultiplayer){Say("single");return true;}
        if(!who.mailReceived.Contains("ArcticPassage_Shed")){Say("locked");return true;}
        int stage=Stage(who);
        if(stage==0){Advance(who,1);Say("tools");return true;}
        if(toolSite){if(stage==1 && Give(who,Tool))Say("toolFound");else if(stage!=1)Say("toolsDone");return true;}
        if(stage==1)
        {
            if(stop==0 && Count(who,Tool)>0){Consume(who,Tool,1);Advance(who,2);Say("supplies");}
            else Say("tools");return true;
        }
        if(stage==2)
        {
            if(stop==1){if(Give(who,Supply))Say("supplyFound");}
            else if(stop==0 && Count(who,Supply)>0){Consume(who,Supply,1);Advance(who,3);Say("repair");}
            else Say("supplies");return true;
        }
        if(stage==3)
        {
            if(stop!=0 || Count(who,"(O)388")<20 || Count(who,"(O)771")<5){Say("repair");return true;}
            l.createQuestionDialogue(T("repairConfirm"),l.createYesNoResponses(),(f,answer)=>
            {
                if(answer!="Yes" || Stage(f)!=3 || Game1.currentSeason!="winter" || Game1.currentLocation!=l
                    || Count(f,"(O)388")<20 || Count(f,"(O)771")<5)return;
                Consume(f,"(O)388",20);Consume(f,"(O)771",5);Advance(f,4);Say("trial");
            },null);return true;
        }
        if(stage==4 && stop!=0){Say("trial");return true;}
        var options=Stops.Select((s,i)=>(s,i)).Where(x=>x.i!=stop && (stage==5 || x.i==1))
            .Select(x=>new Response(x.i.ToString(),T("stop"+x.i))).Append(new Response("cancel",T("cancel"))).ToArray();
        l.createQuestionDialogue(T(stage==4?"trial":"choose"),options,(f,answer)=>
        {
            if(int.TryParse(answer,out int target))Depart(stop,target);
        },null);return true;
    }
    private void Depart(int from,int to)
    {
        int stage=Stage(Game1.player);
        if(Game1.currentSeason!="winter" || Context.IsMultiplayer || from<0 || to<0 || to>=Stops.Length || from==to
            || Game1.currentLocation.Name!="ArcticPassage_"+Stops[from].Name
            || (stage!=5 && !(stage==4 && from==0 && to==1)))return;
        if(WildlifeSightings.PolarBearActive && (from==2 || to==2))
        {
            Say("wildlifeClosed");
            monitor.Log("SLED wildlife safety hold: glacier stop paused for today's distant polar-bear sighting; marked walking return remains open",LogLevel.Info);
            return;
        }
        if(PolarForecast.BlocksSledDeparture(PolarWeather.Today))
        {
            Game1.drawObjectDialogue(helper.Translation.Get("weather.sledClosed"));
            monitor.Log("WEATHER safe hold: sled departure suspended for whiteout; no supplies or progress changed",LogLevel.Info);
            return;
        }
        if(Game1.getLocationFromName("ArcticPassage_"+Stops[to].Name)==null){Say("unavailable");return;}
        try{Game1.activeClickableMenu=new Trip(this,from,to);monitor.Log($"SLED departure {from}->{to}; stage={stage}; no fare",LogLevel.Info);}
        catch(Exception ex){monitor.Log("Sled assets unavailable: "+ex,LogLevel.Error);Say("unavailable");}
    }
    private void Arrive(Trip trip,int to)
    {
        if(!ReferenceEquals(Game1.activeClickableMenu,trip))return;
        Game1.activeClickableMenu=null;
        if(Game1.currentSeason!="winter")return;
        Stop stop=Stops[to];
        // Only a confirmed native arrival can complete the trial, never a cancelled menu.
        awaitingTrial=Stage(Game1.player)==4 && to==1;
        awaitingStop=to;
        Game1.warpFarmer("ArcticPassage_"+stop.Name,stop.Landing.X,stop.Landing.Y,false);
    }
    private Texture2D? parkedSled;
    private bool awaitingTrial;
    private int awaitingStop=-1;
    private void DrawParked(object? sender,RenderedWorldEventArgs e)
    {
        if(!Context.IsWorldReady)return;
        if(Game1.currentSeason!="winter" || Game1.currentLocation.Name!="ArcticPassage_SledTrail")return;
        Texture2D sled=parkedSled ??= helper.ModContent.Load<Texture2D>("assets/sled/sled.png");
        e.SpriteBatch.Draw(sled,Game1.GlobalToLocal(Game1.viewport,new Vector2(26*64,26*64)),null,Color.White,0,Vector2.Zero,2,SpriteEffects.None,.9f);
    }
    private sealed class Trip:IClickableMenu
    {
        private readonly SledTravel owner;
        private readonly int from,to;
        private readonly Texture2D sky,mountains,ground,dogs,sled;
        private float elapsed;private bool done;
        internal Trip(SledTravel owner,int from,int to)
        {
            this.owner=owner;this.from=from;this.to=to;
            Texture2D Load(string path)=>owner.helper.ModContent.Load<Texture2D>(path);
            sky=Load("assets/flight/sky.png");mountains=Load("assets/flight/mountains.png");
            ground=Load("assets/sled/ground.png");dogs=Load("assets/sled/dogs.png");sled=Load("assets/sled/sled.png");
        }
        public override bool readyToClose()=>false;
        public override void receiveKeyPress(Keys key){if(key==Keys.Escape && elapsed>.5f)Finish();}
        public override void receiveGamePadButton(Buttons b){if(b==Buttons.B && elapsed>.5f)Finish();}
        public override void update(GameTime time){base.update(time);elapsed+=Math.Min(.1f,(float)time.ElapsedGameTime.TotalSeconds);if(elapsed>=9)Finish();}
        private void Finish(){if(done)return;done=true;owner.Arrive(this,to);}
        public override void draw(SpriteBatch b)
        {
            int w=Game1.uiViewport.Width,h=Game1.uiViewport.Height;
            b.Draw(Game1.staminaRect,new Rectangle(0,0,w,h),new Color(15,32,47));
            float scale=Math.Min(w/640f,(h-130)/360f),ox=(w-640*scale)/2,oy=(h-360*scale)/2;
            Rectangle R(float x,float y,float rw,float rh)=>new((int)(ox+x*scale),(int)(oy+y*scale),(int)(rw*scale),(int)(rh*scale));
            b.Draw(sky,R(0,0,640,360),Color.White);
            float speed=Math.Clamp(elapsed/1.5f,0,1)*Math.Clamp((9-elapsed)/1.5f,0,1);
            float travel=elapsed<1.5f?elapsed*elapsed*16:elapsed>7.5f?324+48*(elapsed-7.5f)-16*(elapsed-7.5f)*(elapsed-7.5f):36+(elapsed-1.5f)*48;
            int shift=(int)(travel*.2f)%640;
            b.Draw(mountains,R(-shift,35,1280,250),Color.White);
            int gx=(int)travel%640;b.Draw(ground,R(-gx,220,640,140),Color.White);b.Draw(ground,R(640-gx,220,640,140),Color.White);
            // Short-lived runner marks scroll away behind the team.
            for(int n=0;n<14;n++)
            {
                float x=195-n*14-(travel%14);float alpha=(1-n/14f)*speed;
                foreach(int y in new[]{300,310})b.Draw(Game1.staminaRect,R(x,y,12,1),new Color(94,126,151)*alpha);
            }
            float bounce=MathF.Sin(elapsed*14)*speed;
            b.Draw(sled,R(194,272+bounce,80,40),Color.White);
            // Draw the actual farmer's clothing and face in native seated frame 117,
            // using the stateless overload: no sprite, facing, position or movement changes.
            var frame=new FarmerSprite.AnimationFrame(117,100);
            Game1.player.FarmerRenderer.draw(b,frame,117,new Rectangle(48,608,16,32),new Vector2(ox+215*scale,oy+(263+bounce)*scale),Vector2.Zero,.91f,1,Color.White,0,scale/4,Game1.player);
            for(int i=0;i<4;i++)
            {
                float dx=303+i*30,dy=268+(i%2)*27;int f=speed>.05f?(int)(elapsed*9+i)%4:0;
                // Fan traces terminate at the sled bow rather than connecting dogs nose-to-tail.
                Vector2 a=new(ox+271*scale,oy+292*scale),z=new(ox+(dx+9)*scale,oy+(dy+14)*scale);
                Vector2 v=z-a;b.Draw(Game1.staminaRect,a,null,new Color(119,99,73),MathF.Atan2(v.Y,v.X),Vector2.Zero,new Vector2(v.Length(),Math.Max(1,scale)),SpriteEffects.None,.8f);
                b.Draw(dogs,R(dx,dy+MathF.Sin(elapsed*15+i)*speed,40,28),new Rectangle(f*40,0,40,28),Color.White);
            }
            float fade=Math.Clamp((elapsed-8)/1,0,1);b.Draw(Game1.staminaRect,new Rectangle(0,0,w,h),Color.Black*fade);
            b.Draw(Game1.staminaRect,new Rectangle(0,h-108,w,108),new Color(15,32,47));
            AirTravel.DrawLabel(b,owner.T("stop"+from)+" → "+owner.T("stop"+to),32,h-100,w-64);
            AirTravel.DrawLabel(b,owner.T("skip"),32,h-58,w-64);
        }
    }
}
