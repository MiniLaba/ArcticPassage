using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Menus;

namespace ArcticPassage.Runtime;

/// <summary>Winter-only snow-block model at the existing camp exhibit.</summary>
internal sealed class SnowShelterLesson
{
    internal const string Location = "ArcticPassage_WinterCamp";
    internal const string RecordKey = "WhiteBay.ArcticPassage/SnowShelterLesson";
    private readonly IModHelper helper;
    private readonly IMonitor monitor;
    private string T(string key, object? tokens = null) => helper.Translation.Get("shelter." + key, tokens);

    internal SnowShelterLesson(IModHelper helper, IMonitor monitor)
    {
        this.helper = helper; this.monitor = monitor;
        GameLocation.RegisterTileAction("ArcticPassageSnowShelter", Open);
        helper.Events.Input.ButtonPressed += (_, e) =>
        {
            if (!Context.IsWorldReady || e.IsSuppressed()) return;
            if (Game1.activeClickableMenu is LessonMenu lesson)
            {
                // Native snappy-menu navigation may consume arrow keys before
                // receiveKeyPress. Handle this menu's keys once via SMAPI.
                Keys key = e.Button switch
                {
                    SButton.Left or SButton.A or SButton.DPadLeft => Keys.Left,
                    SButton.Right or SButton.D or SButton.DPadRight => Keys.Right,
                    SButton.Enter or SButton.Space or SButton.ControllerA => Keys.Enter,
                    SButton.Escape or SButton.ControllerB => Keys.Escape,
                    _ => Keys.None
                };
                if (key != Keys.None) { helper.Input.Suppress(e.Button); lesson.Control(key); }
                return;
            }
            if (e.Button != SButton.X || e.IsSuppressed() || !Context.IsWorldReady || Game1.eventUp
                || Game1.dialogueUp || Game1.activeClickableMenu != null || !Game1.player.CanMove
                || Game1.player.UsingTool || Game1.currentLocation.Name != Location) return;
            Point sign = Game1.player.TilePoint + (Game1.player.FacingDirection switch
            { 0 => new Point(0, -1), 1 => new Point(1, 0), 2 => new Point(0, 1), _ => new Point(-1, 0) });
            string action = Game1.currentLocation.doesTileHaveProperty(sign.X, sign.Y, "Action", "Buildings");
            if (action != "ArcticPassageSnowShelter") return;
            helper.Input.Suppress(e.Button);
            Game1.currentLocation.performAction(action, Game1.player, new xTile.Dimensions.Location(sign.X, sign.Y));
        };
    }

    private bool Open(GameLocation location, string[] args, Farmer who, Point tile)
    {
        if (location.Name != Location || tile != new Point(20, 35) || who != Game1.player) return false;
        if (Game1.currentSeason != "winter") { Game1.drawObjectDialogue(T("season")); return true; }
        if (Game1.eventUp || Game1.activeClickableMenu != null) return true;
        Game1.activeClickableMenu = new LessonMenu(this);
        monitor.Log("SHELTER opened winter model; no inventory or money changes", LogLevel.Trace);
        return true;
    }

    private bool Valid(int day) => Context.IsWorldReady && Game1.currentSeason == "winter"
        && Game1.Date.TotalDays == day && Game1.currentLocation.Name == Location;

    private sealed class LessonMenu : IClickableMenu
    {
        private readonly SnowShelterLesson owner;
        private readonly SnowBlockPattern model = new();
        private readonly int day;
        private bool misplaced;
        private readonly Color ink = new(36, 60, 76), muted = new(89, 116, 128), gold = new(217, 169, 95);
        private Rectangle Panel => new(xPositionOnScreen + 30, yPositionOnScreen + 116, width * 55 / 100, height - 198);
        private Rectangle Left => new(Panel.X + 12, Panel.Bottom - 53, 58, 40);
        private Rectangle Right => new(Panel.Right - 70, Panel.Bottom - 53, 58, 40);
        private Rectangle Confirm => new(Panel.X + 82, Panel.Bottom - 53, Panel.Width - 164, 40);

