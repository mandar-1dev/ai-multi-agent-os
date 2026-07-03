import os
import json
from app.tools.base_tool import BaseTool


class FileReaderTool(BaseTool):
    name = "file_reader"
    description = "Read and extract raw text from a file on disk (pdf, docx, csv, txt, md, json)."

    def validate(self, **kwargs):
        path = kwargs.get("path")
        if not path or not isinstance(path, str):
            return False, "Missing required string field 'path'"
        if not os.path.exists(path):
            return False, f"File not found: {path}"
        return True, None

    def _run(self, **kwargs):
        path = kwargs["path"]
        ext = path.rsplit(".", 1)[-1].lower()

        if ext == "pdf":
            from pypdf import PdfReader
            reader = PdfReader(path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif ext == "docx":
            import docx
            doc = docx.Document(path)
            text = "\n".join(p.text for p in doc.paragraphs)
        elif ext == "csv":
            import pandas as pd
            df = pd.read_csv(path)
            text = df.to_string()
        elif ext == "json":
            with open(path, "r", encoding="utf-8") as f:
                text = json.dumps(json.load(f), indent=2)
        else:  # txt, md, and other plain-text formats
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        return {"path": path, "file_type": ext, "char_count": len(text), "text": text[:20000]}
