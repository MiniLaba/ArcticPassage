using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Audio;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Menus;

namespace ArcticPassage.Runtime;

/// <summary>Personal airline reservation, check-in and a skippable, non-rewarding arrival.</summary>
internal sealed class AirTravel
{
    internal const string Airport = "ArcticPassage_Airstrip";
    internal const string Invitation = "ArcticPassage_AirlineInvitation";
    private const string Seen = "WhiteBay.ArcticPassage/AirArrival";
    private readonly IModHelper helper;
    private readonly IMonitor monitor;
    private bool awaitingLanding;
    internal string T(string key) => helper.Translation.Get("flight." + key);
    internal Texture2D Texture(string name) => helper.ModContent.Load<Texture2D>("assets/flight/" + name + ".png");
    internal bool Outbound => Game1.currentLocation?.Name == "BusStop";
    internal bool Eligible => Game1.player.mailReceived.Contains(Invitation)
        || Game1.player.mailReceived.Contains("ArcticPassage_Invitation")
        || Game1.player.modData.ContainsKey(FieldGuide.Prefix + "visited");

    internal AirTravel(IModHelper helper, IMonitor monitor)
    {
        this.helper = helper; this.monitor = monitor;
        GameLocation.RegisterTileAction("ArcticPassageFlight", (location, args, who, tile) =>
        {
            if (who != Game1.player || location.Name != Airport) return false;
            Open(); return true;
        });
        helper.Events.Input.ButtonPressed += OnButton;
        helper.Events.Display.RenderedHud += DrawHint;
        helper.Events.Display.MenuChanged += (_, e) =>
        {
            if (e.OldMenu is FlightScene scene && !ReferenceEquals(e.OldMenu, e.NewMenu)) scene.StopAudio();
        };
        helper.Events.Player.Warped += (_, e) =>
        {
            if (!e.IsLocalPlayer || !awaitingLanding) return;
            awaitingLanding = false;
            if (e.NewLocation.Name != Airport) return;
            Game1.player.modData[Seen] = "1";
            // Same native quest ID: existing progression and pending rewards survive.
            if (!Game1.player.mailReceived.Contains("ArcticPassage_Shed")
                && !Game1.player.questLog.Any(q => q.id.Value.StartsWith("ArcticPassage_")))
                Game1.player.addQuest("ArcticPassage_Arrival");
            monitor.Log("AIR ARRIVAL native warp complete; inventory, money and clock retained", LogLevel.Info);
        };
        helper.Events.GameLoop.ReturnedToTitle += (_, _) => awaitingLanding = false;
    }

    private void OnButton(object? sender, ButtonPressedEventArgs e)
    {
        if (!Context.IsWorldReady || e.IsSuppressed() || Game1.eventUp) return;
        if (Game1.activeClickableMenu is BoardingMenu card)
        {
            if (e.Button == SButton.Enter) { helper.Input.Suppress(e.Button); card.Confirm(); }
            return;
        }
        if (e.Button == SButton.G && Game1.activeClickableMenu == null && Game1.player.CanMove
            && Game1.currentLocation is Farm farm)
        {
            Point mailbox = farm.GetMainMailboxPosition();
            if (!Utility.tileWithinRadiusOfPlayer(mailbox.X, mailbox.Y, 1, Game1.player)) return;
            helper.Input.Suppress(e.Button);
            Game1.tryToCheckAt(mailbox.ToVector2(), Game1.player);
            monitor.Log("AIR ACCESS native nearby farm-mailbox interaction", LogLevel.Trace);
            return;
        }
        if (e.Button != SButton.B || Game1.activeClickableMenu != null || !Game1.player.CanMove) return;
        if (Game1.currentLocation.Name != "BusStop" && Game1.currentLocation.Name != Airport) return;
        helper.Input.Suppress(e.Button); Open();
    }

    private void Open()
    {
        if (Context.IsMultiplayer) { Game1.showRedMessage(T("singlePlayer")); return; }
        if (Game1.activeClickableMenu != null || Game1.eventUp || !Game1.player.CanMove) return;
        if (Outbound && !Eligible) { Game1.drawObjectDialogue(T("needInvitation")); return; }
        Game1.activeClickableMenu = new BoardingMenu(this, Outbound);
        monitor.Log($"AIR CHECK-IN {(Outbound ? "outbound" : "return")} native UI; no ticket consumed", LogLevel.Trace);
    }

