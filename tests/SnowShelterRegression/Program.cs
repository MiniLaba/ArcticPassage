using ArcticPassage.Runtime;

int checks = 0;
void Check(bool condition, string message)
{
    if (!condition) throw new Exception(message);
    checks++;
    Console.WriteLine("PASS " + message);
}
var lesson = new SnowBlockPattern();
Check(!lesson.Complete && lesson.Placed == 0, "opening a lesson grants no completion");
for (int row = 0; row < SnowBlockPattern.Courses; row++)
{
    Check(!lesson.Place() && lesson.Placed == row, "aligned seams cannot advance course " + row);
    lesson.Shift(); lesson.Shift();
    Check(!lesson.Place() && lesson.Placed == row, "two shifts return to the same unplaced arrangement " + row);
    lesson.Shift();
    Check(lesson.Place() && lesson.Placed == row + 1, "offset seams place exactly one course " + row);
    Check(lesson.Complete == (row == SnowBlockPattern.Courses - 1), "completion requires the entire model " + row);
}
int finalOffset = lesson.Offset;
lesson.Shift();
Check(!lesson.Place() && lesson.Placed == SnowBlockPattern.Courses && lesson.Offset == finalOffset,
    "repeated confirm/shift cannot advance or mutate a finished model");
var cancelled = new SnowBlockPattern(); cancelled.Shift(); cancelled.Place();
var reopened = new SnowBlockPattern();
Check(!reopened.Complete && reopened.Placed == 0, "abandoning an incomplete model does not carry unearned completion into a new session");
Console.WriteLine($"PASS {checks} model regressions. No game UI, winter unlock, multiplayer or save/reload claim.");
