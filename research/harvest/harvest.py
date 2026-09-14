import json, time, random, urllib.request, urllib.error, urllib.parse, os, sys
OUT = os.path.join(os.path.dirname(__file__), "tweets.jsonl")
LOG = os.path.join(os.path.dirname(__file__), "progress.log")
TARGET = 10000
seen = set()
if os.path.exists(OUT):
    for line in open(OUT):
        seen.add(json.loads(line)["id"])

def log(msg):
    with open(LOG, "a") as f:
        f.write(time.strftime("%H:%M:%S ") + msg + "\n")

def get(url):
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "skill-factory-research"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                log(f"404 on {url[:90]}, skip")
                return None
            wait = 30 * (attempt + 1)
            log(f"http {e.code} retry in {wait}s")
            time.sleep(wait)
        except Exception as e:
            wait = 20 * (attempt + 1)
            log(f"error {e} retry in {wait}s")
            time.sleep(wait)
    return None

def save(results, source):
    new = 0
    with open(OUT, "a") as f:
        for t in results:
            if t.get("author", {}).get("screen_name", "").lower() != "unclebobmartin" or t["id"] in seen:
                continue
            seen.add(t["id"])
            text = (t.get("raw_text") or {}).get("text") or t.get("text", "")
            f.write(json.dumps({"id": t["id"], "created_at": t.get("created_at"), "text": text,
                                "replying_to": t.get("replying_to"), "likes": t.get("likes"),
                                "quote": (t.get("quote") or {}).get("text"), "source": source}) + "\n")
            new += 1
    return new

def paginate(base, source, max_pages, stale_limit=4):
    cursor, stale = None, 0
    for page in range(max_pages):
        url = base + (("&" if "?" in base else "?") + "cursor=" + urllib.parse.quote(cursor) if cursor else "")
        d = get(url)
        if not d or not d.get("results"):
            log(f"{source} page {page} empty, stop")
            return
        new = save(d["results"], source)
        log(f"{source} page {page} new={new} total={len(seen)}")
        stale = stale + 1 if new == 0 else 0
        nxt = (d.get("cursor") or {}).get("bottom")
        if stale >= stale_limit or not nxt or nxt == cursor or len(seen) >= TARGET:
            return
        cursor = nxt
        time.sleep(random.uniform(3, 6))

queries = ["agent", "agents", "AI", "Claude", "codex", "LLM", "harness", "tokens", "context", "prompt",
           "swarm", "gherkin", "mutation", "CRAP", "vibe", "model", "GPT", "grok", "gemini", "cursor",
           "skill", "orchestration", "squad", "worktree", "acceptance test", "coverage", "dependency", "architecture agent",
           "review code", "software engineering dead", "programmers jobs", "copilot", "chatgpt", "anthropic", "openai"]
for q in queries:
    paginate("https://api.fxtwitter.com/2/search?q=" + urllib.parse.quote(f"from:unclebobmartin {q}"), f"search:{q}", 60)
paginate("https://api.fxtwitter.com/2/profile/unclebobmartin/statuses", "timeline", 2000, stale_limit=15)
log("DONE")
