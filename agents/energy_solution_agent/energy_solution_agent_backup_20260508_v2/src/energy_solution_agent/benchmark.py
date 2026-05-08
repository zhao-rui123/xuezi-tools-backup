from __future__ import annotations

from pathlib import Path
from typing import Any

from .engine import analyze_project
from .utils import read_json


def run_benchmarks(example_dir: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for path in sorted(example_dir.glob("*.json")):
        if path.stem.endswith("_template"):
            continue
        try:
            payload = read_json(path)
            output, diagnostics, _ = analyze_project(payload)
        except Exception as exc:
            errors.append({"file": path.name, "error": str(exc)})
            continue
        rows.append(
            {
                "file": path.name,
                "scenario": output["project_summary"]["scenario_type"],
                "province": output["project_summary"]["province"],
                "confidence": output["confidence"]["level"],
                "annual_revenue": output["financial_results"]["annual_savings_or_revenue"],
                "irr": output["financial_results"]["irr"],
                "data_gaps": len(output["data_gaps"]),
                "risks": len(output["risks"]),
                "completeness": diagnostics["data_completeness_grade"],
                "market_profile_status": output["market_and_settlement"]["province_profile_status"],
                "data_quality_level": output["data_quality_results"]["level"],
                "quality_gate_passed": _quality_gate(output),
            }
        )
    result: dict[str, Any] = {
        "summary": _summarize(rows),
        "benchmarks": rows,
    }
    result["summary"]["failed_cases"] = len(errors)
    result["summary"]["total_attempted_cases"] = len(rows) + len(errors)
    result["summary"]["has_errors"] = bool(errors)
    if errors:
        result["errors"] = errors
    return result


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    by_scenario: dict[str, int] = {}
    by_confidence: dict[str, int] = {}
    by_province: dict[str, int] = {}
    avg_revenue = 0.0
    avg_irr = 0.0
    irr_count = 0
    for row in rows:
        by_scenario[row["scenario"]] = by_scenario.get(row["scenario"], 0) + 1
        by_confidence[row["confidence"]] = by_confidence.get(row["confidence"], 0) + 1
        by_province[row["province"]] = by_province.get(row["province"], 0) + 1
        avg_revenue += float(row["annual_revenue"] or 0.0)
        if row["irr"] is not None:
            avg_irr += float(row["irr"])
            irr_count += 1
    return {
        "total_cases": total,
        "successful_cases": total,
        "by_scenario": by_scenario,
        "by_confidence": by_confidence,
        "by_province": by_province,
        "average_annual_revenue": round(avg_revenue / total, 2) if total else 0.0,
        "average_irr": round(avg_irr / irr_count, 4) if irr_count else None,
        "max_data_gaps": max((row["data_gaps"] for row in rows), default=0),
        "max_risks": max((row["risks"] for row in rows), default=0),
        "quality_gate_pass_rate": round(sum(1 for row in rows if row["quality_gate_passed"]) / total, 4) if total else 0.0,
    }


def _quality_gate(output: dict[str, Any]) -> bool:
    if output["confidence"]["level"] == "low":
        return False
    if output["data_quality_results"]["level"] == "low":
        return False
    if len(output["data_gaps"]) > 4:
        return False
    return True
