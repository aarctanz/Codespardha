import { Elysia, t } from "elysia";
import { authPlugin } from "../auth";
import { getProfileStats, getPublicProfile } from "../services/profile";

export const profileRoutes = new Elysia({ prefix: "/profile" })
  .use(authPlugin)

  .get(
    "/stats",
    async ({ user }) => {
      return getProfileStats(user.id);
    },
    { auth: true }
  )

  .get(
    "/:rollNumber",
    async ({ params, set }) => {
      const profile = await getPublicProfile(params.rollNumber);
      if (!profile) {
        set.status = 404;
        return { error: "User not found" };
      }
      return profile;
    },
    {
      auth: true,
      params: t.Object({ rollNumber: t.String() }),
    }
  );
