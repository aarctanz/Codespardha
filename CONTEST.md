# Creating a Contest

## Directory Structure

Create a directory with the following files:

```
my-contest/
├── contest.json      # Contest metadata
├── a.json            # Problem A
├── b.json            # Problem B
├── c.json            # Problem C (optional)
└── ...               # Add as many problems as needed
```

Format files are available in `contest-format/` for reference.

---

## contest.json

```json
{
  "title": "Spring Contest #2",
  "description": "Optional description in plain text.",
  "startTime": "2026-04-01T10:00:00Z",
  "durationMinutes": 180
}
```

| Field             | Type   | Required | Description                        |
|-------------------|--------|----------|------------------------------------|
| `title`           | string | yes      | Contest title                      |
| `description`     | string | no       | Short description                  |
| `startTime`       | string | yes      | ISO 8601 UTC datetime              |
| `durationMinutes` | number | yes      | Contest duration in minutes        |

---

## {problem}.json

Name files `a.json`, `b.json`, `c.json`, etc. They are sorted alphabetically and assigned labels A, B, C automatically.

```json
{
  "title": "Problem Title",
  "description": "Full problem statement in **markdown**.\n\n## Input\nFirst line contains integer $n$.\n\n## Output\nPrint YES or NO.",
  "difficulty": 3,
  "score": 500,
  "timeLimitMs": 1000,
  "memoryLimitMb": 256,
  "tags": ["math", "greedy"],
  "publicTests": [
    { "input": "5\n", "output": "YES\n" },
    { "input": "3\n", "output": "NO\n" }
  ],
  "privateTests": [
    { "input": "100\n", "output": "YES\n" },
    { "input": "7\n", "output": "NO\n" }
  ]
}
```

| Field           | Type     | Required | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| `title`         | string   | yes      | Problem title                                    |
| `description`   | string   | yes      | Full statement in markdown, supports LaTeX `$x$` |
| `difficulty`    | number   | yes      | 1–4 easy, 5–8 medium, 9–10 hard                  |
| `score`         | number   | yes      | Points awarded on AC (e.g. 500, 1000, 1500)      |
| `timeLimitMs`   | number   | no       | Time limit in ms (default: 1000)                 |
| `memoryLimitMb` | number   | no       | Memory limit in MB (default: 256)                |
| `tags`          | string[] | no       | Topic tags                                       |
| `publicTests`   | array    | yes      | Sample test cases shown to students              |
| `privateTests`  | array    | yes      | Hidden test cases used for judging               |

---

## Running the Script

### Locally (with Docker)

```bash
# Copy contest directory into the container
docker cp ./my-contest spring-spring-1:/tmp/my-contest

# Run the script
docker exec spring-spring-1 bun run /app/src/db/create-contest.ts /tmp/my-contest
```

### On the server

Same commands — SSH in and run them.

---

## Notes

- Problems are ordered alphabetically by filename (`a.json` → A, `b.json` → B, etc.)
- `startTime` is in UTC. Convert from IST by subtracting 5:30 (e.g. 3:30 PM IST = 10:00 UTC)
- Students can see problems only after `startTime`
- Wrong attempt penalty is **50 points** per wrong submission before first AC
- Leaderboard is generated automatically on first request after contest ends
- The script will fail if the database is unreachable or a problem file is malformed
