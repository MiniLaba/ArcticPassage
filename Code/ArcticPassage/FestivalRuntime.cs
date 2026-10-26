using HarmonyLib;
using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Menus;
using StardewValley.Tools;

namespace ArcticPassage.Runtime;

/// <summary>Small, date-gated activities for the three native Frosthavn festivals.</summary>
internal sealed class FestivalRuntime
{
    private const string Prefix = "WhiteBay.ArcticPassage/Festival/";
    private readonly IModHelper helper;
    private readonly IMonitor monitor;
    private static FestivalRuntime? instance;

    internal FestivalRuntime(IModHelper helper, IMonitor monitor, Harmony harmony)
    {
        this.helper = helper;
        this.monitor = monitor;
        instance = this;
        harmony.Patch(AccessTools.Method(typeof(Event), nameof(Event.canPlayerUseTool)),
            postfix: new HarmonyMethod(typeof(FestivalRuntime), nameof(AllowChallengeRod)));
        harmony.Patch(AccessTools.Method(typeof(Event), nameof(Event.caughtFish)),
            postfix: new HarmonyMethod(typeof(FestivalRuntime), nameof(ChallengeCatch)));
        harmony.Patch(AccessTools.Method(typeof(GameLocation), nameof(GameLocation.getFish)),
            prefix: new HarmonyMethod(typeof(FestivalRuntime), nameof(ChallengeFishPool)));
        helper.Events.Input.ButtonPressed += OnButton;
        helper.Events.Display.RenderedHud += DrawHint;
    }

    private string T(string key) => helper.Translation.Get("festival." + key);

    internal static string? FestivalForEvent(Event? currentEvent)
        => currentEvent?.isSpecificFestival("spring9") == true ? "spring"
            : currentEvent?.isSpecificFestival("summer18") == true ? "summer"
            : currentEvent?.isSpecificFestival("winter21") == true ? "winter" : null;

    internal static string? CurrentFestival()
    {
        if (!Context.IsWorldReady || Game1.currentLocation?.Name != "Temp") return null;
        return FestivalForEvent(Game1.currentLocation.currentEvent);
    }

    internal static bool CanInteract => CurrentFestival() != null && Game1.player.CanMove
        && !Game1.player.UsingTool && !Game1.dialogueUp && Game1.currentMinigame == null;

    private static void AllowChallengeRod(Event __instance, ref bool __result, ref bool ___drawTool)
    {
        if (__result || !Context.IsWorldReady || !Context.IsMainPlayer
            || !ReferenceEquals(__instance, Game1.currentLocation?.currentEvent)
            || CurrentFestival() != "spring" || !CanInteract
            || Game1.activeClickableMenu != null || Game1.player.CurrentTool is not FishingRod
            || !Game1.player.modData.ContainsKey(Key("spring", "fishStart", Game1.year))) return;
        __result = true;
        ___drawTool = true;
    }

    private static void ChallengeFishPool(GameLocation __instance, ref string __6)
    {
        // The native temporary location has no harbor LocationData of its own.
        if (Context.IsWorldReady && ReferenceEquals(__instance, Game1.currentLocation)
            && CurrentFestival() == "spring") __6 = "ArcticPassage_Harbor";
    }

    private static void ChallengeCatch(Event __instance, string __0, int __1, Farmer __2)
    {
        if (!Context.IsWorldReady || !Context.IsMainPlayer || __2 != Game1.player
            || !ReferenceEquals(__instance, Game1.currentLocation?.currentEvent)
            || CurrentFestival() != "spring") return;
        // Festival catches use Event.caughtFish, not Farmer.caughtFish or the
        // lifetime FishCaught statistic. The native rod releases the fish.
        if (__1 > 0 && __0?.StartsWith("(O)ArcticPassage_", StringComparison.Ordinal) == true
            && __2.modData.ContainsKey(Key("spring", "fishStart", Game1.year)))
        {
            __2.modData[Key("spring", "fishCatch", Game1.year)] = __0;
            instance?.monitor.Log($"FESTIVAL native catch-and-release verified: {__0}, size={__1}", LogLevel.Info);
        }
        __2.forceCanMove();
    }

