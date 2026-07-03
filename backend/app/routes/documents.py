import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.document import Document
from app.tools.file_reader import FileReaderTool
from app.rag.retriever import ingest_document, new_document_id

router = APIRouter(prefix="/api/documents", tags=["documents"])
UPLOAD_DIR = "./uploaded_documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "txt"
    saved_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(saved_path, "wb") as f:
        f.write(await file.read())

    doc = Document(filename=file.filename, file_type=ext, status="processing")
    db.add(doc)
    db.commit()
    db.refresh(doc)

    reader = FileReaderTool()
    result = reader.run(path=saved_path)
    if not result.success:
        doc.status = "failed"
        db.commit()
        return {"error": result.error}

    text = result.data["text"]
    chunk_ids = await ingest_document(doc.id, text, file.filename)

    doc.num_chunks = len(chunk_ids)
    doc.status = "ready"
    doc.summary = text[:500]
    db.commit()

    return {"id": doc.id, "filename": doc.filename, "num_chunks": doc.num_chunks, "status": doc.status}


@router.get("")
def list_documents(db: Session = Depends(get_db)):
    rows = db.query(Document).order_by(Document.created_at.desc()).all()
    return [
        {"id": d.id, "filename": d.filename, "file_type": d.file_type,
         "status": d.status, "num_chunks": d.num_chunks, "created_at": d.created_at}
        for d in rows
    ]
