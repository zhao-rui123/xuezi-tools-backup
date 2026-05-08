"""FastAPI wrapper for Energy Solution Agent - Cloud API Service"""

from __future__ import annotations

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from energy_solution_agent.engine import analyze_project
from energy_solution_agent.report_docx import build_docx_report
from energy_solution_agent.report_excel import build_excel_report

# ═══════════════════════════════════════════════════════════════
# App setup
# ═══════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="能源解决方案 API",
    description="新能源电力方案分析云服务",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for report downloads
app.mount("/files", StaticFiles(directory=str(OUTPUT_DIR)), name="files")

# ═══════════════════════════════════════════════════════════════
# Request/Response models
# ═══════════════════════════════════════════════════════════════

class AnalyzeRequest(BaseModel):
    project_data: dict[str, Any]
    generate_docx: bool = False
    generate_xlsx: bool = False
    enable_live_rules: bool = False


class AnalyzeResponse(BaseModel):
    task_id: str
    output: dict[str, Any]
    report_url: str | None = None
    docx_url: str | None = None
    xlsx_url: str | None = None
    errors: list[str] = []


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str


# ═══════════════════════════════════════════════════════════════
# Routes
# ═══════════════════════════════════════════════════════════════

@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
    )


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    task_id = str(uuid.uuid4())[:8]
    errors = []

    try:
        # Run analysis
        output, diagnostics, report = analyze_project(
            req.project_data,
            enable_live_rules=req.enable_live_rules,
        )

        # Collect warnings
        if diagnostics.get("missing_fields"):
            for field in diagnostics["missing_fields"]:
                errors.append(f"Missing field: {field}")

        report_url = None
        docx_url = None
        xlsx_url = None

        # Generate docx if requested
        if req.generate_docx:
            try:
                docx_path = OUTPUT_DIR / f"{task_id}_report.docx"
                build_docx_report(output, diagnostics, str(docx_path))
                docx_url = f"/files/{task_id}_report.docx"
            except Exception as e:
                errors.append(f"DOCX generation failed: {str(e)}")

        # Generate xlsx if requested
        if req.generate_xlsx:
            try:
                xlsx_path = OUTPUT_DIR / f"{task_id}_report.xlsx"
                build_excel_report(output, diagnostics, str(xlsx_path))
                xlsx_url = f"/files/{task_id}_report.xlsx"
            except Exception as e:
                errors.append(f"XLSX generation failed: {str(e)}")

        return AnalyzeResponse(
            task_id=task_id,
            output=output,
            report_url=f"/files/{task_id}_report.md",
            docx_url=docx_url,
            xlsx_url=xlsx_url,
            errors=errors,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
def download(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if filename.endswith(".docx"):
        return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=filename)
    elif filename.endswith(".xlsx"):
        return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=filename)
    else:
        return FileResponse(file_path, filename=filename)


@app.get("/")
def index():
    return {
        "service": "能源解决方案 API",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "提交项目分析",
            "GET /health": "健康检查",
            "GET /download/{filename}": "下载报告文件",
        },
        "documentation": "/docs",
    }


# ═══════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