    internal void Depart(bool outbound)
    {
        if (outbound && !Eligible) return;
        if (outbound)
        {
            if (Game1.getLocationFromName(Airport) == null) { Game1.showRedMessage(T("unavailable")); return; }
            // Preload before changing menus/music: a missing asset leaves check-in intact.
            try
            {
                var scene = new FlightScene(this, helper, monitor);
                Game1.activeClickableMenu = scene;
                Game1.changeMusicTrack("none");
                monitor.Log("AIR FLIGHT start; 24-second arrival / Esc skips to the same landing", LogLevel.Info);
            }
            catch (Exception ex) { monitor.Log("Flight assets unavailable: " + ex, LogLevel.Error); Game1.showRedMessage(T("unavailable")); }
        }
        else
        {
            Game1.activeClickableMenu = null;
            Game1.warpFarmer("BusStop", 12, 9, false);
            monitor.Log("AIR RETURN included flight to BusStop; no fare or inventory changes", LogLevel.Info);
        }
    }

    internal void Land(FlightScene scene, bool skipped)
    {
        if (!ReferenceEquals(Game1.activeClickableMenu, scene)) return;
        scene.StopAudio();
        awaitingLanding = true;
        Game1.activeClickableMenu = null;
        Game1.warpFarmer(Airport, 25, 26, false);
        monitor.Log($"AIR FLIGHT {(skipped ? "skipped" : "completed")}; requesting native airport arrival", LogLevel.Trace);
    }

    private void DrawHint(object? sender, RenderedHudEventArgs e)
    {
        if (!Context.IsWorldReady || Game1.eventUp || Game1.activeClickableMenu != null) return;
        string name = Game1.currentLocation.Name;
        if (Game1.currentLocation is Farm farm)
        {
            Point mailbox = farm.GetMainMailboxPosition();
            if (Utility.tileWithinRadiusOfPlayer(mailbox.X, mailbox.Y, 1, Game1.player))
                DrawLabel(e.SpriteBatch, T("mailbox"), 32, 98, Game1.uiViewport.Width - 300);
            return;
        }
        if (name != Airport && (name != "BusStop" || !Eligible)) return;
        DrawLabel(e.SpriteBatch, T(name == Airport ? "hintReturn" : "hintOut"), 32, 98, Game1.uiViewport.Width - 300);
    }

    internal static void DrawLabel(SpriteBatch b, string text, int x, int y, int width, Color? colour = null)
    {
        text = Game1.parseText(text, Game1.smallFont, Math.Max(160, width));
        b.DrawString(Game1.smallFont, text, new Vector2(x + 2, y + 2), new Color(14, 33, 47));
        b.DrawString(Game1.smallFont, text, new Vector2(x, y), colour ?? new Color(241, 232, 204));
    }

    private sealed class BoardingMenu : IClickableMenu
    {
        private readonly AirTravel owner;
        private readonly bool outbound;
        private Rectangle button;
        internal BoardingMenu(AirTravel owner, bool outbound) { this.owner = owner; this.outbound = outbound; }
        internal void Confirm() => owner.Depart(outbound);
        public override void receiveLeftClick(int x, int y, bool playSound = true)
        { if (button.Contains(x, y)) Confirm(); }
        public override void draw(SpriteBatch b)
        {
            b.Draw(Game1.staminaRect, new Rectangle(0, 0, Game1.uiViewport.Width, Game1.uiViewport.Height), new Color(13, 32, 46) * .94f);
            int width = Math.Min(1024, Game1.uiViewport.Width - 64), height = Math.Min(560, Game1.uiViewport.Height - 100);
            int x = (Game1.uiViewport.Width - width) / 2, y = (Game1.uiViewport.Height - height) / 2;
            b.Draw(Game1.staminaRect, new Rectangle(x, y, width, height), new Color(231, 226, 206));
            b.Draw(Game1.staminaRect, new Rectangle(x, y, 12, height), new Color(173, 79, 71));
            int stub = x + width * 3 / 4;
            for (int sy = y + 10; sy < y + height - 8; sy += 14)
                b.Draw(Game1.staminaRect, new Rectangle(stub, sy, 2, 6), new Color(145, 155, 149));
            Color ink = new(33, 65, 82);
            // Native font has substantial CJK ascent: leave generous top padding.
            b.DrawString(Game1.smallFont, owner.T("airline"), new Vector2(x + 36, y + 65), ink);
            b.DrawString(Game1.smallFont, owner.T(outbound ? "routeOut" : "routeHome"), new Vector2(x + 36, y + 128), ink);
            b.DrawString(Game1.smallFont, Game1.player.Name, new Vector2(x + 36, y + 194), ink);
            string body = Game1.parseText(owner.T(outbound ? "boardingOut" : "boardingHome"), Game1.smallFont, width * 2 / 3 - 56);
            b.DrawString(Game1.smallFont, body, new Vector2(x + 36, y + 256), ink);
            b.Draw(owner.Texture("plane"), new Rectangle(stub + 12, y + 138, width / 4 - 28, (width / 4 - 28) * 88 / 200), Color.White);
            b.DrawString(Game1.smallFont, "MM 027", new Vector2(stub + 18, y + 290), ink);
            button = new Rectangle(x + 36, y + height - 82, width - 72, 52);
            b.Draw(Game1.staminaRect, button, ink);
            DrawLabel(b, owner.T("confirm"), button.X + 18, button.Y + 10, button.Width - 36);
            DrawLabel(b, owner.T("cancel"), x + 12, y + height + 62, width);
            drawMouse(b);
        }
    }

