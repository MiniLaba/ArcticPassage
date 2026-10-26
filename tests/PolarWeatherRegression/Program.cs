using ArcticPassage.Runtime;
using System.Text.Json;

string root = Path.GetFullPath(args[0]);
int checks = 0;
void Check(bool condition, string message)
{
    if (!condition) throw new InvalidOperationException(message);
    checks++;
}

string[] seasons = ["spring", "summer", "fall", "winter"];
var observed = new HashSet<PolarCondition>();
PolarCondition previous = PolarCondition.Calm;
for (int year = 1; year <= 20; year++)
foreach (string season in seasons)
for (int day = 1; day <= 28; day++)
{
    PolarCondition current = PolarForecast.ForDate(year, season, day);
    Check(current == PolarForecast.ForDate(year, season, day), $"forecast is stable for {year}/{season}/{day}");
    if (season != "winter") Check(current != PolarCondition.Blizzard, $"blizzards stay in winter: {year}/{season}/{day}");
    if (day != 1 || season != "spring" || year != 1)
        Check(!(current != PolarCondition.Calm && previous != PolarCondition.Calm), $"rough days never form a consecutive closure: {year}/{season}/{day}");
    observed.Add(current);
    previous = current;
}
Check(observed.SetEquals([PolarCondition.Calm, PolarCondition.Gale, PolarCondition.Blizzard]), "seasonal samples include calm, gale and winter whiteout states");
Check(!PolarForecast.BlocksFjordDeparture(PolarCondition.Calm), "calm sea permits an outward fjord trip");
Check(PolarForecast.BlocksFjordDeparture(PolarCondition.Gale) && PolarForecast.BlocksFjordDeparture(PolarCondition.Blizzard), "rough sea pauses outbound boat trips");
Check(!PolarForecast.BlocksSledDeparture(PolarCondition.Gale) && PolarForecast.BlocksSledDeparture(PolarCondition.Blizzard), "only winter whiteout pauses the dog team");

using var content = JsonDocument.Parse(File.ReadAllText(Path.Combine(root, "ContentPack/content.json")));
var changes = content.RootElement.GetProperty("Changes").EnumerateArray().ToArray();
var outbound = changes.Single(p => p.GetProperty("LogName").GetString() == "Maps/ArcticPassage_Harbor"
    && p.TryGetProperty("MapTiles", out var tiles) && tiles.EnumerateArray().Any(t => t.GetProperty("Position").GetProperty("X").GetInt32() == 43
        && t.GetProperty("Position").GetProperty("Y").GetInt32() == 24));
Check(outbound.GetProperty("When").GetProperty("HasFlag |contains=ArcticPassage_Boat").GetBoolean(), "outbound custom tile action stays locked until the native boat flag");
Check(outbound.GetProperty("MapTiles")[0].GetProperty("SetProperties").GetProperty("Action").GetString() == "ArcticPassageFjordOutbound", "outbound action is routed through the weather safety gate");
var returning = changes.Single(p => p.GetProperty("LogName").GetString() == "R06 safe fjord return action");
Check(!returning.TryGetProperty("When", out _)
    && returning.GetProperty("MapTiles")[0].GetProperty("SetProperties").GetProperty("Action").GetString() == "ArcticPassageFjordReturn",
    "fjord return action is unconditional in every season and forecast");

using var en = JsonDocument.Parse(File.ReadAllText(Path.Combine(root, "Code/ArcticPassage/Runtime/i18n/default.json")));
using var zh = JsonDocument.Parse(File.ReadAllText(Path.Combine(root, "Code/ArcticPassage/Runtime/i18n/zh.json")));
Check(en.RootElement.EnumerateObject().Select(p => p.Name).OrderBy(x => x)
    .SequenceEqual(zh.RootElement.EnumerateObject().Select(p => p.Name).OrderBy(x => x)), "weather and route-warning keys match in both languages");
foreach (string key in new[] { "guide.weather.title", "guide.weather.calm", "guide.weather.gale", "guide.weather.blizzard", "weather.fjordClosed", "weather.sledClosed" })
    Check(en.RootElement.GetProperty(key).GetString()!.Length > 0 && zh.RootElement.GetProperty(key).GetString()!.Length > 0, "localized forecast text exists: " + key);

Console.WriteLine($"PASS {checks} deterministic polar-weather and route-contract checks. No game session, weather seed, or save was modified.");
