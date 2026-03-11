# backend/mcp_server.py
import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path

# Path ke folder Data_Analis (relatif dari backend/)
DATA_DIR = Path(__file__).parent / "Data_Analis"

def list_files():
    """Tampilkan semua file yang tersedia di Data_Analis"""
    files = list(DATA_DIR.iterdir())
    return [f.name for f in files if f.is_file()]

def read_file(filename: str):
    """Baca file berdasarkan nama & ekstensi"""
    filepath = DATA_DIR / filename

    # Keamanan: pastikan file ada di dalam DATA_DIR saja
    if not filepath.resolve().is_relative_to(DATA_DIR.resolve()):
        raise ValueError("Akses ditolak!")
    if not filepath.exists():
        raise FileNotFoundError(f"{filename} tidak ditemukan")

    ext = filepath.suffix.lower()

    if ext == ".json":
        with open(filepath) as f:
            return json.load(f)          # → dict Python

    elif ext == ".md":
        with open(filepath) as f:
            return f.read()             # → string teks

    elif ext == ".xml":
        tree = ET.parse(filepath)
        root = tree.getroot()
        return ET.tostring(root, encoding="unicode")  # → string XML

    else:
        raise ValueError(f"Format {ext} belum didukung")