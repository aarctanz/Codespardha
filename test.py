"""
Benchmark suite for /run and /submit endpoints.

Usage:
    python test.py <session_cookie>          # run all benchmarks
    python test.py <session_cookie> warmup   # warmup only
    python test.py <session_cookie> steady   # steady-state only
    python test.py <session_cookie> step     # step-load only
    python test.py <session_cookie> saturate # saturation only

Get your session cookie from browser DevTools → Application → Cookies →
better-auth.session_token
"""

import asyncio
import aiohttp
import time
import json
import math
import random
import sys
from dataclasses import dataclass, field
from typing import Optional

BASE = "http://localhost:3001"
SESSION_COOKIE_NAME = "better-auth.session_token"

SESSION_TOKEN = sys.argv[1] if len(sys.argv) > 1 else None
PHASE = sys.argv[2] if len(sys.argv) > 2 else "all"

if not SESSION_TOKEN:
    print("Usage: python test.py <session_cookie> [phase]")
    print("Phases: all, warmup, steady, step, saturate")
    print("\nGet your session cookie from browser DevTools → Application → Cookies")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════
# Test corpus — fixed, realistic payloads grouped by category
# ═══════════════════════════════════════════════════════════════════

def build_corpus(slugs: list[str]) -> dict[str, list[dict]]:
    """Build fixed corpus of test payloads grouped by category."""

    slug = slugs[0] if slugs else "1000A"
    slug2 = slugs[1] if len(slugs) > 1 else slug

    corpus = {}

    # ── Tiny interpreted (Python) ─────────────────────────────────
    corpus["tiny_python"] = [
        {"slug": slug, "engineLanguageId": 3, "sourceCode": (
            "t = int(input())\n"
            "for _ in range(t):\n"
            "    n = int(input())\n"
            "    s = input()\n"
            "    print(min(n // 11, s.count('8')))\n"
        )},
        {"slug": slug, "engineLanguageId": 3, "sourceCode": (
            "t = int(input())\n"
            "for _ in range(t):\n"
            "    print(input()[::-1])\n"
        )},
        {"slug": slug2, "engineLanguageId": 3, "sourceCode": (
            "import sys\ninput = sys.stdin.readline\n"
            "t = int(input())\n"
            "for _ in range(t):\n"
            "    n, x, y = map(int, input().split())\n"
            "    need = math.ceil(n * y / 100)\n"
            "    print(max(0, need - x))\n"
            "import math\n"
        )},
        {"slug": slug, "engineLanguageId": 3, "sourceCode": (
            "for _ in range(int(input())):\n"
            "    n = int(input())\n"
            "    s = input()\n"
            "    print(s.count('8') if n >= 11 else 0)\n"
        )},
    ]

    # ── Tiny compiled (C++) ───────────────────────────────────────
    corpus["tiny_cpp"] = [
        {"slug": slug, "engineLanguageId": 1, "sourceCode": (
            "#include <iostream>\n#include <string>\nusing namespace std;\n"
            "int main(){\n"
            "    int t; cin>>t;\n"
            "    while(t--){\n"
            "        int n; cin>>n;\n"
            "        string s; cin>>s;\n"
            "        int e=0; for(char c:s) if(c=='8') e++;\n"
            "        cout<<min(n/11,e)<<'\\n';\n"
            "    }\n"
            "}\n"
        )},
        {"slug": slug, "engineLanguageId": 1, "sourceCode": (
            "#include <iostream>\nusing namespace std;\n"
            "int main(){\n"
            "    int t; cin>>t;\n"
            "    while(t--){\n"
            "        int n; cin>>n;\n"
            "        string s; cin>>s;\n"
            "        cout<<n/11<<'\\n';\n"
            "    }\n"
            "}\n"
        )},
        {"slug": slug2, "engineLanguageId": 1, "sourceCode": (
            "#include <iostream>\n#include <cmath>\nusing namespace std;\n"
            "int main(){\n"
            "    int t; cin>>t;\n"
            "    while(t--){\n"
            "        long long n,x,y; cin>>n>>x>>y;\n"
            "        long long need=(n*y+99)/100;\n"
            "        cout<<max(0LL,need-x)<<'\\n';\n"
            "    }\n"
            "}\n"
        )},
        {"slug": slug, "engineLanguageId": 1, "sourceCode": (
            "#include <iostream>\n#include <algorithm>\nusing namespace std;\n"
            "int main(){\n"
            "    int t; cin>>t;\n"
            "    while(t--){\n"
            "        int n; cin>>n;\n"
            "        string s; cin>>s;\n"
            "        int cnt=count(s.begin(),s.end(),'8');\n"
            "        cout<<min(n/11,cnt)<<endl;\n"
            "    }\n"
            "}\n"
        )},
    ]

    # ── Medium CPU-bound (sorting, graph-like) ────────────────────
    corpus["medium_cpu"] = [
        # Python — sort a large generated list
        {"slug": slug, "engineLanguageId": 3, "sourceCode": (
            "import random\n"
            "random.seed(42)\n"
            "a = [random.randint(0, 10**9) for _ in range(500000)]\n"
            "a.sort()\n"
            "t = int(input())\n"
            "for _ in range(t):\n"
            "    n = int(input())\n"
            "    s = input()\n"
            "    print(min(n // 11, s.count('8')))\n"
        )},
        # C++ — sort + binary search
        {"slug": slug, "engineLanguageId": 1, "sourceCode": (
            "#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n"
            "int main(){\n"
            "    vector<int> v(500000);\n"
            "    for(int i=0;i<500000;i++) v[i]=i*7%1000003;\n"
            "    sort(v.begin(),v.end());\n"
            "    int t; cin>>t;\n"
            "    while(t--){\n"
            "        int n; cin>>n;\n"
            "        string s; cin>>s;\n"
            "        int e=0; for(char c:s) if(c=='8') e++;\n"
            "        cout<<min(n/11,e)<<'\\n';\n"
            "    }\n"
            "}\n"
        )},
        # Java — array fill + sort
        {"slug": slug, "engineLanguageId": 2, "sourceCode": (
            "import java.util.*;\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        int[] a = new int[500000];\n"
            "        for (int i = 0; i < a.length; i++) a[i] = i * 7 % 1000003;\n"
            "        Arrays.sort(a);\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int t = sc.nextInt();\n"
            "        while (t-- > 0) {\n"
            "            int n = sc.nextInt();\n"
            "            String s = sc.next();\n"
            "            int e = 0;\n"
            "            for (char c : s.toCharArray()) if (c == '8') e++;\n"
            "            System.out.println(Math.min(n / 11, e));\n"
            "        }\n"
            "    }\n"
            "}\n"
        )},
    ]

    # ── Memory-heavy ──────────────────────────────────────────────
    corpus["memory_heavy"] = [
        # Python — allocate large list
        {"slug": slug, "engineLanguageId": 3, "sourceCode": (
            "a = [0] * (50 * 10**6)\n"
            "a[0] = 1\n"
            "t = int(input())\n"
            "for _ in range(t):\n"
            "    n = int(input())\n"
            "    s = input()\n"
            "    print(min(n // 11, s.count('8')))\n"
        )},
        # C++ — allocate large vector
        {"slug": slug, "engineLanguageId": 1, "sourceCode": (
            "#include <iostream>\n#include <vector>\nusing namespace std;\n"
            "int main(){\n"
            "    vector<int> v(50000000, 0);\n"
            "    v[0]=1;\n"
            "    int t; cin>>t;\n"
            "    while(t--){\n"
            "        int n; cin>>n;\n"
            "        string s; cin>>s;\n"
            "        int e=0; for(char c:s) if(c=='8') e++;\n"
            "        cout<<min(n/11,e)<<'\\n';\n"
            "    }\n"
            "}\n"
        )},
        # Python — OOM (should get runtime_error / memory_limit)
        {"slug": slug, "engineLanguageId": 3, "sourceCode": (
            "x = [0] * (10**9)\nprint(len(x))\n"
        )},
    ]

    # ── Bad cases (errors) ────────────────────────────────────────
    corpus["bad_cases"] = [
        # TLE — Python infinite loop
        {"slug": slug, "engineLanguageId": 3, "sourceCode": "while True: pass\n"},
        # TLE — C++ infinite loop
        {"slug": slug, "engineLanguageId": 1, "sourceCode": (
            "#include <iostream>\nint main(){while(true);}\n"
        )},
        # RE — Python exception
        {"slug": slug, "engineLanguageId": 3, "sourceCode": "raise RuntimeError('boom')\n"},
        # RE — C++ segfault
        {"slug": slug, "engineLanguageId": 1, "sourceCode": (
            "#include <iostream>\nint main(){int*p=nullptr;*p=42;}\n"
        )},
        # WA — wrong output
        {"slug": slug, "engineLanguageId": 3, "sourceCode": "print('wrong answer')\n"},
        {"slug": slug, "engineLanguageId": 1, "sourceCode": (
            "#include <iostream>\nint main(){std::cout<<\"wrong\";}\n"
        )},
        # CE — Python syntax error
        {"slug": slug, "engineLanguageId": 3, "sourceCode": "def func(\n"},
        # CE — C++ compile error
        {"slug": slug, "engineLanguageId": 1, "sourceCode": (
            "int main(){undeclared_variable = 42;}\n"
        )},
        # CE — Java bad class
        {"slug": slug, "engineLanguageId": 2, "sourceCode": (
            "public class Wrong { public static void main(String[] a) { x(); } }\n"
        )},
        # Empty source
        {"slug": slug, "engineLanguageId": 3, "sourceCode": ""},
        {"slug": slug, "engineLanguageId": 1, "sourceCode": ""},
    ]

    return corpus


