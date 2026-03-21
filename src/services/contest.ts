import { eq, desc } from "drizzle-orm";
import { db } from "../db";
import { contest } from "../db/schema";

export async function getAllContests() {
  return db
    .select()
    .from(contest)
    .orderBy(desc(contest.contestNumber));
}

export async function getContestByNumber(contestNumber: number) {
  const [row] = await db
    .select()
    .from(contest)
    .where(eq(contest.contestNumber, contestNumber))
    .limit(1);
  return row ?? null;
}
