import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { drizzle } from "drizzle-orm/postgres-js";
import { client } from "./db";
import * as schema from "./db/schema";

const db = drizzle(client, { schema });

export const auth = betterAuth({
  database: drizzleAdapter(db, {
    provider: "pg",
    schema,
  }),
  baseURL: process.env.APP_BASE_URL,
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      mapProfileToUser: (profile) => {
        return {
          rollNumber: profile.email.split("@")[0],
        };
      },
    },
  },
  user: {
    additionalFields: {
      role: {
        type: "string",
        defaultValue: "student",
        input: false,
        returned: true,
      },
      rollNumber: {
        type: "string",
        required: false,
        input: false,
        returned: true,
      },
    },
  },
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60,
    },
  },
  account: {
    accountLinking: {
      enabled: true,
      trustedProviders: ["google"],
    },
  },
});