    private void DrawHint(object? sender, RenderedHudEventArgs e)
    {
        string? festival = CurrentFestival();
        if (festival == null || !CanInteract || Game1.activeClickableMenu != null) return;
        string text = T("key");
        Vector2 size = Game1.smallFont.MeasureString(text);
        int x = Game1.uiViewport.Width - (int)size.X - 32;
        e.SpriteBatch.Draw(Game1.staminaRect, new Rectangle(x - 9, Game1.uiViewport.Height - 56,
            (int)size.X + 18, (int)size.Y + 12), new Color(24, 40, 49) * .78f);
        e.SpriteBatch.DrawString(Game1.smallFont, text, new Vector2(x, Game1.uiViewport.Height - 50), new Color(239, 230, 203));
    }

    private void OnButton(object? sender, ButtonPressedEventArgs e)
    {
        if (e.Button != SButton.F || e.IsSuppressed() || Game1.activeClickableMenu != null || !CanInteract
            || !Context.IsWorldReady || !Context.IsMainPlayer) return;
        string? festival = CurrentFestival();
        if (festival == null) return;
        helper.Input.Suppress(e.Button);

        if (festival == "spring" && TrySubmitFishingChallenge()) return;
        ShowChoices(festival);
    }

    private void ShowChoices(string festival)
    {
        string prompt = T(festival + ".prompt");
        Response[] options = festival switch
        {
            "spring" => [
                new Response("cast", T("spring.cast")),
                new Response("quiz", T("spring.quiz")),
                new Response("soup", T("spring.soup")),
                new Response("cancel", T("cancel"))
            ],
            "summer" => [
                new Response("birds", T("summer.birds")),
                new Response("quiz", T("summer.quiz")),
                new Response("cancel", T("cancel"))
            ],
            _ => [
                new Response("soup", T("winter.soup")),
                new Response("view", T("winter.view")),
                new Response("cancel", T("cancel"))
            ]
        };
        Game1.currentLocation.createQuestionDialogue(prompt, options, (_, answer) => Choose(festival, answer), null);
    }

    private void Choose(string festival, string answer)
    {
        if (answer == "cancel" || CurrentFestival() != festival) return;
        switch (festival, answer)
        {
            case ("spring", "cast"):
                if (!Game1.player.Items.Any(item => item is FishingRod))
                { Game1.drawObjectDialogue(T("spring.noRod")); return; }
                Game1.player.modData[Key("spring", "fishStart", Game1.year)] = "native-event-catch";
                Game1.drawObjectDialogue(T("spring.castStart"));
                monitor.Log("FESTIVAL spring fishing challenge started from the temporary harbor map", LogLevel.Info);
                break;
            case ("spring", "quiz"):
                AskQuiz("spring", T("spring.quizPrompt"), [
                    new Response("low", T("answer.low")),
                    new Response("mid", T("answer.mid")),
                    new Response("high", T("answer.high"))
                ], "mid", "spring.quizRight", "spring.quizWrong");
                break;
            case ("spring", "soup"):
                BuyMeal("spring", "spring.mealNoMoney", "spring.mealBought", "ArcticPassage_FishPotatoStew");
                break;
            case ("summer", "birds"):
                Game1.player.modData[Key("summer", "shoreObservation", Game1.year)] = "recorded";
                ClaimReward("summer");
                monitor.Log("FESTIVAL summer shore-safe seabird observation recorded", LogLevel.Info);
                break;
            case ("summer", "quiz"):
                AskQuiz("summer", T("summer.quizPrompt"), [
                    new Response("cliffs", T("answer.cliffs")),
                    new Response("boat", T("answer.boat")),
                    new Response("shore", T("answer.shore"))
                ], "shore", "summer.quizRight", "summer.quizWrong");
                break;
            case ("winter", "soup"):
                if (!BuyMeal("winter", "winter.mealNoMoney", "winter.soupBought", "ArcticPassage_CharSoup")) return;
                if (ClaimReward("winter")) WarmTown();
                break;
            case ("winter", "view"):
                Game1.drawObjectDialogue(T("winter.viewTaken"));
                if (ClaimReward("winter")) WarmTown();
                break;
        }
    }

