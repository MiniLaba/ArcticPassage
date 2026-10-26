namespace ArcticPassage.Runtime;

/// <summary>
/// A gentle, playable photoperiod for a fictional settlement near 69°N.
/// It changes only the eight authored outdoor regions' lightmap; the Valley's
/// clock, weather, sleep schedule, and location contexts remain native.
/// </summary>
internal static class PolarPhotoperiod
{
    internal readonly record struct Sample(float Darkness, float WinterDayBlue);

    private const int Day = 24 * 60;

    internal static Sample At(string season, int dayOfMonth, int timeOfDay)
        => AtMinute(season, dayOfMonth, ToMinutes(timeOfDay));

    internal static Sample AtMinute(string season, int dayOfMonth, float minuteOfDay)
    {
        float seasonDay = Math.Clamp((dayOfMonth - 1) / 27f, 0f, 1f);
        float minute = minuteOfDay % Day;
        int lightStart;
        int lightEnd;
        float nightDepth;
        float winterDayBlue = 0f;

        switch (season)
        {
            // In spring, the last light holds later each week and the night
            // remains a readable blue hour instead of a generic black fade.
            case "spring":
                lightStart = Mix(6 * 60 + 30, 4 * 60, seasonDay);
                lightEnd = Mix(18 * 60 + 45, 22 * 60 + 15, seasonDay);
                nightDepth = Mix(.86f, .40f, seasonDay);
                break;

            // Early summer keeps a midnight glow. It gradually yields to a
            // short, cool night as the season approaches its end.
            case "summer":
                lightStart = Mix(2 * 60 + 30, 4 * 60 + 45, seasonDay);
                lightEnd = Mix(23 * 60 + 30, 20 * 60 + 45, seasonDay);
                nightDepth = Mix(.10f, .54f, SmoothStep(.48f, 1f, seasonDay));
                break;

            // The sun retreats quickly in autumn, leaving a long low dusk.
            case "fall":
                lightStart = Mix(5 * 60, 9 * 60 + 15, seasonDay);
                lightEnd = Mix(20 * 60, 14 * 60 + 45, seasonDay);
                nightDepth = Mix(.48f, .91f, seasonDay);
                break;

            // Winter uses a compressed noon twilight, with blue ambient
            // light throughout the day. The short midday twilight window closes early.
            case "winter":
                // There is no sun-above-horizon interval here: this is the
                // brief blue civil twilight around midday during polar night.
                float twilightSpan = 1f - SmoothStep(.04f, .30f, seasonDay);
                lightStart = Mix(10 * 60 + 5, 9 * 60 + 10, twilightSpan);
                lightEnd = Mix(13 * 60 + 55, 14 * 60 + 50, twilightSpan);
                winterDayBlue = Mix(.22f, .34f, SmoothStep(.04f, .78f, seasonDay));
                nightDepth = .96f;
                break;

            default:
                // Unknown seasons retain a conservative, readable twilight.
                lightStart = 6 * 60;
                lightEnd = 20 * 60;
                nightDepth = .78f;
                break;
        }

        float nocturnal = NightCurve(minute, lightStart, lightEnd, 112);
        float darkness = winterDayBlue + (nightDepth - winterDayBlue) * nocturnal;
        return new Sample(Math.Clamp(darkness, 0f, 1f), winterDayBlue);
    }

    private static float NightCurve(float minute, int lightStart, int lightEnd, int twilightMinutes)
    {
        if (minute >= lightStart && minute < lightEnd)
            return 0f;

        float elapsed = minute >= lightEnd ? minute - lightEnd : Day - lightEnd + minute;
        float duration = Day - lightEnd + lightStart;
        float dusk = SmoothStep(0f, twilightMinutes, elapsed);
        float dawn = 1f - SmoothStep(duration - twilightMinutes, duration, elapsed);
        return dusk * dawn;
    }

    private static int ToMinutes(int timeOfDay) => timeOfDay / 100 * 60 + timeOfDay % 100;
    private static int Mix(int from, int to, float amount) => (int)MathF.Round(from + (to - from) * amount);
    private static float Mix(float from, float to, float amount) => from + (to - from) * amount;

    private static float SmoothStep(float from, float to, float value)
    {
        if (to <= from) return value >= to ? 1f : 0f;
        float t = Math.Clamp((value - from) / (to - from), 0f, 1f);
        return t * t * (3f - 2f * t);
    }
}
