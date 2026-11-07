import os
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.db.session import get_db
from backend.app.db.models import User, Document
from backend.app.core.security import get_current_user
from backend.app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["AI Document Generation"])

class GenerateDocumentRequest(BaseModel):
    title: str
    doc_type: str # docx, pdf, xlsx, pptx, csv, txt
    prompt: Optional[str] = None
    content: Optional[str] = None

@router.get("")
async def list_documents(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Document).where(Document.user_id == user.id).order_by(Document.created_at.desc())
    result = await db.execute(stmt)
    docs = list(result.scalars().all())

    if not docs:
        # Pre-seed sample executive brief
        d1 = await DocumentService.create_document(
            db, user.id,
            title="Enterprise AI Executive Strategy 2026",
            doc_type="docx",
            content="## Executive Strategy Brief\n\n- Phase 1: Deploy context-aware executive AI agents.\n- Phase 2: Integrate Gmail and Google Calendar with Level 3 safeguards.\n- Phase 3: Scale enterprise multi-agent workflows.\n\n### Key Deliverables\n1. Zero data leakage architecture\n2. Real-time executive task prioritization"
        )
        d2 = await DocumentService.create_document(
            db, user.id,
            title="Q3 Operational Financial Model",
            doc_type="xlsx",
            content="Metric, Q1 Actual, Q2 Actual, Q3 Projected\nARR ($M), 4.2, 5.8, 7.5\nGross Margin, 78%, 81%, 83%\nNet Retention, 122%, 128%, 132%"
        )
        docs = [d1, d2]

    return [
        {
            "id": d.id,
            "title": d.title,
            "doc_type": d.doc_type,
            "file_size_bytes": d.file_size_bytes,
            "status": d.status,
            "download_url": f"/api/documents/{d.id}/download",
            "created_at": d.created_at.isoformat()
        } for d in docs
    ]

@router.post("/generate")
async def generate_document(
    payload: GenerateDocumentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    content = payload.content or (
        f"## Executive Report: {payload.title}\n\n"
        "Synthesized by Technopie AI Autonomous Document Agent.\n\n"
        "### Key Findings\n"
        "- Structured analysis completed according to parameters.\n"
        "- Operational efficiency gains verified.\n"
        "- Recommendations aligned with executive priorities."
    )
    doc = await DocumentService.create_document(
        db,
        user_id=user.id,
        title=payload.title,
        doc_type=payload.doc_type,
        content=content,
        source_prompt=payload.prompt
    )
    return {
        "id": doc.id,
        "title": doc.title,
        "doc_type": doc.doc_type,
        "file_size_bytes": doc.file_size_bytes,
        "download_url": f"/api/documents/{doc.id}/download"
    }

@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Document).where(Document.id == document_id, Document.user_id == user.id)
    result = await db.execute(stmt)
    doc = result.scalars().first()
    if not doc or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Document not found or access denied.")

    media_types = {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pdf": "application/pdf",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "csv": "text/csv",
        "txt": "text/plain"
    }
    media_type = media_types.get(doc.doc_type, "application/octet-stream")
    filename = os.path.basename(doc.file_path)
    return FileResponse(doc.file_path, media_type=media_type, filename=filename)
