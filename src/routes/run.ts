import { Elysia, t } from "elysia";
import { getLogger } from "@logtape/logtape";
import { authPlugin } from "../auth";
import { runAgainstSamples, RunError } from "../services/run";
import { hasApproach } from "../services/approach";
import { checkRunRateLimit, recordRun } from "../lib/ratelimit";

const logger = getLogger(["spring", "run"]);

export const runRoutes = new Elysia().use(authPlugin).post(
  "/run",
  async ({ user, body, set }) => {
    try {
      if (!(await hasApproach(user.id, body.slug))) {
        set.status = 403;
        return { error: "Submit your approach before running code" };
      }
      const wait = checkRunRateLimit(user.id, body.slug);
      if (wait !== null) {
        set.status = 429;
        return { error: `Too many runs. Try again in ${wait}s` };
      }
      recordRun(user.id, body.slug);
      return await runAgainstSamples(
        body.slug,
        body.engineLanguageId,
        body.sourceCode
      );
    } catch (err) {
      if (err instanceof RunError) {
        set.status = err.statusCode;
        return { error: err.message };
      }
      const msg = err instanceof Error ? err.message : "Unknown error";
      logger.error`/run failed: ${msg}`;
      set.status = 500;
      return { error: "Code execution failed. Please try again." };
    }
  },
  {
    auth: true,
    body: t.Object({
      slug: t.String(),
      engineLanguageId: t.Number(),
      sourceCode: t.String(),
    }),
  }
);