# ═══════════════════════════════════════════════════════════════════
# Stats collection
# ═══════════════════════════════════════════════════════════════════

@dataclass
class Stats:
    total: int = 0
    success: int = 0
    failed: int = 0
    errors: list = field(default_factory=list)
    latencies: list = field(default_factory=list)
    statuses: dict = field(default_factory=dict)

    def record(self, elapsed_ms: float, status_key: str, is_error: bool = False, error_msg: str = ""):
        self.total += 1
        self.latencies.append(elapsed_ms)
        self.statuses[status_key] = self.statuses.get(status_key, 0) + 1
        if is_error:
            self.failed += 1
            if error_msg:
                self.errors.append(error_msg)
        else:
            self.success += 1

    def merge(self, other: "Stats"):
        self.total += other.total
        self.success += other.success
        self.failed += other.failed
        self.errors.extend(other.errors)
        self.latencies.extend(other.latencies)
        for k, v in other.statuses.items():
            self.statuses[k] = self.statuses.get(k, 0) + v


def percentile(sorted_lats: list[float], p: float) -> float:
    if not sorted_lats:
        return 0.0
    idx = min(int(len(sorted_lats) * p), len(sorted_lats) - 1)
    return sorted_lats[idx]


def print_stats(label: str, stats: Stats, wall_time: float):
    print(f"\n  {'─' * 50}")
    print(f"  {label}")
    print(f"  Total: {stats.total} | OK: {stats.success} | Fail: {stats.failed}")
    print(f"  Wall: {wall_time:.1f}s", end="")
    if wall_time > 0:
        print(f" | Throughput: {stats.total / wall_time:.1f} req/s", end="")
    print()

    if stats.latencies:
        lats = sorted(stats.latencies)
        print(
            f"  Latency — min: {lats[0]:.0f}ms  p50: {percentile(lats, 0.50):.0f}ms  "
            f"p95: {percentile(lats, 0.95):.0f}ms  p99: {percentile(lats, 0.99):.0f}ms  "
            f"max: {lats[-1]:.0f}ms"
        )

    if stats.statuses:
        print(f"  Statuses: {json.dumps(stats.statuses, sort_keys=True)}")

    if stats.errors:
        print(f"  Errors ({len(stats.errors)}):")
        for e in stats.errors[:5]:
            print(f"    {e}")
    print(f"  {'─' * 50}")


