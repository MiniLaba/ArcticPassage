namespace ArcticPassage.Runtime;

/// <summary>Three courses of a small teaching model, not a structural simulation.</summary>
internal sealed class SnowBlockPattern
{
    internal const int Courses = 3;
    internal int Placed { get; private set; }
    internal int Offset { get; private set; }
    internal bool Complete => Placed == Courses;
    internal void Shift() { if (!Complete) Offset = 1 - Offset; }
    internal bool Place()
    {
        if (Complete || Offset != (Placed + 1) % 2) return false;
        Placed++;
        Offset = Placed % 2;
        return true;
    }
}
