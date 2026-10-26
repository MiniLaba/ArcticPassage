using ArcticPassage.Runtime;
using System.Text.Json;
using System.Text.RegularExpressions;

// Deterministic regression of player-facing guidance, not a normal-play test.
string root = Path.GetFullPath(args[0]);
int checks = 0;
void Check(bool condition, string message)
{
    if (!condition) throw new Exception(message);
    checks++;
    Console.WriteLine("PASS " + message);
}
HashSet<string> Mail(params string[] flags) => flags.Select(f => HarborProgress.Prefix + f).ToHashSet();
string Step(string[] quests, HashSet<string> mail, bool reward = false)
    => HarborProgress.NextStep(quests.Select(q => HarborProgress.Prefix + q), mail, reward);

var mail = Mail();
Check(Step(["Arrival"], mail) == "Arrival", "arrival keeps the guesthouse objective");
foreach (string season in new[] { "spring", "summer", "fall", "winter" })
    Check(Step(["SledTools", "FirstCatch_" + season], mail) == "FirstCatch_" + season, season + " first shipment survives an earlier winter side quest");
Check(Step([], mail, true) == "claim", "pending native reward is discoverable without an active main quest");
mail.Add(HarborProgress.Prefix + "WoodDelivered");
Check(Step(["BoatRepair"], mail, true) == "shedWait", "wood delivery cannot advertise the unfinished facility");
Check(HarborProgress.RemainingIronTrades(mail) == 0, "barter remains closed before the actual shed opening");
mail.Add(HarborProgress.Prefix + "Shed");
Check(Step(["SledTools", "BoatRepair"], mail) == "BoatRepair", "winter side quest cannot hide boat repair");
Check(HarborProgress.RemainingIronTrades(mail) == 2, "shed opening exposes exactly two lifetime exchanges");
foreach (int receipt in new[] { 1, 2 })
{
    var once = Mail("WoodDelivered", "Shed", "LocalRepairIron_" + receipt);
    Check(HarborProgress.RemainingIronTrades(once) == 1, "either first-purchased receipt leaves exactly one exchange: " + receipt);
}
mail.Add(HarborProgress.Prefix + "LocalRepairIron_2");
mail.Add(HarborProgress.Prefix + "LocalRepairIron_1");
Check(HarborProgress.RemainingIronTrades(mail) == 0, "both persistent receipts exhaust the exchanges");
mail.Add(HarborProgress.Prefix + "IronDelivered");
Check(Step(["FjordVisit"], mail) == "boatWait", "same-day fjord follow-up correctly waits for tomorrow");
Check(Step([], mail, true) == "boatWait", "unclaimed delivery reward does not lose overnight repair guidance");
Check(HarborProgress.RemainingIronTrades(Mail("Shed", "IronDelivered")) == 0, "mined iron delivery closes unspent fish exchanges too");
mail.Add(HarborProgress.Prefix + "Boat");
Check(Step(["SledTrial", "FjordVisit"], mail) == "FjordVisit", "native next-day boat flag enables the pier instruction");
Check(Step(["DeepCatch"], mail) == "DeepCatch", "fjord completion leads to the existing deep-water objective");
Check(Step(["SledTrial"], mail) == "free", "unfinished side quest does not reset a completed harbor chain");
Check(HarborProgress.RemainingIronTrades(Mail("Shed", "Boat")) == 0, "old open-boat saves cannot regain barter by missing delivery flags");
foreach (string chapter in HarborProgress.Chapters.Skip(1))
    Check(Step(["SledTrial", chapter], mail) == chapter, "guide retains the active later chapter: " + chapter);
Check(HarborProgress.MissingChapterSuccessor(new HashSet<string> { "DeepCatch" }, new HashSet<string> { "DeepCatch" }) == "FieldReport",
    "legacy completed deep-catch task awaiting payment receives the new successor without repeating delivery");
Check(HarborProgress.MissingChapterSuccessor(new HashSet<string> { "DeepCatch" }, new HashSet<string> { "FieldReport" }) == null,
    "existing successor cannot be duplicated");
