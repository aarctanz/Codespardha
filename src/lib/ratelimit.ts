import { eq, and, desc } from "drizzle-orm";
import { db } from "../db";
import { submission, problem } from "../db/schema";

const SUBMIT_COOLDOWN_MS = 15_000;
const RUN_COOLDOWN_MS = 3_000;

// In-memory map for /run cooldowns: "userId:problemId" -> last run timestamp
const runTimestamps = new Map<string, number>();

// Clean up stale entries every 5 minutes
setInterval(() => {
  const cutoff = Date.now() - RUN_COOLDOWN_MS * 2;
  for (const [key, ts] of runTimestamps) {
    if (ts < cutoff) runTimestamps.delete(key);
  }
}, 5 * 60 * 1000);

export async function checkSubmitRateLimit(
  userId: string,
  slug: string
): Promise<number | null> {
  const [last] = await db
    .select({ createdAt: submission.createdAt })
    .from(submission)
    .innerJoin(problem, eq(submission.problemId, problem.id))
    .where(and(eq(submission.userId, userId), eq(problem.slug, slug)))
    .orderBy(desc(submission.createdAt))
    .limit(1);

  if (!last) return null;

  const elapsed = Date.now() - last.createdAt.getTime();
  if (elapsed < SUBMIT_COOLDOWN_MS) {
    return Math.ceil((SUBMIT_COOLDOWN_MS - elapsed) / 1000);
  }
  return null;
}

export function checkRunRateLimit(
  userId: string,
  slug: string
): number | null {
  const key = `${userId}:${slug}`;
  const lastRun = runTimestamps.get(key);

  if (!lastRun) return null;

  const elapsed = Date.now() - lastRun;
  if (elapsed < RUN_COOLDOWN_MS) {
    return Math.ceil((RUN_COOLDOWN_MS - elapsed) / 1000);
  }
  return null;
}

export function recordRun(userId: string, slug: string): void {
  runTimestamps.set(`${userId}:${slug}`, Date.now());
}
