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
                case SButton.Tab: case SButton.Right: book.Page = (book.Page + 1) % 3; break;
                case SButton.Left: book.Page = (book.Page + 2) % 3; break;
                case SButton.Up: book.Site = (book.Site + Sites.Length - 1) % Sites.Length; break;
                case SButton.Down: book.Site = (book.Site + 1) % Sites.Length; break;
                case SButton.R: Record(); break;
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

    internal string Objective()
    {
        if (CurrentRegion == "Airstrip") return T("goal.airport");
        var q = Game1.player.questLog.FirstOrDefault(q => q.id.Value.StartsWith("ArcticPassage_") && !q.completed.Value);
        if (q != null)
        {
            string id = q.id.Value[14..];
            if (id.StartsWith("FirstCatch_"))
            {
                string season = id[11..];
                if (!Game1.player.Items.Any(item => item is FishingRod)) return T("goal.noRod");
                string fish = season == "fall" ? "AtlanticCod" : season == "winter" ? "PolarCod" : "Capelin";
                int count = Game1.player.Items.Where(item => item?.QualifiedItemId == "(O)ArcticPassage_" + fish).Sum(item => item.Stack);
                return T("goal.catch") + " " + T("fish." + fish) + "\n"
                    + helper.Translation.Get("guide.goal.catchProgress", new { count = Math.Min(count, 3) });
            }
            if (new[] { "Arrival", "Shed", "BoatRepair", "FjordVisit", "DeepCatch" }.Contains(id)) return T("goal." + id);
        }
        if (Game1.player.questLog.Any(q => q.id.Value.StartsWith("ArcticPassage_") && q.completed.Value && q.HasReward())) return T("goal.claim");
        if (Game1.player.mailReceived.Contains("ArcticPassage_Boat")) return T("goal.free");
        return T("goal.start");
    }

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
        private Rectangle Tab(int i) => new(xPositionOnScreen + 36 + i * ((width - 72) / 3), yPositionOnScreen + 91, (width - 72) / 3 - 8, 40);
        public override void receiveLeftClick(int x, int y, bool playSound = true)
        {
            for (int i = 0; i < 3; i++) if (Tab(i).Contains(x, y)) { Page = i; return; }
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
            base.receiveLeftClick(x, y, playSound);
        }
        public override void draw(SpriteBatch b)
        {
            Box(b, new Rectangle(0, 0, Game1.uiViewport.Width, Game1.uiViewport.Height), Color.Black * .55f);
            Box(b, new Rectangle(xPositionOnScreen - 6, yPositionOnScreen - 6, width + 12, height + 12), ink);
            Box(b, new Rectangle(xPositionOnScreen, yPositionOnScreen, width, height), paper);
            Text(b, guide.T("title"), xPositionOnScreen + 36, yPositionOnScreen + 20, width - 90, ink, 1f);
            Text(b, "FROSTHAVN  /  ARCTIC PASSAGE", xPositionOnScreen + 38, yPositionOnScreen + 59, width - 90, muted, .48f);
            for (int i = 0; i < 3; i++)
            {
                Rectangle tab = Tab(i); Box(b, tab, Page == i ? ink : new Color(215, 220, 205));
                Text(b, (i + 1) + "  " + guide.T("tab." + i), tab.X + 12, tab.Y + 5, tab.Width - 18, Page == i ? paper : ink, .73f);
            }
            Rectangle area = Content;
            if (Page == 0) Today(b, area);
            else if (Page == 1) Map(b, area);
            else Notes(b, area);
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
            y += Text(b, guide.T(open ? "boatOpen" : "boatClosed"), rx, y, rw, muted, .72f) + 20;
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
    }
}
