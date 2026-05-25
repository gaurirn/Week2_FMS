"""
Analytics + ETL Router

Endpoints (mounted under /api/v1/analytics)
-------------------------------------------
    POST  /analytics/etl/upload         multipart upload + run ETL
    POST  /analytics/etl/run-sample     run ETL from the bundled sample dataset
    GET   /analytics/etl/runs           list previous ETL runs
    GET   /analytics/summary            dashboard aggregates
    GET   /analytics/programs           per-program aggregates
    GET   /analytics/report.csv         download cleaned analytics as CSV
    GET   /analytics/report.xlsx        download cleaned analytics as Excel
"""

import io
import os
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.analytics_schema import (
    AnalyticsSummary,
    EtlRunListResponse,
    EtlRunResponse,
    ProgramAnalyticsItem,
)
from app.schemas.feedback_schema import APIResponse
from app.services.analytics_service import (
    AnalyticsService,
    analytics_service,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_analytics_service() -> AnalyticsService:
    return analytics_service


# ----------------------------------------------------------------------
# ETL — upload
# ----------------------------------------------------------------------
@router.post(
    "/etl/upload",
    response_model=APIResponse[EtlRunResponse],
    summary="Upload a CSV/Excel file and run the ETL pipeline",
)
async def etl_upload(
    file: UploadFile = File(...),
    mode: str = "replace",
    db: Session = Depends(get_db),
    service: AnalyticsService = Depends(get_analytics_service),
):
    if mode not in ("replace", "append"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="mode must be 'replace' or 'append'.",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    try:
        result = service.run_etl_from_bytes(
            db, contents=contents, filename=file.filename or "upload.csv", mode=mode
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if result.status == "failed":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=result.error_message or "ETL failed.",
        )

    payload = EtlRunResponse.model_validate(
        {
            "run_id": result.run_id,
            "source_filename": result.source_filename,
            "source_kind": result.source_kind,
            "rows_extracted": result.rows_extracted,
            "rows_transformed": result.rows_transformed,
            "rows_loaded": result.rows_loaded,
            "rows_rejected": result.rows_rejected,
            "duplicates_removed": result.duplicates_removed,
            "invalid_ratings_dropped": result.invalid_ratings_dropped,
            "missing_fields_dropped": result.missing_fields_dropped,
            "duration_ms": result.duration_ms,
            "status": result.status,
            "error_message": result.error_message,
            "run_at": __import__("datetime").datetime.utcnow(),
        }
    )
    return APIResponse[EtlRunResponse](
        message=f"ETL completed: {result.rows_loaded} rows loaded.",
        data=payload,
    )


# ----------------------------------------------------------------------
# ETL — run against bundled sample dataset
# ----------------------------------------------------------------------
@router.post(
    "/etl/run-sample",
    response_model=APIResponse[EtlRunResponse],
    summary="Run the ETL against the bundled sample dataset",
)
def etl_run_sample(
    mode: str = "replace",
    db: Session = Depends(get_db),
    service: AnalyticsService = Depends(get_analytics_service),
):
    # Project layout: backend/app/routers/analytics_router.py
    # Sample CSV: datasets/sample_feedback.csv at the repo root.
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.normpath(os.path.join(here, "..", "..", "..", "datasets", "sample_feedback.csv")),
        os.path.normpath(os.path.join(here, "..", "..", "datasets", "sample_feedback.csv")),
        os.path.normpath(os.path.join(os.getcwd(), "datasets", "sample_feedback.csv")),
    ]
    path = next((p for p in candidates if os.path.exists(p)), None)
    if path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample dataset not found. Expected datasets/sample_feedback.csv.",
        )
    result = service.run_etl_from_path(db, path=path, mode=mode)
    payload = EtlRunResponse.model_validate(
        {
            "run_id": result.run_id,
            "source_filename": result.source_filename,
            "source_kind": result.source_kind,
            "rows_extracted": result.rows_extracted,
            "rows_transformed": result.rows_transformed,
            "rows_loaded": result.rows_loaded,
            "rows_rejected": result.rows_rejected,
            "duplicates_removed": result.duplicates_removed,
            "invalid_ratings_dropped": result.invalid_ratings_dropped,
            "missing_fields_dropped": result.missing_fields_dropped,
            "duration_ms": result.duration_ms,
            "status": result.status,
            "error_message": result.error_message,
            "run_at": __import__("datetime").datetime.utcnow(),
        }
    )
    return APIResponse[EtlRunResponse](
        message=f"Sample ETL completed: {result.rows_loaded} rows loaded.",
        data=payload,
    )


# ----------------------------------------------------------------------
# ETL — history
# ----------------------------------------------------------------------
@router.get(
    "/etl/runs",
    response_model=APIResponse[EtlRunListResponse],
    summary="List previous ETL runs",
)
def etl_runs(
    limit: int = 50,
    db: Session = Depends(get_db),
    service: AnalyticsService = Depends(get_analytics_service),
):
    runs = service.list_etl_runs(db, limit=limit)
    items = [EtlRunResponse.model_validate(r) for r in runs]
    return APIResponse[EtlRunListResponse](
        data=EtlRunListResponse(total=len(items), items=items)
    )


# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------
@router.get(
    "/summary",
    response_model=APIResponse[AnalyticsSummary],
    summary="Aggregated analytics for the dashboard",
)
def get_summary(
    db: Session = Depends(get_db),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return APIResponse[AnalyticsSummary](data=service.get_summary(db))


# ----------------------------------------------------------------------
# Per-program aggregates
# ----------------------------------------------------------------------
@router.get(
    "/programs",
    response_model=APIResponse[List[ProgramAnalyticsItem]],
    summary="Per-program analytics",
)
def get_programs(
    db: Session = Depends(get_db),
    service: AnalyticsService = Depends(get_analytics_service),
):
    items = [
        ProgramAnalyticsItem.model_validate(p)
        for p in service.list_programs(db)
    ]
    return APIResponse[List[ProgramAnalyticsItem]](data=items)


# ----------------------------------------------------------------------
# Downloadable reports
# ----------------------------------------------------------------------
@router.get(
    "/report.csv",
    summary="Download cleaned analytics as CSV",
)
def report_csv(
    db: Session = Depends(get_db),
    service: AnalyticsService = Depends(get_analytics_service),
):
    import csv

    rows = service.all_clean_rows(db)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "analytics_id",
            "etl_run_id",
            "participant_name",
            "program_name",
            "rating",
            "sentiment",
            "comments",
            "submitted_at",
        ]
    )
    for r in rows:
        writer.writerow(
            [
                r.analytics_id,
                r.etl_run_id or "",
                r.participant_name,
                r.program_name,
                r.rating,
                r.sentiment,
                (r.comments or "").replace("\n", " "),
                r.submitted_at.isoformat() if r.submitted_at else "",
            ]
        )

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="feedback_analytics.csv"'},
    )


@router.get(
    "/report.xlsx",
    summary="Download cleaned analytics as Excel",
)
def report_xlsx(
    db: Session = Depends(get_db),
    service: AnalyticsService = Depends(get_analytics_service),
):
    import pandas as pd

    rows = service.all_clean_rows(db)
    data = [
        {
            "analytics_id": r.analytics_id,
            "etl_run_id": r.etl_run_id,
            "participant_name": r.participant_name,
            "program_name": r.program_name,
            "rating": r.rating,
            "sentiment": r.sentiment,
            "comments": r.comments,
            "submitted_at": r.submitted_at,
        }
        for r in rows
    ]
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Feedback Analytics")
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="feedback_analytics.xlsx"'
        },
    )
