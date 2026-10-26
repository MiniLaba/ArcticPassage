using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Menus;
using StardewValley.Tools;

namespace ArcticPassage.Runtime;

/// <summary>Personal route book and in-place field observations; stored by the native farmer save.</summary>
internal sealed class FieldGuide
{
    internal const string Prefix = "WhiteBay.ArcticPassage/FieldGuide/";
    internal static readonly (string Id, string Location, Point Tile)[] Sites =
    [
        ("rock", "ArcticPassage_Town", new(25, 24)),
        ("harbor", "ArcticPassage_Harbor", new(32, 11)),
        ("ice", "ArcticPassage_Icefjord", new(35, 31)),
        ("tundra", "ArcticPassage_Tundra", new(25, 4)),
        ("camp", "ArcticPassage_WinterCamp", new(19, 37))
    ];
    private readonly IModHelper helper;
    private readonly IMonitor monitor;
    private readonly WildlifeSightings wildlife;
    private readonly PolarPhenomena phenomena;
    private readonly SecretDiscoveries secrets;
    private string notice = "";
    private readonly Dictionary<string, Texture2D> thumbnails = [];
    internal string T(string key) => helper.Translation.Get("guide." + key);
    internal bool Has(string id) => Game1.player.modData.ContainsKey(Prefix + id);
    internal int Count => Sites.Count(s => Has(s.Id));
    internal string CurrentRegion => Game1.currentLocation.Name switch
    {
        "ArcticPassage_Guesthouse" or "ArcticPassage_Fishery" or "ArcticPassage_CommunityHouse" => "Town",
        "ArcticPassage_ResearchStation" => "WinterCamp",
        var name when name.StartsWith("ArcticPassage_") => name[14..],
        _ => "Valley"
    };
    internal Texture2D Thumbnail(string region)
    {
        string key = region + "_" + Game1.currentSeason;
        if (!thumbnails.TryGetValue(key, out Texture2D? texture))
            thumbnails[key] = texture = helper.ModContent.Load<Texture2D>("assets/guide/" + key + ".png");
        return texture;
    }

    internal FieldGuide(IModHelper helper, IMonitor monitor)
    {
        this.helper = helper; this.monitor = monitor;
        wildlife = new WildlifeSightings(helper, monitor);
        phenomena = new PolarPhenomena(helper, monitor);
        secrets = new SecretDiscoveries(helper, monitor, wildlife, phenomena);
        _ = new FieldResearch(helper, monitor);
        helper.Events.Player.Warped += (_, e) =>
        {
            if (!e.IsLocalPlayer || !e.NewLocation.Name.StartsWith("ArcticPassage_")) return;
            bool first = !Has("visited");
            Game1.player.modData[Prefix + "visited"] = "1";
            if (first) Game1.addHUDMessage(new HUDMessage(T(e.NewLocation.Name == AirTravel.Airport ? "airWelcome" : "welcome"), 2));
        };
        helper.Events.Input.ButtonPressed += OnButton;
    }

