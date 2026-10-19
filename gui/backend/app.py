from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import sys, time

# Permite importar el paquete brokenlinkcrawler (raíz del repo, 2 niveles por encima)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from brokenlinkcrawler.crawler import crawl


@dataclass
class CrawlTask:
    id: str
    url: str
    status: str
    progress: dict
    started_at: str
    results: dict = None
    error: str = None


app = FastAPI()
current_task = None
history = []


@app.post("/api/crawl")
async def start_crawl(body: dict, bg_tasks: BackgroundTasks):
    global current_task
    task_id = f"crawl_{int(time.time() * 1000)}"
    url = (body.get("url") or "").strip()
    if url and "://" not in url:
        url = "https://" + url
    current_task = CrawlTask(task_id, url, "running",
                             {"checked": 0, "queued": 0, "broken": 0},
                             datetime.now().isoformat())
    bg_tasks.add_task(run_crawler, current_task, body)
    return {"task_id": task_id, "status": "started"}


# `def` (no async): FastAPI lo ejecuta en un threadpool y no bloquea el servidor
def run_crawler(task: CrawlTask, config: dict):
    def progress(event, **d):
        if event == "checking":
            task.progress["checked"] = d["checked"]
            task.progress["queued"] = d["queued"]
        elif event == "result" and d.get("status") == "BROKEN":
            task.progress["broken"] += 1

    try:
        report = crawl(
            task.url,
            max_pages=int(config.get("max_pages", 100)),
            max_links=int(config.get("max_links", 10000)),
            timeout=float(config.get("timeout", 10)),
            delay=float(config.get("delay", 0.0)),
            respect_robots=not config.get("ignore_robots", False),
            progress=progress,
        )
        task.results = {
            "total_links": report["pages_checked"],
            "broken_links": len(report["broken"]),
            "pages_crawled": report["pages_checked"],
            "truncated": report["truncated"],
            "broken": report["broken"],
        }
        task.status = "completed"
        history.append(asdict(task))
    except Exception as e:
        task.status = "failed"
        task.error = str(e)


@app.get("/api/crawl/{task_id}")
async def get_status(task_id: str):
    if current_task and current_task.id == task_id:
        return asdict(current_task)
    return JSONResponse({"error": "Not found"}, status_code=404)


@app.get("/api/history")
async def get_history():
    return {"crawls": history}


@app.get("/")
async def root():
    dist_file = Path(__file__).parent / "dist" / "index.html"
    if dist_file.exists():
        return FileResponse(dist_file)
    return {"status": "ok"}