# ═══════════════════════════════════════════════════════════════════
# Request helpers
# ═══════════════════════════════════════════════════════════════════

def make_cookie_jar():
    jar = aiohttp.CookieJar()
    from yarl import URL
    from http.cookies import SimpleCookie
    c = SimpleCookie()
    c[SESSION_COOKIE_NAME] = SESSION_TOKEN
    c[SESSION_COOKIE_NAME]["path"] = "/"
    jar.update_cookies(c, URL(BASE))
    return jar


async def do_run(session: aiohttp.ClientSession, payload: dict, stats: Stats):
    start = time.monotonic()
    try:
        async with session.post(f"{BASE}/run", json=payload) as resp:
            body = await resp.json()
            elapsed = (time.monotonic() - start) * 1000
            status_key = body.get("status", body.get("error", f"http_{resp.status}"))
            stats.record(elapsed, status_key, is_error=resp.status >= 500,
                         error_msg=f"[run] {resp.status}: {body}" if resp.status >= 500 else "")
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        stats.record(elapsed, "exception", is_error=True, error_msg=f"[run] {e}")


async def do_submit(session: aiohttp.ClientSession, payload: dict, stats: Stats) -> Optional[str]:
    start = time.monotonic()
    try:
        async with session.post(f"{BASE}/submit", json=payload) as resp:
            body = await resp.json()
            elapsed = (time.monotonic() - start) * 1000
            if resp.status == 200 and "submissionId" in body:
                stats.record(elapsed, "created")
                return body["submissionId"]
            elif resp.status < 500:
                stats.record(elapsed, body.get("error", f"http_{resp.status}"))
            else:
                stats.record(elapsed, f"http_{resp.status}", is_error=True,
                             error_msg=f"[submit] {resp.status}: {body}")
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        stats.record(elapsed, "exception", is_error=True, error_msg=f"[submit] {e}")
    return None


