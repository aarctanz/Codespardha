import { Elysia, t } from "elysia";
import { authPlugin } from "../auth";
import { createSubmission, SubmitError } from "../services/submit";
import { hasApproach } from "../services/approach";
import { checkSubmitRateLimit } from "../lib/ratelimit";

export const submitRoutes = new Elysia().use(authPlugin).post(
  "/submit",
  async ({ body, user, set }) => {
    try {
      if (!(await hasApproach(user.id, body.slug))) {
        set.status = 403;
        return { error: "Submit your approach before submitting code" };
      }
      const wait = await checkSubmitRateLimit(user.id, body.slug);
      if (wait !== null) {
        set.status = 429;
        return { error: `Too many submissions. Try again in ${wait}s` };
      }
      const submissionId = await createSubmission(
        user.id,
        body.slug,
        body.engineLanguageId,
        body.sourceCode
      );
      return { submissionId };
    } catch (err) {
      if (err instanceof SubmitError) {
        set.status = err.statusCode;
        return { error: err.message };
      }
      set.status = 500;
      return { error: "Submission failed. Please try again." };
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
