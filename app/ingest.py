"""PDF ingestion: extract text page by page and split it into overlapping chunks.

Every chunk carries the metadata that the access-control filter needs
(company_id, document) plus what the UI needs to cite it (title, page).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from .access import AccessPolicy

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(])")
_LEADING_DATE = re.compile(r"^[A-Z][a-z]+ \d{1,2}, \d{4}\s+")
_FOOTER = re.compile(r"FICTIONAL SAMPLE DOCUMENT.*?invented\.\s*(Page \d+)?", re.S)


@dataclass(frozen=True)
class Chunk:
    id: str
    company_id: str
    document: str
    title: str
    page: int
    text: str


def clean(text: str) -> str:
    text = _FOOTER.sub(" ", text)
    text = text.replace("­", "")
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]


def chunk_sentences(sentences: list[tuple[int, str]], max_words: int, overlap: int) -> list[tuple[int, str]]:
    """Group (page, sentence) pairs into chunks of about max_words words.

    Chunks may cross a page break (so a question at the bottom of a page stays
    with its answer at the top of the next); a chunk is cited by the page its
    first sentence is on.
    """
    chunks, current, words = [], [], 0
    for page, s in sentences:
        n = len(s.split())
        # Never cut between an analyst's question and the answer that follows it.
        if current and words + n > max_words and not current[-1][1].endswith("?"):
            chunks.append((current[0][0], " ".join(x for _, x in current)))
            current = current[-overlap:] if overlap else []
            words = sum(len(x.split()) for _, x in current)
        current.append((page, s))
        words += n
    if current:
        chunks.append((current[0][0], " ".join(x for _, x in current)))
    return chunks


def load_pdf(path: Path, company_id: str, max_words: int, overlap: int) -> list[Chunk]:
    reader = PdfReader(str(path))
    title = (reader.metadata.title if reader.metadata and reader.metadata.title else path.stem)
    sentences: list[tuple[int, str]] = []
    for page_no, page in enumerate(reader.pages, start=1):
        # The title is kept as metadata, so drop it from the body text to stop
        # the cover line from matching every query about this company.
        text = clean(page.extract_text() or "").replace(clean(title), " ").strip()
        text = _LEADING_DATE.sub("", text)
        sentences.extend((page_no, s) for s in split_sentences(text))
    return [Chunk(f"{path.name}#c{i}", company_id, path.name, title, page, text)
            for i, (page, text) in enumerate(chunk_sentences(sentences, max_words, overlap))]


def load_corpus(pdf_dir: Path, policy: AccessPolicy, max_words: int = 90, overlap: int = 1) -> list[Chunk]:
    """Load every PDF listed in the policy. A PDF that is not listed is ignored,
    so nothing can become searchable without an owner company."""
    chunks: list[Chunk] = []
    for company in policy.companies.values():
        for doc in company.documents:
            path = Path(pdf_dir) / doc
            if not path.exists():
                raise FileNotFoundError(f"{doc} is listed for {company.name} but missing from {pdf_dir}")
            chunks.extend(load_pdf(path, company.id, max_words, overlap))
    return chunks
