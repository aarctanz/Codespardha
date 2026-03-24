import { eq, and } from "drizzle-orm";
import { db } from "../db";
import { approach, problem } from "../db/schema";

export async function upsertApproach(
  userId: string,
  slug: string,
  content: string
) {
  const [prob] = await db
    .select({ id: problem.id })
    .from(problem)
    .where(eq(problem.slug, slug))
    .limit(1);

  if (!prob) throw new ApproachError("Problem not found", 404);

  const [result] = await db
    .insert(approach)
    .values({ userId, problemId: prob.id, content })
    .onConflictDoUpdate({
      target: [approach.userId, approach.problemId],
      set: { content, updatedAt: new Date() },
    })
    .returning({
      id: approach.id,
      content: approach.content,
      createdAt: approach.createdAt,
      updatedAt: approach.updatedAt,
    });

  return result;
}

export async function getApproach(userId: string, slug: string) {
  const rows = await db
    .select({
      id: approach.id,
      content: approach.content,
      createdAt: approach.createdAt,
      updatedAt: approach.updatedAt,
    })
    .from(approach)
    .innerJoin(problem, eq(approach.problemId, problem.id))
    .where(and(eq(approach.userId, userId), eq(problem.slug, slug)))
    .limit(1);

  return rows[0] ?? null;
}

export async function hasApproach(userId: string, slug: string): Promise<boolean> {
  const rows = await db
    .select({ id: approach.id })
    .from(approach)
    .innerJoin(problem, eq(approach.problemId, problem.id))
    .where(and(eq(approach.userId, userId), eq(problem.slug, slug)))
    .limit(1);
  

  return rows.length > 0;
}

export class ApproachError extends Error {
  constructor(
    message: string,
    public statusCode: number
  ) {
    super(message);
  }
}
