import { eq } from "drizzle-orm";
import { db } from "../db";
import { language } from "../db/schema";

export async function getActiveLanguages() {
  return db
    .select({
      engineLanguageId: language.engineLanguageId,
      name: language.name,
      version: language.version,
    })
    .from(language)
    .where(eq(language.isActive, true))
    .orderBy(language.name);
}
