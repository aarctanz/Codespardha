import { Elysia } from "elysia";
import { connect, client } from "./db";

try {
  await connect();
} catch (err) {
  console.error(
    "[spring] failed to connect to database:",
    err instanceof Error ? err.message : err
  );
  await client.end();
  process.exit(1);
}

const app = new Elysia().get("/", () => "Hello Elysia").listen(3000);

console.log(
  `[spring] server running at ${app.server?.hostname}:${app.server?.port}`
);
