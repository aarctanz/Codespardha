CREATE SEQUENCE "public"."contest_number_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1000 CACHE 1;--> statement-breakpoint
ALTER TABLE "contest" ADD COLUMN "contest_number" integer DEFAULT nextval('contest_number_seq') NOT NULL;--> statement-breakpoint
ALTER TABLE "problem" ADD COLUMN "slug" text NOT NULL;--> statement-breakpoint
ALTER TABLE "contest" ADD CONSTRAINT "contest_contest_number_unique" UNIQUE("contest_number");--> statement-breakpoint
ALTER TABLE "problem" ADD CONSTRAINT "problem_slug_unique" UNIQUE("slug");