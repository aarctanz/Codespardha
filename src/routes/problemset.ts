import { Elysia, t } from "elysia";
import { authPlugin } from "../auth";
import * as problemService from "../services/problem";
import {
  upsertApproach,
  getApproach,
  ApproachError,
} from "../services/approach";

export const problemsetRoutes = new Elysia({ prefix: "/problemset" })
  .use(authPlugin)

  // List all visible problems
  .get(
    "/",
    async ({ user }) => {
      return problemService.getVisibleProblems(user?.id ?? null);
    },
    { auth: true },
  )

  // Get problem by slug with sample test cases (e.g. 1000A)
  .get(
    "/:slug",
    async ({ params, set, user }) => {
      const problem = await problemService.getProblemBySlug(
        params.slug,
        user?.id ?? null,
      );
      if (!problem) {
        set.status = 404;
        return { error: "Problem not found" };
      }
      return problem;
    },
    {
      auth: true,
      params: t.Object({ slug: t.String() }),
    },
  )

  // Create or update approach for a problem
  .post(
    "/:slug/approach",
    async ({ user, params, body, set }) => {
      try {
        return await upsertApproach(user.id, params.slug, body.content);
      } catch (err) {
        if (err instanceof ApproachError) {
          set.status = err.statusCode;
          return { error: err.message };
        }
        set.status = 500;
        return { error: "Failed to save approach" };
      }
    },
    {
      auth: true,
      body: t.Object({ content: t.String() }),
    },
  )

  // Get own approach for a problem
  .get(
    "/:slug/approach",
    async ({ user, params, set }) => {
      const result = await getApproach(user.id, params.slug);
      if (!result) {
        set.status = 404;
        return { error: "No approach found" };
      }
      return result;
    },
    { auth: true },
  );
