namespace ArcticPassage.Runtime;

/// <summary>Build the entire deduction before touching a backpack.</summary>
internal static class QualityTrade
{
    internal readonly record struct Lot(int Slot, string Id, int Quality, int Count);
    internal readonly record struct Take(int Slot, int Count);

    internal static IReadOnlyList<Take>? Plan(IEnumerable<Lot> inventory, string id, int count)
    {
        if (count <= 0) return null;
        var result = new List<Take>();
        foreach (var lot in inventory.Where(i => i.Id == id && i.Quality >= 1 && i.Count > 0)
                     .OrderBy(i => i.Quality).ThenBy(i => i.Slot))
        {
            int take = Math.Min(count, lot.Count);
            result.Add(new(lot.Slot, take));
            count -= take;
            if (count == 0) return result;
        }
        return null;
    }
}