    private void AskQuiz(string festival, string prompt, Response[] answers, string correct, string success, string failure)
    {
        string attempt = Key(festival, "quizAttempt", Game1.year);
        if (Game1.player.modData.ContainsKey(attempt))
        {
            Game1.drawObjectDialogue(T("already"));
            return;
        }
        Game1.currentLocation.createQuestionDialogue(prompt, answers, (_, answer) =>
        {
            if (CurrentFestival() != festival) return;
            Game1.player.modData[attempt] = answer;
            if (answer == correct)
            {
                Game1.drawObjectDialogue(T(success));
                if (ClaimReward(festival) && festival == "spring") GiveFriendship("ArcticPassage_Roan", 15);
            }
            else Game1.drawObjectDialogue(T(failure));
        }, null);
    }

    private bool TrySubmitFishingChallenge()
    {
        string key = Key("spring", "fishStart", Game1.year);
        if (!Game1.player.modData.ContainsKey(key)
            || !Game1.player.modData.ContainsKey(Key("spring", "fishCatch", Game1.year))) return false;
        Game1.player.modData.Remove(key);
        Game1.drawObjectDialogue(T("spring.catchComplete"));
        if (ClaimReward("spring")) GiveFriendship("ArcticPassage_Ada", 15);
        monitor.Log("FESTIVAL spring challenge completed from a native festival catch-and-release; no fish item or lifetime catch statistic granted", LogLevel.Info);
        return true;
    }

    private bool BuyMeal(string festival, string insufficientKey, string boughtKey, string itemId, bool showFoodMessage = true)
    {
        const int price = 100;
        if (Game1.player.Money < price)
        {
            Game1.drawObjectDialogue(T(insufficientKey));
            return false;
        }
        if (CurrentFestival() != festival) return false;
        Game1.player.Money -= price;
        Game1.player.addItemByMenuIfNecessaryElseHoldUp(ItemRegistry.Create("(O)" + itemId));
        Game1.playSound("purchaseClick");
        if (showFoodMessage) Game1.addHUDMessage(new HUDMessage(T(boughtKey), 2));
        monitor.Log($"FESTIVAL {festival} native meal transaction -{price}g item=(O){itemId}", LogLevel.Info);
        return true;
    }

    private void WarmTown()
    {
        string key = Key("winter", "friendship", Game1.year);
        if (Game1.player.modData.ContainsKey(key)) return;
        foreach (string npc in new[] { "Ada", "Mira", "Roan", "Nora", "Levin", "Amma" })
            GiveFriendship("ArcticPassage_" + npc, 25);
        Game1.player.modData[key] = Game1.dayOfMonth.ToString();
    }

    private static void GiveFriendship(string npc, int points)
    {
        if (!Game1.player.friendshipData.TryGetValue(npc, out Friendship? friendship))
        {
            friendship = new Friendship(0);
            Game1.player.friendshipData[npc] = friendship;
        }
        friendship.Points = Math.Min(2500, friendship.Points + points);
    }

    private bool ClaimReward(string festival)
    {
        if (CurrentFestival() != festival) return false;
        // A second item menu would discard the paid meal's pending overflow.
        // Leave the annual reward unclaimed so F -> lantern walk can retry it.
        if (Game1.activeClickableMenu is ItemGrabMenu) return false;
        string claim = Key(festival, "reward", Game1.year);
        if (Game1.player.modData.ContainsKey(claim))
        {
            Game1.drawObjectDialogue(T("already"));
            return false;
        }
        string itemId = festival switch
        {
            "spring" => "ArcticPassage_HarborKnot",
            "summer" => "ArcticPassage_MidnightSunDisplay",
            _ => "ArcticPassage_WinterLantern"
        };
        Item item = ItemRegistry.Create("(BC)" + itemId);
        Game1.player.addItemByMenuIfNecessaryElseHoldUp(item);
        Game1.player.modData[claim] = Game1.dayOfMonth.ToString();
        Game1.playSound("reward");
        monitor.Log($"FESTIVAL {festival} year {Game1.year} native placeable reward granted", LogLevel.Info);
        return true;
    }

    private static string Key(string festival, string kind, int year)
        => Prefix + festival + "/" + kind + "/" + year;
}
