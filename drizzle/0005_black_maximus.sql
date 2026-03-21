CREATE TYPE "public"."submission_status" AS ENUM('pending', 'compiling', 'running', 'accepted', 'wrong_answer', 'time_limit_exceeded', 'runtime_error', 'compilation_error', 'internal_error');--> statement-breakpoint
CREATE TABLE "submission" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" text NOT NULL,
	"problem_id" uuid NOT NULL,
	"engine_language_id" integer NOT NULL,
	"source_code" text NOT NULL,
	"exec0_id" integer,
	"status" "submission_status" DEFAULT 'pending' NOT NULL,
	"score" integer DEFAULT 0 NOT NULL,
	"time_sec" real,
	"memory_kb" integer,
	"compile_output" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "submission_test_result" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"submission_id" uuid NOT NULL,
	"position" integer NOT NULL,
	"status" "submission_status" DEFAULT 'pending' NOT NULL,
	"time_sec" real,
	"memory_kb" integer,
	"stdout" text,
	"stderr" text,
	"exit_code" integer
);
--> statement-breakpoint
ALTER TABLE "submission" ADD CONSTRAINT "submission_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "submission" ADD CONSTRAINT "submission_problem_id_problem_id_fk" FOREIGN KEY ("problem_id") REFERENCES "public"."problem"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "submission_test_result" ADD CONSTRAINT "submission_test_result_submission_id_submission_id_fk" FOREIGN KEY ("submission_id") REFERENCES "public"."submission"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "submission_user_id_idx" ON "submission" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX "submission_problem_id_idx" ON "submission" USING btree ("problem_id");--> statement-breakpoint
CREATE INDEX "submission_test_result_submission_id_idx" ON "submission_test_result" USING btree ("submission_id");