async def send_at_rate(
    session: aiohttp.ClientSession,
    payloads: list[dict],
    endpoint: str,
    rps: float,
    duration_sec: float,
    stats: Stats,
):
    """Send requests at a target rate for a given duration."""
    interval = 1.0 / rps
    end_time = time.monotonic() + duration_sec
    tasks = []
    idx = 0

    while time.monotonic() < end_time:
        payload = payloads[idx % len(payloads)]
        idx += 1
        if endpoint == "run":
            tasks.append(asyncio.create_task(do_run(session, payload, stats)))
        else:
            tasks.append(asyncio.create_task(do_submit(session, payload, stats)))
        await asyncio.sleep(interval)

    if tasks:
        await asyncio.gather(*tasks)


def pick_payloads(corpus: dict, count: int) -> list[dict]:
    """Pick `count` payloads round-robin across all corpus groups."""
    all_payloads = []
    for group in corpus.values():
        all_payloads.extend(group)
    result = []
    for i in range(count):
        result.append(all_payloads[i % len(all_payloads)])
    random.shuffle(result)
    return result


def pick_payloads_from(corpus: dict, groups: list[str], count: int) -> list[dict]:
    """Pick payloads from specific corpus groups."""
    pool = []
    for g in groups:
        pool.extend(corpus.get(g, []))
    if not pool:
        pool = pick_payloads(corpus, count)
    result = [pool[i % len(pool)] for i in range(count)]
    random.shuffle(result)
    return result


# ═══════════════════════════════════════════════════════════════════
# Benchmark phases
# ═══════════════════════════════════════════════════════════════════

async def phase_warmup(session: aiohttp.ClientSession, corpus: dict):
    """1-minute warm-up at low rate to prime caches, JIT, connections."""
    print("\n" + "=" * 70)
    print("PHASE: WARM-UP (1 min at 2 req/s)")
    print("=" * 70)

    stats = Stats()
    payloads = pick_payloads(corpus, 200)
    start = time.monotonic()
    await send_at_rate(session, payloads, "run", rps=2, duration_sec=60, stats=stats)
    print_stats("Warm-up", stats, time.monotonic() - start)
    return stats


