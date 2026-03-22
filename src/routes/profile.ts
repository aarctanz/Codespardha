import { Elysia } from "elysia";
import { authPlugin } from "../auth";
import { getProfileStats } from "../services/profile";

export const profileRoutes = new Elysia({ prefix: "/profile" })
  .use(authPlugin)

  .get(
    "/stats",
    async ({ user }) => {
      return getProfileStats(user.id);
    },
    { auth: true }
  );
