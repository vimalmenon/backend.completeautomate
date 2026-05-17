from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from backend.manager import PromptManager

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")


def _prompt_to_row(prompt, pm: PromptManager) -> dict:
    results = pm.get_results(prompt.task)
    scores = [r.score for r in results if r.score is not None]
    return {
        "task": prompt.task.value,
        "description": prompt.description,
        "latest_score": scores[-1] if scores else None,
        "result_count": len(results),
    }


def _prompt_details(prompt, pm: PromptManager) -> dict:
    results = pm.get_results(prompt.task)
    results_sorted = sorted(results, key=lambda x: x.created_at, reverse=True)
    return {
        "description": prompt.description,
        "active_version": str(prompt.active_version),
        "ai": prompt.ai.value if hasattr(prompt.ai, "value") else str(prompt.ai),
        "prompt": prompt.prompt,
        "system_message": prompt.system_message,
        "last_updated": (
            prompt.last_updated.isoformat()
            if hasattr(prompt.last_updated, "isoformat")
            else str(prompt.last_updated)
        ),
        "results": [
            {
                "result_id": str(r.result_id),
                "score": r.score,
                "response": r.response,
                "prompt_data_snapshot": r.prompt_data_snapshot,
                "created_at": (
                    r.created_at.isoformat()
                    if hasattr(r.created_at, "isoformat")
                    else str(r.created_at)
                ),
            }
            for r in results_sorted
        ],
    }


@router.get("/dashboard/prompts", response_class=HTMLResponse)
async def prompt_results_dashboard(request: Request):
    """Render an HTML dashboard of prompt evaluation results."""
    try:
        pm = PromptManager()
        prompts = pm.get_prompts()

        prompts_data = [_prompt_to_row(p, pm) for p in prompts]
        details = {p.task.value: _prompt_details(p, pm) for p in prompts}

        total_results = sum(p["result_count"] for p in prompts_data)
        evaluated_count = sum(1 for p in prompts_data if p["latest_score"] is not None)
        all_scores = [p["latest_score"] for p in prompts_data if p["latest_score"] is not None]
        avg_score = round(sum(all_scores) / len(all_scores)) if all_scores else 0

        return templates.TemplateResponse(
            "prompt_result_dashboard.html",
            {
                "request": request,
                "prompts": prompts_data,
                "details": details,
                "result_count": total_results,
                "evaluated_count": evaluated_count,
                "avg_score": avg_score,
                "error": None,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "prompt_result_dashboard.html",
            {
                "request": request,
                "error": str(e),
                "prompts": [],
                "details": {},
                "result_count": 0,
                "evaluated_count": 0,
                "avg_score": 0,
            },
        )