async def phase_steady(session: aiohttp.ClientSession, corpus: dict):
    """5-minute steady load per group at moderate rate."""
    print("\n" + "=" * 70)
    print("PHASE: STEADY-STATE (5 min per group at 5 req/s)")
    print("=" * 70)

    groups = ["tiny_python", "tiny_cpp", "medium_cpu", "memory_heavy", "bad_cases"]
    all_stats = Stats()

    for group in groups:
        print(f"\n  ▶ Group: {group}")
        stats = Stats()
        payloads = corpus.get(group, pick_payloads(corpus, 50))
        start = time.monotonic()
        await send_at_rate(session, payloads, "run", rps=5, duration_sec=300, stats=stats)
        print_stats(f"Steady/{group}", stats, time.monotonic() - start)
        all_stats.merge(stats)

    # Also test /submit steady
    print(f"\n  ▶ Group: submit_mixed")
    submit_stats = Stats()
    payloads = pick_payloads_from(corpus, ["tiny_python", "tiny_cpp"], 200)
    start = time.monotonic()
    await send_at_rate(session, payloads, "submit", rps=3, duration_sec=300, stats=submit_stats)
    print_stats("Steady/submit_mixed", submit_stats, time.monotonic() - start)
    all_stats.merge(submit_stats)

    return all_stats


async def phase_step_load(session: aiohttp.ClientSession, corpus: dict):
    """Step-load: increase rate from 5 to 40 req/s in steps, 2 min each."""
    print("\n" + "=" * 70)
    print("PHASE: STEP-LOAD (/run — 5,10,20,30,40 req/s × 2 min each)")
    print("=" * 70)

    rates = [5, 10, 20, 30, 40]
    payloads = pick_payloads_from(corpus, ["tiny_python", "tiny_cpp", "bad_cases"], 500)
    results = []

    for rps in rates:
        print(f"\n  ▶ Rate: {rps} req/s")
        stats = Stats()
        start = time.monotonic()
        await send_at_rate(session, payloads, "run", rps=rps, duration_sec=120, stats=stats)
        wall = time.monotonic() - start
        print_stats(f"Step/{rps}rps", stats, wall)

        lats = sorted(stats.latencies)
        results.append({
            "rps_target": rps,
            "rps_actual": round(stats.total / wall, 1) if wall > 0 else 0,
            "total": stats.total,
            "failed": stats.failed,
            "p50": round(percentile(lats, 0.50)),
            "p95": round(percentile(lats, 0.95)),
            "p99": round(percentile(lats, 0.99)),
            "max": round(lats[-1]) if lats else 0,
            "error_rate": round(stats.failed / max(stats.total, 1) * 100, 1),
        })

    # Step-load for /submit too
    print(f"\n  ── /submit step-load ──")
    submit_rates = [5, 10, 20]
    for rps in submit_rates:
        print(f"\n  ▶ Rate: {rps} req/s")
        stats = Stats()
        start = time.monotonic()
        await send_at_rate(session, payloads, "submit", rps=rps, duration_sec=120, stats=stats)
        wall = time.monotonic() - start
        print_stats(f"Step-Submit/{rps}rps", stats, wall)

        lats = sorted(stats.latencies)
        results.append({
            "endpoint": "submit",
            "rps_target": rps,
            "rps_actual": round(stats.total / wall, 1) if wall > 0 else 0,
            "total": stats.total,
            "failed": stats.failed,
            "p50": round(percentile(lats, 0.50)),
            "p95": round(percentile(lats, 0.95)),
            "p99": round(percentile(lats, 0.99)),
            "max": round(lats[-1]) if lats else 0,
            "error_rate": round(stats.failed / max(stats.total, 1) * 100, 1),
        })

    print("\n\n  ═══ STEP-LOAD SUMMARY ═══")
    print(f"  {'Endpoint':<10} {'Target':>6} {'Actual':>7} {'Total':>6} {'Fail':>5} "
          f"{'p50':>6} {'p95':>6} {'p99':>6} {'Max':>7} {'Err%':>6}")
    print(f"  {'─' * 75}")
    for r in results:
        ep = r.get("endpoint", "run")
        print(f"  {ep:<10} {r['rps_target']:>5}/s {r['rps_actual']:>6}/s {r['total']:>6} "
              f"{r['failed']:>5} {r['p50']:>5}ms {r['p95']:>5}ms {r['p99']:>5}ms "
              f"{r['max']:>6}ms {r['error_rate']:>5}%")

    return results


