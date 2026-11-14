"""Turn an uploaded CV file into plain text: .txt, .pdf (via pypdf) and .docx (no extra deps)."""
from __future__ import annotations

import io
import re
import zipfile

SUPPORTED = (".txt", ".pdf", ".docx")


class UnsupportedFile(ValueError):
    pass


def to_text(filename: str, data: bytes) -> str:
    name = filename.lower()
    if name.endswith(".txt"):
        return data.decode("utf-8", errors="replace")
    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
        except ImportError as e:  # pragma: no cover
            raise UnsupportedFile("PDF support is not installed on this server") from e
        try:
            reader = PdfReader(io.BytesIO(data))
            return "\n".join((p.extract_text() or "") for p in reader.pages[:10])
        except Exception as e:  # noqa: BLE001 - malformed PDFs raise many types
            raise UnsupportedFile("that PDF could not be read") from e
    if name.endswith(".docx"):
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                xml = z.read("word/document.xml").decode("utf-8", errors="replace")
        except (zipfile.BadZipFile, KeyError) as e:
            raise UnsupportedFile("that Word file could not be read") from e
        xml = re.sub(r"</w:p>", "\n", xml)
        xml = re.sub(r"<w:tab/>", "\t", xml)
        text = re.sub(r"<[^>]+>", "", xml)
        return (text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                .replace("&quot;", '"').replace("&apos;", "'"))
    raise UnsupportedFile("please upload a .txt, .pdf or .docx file")
