#!/usr/bin/env convertidor.py
import sys
from pathlib import Path

try:
    import cairosvg
except ImportError:
    print("❌ Instala cairosvg: pip install cairosvg")
    sys.exit(1)

svg_files = list(Path(".").glob("*.svg"))
if not svg_files:
    print("⚠️ No hay archivos .svg")
    sys.exit(0)

print(f"📁 Convirtiendo {len(svg_files)} archivos (escala 6x)...\n")

for svg in svg_files:
    png = svg.with_suffix(".png")
    if png.exists():
        png.unlink()  # reemplazar PNG antiguo

    try:
        cairosvg.svg2png(
            url=str(svg),
            write_to=str(png),
            scale=6,  # +resolución → calidad para zoom
        )
        print(f"✅ {svg.name} -> {png.name}")
    except Exception as e:
        print(f"❌ {svg.name}: {e}")
