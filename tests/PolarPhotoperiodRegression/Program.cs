using ArcticPassage.Runtime;

int checks = 0;
void Check(bool condition, string description)
{
    if (!condition) throw new InvalidOperationException(description);
    checks++;
    Console.WriteLine("PASS " + description);
}

var springNoon = PolarPhotoperiod.At("spring", 14, 1200);
var springNight = PolarPhotoperiod.At("spring", 14, 2400);
var highSummerMidnight = PolarPhotoperiod.At("summer", 2, 2400);
var lateSummerMidnight = PolarPhotoperiod.At("summer", 27, 2400);
var winterNoon = PolarPhotoperiod.At("winter", 20, 1200);
var winterNight = PolarPhotoperiod.At("winter", 20, 2400);

Check(springNoon.Darkness < .02f, "spring noon stays fully readable");
Check(springNight.Darkness > .6f, "spring night reaches a clear blue-hour contrast");
Check(highSummerMidnight.Darkness < .15f, "early summer midnight retains polar glow");
Check(lateSummerMidnight.Darkness > highSummerMidnight.Darkness + .25f,
    "summer dusk deepens gradually through the season");
Check(winterNoon.Darkness is > .20f and < .40f && winterNoon.WinterDayBlue > .20f,
    "winter noon keeps playable blue twilight");
Check(winterNight.Darkness > winterNoon.Darkness + .45f,
    "winter night remains distinct from its dim daytime");
Check(Math.Abs(PolarPhotoperiod.At("summer", 2, 2600).Darkness
    - PolarPhotoperiod.At("summer", 2, 200).Darkness) < .001f,
    "extended 26:00 clock maps safely to the same pre-dawn light");
Check(Math.Abs(PolarPhotoperiod.AtMinute("winter", 20, 1560).Darkness
    - PolarPhotoperiod.At("winter", 20, 200).Darkness) < .001f,
    "fractional-minute model wraps the extended game clock");
Check(Math.Abs(PolarPhotoperiod.AtMinute("fall", 15, 18 * 60 + 112f).Darkness
    - PolarPhotoperiod.AtMinute("fall", 15, 18 * 60 + 112.25f).Darkness) < .003f,
    "dusk changes smoothly between rendered frames");

foreach (string season in new[] { "spring", "summer", "fall", "winter", "unknown" })
    for (int day = 1; day <= 28; day += 3)
        for (int time = 0; time <= 2600; time += 100)
        {
            var sample = PolarPhotoperiod.At(season, day, time);
            if (!float.IsFinite(sample.Darkness) || sample.Darkness is < 0 or > 1
                || !float.IsFinite(sample.WinterDayBlue) || sample.WinterDayBlue is < 0 or > 1)
                throw new InvalidOperationException($"Out-of-range sample: {season} day {day} at {time}");
            checks++;
        }

Console.WriteLine($"PASS {checks} polar-photoperiod regression checks.");
