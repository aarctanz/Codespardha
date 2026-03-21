import { Elysia, t } from "elysia";
import { createSubmission, SubmitError } from "../services/submit";

export const submitRoutes = new Elysia().post(
  "/submit",
  async ({ body, user, set }) => {
    try {
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