async def phase_saturate(session: aiohttp.ClientSession, corpus: dict):
    """Saturation: ramp up until p95 latency doubles or error rate > 5%."""
    print("\n" + "=" * 70)
    print("PHASE: SATURATION (ramp until knee-point)")
    print("=" * 70)

    payloads = pick_payloads_from(corpus, ["tiny_python", "tiny_cpp"], 500)
    baseline_p95 = None
    results = []
    rps = 5

    while rps <= 200:
        print(f"\n  ▶ Probing {rps} req/s for 60s...")
        stats = Stats()
        start = time.monotonic()
        await send_at_rate(session, payloads, "run", rps=rps, duration_sec=60, stats=stats)
        wall = time.monotonic() - start

        lats = sorted(stats.latencies)
        p95 = percentile(lats, 0.95)
        error_rate = stats.failed / max(stats.total, 1) * 100

        print_stats(f"Saturate/{rps}rps", stats, wall)

        if baseline_p95 is None:
            baseline_p95 = p95

        results.append({
            "rps": rps,
            "actual_rps": round(stats.total / wall, 1),
            "p95": round(p95),
            "error_rate": round(error_rate, 1),
            "total": stats.total,
        })

        # Knee-point detection
        if p95 > baseline_p95 * 3:
            print(f"\n  ⚠ KNEE-POINT: p95 tripled ({baseline_p95:.0f}ms → {p95:.0f}ms) at {rps} req/s")
            break
        if error_rate > 5:
            print(f"\n  ⚠ KNEE-POINT: error rate {error_rate:.1f}% at {rps} req/s")
            break

        # Ramp: +5 until 30, then +10
        rps += 5 if rps < 30 else 10

    print("\n\n  ═══ SATURATION SUMMARY ═══")
    print(f"  {'RPS':>5} {'Actual':>7} {'p95':>7} {'Err%':>6} {'Total':>6}")
    print(f"  {'─' * 40}")
    for r in results:
        marker = " ◀" if r == results[-1] and len(results) > 1 else ""
        print(f"  {r['rps']:>4}/s {r['actual_rps']:>6}/s {r['p95']:>6}ms "
              f"{r['error_rate']:>5}% {r['total']:>6}{marker}")

    return results


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

async def main():
    print("=" * 70)
    print("BENCHMARK SUITE — /run and /submit")
    print("=" * 70)

    jar = make_cookie_jar()
    timeout = aiohttp.ClientTimeout(total=300)
    session = aiohttp.ClientSession(cookie_jar=jar, timeout=timeout)

    # Auth check
    print("\n[Setup] Verifying auth...")
    try:
        async with session.get(f"{BASE}/auth/get-session") as resp:
            if resp.status != 200:
                print(f"  ERROR: Auth failed ({resp.status})")
                await session.close()
                return
            data = await resp.json()
            user = data.get("user") if data else None
            if not user:
                print("  ERROR: No user in session. Token may be expired.")
                await session.close()
                return
            print(f"  Authenticated as: {user.get('name', '?')} ({user.get('email', '?')})")
    except Exception as e:
        print(f"  ERROR: {e}")
        await session.close()
        return

    # Fetch problems for corpus
    print("[Setup] Fetching problems...")
    try:
        async with session.get(f"{BASE}/problemset") as resp:
            problems = await resp.json() if resp.status == 200 else []
    except Exception:
        problems = []
    slugs = [p["slug"] for p in problems] if problems else ["1000A"]
    print(f"  Using slugs: {slugs}")

    corpus = build_corpus(slugs)
    total_payloads = sum(len(v) for v in corpus.values())
    print(f"  Corpus: {total_payloads} payloads across {len(corpus)} groups")
    for name, items in corpus.items():
        print(f"    {name}: {len(items)} payloads")

    try:
        if PHASE in ("all", "warmup"):
            await phase_warmup(session, corpus)

        if PHASE in ("all", "steady"):
            await phase_steady(session, corpus)

        if PHASE in ("all", "step"):
            await phase_step_load(session, corpus)

        if PHASE in ("all", "saturate"):
            await phase_saturate(session, corpus)

        print("\n" + "=" * 70)
        print("BENCHMARK COMPLETE")
        print("=" * 70)

    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(main())
