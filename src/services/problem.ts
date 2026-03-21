import { eq, lte, desc, asc, and } from "drizzle-orm";
import { db } from "../db";
import { problem, testCase } from "../db/schema";

export async function getVisibleProblems() {
  return db
    .select()
    .from(problem)
    .where(lte(problem.visibleFrom, new Date()))
    .orderBy(desc(problem.createdAt));
}

export async function getProblemBySlug(slug: string) {
  const [row] = await db
    .select()
    .from(problem)
    .where(eq(problem.slug, slug))
    .limit(1);
  if (!row) return null;

  // Only visible if visibleFrom has passed
  if (row.visibleFrom && row.visibleFrom > new Date()) return null;

  const sampleTestCases = await db
    .select()
    .from(testCase)
    .where(
      and(eq(testCase.problemId, row.id), eq(testCase.isSample, true))
    )
    .orderBy(asc(testCase.order));

  return { ...row, testCases: sampleTestCases };
}

export async function getProblemsByContest(contestId: string) {
  return db
    .select()
    .from(problem)
    .where(eq(problem.contestId, contestId))
    .orderBy(problem.label);
}