    private void OnButton(object? sender, ButtonPressedEventArgs e)
    {
        if (!Context.IsWorldReady || Game1.eventUp) return;
        if (Game1.activeClickableMenu is GuideMenu book)
        {
            bool used = true;
            switch (e.Button)
            {
                case SButton.K: book.exitThisMenu(); break;
                case SButton.D1: book.Page = 0; break;
                case SButton.D2: book.Page = 1; break;
                case SButton.D3: book.Page = 2; break;
                case SButton.D4: book.Page = 3; break;
                case SButton.D5: book.Page = 4; break;
                case SButton.D6: book.Page = 5; break;
                case SButton.D7: book.Page = 6; break;
                case SButton.Tab: case SButton.Right: book.Page = (book.Page + 1) % 7; break;
                case SButton.Left: book.Page = (book.Page + 6) % 7; break;
                case SButton.Up when book.Page == 3: book.WildlifeIndex = (book.WildlifeIndex + WildlifeSightings.All.Length - 1) % WildlifeSightings.All.Length; break;
                case SButton.Down when book.Page == 3: book.WildlifeIndex = (book.WildlifeIndex + 1) % WildlifeSightings.All.Length; break;
                case SButton.Up when book.Page == 4: book.PhenomenonIndex = (book.PhenomenonIndex + PolarPhenomena.Ids.Length - 1) % PolarPhenomena.Ids.Length; break;
                case SButton.Down when book.Page == 4: book.PhenomenonIndex = (book.PhenomenonIndex + 1) % PolarPhenomena.Ids.Length; break;
                case SButton.Up when book.Page == 5: book.ResearchIndex = (book.ResearchIndex + FieldResearch.Fish.Length - 1) % FieldResearch.Fish.Length; break;
                case SButton.Down when book.Page == 5: book.ResearchIndex = (book.ResearchIndex + 1) % FieldResearch.Fish.Length; break;
                case SButton.Up when book.Page == 6: book.SecretIndex = (book.SecretIndex + SecretDiscoveries.All.Length - 1) % SecretDiscoveries.All.Length; break;
                case SButton.Down when book.Page == 6: book.SecretIndex = (book.SecretIndex + 1) % SecretDiscoveries.All.Length; break;
                case SButton.Up: book.Site = (book.Site + Sites.Length - 1) % Sites.Length; break;
                case SButton.Down: book.Site = (book.Site + 1) % Sites.Length; break;
                case SButton.R when book.Page == 3: RecordWildlife(book.WildlifeIndex); break;
                case SButton.R when book.Page == 4: RecordPhenomenon(book.PhenomenonIndex); break;
                case SButton.R when book.Page == 6: RecordSecret(book.SecretIndex); break;
                case SButton.R when book.Page == 2: Record(); break;
                case SButton.U when book.Page == 0: notice = T(ShipmentRebooking.Change(monitor)); break;
                case SButton.J when book.Page == 0 && KeyboardJournal.HasReward: KeyboardJournal.OpenReward(); break;
                default: used = false; break;
            }
            if (used) helper.Input.Suppress(e.Button);
            return;
        }
        if (e.Button != SButton.K || Game1.activeClickableMenu != null || !Game1.player.CanMove
            || (!Game1.currentLocation.Name.StartsWith("ArcticPassage_") && !Has("visited"))) return;
        helper.Input.Suppress(e.Button);
        Game1.activeClickableMenu = new GuideMenu(this);
        monitor.Log($"GUIDE OPEN {Game1.currentLocation.Name} tile={Game1.player.Tile} notes={Count}", LogLevel.Trace);
    }

    internal int Nearby()
    {
        if (!Context.IsWorldReady) return -1;
        for (int i = 0; i < Sites.Length; i++)
            if (Game1.currentLocation.Name == Sites[i].Location
                && Vector2.Distance(Game1.player.Tile, Sites[i].Tile.ToVector2()) <= 2f) return i;
        return -1;
    }

    internal void Record()
    {
        int nearby = Nearby();
        if (nearby < 0) { notice = T("tooFar"); return; }
        string id = Sites[nearby].Id;
        if (Has(id)) { notice = T("already"); return; }
        string stamp = $"{Game1.year}|{Game1.currentSeason}|{Game1.dayOfMonth}|{Game1.timeOfDay}";
        Game1.player.modData[Prefix + id] = stamp;
        Game1.playSound("newArtifact");
        notice = T("recorded") + " " + T("site." + id + ".name");
        monitor.Log($"GUIDE RECORD {id} stamp={stamp} location={Game1.currentLocation.Name} tile={Game1.player.Tile} total={Count}", LogLevel.Info);
    }

    private void RecordWildlife(int index)
    {
        bool recorded = wildlife.Record(index, out string message);
        notice = message;
        if (recorded && index is 5 or 8)
            secrets.MirrorFieldObservation(WildlifeSightings.All[index].Id);
    }

    private void RecordPhenomenon(int index)
    {
        bool recorded = phenomena.Record(index, out string message);
        notice = message;
        if (recorded && index == 0)
            secrets.MirrorFieldObservation(PolarPhenomena.Ids[index]);
    }

    private void RecordSecret(int index)
    {
        secrets.Record(index, out string message);
        notice = message;
    }

