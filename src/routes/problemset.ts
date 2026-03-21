import { Elysia, t } from "elysia";
import * as problemService from "../services/problem";

export const problemsetRoutes = new Elysia({ prefix: "/problemset" })

  // List all visible problems
  .get("/", async () => {
    return problemService.getVisibleProblems();
  })

  // Get problem by slug with sample test cases (e.g. 1000A)
  .get(
    "/:slug",
    async ({ params, set }) => {
      const problem = await problemService.getProblemBySlug(params.slug);
      if (!problem) {
        set.status = 404;
        return { error: "Problem not found" };
      }
      return problem;
    },
    {
      params: t.Object({ slug: t.String() }),
    }
  );
