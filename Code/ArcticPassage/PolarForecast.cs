namespace ArcticPassage.Runtime;

internal enum PolarCondition
{
    Calm,
    Gale,
    Blizzard
}

/// <summary>Stable seasonal forecasts with no world RNG or save-state mutation.</summary>
internal static class PolarForecast
{
    internal static PolarCondition ForDate(int year, string season, int day)
    {
        int ordinal = Ordinal(year, season, day);
        PolarCondition today = Raw(ordinal, season);
        // A single rough day can delay travel, but a storm front never seals a
        // route on successive days. Return routes remain independent of weather.
        string previousSeason = day > 1 ? season : PreviousSeason(season);
        return today != PolarCondition.Calm && Raw(ordinal - 1, previousSeason) != PolarCondition.Calm
            ? PolarCondition.Calm
            : today;
    }

    internal static bool BlocksFjordDeparture(PolarCondition condition)
        => condition is PolarCondition.Gale or PolarCondition.Blizzard;

    internal static bool BlocksSledDeparture(PolarCondition condition)
        => condition == PolarCondition.Blizzard;

    internal static string Key(PolarCondition condition) => condition switch
    {
        PolarCondition.Gale => "gale",
        PolarCondition.Blizzard => "blizzard",
        _ => "calm"
    };

    private static int Ordinal(int year, string season, int day)
        => ((Math.Max(1, year) - 1) * 112) + (SeasonIndex(season) * 28) + (Math.Clamp(day, 1, 28) - 1);

    private static int SeasonIndex(string season) => season switch
    {
        "summer" => 1,
        "fall" => 2,
        "winter" => 3,
        _ => 0
    };

    private static string PreviousSeason(string season) => season switch
    {
        "spring" => "winter",
        "summer" => "spring",
        "fall" => "summer",
        _ => "fall"
    };

    private static PolarCondition Raw(int ordinal, string season)
    {
        uint value = unchecked((uint)ordinal + 0x9E3779B9u);
        value ^= value >> 16;
        value *= 0x7FEB352Du;
        value ^= value >> 15;
        value *= 0x846CA68Bu;
        value ^= value >> 16;
        int roll = (int)(value % 100);
        if (season == "winter")
            return roll < 13 ? PolarCondition.Blizzard : roll < 42 ? PolarCondition.Gale : PolarCondition.Calm;
        int galeChance = season switch { "spring" => 14, "fall" => 18, _ => 10 };
        return roll < galeChance ? PolarCondition.Gale : PolarCondition.Calm;
    }
}
