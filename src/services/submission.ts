import { eq, and, desc, asc, count, sql } from "drizzle-orm";
import { db } from "../db";
import { submission, submissionTestResult, problem, language, testCase, contest } from "../db/schema";

const DEFAULT_PAGE_SIZE = 20;

export async function getUserSubmissions(userId: string, page: number = 1, pageSize: number = DEFAULT_PAGE_SIZE) {
  const offset = (page - 1) * pageSize;

  const [items, [{ total }]] = await Promise.all([
    db
      .select({
        id: submission.id,
        slug: problem.slug,
        problemTitle: problem.title,
        languageName: language.name,
        engineLanguageId: submission.engineLanguageId,
        status: submission.status,
        score: submission.score,
        timeSec: submission.timeSec,
        memoryKb: submission.memoryKb,
        createdAt: submission.createdAt,
      })
      .from(submission)
      .innerJoin(problem, eq(submission.problemId, problem.id))
      .innerJoin(
        language,
        eq(submission.engineLanguageId, language.engineLanguageId)
      )
      .where(eq(submission.userId, userId))
      .orderBy(desc(submission.createdAt))
      .limit(pageSize)
      .offset(offset),
    db
      .select({ total: count() })
      .from(submission)
      .where(eq(submission.userId, userId)),
  ]);

  return {
    items,
    page,
    pageSize,
    total,
    totalPages: Math.ceil(total / pageSize),
  };
}

export async function getSubmissionById(submissionId: string, userId: string) {
  const [sub] = await db
    .select({
      id: submission.id,
      userId: submission.userId,
      problemId: submission.problemId,
      contestId: submission.contestId,
      slug: problem.slug,
      problemTitle: problem.title,
      languageName: language.name,
      engineLanguageId: submission.engineLanguageId,
      sourceCode: submission.sourceCode,
      status: submission.status,
      score: submission.score,
      timeSec: submission.timeSec,
      memoryKb: submission.memoryKb,
      compileOutput: submission.compileOutput,
      createdAt: submission.createdAt,
    })
    .from(submission)
    .innerJoin(problem, eq(submission.problemId, problem.id))
    .innerJoin(
      language,
      eq(submission.engineLanguageId, language.engineLanguageId)
    )
    .where(and(eq(submission.id, submissionId), eq(submission.userId, userId)))
    .limit(1);

  if (!sub) return null;

  // Check if contest is still active
  let contestActive = false;
  if (sub.contestId) {
    const [c] = await db
      .select({ endTime: contest.endTime })
      .from(contest)
      .where(eq(contest.id, sub.contestId))
      .limit(1);
    if (c && new Date() < c.endTime) contestActive = true;
  }

  const testResults = await db
    .select({
      position: submissionTestResult.position,
      status: submissionTestResult.status,
      timeSec: submissionTestResult.timeSec,
      memoryKb: submissionTestResult.memoryKb,
      stdout: submissionTestResult.stdout,
      stderr: submissionTestResult.stderr,
      exitCode: submissionTestResult.exitCode,
      stdin: testCase.input,
      expectedOutput: testCase.expectedOutput,
    })
    .from(submissionTestResult)
    .innerJoin(
      testCase,
      and(
        eq(testCase.problemId, sub.problemId),
        eq(testCase.order, sql`${submissionTestResult.position} - 1`)
      )
    )
    .where(eq(submissionTestResult.submissionId, submissionId))
    .orderBy(asc(submissionTestResult.position));

  const { userId: _, problemId: __, contestId: ___, ...rest } = sub;

  if (contestActive) {
    return {
      ...rest,
      testResults: testResults.map((tr) => ({
        position: tr.position,
        status: tr.status,
      })),
    };
  }

  return { ...rest, testResults };
}