    internal string Objective()
    {
        if (CurrentRegion == "Airstrip") return T("goal.airport");
        var mail = Game1.player.mailReceived.ToHashSet(StringComparer.Ordinal);
        string id = HarborProgress.NextStep(
            Game1.player.questLog.Where(q => !q.completed.Value).Select(q => q.id.Value), mail,
            Game1.player.questLog.Any(q => q.id.Value.StartsWith(HarborProgress.Prefix) && q.completed.Value && q.HasReward()));
        if (id.StartsWith("FirstCatch_"))
        {
            string season = id[11..];
            if (!Game1.player.Items.Any(item => item is FishingRod)) return T("goal.noRod");
            string fish = season == "fall" ? "AtlanticCod" : season == "winter" ? "PolarCod" : "Capelin";
            int count = CountItem("(O)ArcticPassage_" + fish);
            return T("goal.catch") + " " + T("fish." + fish) + "\n"
                + helper.Translation.Get("guide.goal.catchProgress", new { count = Math.Min(count, 3) });
        }
        if (id == "BoatRepair")
        {
            int count = Math.Min(2, CountItem("(O)335"));
            string text = helper.Translation.Get("guide.goal.ironProgress", new { count });
            if (count < 2)
            {
                int trades = HarborProgress.RemainingIronTrades(mail);
                string fish = ShipmentRebooking.SeasonalFish;
                text += "\n" + (trades > 0
                    ? helper.Translation.Get("guide.goal.ironTrade", new { fish = T("fish." + fish), count = Math.Min(3, CountItem("(O)ArcticPassage_" + fish)), trades })
                    : T("goal.ironSource"));
            }
            return text;
        }
        if (id == "DeepCatch")
        {
            // Show the farmer's real fishing level and inventory count. This is
            // guidance only: it never grants XP, a rod, or the quest fish.
            int halibut = Math.Min(1, CountItem("(O)ArcticPassage_Halibut"));
            bool hasSuitableRod = Game1.player.Items.Any(item => item is FishingRod rod
                && rod.QualifiedItemId != "(T)TrainingRod");
            return T("goal.DeepCatch") + "\n"
                + helper.Translation.Get("guide.goal.deepProgress", new
                {
                    level = Game1.player.FishingLevel,
                    rod = T(hasSuitableRod ? "goal.rodReady" : "goal.rodNeeded"),
                    count = halibut
                });
        }
        return T("goal." + id);
    }

    private static int CountItem(string qualifiedId)
        => Game1.player.Items.Where(item => item?.QualifiedItemId == qualifiedId).Sum(item => item.Stack);

    internal string RecordStamp(string id)
    {
        if (!Game1.player.modData.TryGetValue(Prefix + id, out string? raw)) return T("unseen");
        string[] p = raw.Split('|');
        if (p.Length != 4 || !int.TryParse(p[3], out int time)) return T("seen");
        return $"{T("seen")} · {p[0]} / {p[1]} {p[2]} · {time / 100:00}:{time % 100:00}";
    }

