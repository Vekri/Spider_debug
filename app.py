"""Vercel entrypoint for the spider debugger."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

import spelling

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"
SAMPLES = ROOT / "samples"
TEXT_LIMIT = 150_000
SAMPLE_NAMES = {"buggy_code.py", "meeting_notes.txt"}
_CHECKER = None

app = FastAPI(title="Spider debug")


def checker():
    global _CHECKER
    if _CHECKER is None:
        _CHECKER = spelling.build_checker()
    return _CHECKER


class SpellRequest(BaseModel):
    text: str = ""
    filename: str = "notes.txt"


@app.get("/api/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.post("/api/spell")
def spell_endpoint(body: SpellRequest) -> dict[str, object]:
    text = body.text[:TEXT_LIMIT]
    filename = Path(body.filename).name or "notes.txt"
    report = spelling.find_fixes(text, filename, checker())
    return {
        "text": text,
        "filename": filename,
        "fixes": report.fixes,
        "corrected": spelling.apply_fixes(text, report.fixes),
        "limited": report.limited,
        "trimmed": len(body.text) > TEXT_LIMIT,
    }


@app.get("/")
def home() -> FileResponse:
    return FileResponse(PUBLIC / "index.html")


@app.get("/samples/{name}")
def sample(name: str) -> FileResponse:
    if name not in SAMPLE_NAMES:
        raise HTTPException(status_code=404)
    return FileResponse(SAMPLES / name)


@app.get("/{asset:path}")
def asset(asset: str) -> FileResponse:
    file = (PUBLIC / asset).resolve()
    if not file.is_relative_to(PUBLIC.resolve()) or not file.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(file)
