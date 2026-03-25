import { eq, sql, count } from "drizzle-orm";
import { db } from "../db";
import { user, userProblemSolved, problem, submission } from "../db/schema";

export async function getPublicProfile(rollNumber: string) {
  const [row] = await db
    .select({
      id: user.id,
      name: user.name,
      image: user.image,
      rollNumber: user.rollNumber,
    })
    .from(user)
    .where(eq(user.rollNumber, rollNumber))
    .limit(1);

  if (!row) return null;

  const stats = await getProfileStats(row.id);
  return { name: row.name, image: row.image, rollNumber: row.rollNumber, ...stats };
}

export async function getProfileStats(userId: string) {
  const rows = await db
    .select({
      difficulty: problem.difficulty,
      count: count(),
    })
    .from(userProblemSolved)
    .innerJoin(problem, eq(userProblemSolved.problemId, problem.id))
    .where(eq(userProblemSolved.userId, userId))
    .groupBy(problem.difficulty);

  const stats = { easy: 0, medium: 0, hard: 0, total: 0 };

  for (const row of rows) {
    const d = row.difficulty;
    if (d === null || d <= 4) stats.easy += row.count;
    else if (d <= 8) stats.medium += row.count;
    else stats.hard += row.count;
  }
  stats.total = stats.easy + stats.medium + stats.hard;

  // Total problems available per difficulty
  const totalRows = await db
    .select({
      difficulty: problem.difficulty,
      count: count(),
    })
    .from(problem)
    .groupBy(problem.difficulty);

  const totalProblems = { easy: 0, medium: 0, hard: 0, total: 0 };
  for (const row of totalRows) {
    const d = row.difficulty;
    if (d === null || d <= 4) totalProblems.easy += row.count;
    else if (d <= 8) totalProblems.medium += row.count;
    else totalProblems.hard += row.count;
  }
  totalProblems.total = totalProblems.easy + totalProblems.medium + totalProblems.hard;

  // Acceptance rate
  const [{ totalSubmissions, acceptedSubmissions }] = await db
    .select({
      totalSubmissions: count(),
      acceptedSubmissions: count(
        sql`CASE WHEN ${submission.status} = 'accepted' THEN 1 END`
      ),
    })
    .from(submission)
    .where(eq(submission.userId, userId));

  return {
    solved: stats,
    total: totalProblems,
    submissions: totalSubmissions,
    accepted: acceptedSubmissions,
    acceptanceRate: totalSubmissions > 0
      ? Math.round((acceptedSubmissions / totalSubmissions) * 10000) / 100
      : 0,
  };
}