    private sealed class GuideMenu : IClickableMenu
    {
        private readonly FieldGuide guide;
        internal int Page;
        internal int Site;
        internal int WildlifeIndex;
        internal int PhenomenonIndex;
        internal int ResearchIndex;
        internal int SecretIndex;
        private readonly Color ink = new(40, 66, 77), muted = new(90, 114, 119), paper = new(240, 235, 215);
        private Rectangle Content => new(xPositionOnScreen + 36, yPositionOnScreen + 145, width - 72, height - 221);
        internal GuideMenu(FieldGuide guide) : base(0, 0, 1100, 710, true)
        {
            this.guide = guide;
            guide.notice = "";
            Resize();
            int nearby = guide.Nearby(); if (nearby >= 0) Site = nearby;
        }
        private void Resize()
        {
            width = Math.Min(1100, Game1.uiViewport.Width - 40); height = Math.Min(710, Game1.uiViewport.Height - 40);
            xPositionOnScreen = (Game1.uiViewport.Width - width) / 2;
            yPositionOnScreen = (Game1.uiViewport.Height - height) / 2;
            initializeUpperRightCloseButton();
        }
        public override void gameWindowSizeChanged(Rectangle oldBounds, Rectangle newBounds) => Resize();
        private void Box(SpriteBatch b, Rectangle rect, Color col) => b.Draw(Game1.staminaRect, rect, col);
        private float Text(SpriteBatch b, string text, float x, float y, float w, Color? col = null, float scale = .78f)
        {
            string wrapped = Game1.parseText(text, Game1.smallFont, Math.Max(32, (int)(w / scale)));
            b.DrawString(Game1.smallFont, wrapped, new Vector2(x, y), col ?? ink, 0, Vector2.Zero, scale, SpriteEffects.None, 1);
            return Game1.smallFont.MeasureString(wrapped).Y * scale;
        }
        private Rectangle Tab(int i) => new(xPositionOnScreen + 36 + i * ((width - 72) / 7), yPositionOnScreen + 91, (width - 72) / 7 - 6, 40);
        public override void receiveLeftClick(int x, int y, bool playSound = true)
        {
            for (int i = 0; i < 7; i++) if (Tab(i).Contains(x, y)) { Page = i; return; }
            Rectangle area = Content;
            if (Page == 0 && KeyboardJournal.HasReward && RewardButton(area).Contains(x, y))
            { KeyboardJournal.OpenReward(); return; }
            if (Page == 0 && ShipmentRebooking.CanChange() && RebookButton(area).Contains(x, y))
            { guide.notice = guide.T(ShipmentRebooking.Change(guide.monitor)); return; }
            if (Page == 2)
            {
                for (int i = 0; i < Sites.Length; i++)
                    if (new Rectangle(area.X, area.Y + i * 69, 235, 61).Contains(x, y)) { Site = i; return; }
                if (new Rectangle(area.Right - 240, area.Bottom - 48, 240, 44).Contains(x, y)) { guide.Record(); return; }
            }
            if (Page == 3)
            {
                int rowHeight = Math.Max(34, (area.Height - 34) / WildlifeSightings.All.Length);
                for (int i = 0; i < WildlifeSightings.All.Length; i++)
                    if (new Rectangle(area.X, area.Y + 30 + i * rowHeight, 318, rowHeight - 3).Contains(x, y)) { WildlifeIndex = i; return; }
                if (new Rectangle(area.Right - 240, area.Bottom - 48, 240, 44).Contains(x, y))
                { guide.RecordWildlife(WildlifeIndex); return; }
            }
            if (Page == 4)
            {
                int rowHeight = Math.Max(48, (area.Height - 34) / PolarPhenomena.Ids.Length);
                for (int i = 0; i < PolarPhenomena.Ids.Length; i++)
                    if (new Rectangle(area.X, area.Y + 30 + i * rowHeight, 318, rowHeight - 3).Contains(x, y)) { PhenomenonIndex = i; return; }
                if (new Rectangle(area.Right - 240, area.Bottom - 48, 240, 44).Contains(x, y))
                { guide.RecordPhenomenon(PhenomenonIndex); return; }
            }
            if (Page == 5)
            {
                int rowHeight = Math.Max(34, (area.Height - 34) / FieldResearch.Fish.Length);
                for (int i = 0; i < FieldResearch.Fish.Length; i++)
                    if (new Rectangle(area.X, area.Y + 30 + i * rowHeight, 318, rowHeight - 3).Contains(x, y)) { ResearchIndex = i; return; }
            }
            if (Page == 6)
            {
                int rowHeight = Math.Max(40, (area.Height - 34) / SecretDiscoveries.All.Length);
                for (int i = 0; i < SecretDiscoveries.All.Length; i++)
                    if (new Rectangle(area.X, area.Y + 30 + i * rowHeight, 318, rowHeight - 3).Contains(x, y)) { SecretIndex = i; return; }
                if (new Rectangle(area.Right - 240, area.Bottom - 48, 240, 44).Contains(x, y))
                { guide.RecordSecret(SecretIndex); return; }
            }
            base.receiveLeftClick(x, y, playSound);
        }
        public override void draw(SpriteBatch b)
        {
            Box(b, new Rectangle(0, 0, Game1.uiViewport.Width, Game1.uiViewport.Height), Color.Black * .55f);
            Box(b, new Rectangle(xPositionOnScreen - 6, yPositionOnScreen - 6, width + 12, height + 12), ink);
            Box(b, new Rectangle(xPositionOnScreen, yPositionOnScreen, width, height), paper);
            Text(b, guide.T("title"), xPositionOnScreen + 36, yPositionOnScreen + 20, width - 90, ink, 1f);
            Text(b, "FROSTHAVN", xPositionOnScreen + 38, yPositionOnScreen + 59, width - 90, muted, .48f);
            for (int i = 0; i < 7; i++)
            {
                Rectangle tab = Tab(i); Box(b, tab, Page == i ? ink : new Color(215, 220, 205));
                Text(b, (i + 1) + "  " + guide.T("tab." + i), tab.X + 12, tab.Y + 5, tab.Width - 18, Page == i ? paper : ink, .73f);
            }
            Rectangle area = Content;
            if (Page == 0) Today(b, area);
            else if (Page == 1) Map(b, area);
            else if (Page == 2) Notes(b, area);
            else if (Page == 3) Wildlife(b, area);
            else if (Page == 4) Phenomena(b, area);
            else if (Page == 5) Research(b, area);
            else Secrets(b, area);
            Text(b, guide.T("keys"), xPositionOnScreen + 36, yPositionOnScreen + height - 48, width - 72, muted, .58f);
            base.draw(b); drawMouse(b);
        }
        private void Today(SpriteBatch b, Rectangle a)
        {
            float left = a.Width * .59f;
            float y = a.Y;
            y += Text(b, guide.T("next"), a.X, y, left, muted) + 14;
            y += Text(b, guide.Objective(), a.X, y, left - 24, ink, .85f) + 27;
            y += Text(b, guide.T("daily"), a.X, y, left - 24, muted) + 12;
            Text(b, guide.T("loop"), a.X, y, left - 24);
            if (ShipmentRebooking.CanChange())
            {
                Text(b, guide.T("changeHelp") + " " + guide.T("fish." + ShipmentRebooking.SeasonalFish), a.X, a.Bottom - 173, left - 24, muted, .68f);
                Rectangle change = RebookButton(a); Box(b, change, ink);
                Text(b, guide.T("changeButton"), change.X + 12, change.Y + 9, change.Width - 24, paper, .72f);
            }
            if (guide.notice.Length > 0) Text(b, guide.notice, a.X, a.Bottom - 96, left - 24, ink, .68f);
            if (KeyboardJournal.HasReward)
            {
                Rectangle reward = RewardButton(a); Box(b, reward, ink);
                Text(b, guide.T("rewardButton"), reward.X + 12, reward.Y + 9, reward.Width - 24, paper, .72f);
            }
            float rx = a.X + left + 18, rw = a.Width - left - 18;
            Box(b, new Rectangle((int)rx - 12, a.Y, (int)rw + 12, a.Height), new Color(219, 228, 217));
            float ry = a.Y + 12;
            ry += Text(b, guide.T("season." + Game1.currentSeason), rx, ry, rw - 12, ink, .9f) + 18;
            ry += Text(b, guide.T("weather.title"), rx, ry, rw - 14, muted, .66f) + 4;
            ry += Text(b, guide.T("weather." + PolarForecast.Key(PolarWeather.Today)), rx, ry, rw - 14, ink, .68f) + 16;
            ry += Text(b, guide.T("fishing." + Game1.currentSeason), rx, ry, rw - 14, ink, .72f) + 22;
            ry += Text(b, guide.T("return"), rx, ry, rw - 14, muted, .70f) + 18;
            Text(b, guide.T("service"), rx, ry, rw - 14, muted, .68f);
        }
        private Rectangle RebookButton(Rectangle a) => new(a.X, a.Bottom - 48, Math.Min(320, (int)(a.Width * .55f)), 44);
        private Rectangle RewardButton(Rectangle a) => new(a.X, a.Bottom - (ShipmentRebooking.CanChange() ? 104 : 48), Math.Min(400, (int)(a.Width * .55f)), 44);
        private void Map(SpriteBatch b, Rectangle a)
        {
            int mw = (int)(a.Width * .58f), ox = a.X, oy = a.Y;
            Box(b, new Rectangle(ox, oy, mw, a.Height), new Color(191, 210, 214));
            // Solid paths and the airport shuttle mirror the playable graph.
            Vector2 town = new(ox + mw * .18f, oy + a.Height * .77f);
            Vector2 tundra = new(ox + mw * .18f, oy + a.Height * .49f);
            Vector2 camp = new(ox + mw * .83f, oy + a.Height * .21f);
            Vector2 airport = new(ox + mw * .50f, oy + a.Height * .77f);
            Vector2 harbor = new(ox + mw * .83f, oy + a.Height * .77f);
            Vector2 fjord = new(ox + mw * .83f, oy + a.Height * .49f);
            Vector2 mountain = new(ox + mw * .50f, oy + a.Height * .49f);
            Vector2 glacier = new(ox + mw * .50f, oy + a.Height * .21f);
            void Road(Vector2 p, Vector2 q, Color col)
            {
                Vector2 d = q - p;
                b.Draw(Game1.staminaRect, p, null, col, MathF.Atan2(d.Y, d.X), new Vector2(0, .5f), new Vector2(d.Length(), 5), SpriteEffects.None, 0);
            }
            Road(town, tundra, muted); Road(town, harbor, muted); Road(tundra, camp, muted);
            Road(tundra, mountain, muted); Road(mountain, glacier, muted); Road(mountain, camp, muted);
            Road(airport, town, new Color(122, 142, 158));
            bool open = Game1.player.mailReceived.Contains("ArcticPassage_Boat");
            Road(harbor, fjord, open ? new Color(69, 119, 140) : new Color(145, 149, 139));
            foreach (var node in new[] { ("Town", town), ("Tundra", tundra), ("Harbor", harbor), ("Icefjord", fjord), ("WinterCamp", camp), ("Airstrip", airport), ("SledTrail", mountain), ("Glacier", glacier) })
            {
                int cardW = Math.Min(115, (int)(mw * .23f)), cardH = cardW * 3 / 4;
                Rectangle image = new((int)node.Item2.X - cardW / 2, (int)node.Item2.Y - cardH / 2, cardW, cardH);
                Box(b, new Rectangle(image.X - 4, image.Y - 4, image.Width + 8, image.Height + 8), guide.CurrentRegion == node.Item1 ? new Color(180, 101, 68) : ink);
                b.Draw(guide.Thumbnail(node.Item1), image, Color.White);
                Text(b, guide.T("region." + node.Item1), image.X, image.Bottom + 7, cardW + 12, ink, .68f);
            }
            Text(b, guide.T("mapLegend"), ox + 16, a.Bottom - 50, mw - 32, muted, .55f);
            float rx = ox + mw + 26, rw = a.Width - mw - 26, y = oy;
            y += Text(b, guide.T("routeTitle"), rx, y, rw, ink, .9f) + 18;
            y += Text(b, guide.T("directions"), rx, y, rw, ink, .72f) + 20;
            string boatHint = open ? "boatOpen" : Game1.player.mailReceived.Contains("ArcticPassage_IronDelivered") ? "goal.boatWait" : "boatClosed";
            y += Text(b, guide.T(boatHint), rx, y, rw, muted, .72f) + 20;
            Text(b, guide.T("return"), rx, y, rw, muted, .70f);
        }
        private void Notes(SpriteBatch b, Rectangle a)
        {
            for (int i = 0; i < Sites.Length; i++)
            {
                Rectangle row = new(a.X, a.Y + i * 69, 235, 61);
                Box(b, row, Site == i ? ink : new Color(217, 222, 207));
                Text(b, (guide.Has(Sites[i].Id) ? "+ " : "· ") + guide.T("site." + Sites[i].Id + ".name"), row.X + 10, row.Y + 13, 215, Site == i ? paper : ink, .68f);
            }
            Text(b, guide.Count + " / " + Sites.Length + "  " + guide.T("recordCount"), a.X, a.Y + Sites.Length * 69 + 12, 235, muted, .66f);
            string id = Sites[Site].Id; float x = a.X + 267, w = a.Width - 267, y = a.Y;
            y += Text(b, guide.T("site." + id + ".name"), x, y, w, ink, .95f) + 12;
            y += Text(b, guide.RecordStamp(id), x, y, w, muted, .58f) + 22;
            y += Text(b, guide.Has(id) ? guide.T("site." + id + ".body") : guide.T("site." + id + ".where"), x, y, w, ink, .76f) + 20;
            Text(b, guide.T("observeHelp"), x, y, w, muted, .65f);
            if (guide.notice.Length > 0) Text(b, guide.notice, x, a.Bottom - 94, w, ink, .65f);
            Rectangle button = new(a.Right - 240, a.Bottom - 48, 240, 44);
            Box(b, button, guide.Nearby() >= 0 ? ink : muted);
            Text(b, guide.T("recordButton"), button.X + 12, button.Y + 9, 216, paper, .68f);
        }