    internal sealed class FlightScene : IClickableMenu
    {
        private readonly AirTravel owner;
        private readonly IMonitor monitor;
        private readonly Texture2D sky, mountains, sea, runway, plane;
        private SoundEffect? sound;
        private SoundEffectInstance? engine;
        private float elapsed;
        private bool stopped, finished;
        private int phase = -1;
        internal FlightScene(AirTravel owner, IModHelper helper, IMonitor monitor)
        {
            this.owner = owner; this.monitor = monitor;
            sky = owner.Texture("sky"); mountains = owner.Texture("mountains"); sea = owner.Texture("sea");
            runway = owner.Texture("runway"); plane = owner.Texture("plane");
            // Sound failure must not prevent safe travel. Respect the player's sound slider.
            try
            {
                using var file = File.OpenRead(Path.Combine(helper.DirectoryPath, "assets/flight/propeller.wav"));
                sound = SoundEffect.FromStream(file); engine = sound.CreateInstance();
                engine.LoopCount = uint.MaxValue; engine.Volume = 0; engine.Play();
            }
            catch (Exception ex) { monitor.Log("Flight engine audio unavailable: " + ex.Message, LogLevel.Warn); }
        }
        public override bool readyToClose() => false;
        public override void receiveKeyPress(Keys key)
        { if (key == Keys.Escape && elapsed >= .5f) Finish(true); }
        public override void receiveGamePadButton(Buttons b)
        { if (b == Buttons.B && elapsed >= .5f) Finish(true); }
        public override void update(GameTime time)
        {
            base.update(time);
            elapsed += Math.Min(.1f, (float)time.ElapsedGameTime.TotalSeconds);
            int next = elapsed < 8 ? 0 : elapsed < 14 ? 1 : elapsed < 20 ? 2 : 3;
            if (next != phase) { phase = next; monitor.Log($"AIR FLIGHT phase={phase} seconds={elapsed:F1}", LogLevel.Trace); }
            if (engine != null && !stopped)
            {
                float fade = Math.Min(1, elapsed / 2) * Math.Clamp((24 - elapsed) / 3, 0, 1);
                engine.Volume = Math.Clamp(Game1.options.soundVolumeLevel * .22f * fade, 0, 1);
                engine.Pitch = elapsed < 14 ? -.15f : MathHelper.Lerp(-.15f, -.55f, Math.Clamp((elapsed - 14) / 8, 0, 1));
            }
            if (elapsed >= 24) Finish(false);
        }
        private void Finish(bool skip) { if (finished) return; finished = true; owner.Land(this, skip); }
        internal void StopAudio()
        {
            if (stopped) return; stopped = true;
            engine?.Stop(); engine?.Dispose(); sound?.Dispose(); engine = null; sound = null;
        }
        public override void emergencyShutDown() { StopAudio(); base.emergencyShutDown(); }
        public override void draw(SpriteBatch b)
        {
            int vw = Game1.uiViewport.Width, vh = Game1.uiViewport.Height;
            b.Draw(Game1.staminaRect, new Rectangle(0, 0, vw, vh), new Color(13, 30, 43));
            float scale = Math.Min(vw / 640f, (vh - 140) / 360f);
            float ox = (vw - 640 * scale) / 2, oy = (vh - 360 * scale) / 2;
            Rectangle R(float x, float y, float w, float h) => new((int)(ox + x * scale), (int)(oy + y * scale), (int)Math.Ceiling(w * scale), (int)Math.Ceiling(h * scale));
            void Tile(Texture2D tex, float offset, float y, float opacity = 1)
            {
                float left = -(offset % tex.Width);
                for (float x = left; x < 640; x += tex.Width) b.Draw(tex, R(x, y, tex.Width, tex.Height), Color.White * opacity);
            }
            b.Draw(sky, R(0, 0, 640, 360), Color.White);
            Tile(mountains, elapsed * 6, 85);
            Tile(sea, elapsed * 23, 215);
            float descend = MathHelper.SmoothStep(0, 1, Math.Clamp((elapsed - 8) / 6, 0, 1));
            float road = elapsed <= 8 ? 0 : elapsed <= 14 ? (elapsed - 8) * 70 : 420 + 70 * (Math.Min(elapsed, 20) - 14) - 35 / 6f * MathF.Pow(Math.Min(elapsed, 20) - 14, 2);
            Tile(runway, road, 200, descend);
            float px = MathHelper.Lerp(-210, 235, MathHelper.SmoothStep(0, 1, Math.Clamp(elapsed / 4, 0, 1)));
            px += Math.Clamp((elapsed - 14) / 6, 0, 1) * 25;
            float py = MathHelper.Lerp(103 + MathF.Sin(elapsed * .8f) * 2, 205, descend);
            // Moving ground shadow converges with the skis during final approach.
            if (elapsed > 8) b.Draw(Game1.staminaRect, R(px + 28, 282, 145, 3), new Color(69, 104, 130) * (.2f + .2f * descend));
            b.Draw(plane, R(px, py, 200, 88), Color.White);
            if (elapsed < 21)
            {
                bool diagonal = (int)(elapsed * 24) % 2 == 0;
                b.Draw(Game1.staminaRect, new Vector2(ox + (px + 154) * scale, oy + (py + 39) * scale), null,
                    new Color(195, 218, 216) * .65f, diagonal ? .2f : -.2f, new Vector2(.5f, .5f), new Vector2(scale * 2, scale * 27), SpriteEffects.None, 0);
            }
            if (elapsed >= 14 && elapsed < 19)
                for (int i = 0; i < 22; i++)
                {
                    float f = (elapsed * 2 + i * .17f) % 1;
                    b.Draw(Game1.staminaRect, R(px + 40 - f * 80, 285 - f * (4 + i % 4), 2 + i % 3, 1), new Color(236, 245, 242) * (1 - f));
                }
            // Cover overdraw at the edge of the cinematic viewport (including narrow windows).
            int top = (int)oy, bottom = (int)(oy + 360 * scale);
            b.Draw(Game1.staminaRect, new Rectangle(0, 0, vw, Math.Max(0, top)), new Color(13, 30, 43));
            b.Draw(Game1.staminaRect, new Rectangle(0, bottom, vw, Math.Max(0, vh - bottom)), new Color(13, 30, 43));
            int left = (int)ox, right = (int)(ox + 640 * scale);
            if (left > 0) b.Draw(Game1.staminaRect, new Rectangle(0, 0, left, vh), new Color(13, 30, 43));
            if (right < vw) b.Draw(Game1.staminaRect, new Rectangle(right, 0, vw - right, vh), new Color(13, 30, 43));
            DrawLabel(b, owner.T("phase" + phase), Math.Max(24, left + 20), Math.Max(68, top - 12), vw - 48);
            DrawLabel(b, owner.T("skip"), Math.Max(24, left + 20), Math.Min(vh - 46, bottom + 18), vw - 48);
            float fade = Math.Max(Math.Clamp((1 - elapsed) / 1, 0, 1), Math.Clamp((elapsed - 23) / 1, 0, 1));
            if (fade > 0) b.Draw(Game1.staminaRect, new Rectangle(0, 0, vw, vh), Color.Black * fade);
        }
    }
}