        internal LessonMenu(SnowShelterLesson owner) : base(0, 0, 1000, 670, true)
        { this.owner = owner; day = Game1.Date.TotalDays; Resize(); }
        private void Resize()
        {
            width = Math.Min(1000, Game1.uiViewport.Width - 32); height = Math.Min(670, Game1.uiViewport.Height - 32);
            xPositionOnScreen = (Game1.uiViewport.Width - width) / 2;
            yPositionOnScreen = (Game1.uiViewport.Height - height) / 2;
            initializeUpperRightCloseButton();
        }
        public override void gameWindowSizeChanged(Rectangle oldBounds, Rectangle newBounds) => Resize();
        private void Shift() { model.Shift(); misplaced = false; Game1.playSound("shwip"); }
        private void Place()
        {
            if (!owner.Valid(day)) { exitThisMenu(); return; }
            if (model.Complete) { exitThisMenu(); return; }
            if (!model.Place()) { misplaced = true; Game1.playSound("cancel"); return; }
            misplaced = false; Game1.playSound("dwop");
            owner.monitor.Log($"SHELTER course placed {model.Placed}/{SnowBlockPattern.Courses}", LogLevel.Trace);
            if (!model.Complete) return;
            // The native farmer save owns this personal record. Replays never
            // overwrite the original date or award money/items/blueprints.
            bool first = !Game1.player.modData.ContainsKey(RecordKey);
            if (first) Game1.player.modData[RecordKey] = $"{Game1.year}|winter|{Game1.dayOfMonth}";
            owner.monitor.Log($"SHELTER model completed first={first}; personal record only, no reward", LogLevel.Info);
        }
        internal void Control(Keys key)
        {
            owner.monitor.Log($"SHELTER control {key}; placed={model.Placed}", LogLevel.Trace);
            if (key == Keys.Escape) exitThisMenu();
            else if (key is Keys.Left or Keys.Right or Keys.A or Keys.D) Shift();
            else if (key is Keys.Enter or Keys.Space) Place();
        }
        public override void receiveKeyPress(Keys key)
        {
            // Keyboard/controller directions can also be synthesized by the
            // native menu navigator. Only the SMAPI ButtonPressed path moves
            // this two-position model, otherwise one tap may toggle twice.
            if (key is Keys.Left or Keys.Right or Keys.A or Keys.D or Keys.Enter or Keys.Space or Keys.Escape) return;
            base.receiveKeyPress(key);
        }
        public override void receiveGamePadButton(Buttons button)
        {
            if (button is Buttons.B or Buttons.A or Buttons.DPadLeft or Buttons.DPadRight) return;
            base.receiveGamePadButton(button);
        }
        public override void receiveLeftClick(int x, int y, bool playSound = true)
        {
            if (Left.Contains(x, y) || Right.Contains(x, y)) Shift();
            else if (Confirm.Contains(x, y)) Place();
            else base.receiveLeftClick(x, y, playSound);
        }
        public override void update(GameTime time)
        {
            base.update(time);
            if (!owner.Valid(day)) exitThisMenu();
        }
        private static void Fill(SpriteBatch b, Rectangle r, Color c) => b.Draw(Game1.staminaRect, r, c);
        private float Text(SpriteBatch b, string text, int x, int y, int width, Color c, float scale = .75f)
        {
            string wrapped = Game1.parseText(text, Game1.smallFont, Math.Max(32, (int)(width / scale)));
            b.DrawString(Game1.smallFont, wrapped, new Vector2(x, y), c, 0, Vector2.Zero, scale, SpriteEffects.None, 1);
            return Game1.smallFont.MeasureString(wrapped).Y * scale;
        }
        public override void draw(SpriteBatch b)
        {
            Fill(b, new Rectangle(0, 0, Game1.uiViewport.Width, Game1.uiViewport.Height), Color.Black * .55f);
            Rectangle paper = new(xPositionOnScreen, yPositionOnScreen, width, height);
            Fill(b, paper, ink); Fill(b, new Rectangle(paper.X + 5, paper.Y + 5, width - 10, height - 10), new Color(239, 237, 222));
            Text(b, owner.T("title"), paper.X + 30, paper.Y + 25, width - 80, ink, .95f);
            Text(b, owner.T(Game1.player.modData.ContainsKey(RecordKey) ? "subtitleDone" : "subtitle"),
                paper.X + 30, paper.Y + 65, width - 80, muted, .65f);
            Rectangle panel = Panel;
            Fill(b, panel, new Color(35, 57, 78));
            // Pixel-shaped snow courses taper inward. Their seam offset is the
            // player's action; no external generated images or new map are used.
            int unit = Math.Max(8, Math.Min(18, (panel.Width - 36) / 28));
            int cx = panel.Center.X, floor = panel.Bottom - 132;
            for (int row = 0; row <= SnowBlockPattern.Courses; row++)
            {
                bool active = !model.Complete && row == model.Placed + 1;
                bool built = row <= model.Placed;
                int span = (24 - row * 4) * unit, block = 4 * unit, rh = 3 * unit;
                int left = cx - span / 2, yy = floor - row * rh;
                int offset = active ? model.Offset : row % 2;
                Color snow = built ? new(213, 230, 239) : active ? new(235, 242, 242) : new(65, 90, 110);
                // Anchor seams to the shared centre, not to each narrowing
                // course's left edge, which already shifts by half a block.
                for (int xx = cx - 16 * unit + offset * block / 2; xx < left + span; xx += block)
                {
                    int a = Math.Max(left, xx), z = Math.Min(left + span, xx + block - 3);
                    if (z <= a) continue;
                    Rectangle stone = new(a, yy, z - a, rh - 3);
                    Fill(b, stone, snow);
                    Fill(b, new Rectangle(a + 2, yy + rh - 9, z - a - 2, 6), built || active ? new Color(153, 183, 204) : new Color(51, 77, 98));
                    if (active) Fill(b, new Rectangle(a, yy, z - a, 3), gold);
                }
            }
            if (model.Complete)
                Fill(b, new Rectangle(cx - 2 * unit, floor - 10 * unit, 4 * unit, unit), gold);
            foreach (Rectangle button in new[] { Left, Right, Confirm }) Fill(b, button, new Color(66, 95, 113));
            Text(b, "<", Left.X + 20, Left.Y + 6, 32, Color.White);
            Text(b, ">", Right.X + 20, Right.Y + 6, 32, Color.White);
            Text(b, owner.T(model.Complete ? "close" : "place"), Confirm.X + 10, Confirm.Y + 6, Confirm.Width - 20, Color.White, .65f);
            int rx = panel.Right + 22, rw = paper.Right - rx - 26, ry = panel.Y;
            ry += (int)Text(b, owner.T(model.Complete ? "complete" : "instruction"), rx, ry, rw, ink, .8f) + 22;
            ry += (int)Text(b, owner.T("context"), rx, ry, rw, muted, .68f) + 18;
            Text(b, owner.T(model.Complete ? "save" : misplaced ? "retry" : "progress", new { count = model.Placed }),
                rx, ry, rw, misplaced ? new Color(157, 86, 58) : ink, .7f);
            Text(b, owner.T("keys"), paper.X + 30, paper.Bottom - 43, width - 70, muted, .6f);
            base.draw(b); drawMouse(b);
        }
    }
}
