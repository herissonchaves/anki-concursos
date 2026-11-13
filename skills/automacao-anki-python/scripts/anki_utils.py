"""Read-only Anki helpers. No network, no modification of source collections."""
from __future__ import annotations

import contextlib
import hashlib
import html
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import unicodedata
import zipfile
from urllib.parse import quote

MAX_SQLITE_UNCOMPRESSED = 512 * 1024 * 1024


def decompress_database(source, target):
    """Bound decompressed output; never fall back to the compatibility stub."""
    try:
        from compression import zstd
        reader = zstd.open(source, 'rb')
    except ImportError:
        try:
            import zstandard
        except ImportError as exc:
            raise ValueError('Backup moderno exige Python 3.14+ ou zstandard; não usar o stub legado.') from exc
        reader = zstandard.ZstdDecompressor().stream_reader(source)
    total = 0
    try:
        with reader, target.open('wb') as out:
            while chunk := reader.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_SQLITE_UNCOMPRESSED:
                    raise ValueError('Banco descomprimido excede limite de segurança')
                out.write(chunk)
    except Exception as exc:
        raise ValueError('Banco moderno inválido ou excede limite; stub legado não será usado') from exc


def register_read_collations(conn):
    # Approximation for read-only integrity checks, never use to rebuild indexes.
    conn.create_collation('unicase', lambda a, b: (a.casefold() > b.casefold()) - (a.casefold() < b.casefold()))


def plain(text: str) -> str:
    """Strip Anki markup for approximate comparison; NOT a semantic judge."""
    text = re.sub(r"\{\{c\d+::(.*?)(?:::[^{}]*)?\}\}", r"\1", text or "", flags=re.S)
    text = re.sub(r"\[sound:[^]]+\]", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(html.unescape(text).split())


def normalized(text: str) -> str:
    val = unicodedata.normalize("NFKD", plain(text)).casefold()
    val = "".join(c for c in val if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^\w]+", " ", val).split())


def digest(text: str) -> str:
    return hashlib.sha256(normalized(text).encode("utf-8")).hexdigest()[:16]


@contextlib.contextmanager
def open_colpkg(package: Path):
    """Extract only a SQLite member into a private temp file and open read-only."""
    package = Path(package)
    if not package.is_file() or package.suffix.lower() != ".colpkg":
        raise ValueError("Informe um backup .colpkg existente")
    with zipfile.ZipFile(package) as archive:
        names = set(archive.namelist())
        if len(names) != len(archive.namelist()):
            raise ValueError('ZIP com nomes duplicados')
        if 'collection.anki21b' in names:
            member = 'collection.anki21b'
        # For newer exports the legacy .anki2 may be a minimal compatibility stub.
        elif "collection.anki21" in names:
            member = "collection.anki21"
        elif "collection.anki2" in names:
            member = "collection.anki2"
        else:
            raise ValueError("Backup sem SQLite compatível (collection.anki21 ou collection.anki2). Arquivos .anki21b exigem leitor específico.")
        entry = archive.getinfo(member)
        if entry.file_size > MAX_SQLITE_UNCOMPRESSED:
            raise ValueError("Banco excede limite de segurança de 512 MiB")
        with tempfile.TemporaryDirectory(prefix="anki_ro_") as tmp:
            target = Path(tmp) / "collection.sqlite"
            if member.endswith('21b'):
                with archive.open(member) as source:
                    decompress_database(source, target)
            else:
                with archive.open(member) as source, target.open("wb") as out:
                    import shutil
                    shutil.copyfileobj(source, out, length=1024 * 1024)
            if not member.endswith('21b') and target.stat().st_size != entry.file_size:
                raise ValueError("Arquivo SQLite extraído incompleto")
            with target.open('rb') as f:
                if f.read(16) != b'SQLite format 3\x00':
                    raise ValueError('Conteúdo não é banco SQLite válido; não usar stub')
            uri = "file:" + quote(str(target), safe="/") + "?mode=ro&immutable=1"
            conn = sqlite3.connect(uri, uri=True)
            register_read_collations(conn)
            try:
                if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                    raise ValueError("Falha na integridade SQLite")
                yield conn, member, "collection.anki21b" in names
            finally:
                conn.close()


def table_names(conn: sqlite3.Connection) -> set[str]:
    return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def note_fronts(conn: sqlite3.Connection):
    """Returns note ids and first fields from Anki notes; use solely in memory."""
    if "notes" not in table_names(conn):
        return []
    try:
        return [(str(i), plain((f or "").split("\x1f")[0])) for i, f in conn.execute("SELECT id,flds FROM notes")]
    except sqlite3.DatabaseError as ex:
        raise ValueError("Não foi possível ler notas deste esquema Anki") from ex