        private void Wildlife(SpriteBatch b, Rectangle a)
        {
            int listWidth = 318;
            int rowHeight = Math.Max(34, (a.Height - 34) / WildlifeSightings.All.Length);
            Text(b, guide.helper.Translation.Get("guide.wildlife.progress", new { count = WildlifeSightings.Count, total = WildlifeSightings.All.Length }),
                a.X, a.Y, listWidth, muted, .65f);
            for (int i = 0; i < WildlifeSightings.All.Length; i++)
            {
                WildlifeSightings.Species species = WildlifeSightings.All[i];
                Rectangle row = new(a.X, a.Y + 30 + i * rowHeight, listWidth, rowHeight - 3);
                bool selected = WildlifeIndex == i;
                Box(b, row, selected ? ink : new Color(217, 222, 207));
                string mark = WildlifeSightings.Has(species.Id) ? "+ " : "· ";
                Text(b, mark + guide.T("wildlife." + species.Id + ".name"), row.X + 9, row.Y + 6,
                    row.Width - 18, selected ? paper : ink, .62f);
            }
            WildlifeSightings.Species selectedSpecies = WildlifeSightings.All[WildlifeIndex];
            float x = a.X + listWidth + 26, w = a.Width - listWidth - 26, y = a.Y;
            Box(b, new Rectangle((int)x - 10, a.Y, (int)w + 10, a.Height), new Color(219, 228, 217));
            y += Text(b, guide.T("wildlife." + selectedSpecies.Id + ".name"), x, y, w - 12, ink, .94f) + 13;
            y += Text(b, WildlifeSightings.Stamp(guide.helper, selectedSpecies.Id), x, y, w - 12, muted, .62f) + 18;
            y += Text(b, guide.T("wildlife." + selectedSpecies.Id + ".where"), x, y, w - 12, ink, .72f) + 14;
            y += Text(b, guide.T("wildlife." + selectedSpecies.Id + ".body"), x, y, w - 12, ink, .72f) + 16;
            Text(b, guide.T("wildlife.help"), x, y, w - 12, muted, .62f);
            if (guide.notice.Length > 0) Text(b, guide.notice, x, a.Bottom - 94, w - 12, ink, .65f);
            Rectangle button = new(a.Right - 240, a.Bottom - 48, 240, 44);
            Box(b, button, WildlifeSightings.IsNearby(WildlifeIndex) ? ink : muted);
            Text(b, guide.T("wildlife.recordButton"), button.X + 12, button.Y + 9, 216, paper, .66f);
        }

