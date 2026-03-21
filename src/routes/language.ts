import { Elysia } from "elysia";
import * as languageService from "../services/language";

export const languageRoutes = new Elysia({ prefix: "/languages" }).get(
  "/",
  async () => {
    return languageService.getActiveLanguages();
  }
);
