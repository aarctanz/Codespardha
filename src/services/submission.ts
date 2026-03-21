import { eq, and, desc, asc } from "drizzle-orm";
import { db } from "../db";
import { submission, submissionTestResult, problem, language } from "../db/schema";

export async function getUserSubmissions(userId: string) {
  return db
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
    .orderBy(desc(submission.createdAt));
}

export async function getSubmissionById(submissionId: string, userId: string) {
  const [sub] = await db
    .select({
      id: submission.id,
      userId: submission.userId,
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

  const testResults = await db
    .select({
      position: submissionTestResult.position,
      status: submissionTestResult.status,
      timeSec: submissionTestResult.timeSec,
      memoryKb: submissionTestResult.memoryKb,
      stdout: submissionTestResult.stdout,
      stderr: submissionTestResult.stderr,
      exitCode: submissionTestResult.exitCode,
    })
    .from(submissionTestResult)
    .where(eq(submissionTestResult.submissionId, submissionId))
    .orderBy(asc(submissionTestResult.position));

  const { userId: _, ...rest } = sub;
  return { ...rest, testResults };
}