        private void Phenomena(SpriteBatch b, Rectangle a)
        {
            int listWidth = 318;
            int rowHeight = Math.Max(48, (a.Height - 34) / PolarPhenomena.Ids.Length);
            Text(b, guide.helper.Translation.Get("guide.phenomena.progress", new { count = PolarPhenomena.Count, total = PolarPhenomena.Ids.Length }),
                a.X, a.Y, listWidth, muted, .65f);
            for (int i = 0; i < PolarPhenomena.Ids.Length; i++)
            {
                string id = PolarPhenomena.Ids[i];
                Rectangle row = new(a.X, a.Y + 30 + i * rowHeight, listWidth, rowHeight - 4);
                bool selected = PhenomenonIndex == i;
                Box(b, row, selected ? ink : new Color(217, 222, 207));
                Text(b, (PolarPhenomena.Has(id) ? "+ " : "· ") + guide.T("phenomena." + id + ".name"),
                    row.X + 9, row.Y + 9, row.Width - 18, selected ? paper : ink, .65f);
            }
            string selectedId = PolarPhenomena.Ids[PhenomenonIndex];
            float x = a.X + listWidth + 26, w = a.Width - listWidth - 26, y = a.Y;
            Box(b, new Rectangle((int)x - 10, a.Y, (int)w + 10, a.Height), new Color(219, 228, 217));
            y += Text(b, guide.T("phenomena." + selectedId + ".name"), x, y, w - 12, ink, .94f) + 13;
            y += Text(b, PolarPhenomena.Stamp(guide.helper, selectedId), x, y, w - 12, muted, .62f) + 18;
            y += Text(b, guide.T("phenomena." + selectedId + ".where"), x, y, w - 12, ink, .72f) + 14;
            y += Text(b, guide.T("phenomena." + selectedId + ".body"), x, y, w - 12, ink, .72f) + 16;
            Text(b, guide.T("phenomena.help"), x, y, w - 12, muted, .62f);
            if (guide.notice.Length > 0) Text(b, guide.notice, x, a.Bottom - 94, w - 12, ink, .65f);
            Rectangle button = new(a.Right - 240, a.Bottom - 48, 240, 44);
            Box(b, button, PolarPhenomena.IsNearby(PhenomenonIndex) ? ink : muted);
            Text(b, guide.T("phenomena.recordButton"), button.X + 12, button.Y + 9, 216, paper, .66f);
        }

