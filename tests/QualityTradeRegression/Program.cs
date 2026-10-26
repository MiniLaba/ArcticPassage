using ArcticPassage.Runtime;

const string fish = "(O)ArcticPassage_Capelin";
int checks = 0;
void Check(bool condition, string name) { if (!condition) throw new Exception(name); checks++; Console.WriteLine("PASS " + name); }
QualityTrade.Lot[] mixed = [new(0, fish, 0, 9), new(1, fish, 4, 1), new(2, fish, 1, 1), new(3, fish, 2, 2), new(4, "(O)145", 1, 20)];
var plan = QualityTrade.Plan(mixed, fish, 2)!;
Check(plan.SequenceEqual(new[] { new QualityTrade.Take(2, 1), new QualityTrade.Take(3, 1) }), "mixed inventory preserves normal and iridium fish and consumes exactly two eligible fish");
Check(QualityTrade.Plan([new(0, fish, 0, 99), new(1, fish, 1, 1)], fish, 2) == null, "normal fish cannot fill a missing silver fish; insufficient delivery has no partial plan");
Check(QualityTrade.Plan([new(0, "(O)145", 4, 2)], fish, 2) == null, "wrong species is rejected even at iridium quality");
Check(QualityTrade.Plan([new(0, fish, 1, 0)], fish, 1) == null, "empty stacks cannot be delivered");
Check(QualityTrade.Plan(mixed, fish, 0) == null, "zero or negative order quantity is invalid");
Check(QualityTrade.Plan([], fish, 2) == null, "empty inventory is rejected");
Check(QualityTrade.Plan([new(5, fish, 4, 2)], fish, 2)!.Single() == new QualityTrade.Take(5, 2), "two iridium fish remain eligible when no lower quality exists");
Check(QualityTrade.Plan([new(3, fish, 1, 2), new(1, fish, 1, 2)], fish, 2)!.Single().Slot == 1, "equal-quality delivery is deterministic by backpack slot");
Check(mixed[0].Count == 9 && mixed[3].Count == 2, "planning does not mutate inventory");
Console.WriteLine($"{checks} quality-trade regression checks passed; this is not ordinary gameplay evidence.");