Check(HarborProgress.MissingChapterSuccessor(new HashSet<string> { "DeepCatch" }, new HashSet<string> { "DriedOrder" }) == null,
    "a later active chapter prevents reopening earlier tasks");
Check(HarborProgress.MissingChapterSuccessor(new HashSet<string> { "StormRoute" }, new HashSet<string>()) == "CampVisit",
    "saved completion receipt can restore a missing next chapter");
Check(HarborProgress.MissingChapterSuccessor(new HashSet<string> { "WarmHarbor" }, new HashSet<string>()) == null,
    "completed finale never restarts the story");
Check(HarborProgress.MissingChapterSuccessor(new HashSet<string>(), new HashSet<string>()) == null,
    "no completion evidence never fabricates old delivery credit");

using var content = JsonDocument.Parse(File.ReadAllText(Path.Combine(root, "ContentPack/content.json")));
var changes = content.RootElement.GetProperty("Changes").EnumerateArray().ToArray();
var supplies = changes.Where(p => p.GetProperty("Target").GetString() == "Data/Shops")
    .Select(p => p.GetProperty("Entries")).First(e => e.TryGetProperty("ArcticPassage_Supplies", out _))
    .GetProperty("ArcticPassage_Supplies").GetProperty("Items").EnumerateArray().ToArray();
var rods = supplies.Where(i => i.GetProperty("ItemId").GetString() == "(T)BambooPole").ToArray();
Check(rods.Length == 1 && rods[0].GetProperty("Price").GetInt32() == 500
    && rods[0].GetProperty("Condition").GetString() == "PLAYER_HAS_MAIL Current ArcticPassage_Shed",
    "one paid normal rod is locally obtainable after shed repair for the halibut objective");
Check(supplies.Count(i => i.GetProperty("ItemId").GetString() == "(T)TrainingRod") == 1,
    "the cheap beginner rod remains available");
var quest = changes.Where(p => p.GetProperty("Target").GetString() == "Data/Quests")
    .Select(p => p.GetProperty("Entries")).First(e => e.TryGetProperty("ArcticPassage_BoatRepair", out _));
Check(quest.GetProperty("ArcticPassage_BoatRepair").GetString()!.Contains("ArcticPassage_FjordVisit"), "shipped boat task really has the immediate fjord follow-up under regression");
var trigger = changes.Where(p => p.GetProperty("Target").GetString() == "Data/TriggerActions")
    .Select(p => p.GetProperty("Entries")).First(e => e.TryGetProperty("ArcticPassage_BoatComplete", out _))
    .GetProperty("ArcticPassage_BoatComplete");
Check(trigger.GetProperty("Trigger").GetString() == "DayStarted"
    && trigger.GetProperty("Condition").GetString()!.Contains("ArcticPassage_IronDelivered")
    && trigger.GetProperty("Actions").EnumerateArray().Any(a => a.GetString()!.Contains("ArcticPassage_Boat received")),
    "shipped native trigger, rather than guidance code, remains responsible for opening the boat next day");

using var en = JsonDocument.Parse(File.ReadAllText(Path.Combine(root, "Code/ArcticPassage/Runtime/i18n/default.json")));
using var zh = JsonDocument.Parse(File.ReadAllText(Path.Combine(root, "Code/ArcticPassage/Runtime/i18n/zh.json")));
foreach (string key in new[] { "boatWait", "shedWait", "ironProgress", "ironTrade", "ironSource", "deepProgress", "rodReady", "rodNeeded" })
{
    string full = "guide.goal." + key;
    string english = en.RootElement.GetProperty(full).GetString()!;
    string chinese = zh.RootElement.GetProperty(full).GetString()!;
    string Tokens(string s) => string.Join(",", Regex.Matches(s, @"\{\{\w+\}\}").Select(m => m.Value).OrderBy(t => t));
    Check(english.Length > 0 && chinese.Length > 0 && Tokens(english) == Tokens(chinese), "nonempty bilingual guidance with matching tokens: " + key);
}
Console.WriteLine($"PASS {checks} guidance/data contract checks. No game session, fish catch, boat trip or save/reload is claimed.");