        private void Research(SpriteBatch b, Rectangle a)
        {
            int listWidth = 318;
            int rowHeight = Math.Max(34, (a.Height - 34) / FieldResearch.Fish.Length);
            Text(b, guide.T("research.fishHeader"), a.X, a.Y, listWidth, muted, .65f);
            for (int i = 0; i < FieldResearch.Fish.Length; i++)
            {
                string id = FieldResearch.Fish[i];
                Rectangle row = new(a.X, a.Y + 30 + i * rowHeight, listWidth, rowHeight - 3);
                bool selected = ResearchIndex == i;
                Box(b, row, selected ? ink : new Color(217, 222, 207));
                Text(b, (FieldResearch.HasFishEvidence(id) ? "+ " : "· ") + guide.T("research.fish." + id),
                    row.X + 9, row.Y + 6, row.Width - 18, selected ? paper : ink, .61f);
            }
            string selectedFish = FieldResearch.Fish[ResearchIndex];
            float x = a.X + listWidth + 26, w = a.Width - listWidth - 26, y = a.Y;
            Box(b, new Rectangle((int)x - 10, a.Y, (int)w + 10, a.Height), new Color(219, 228, 217));
            y += Text(b, guide.T("research.title"), x, y, w - 12, ink, .92f) + 14;
            y += Text(b, guide.T("research.fish." + selectedFish), x, y, w - 12, muted, .72f) + 18;
            foreach (var item in new[]
            {
                ("fish", FieldResearch.FishCount, FieldResearch.Fish.Length),
                ("animals", FieldResearch.AnimalCount, 8),
                ("phenomena", FieldResearch.PhenomenonCount, 4),
                ("landforms", FieldResearch.LandformCount, 4),
                ("samples", FieldResearch.SampleCount, 3)
            })
            {
                string row = guide.helper.Translation.Get("guide.research.progress." + item.Item1,
                    new { count = item.Item2, total = item.Item3 });
                y += Text(b, row, x, y, w - 12, ink, .72f) + 14;
            }
            y += Text(b, FieldResearch.Complete ? guide.T("research.rewardReady") : guide.T("research.rewardLocked"),
                x, y + 4, w - 12, muted, .66f) + 12;
            if (guide.notice.Length > 0) Text(b, guide.notice, x, a.Bottom - 94, w - 12, ink, .65f);
        }

        private void Secrets(SpriteBatch b, Rectangle a)
        {
            int listWidth = 318;
            int rowHeight = Math.Max(40, (a.Height - 34) / SecretDiscoveries.All.Length);
            Text(b, guide.helper.Translation.Get("guide.secret.progress", new { count = SecretDiscoveries.Count, total = SecretDiscoveries.All.Length }),
                a.X, a.Y, listWidth, muted, .65f);
            for (int i = 0; i < SecretDiscoveries.All.Length; i++)
            {
                var entry = SecretDiscoveries.All[i];
                Rectangle row = new(a.X, a.Y + 30 + i * rowHeight, listWidth, rowHeight - 3);
                bool selected = SecretIndex == i;
                Box(b, row, selected ? ink : new Color(217, 222, 207));
                string title = SecretDiscoveries.Has(entry.Id) ? guide.T("secret." + entry.Id + ".name") : guide.T("secret.unknown");
                Text(b, (SecretDiscoveries.Has(entry.Id) ? "+ " : "· ") + title, row.X + 9, row.Y + 6,
                    row.Width - 18, selected ? paper : ink, .62f);
            }

            var selectedEntry = SecretDiscoveries.All[SecretIndex];
            bool found = SecretDiscoveries.Has(selectedEntry.Id);
            float x = a.X + listWidth + 26, w = a.Width - listWidth - 26, y = a.Y;
            Box(b, new Rectangle((int)x - 10, a.Y, (int)w + 10, a.Height), new Color(219, 228, 217));
            y += Text(b, found ? guide.T("secret." + selectedEntry.Id + ".name") : guide.T("secret.clueTitle"),
                x, y, w - 12, ink, .94f) + 13;
            y += Text(b, SecretDiscoveries.Stamp(guide.helper, selectedEntry.Id), x, y, w - 12, muted, .62f) + 16;
            y += Text(b, guide.T("secret." + selectedEntry.Id + ".clue"), x, y, w - 12, ink, .72f) + 14;
            if (found)
                y += Text(b, guide.T("secret." + selectedEntry.Id + ".body"), x, y, w - 12, ink, .72f) + 14;
            else
                y += Text(b, guide.T("secret.help"), x, y, w - 12, muted, .62f) + 14;
            if (guide.notice.Length > 0) Text(b, guide.notice, x, a.Bottom - 94, w - 12, ink, .65f);
            Rectangle button = new(a.Right - 240, a.Bottom - 48, 240, 44);
            Box(b, button, SecretDiscoveries.IsNearby(SecretIndex) ? ink : muted);
            Text(b, guide.T("secret.recordButton"), button.X + 12, button.Y + 9, 216, paper, .66f);
        }
    }
}
