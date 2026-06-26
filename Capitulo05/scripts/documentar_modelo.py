#!/usr/bin/env python3
"""Genera un Data Dictionary Markdown desde un modelo Power BI.

Soporta dos entradas:
1. Un archivo .bim exportado desde Tabular Editor.
2. Una carpeta PBIP/TMDL que contenga archivos .tmdl.

El parser TMDL es intencionalmente simple: extrae nombres de tablas, columnas,
medidas y expresiones cuando están presentes en texto. Si no encuentra metadatos,
genera una plantilla canónica del laboratorio.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

CANONICAL_TABLES = [
    {"name": "FactVentas", "description": "Ventas transaccionales", "columns": ["OrderDate", "ProductKey", "CustomerKey", "CanalKey", "PromocionKey", "Cantidad", "ImporteVenta", "ImporteCosto", "OrderMonthDate"]},
    {"name": "DimFecha", "description": "Calendario corporativo", "columns": ["DateKey", "Date", "Year", "QuarterNumber", "MonthNumber", "MonthName"]},
    {"name": "DimProducto", "description": "Productos y jerarquías", "columns": ["ProductKey", "ProductName", "Category", "Subcategory", "Brand"]},
    {"name": "DimCliente", "description": "Clientes y segmento", "columns": ["CustomerKey", "CustomerName", "CustomerSegment", "GeographyKey"]},
    {"name": "DimGeografia", "description": "País, región y ciudad", "columns": ["GeographyKey", "Country", "Region", "City"]},
    {"name": "FactPresupuesto", "description": "Presupuesto mensual", "columns": ["DateKey", "ImporteVentaBudget", "CantidadBudget"]},
    {"name": "FactForecast", "description": "Forecast mensual", "columns": ["DateKey", "ImporteVentaForecast", "CantidadForecast"]},
    {"name": "FactVentas_Agg", "description": "Agregación mes x producto x geografía", "columns": ["OrderMonthDate", "ProductKey", "GeographyKey", "TotalImporteVenta", "TotalCantidad", "TotalImporteCosto", "TransactionCount"]},
]

CANONICAL_MEASURES = [
    {"table": "_Medidas", "name": "Ventas", "expression": "SUM(FactVentas[ImporteVenta])"},
    {"table": "_Medidas", "name": "Costo", "expression": "SUM(FactVentas[ImporteCosto])"},
    {"table": "_Medidas", "name": "Unidades", "expression": "SUM(FactVentas[Cantidad])"},
    {"table": "_Medidas", "name": "Margen", "expression": "[Ventas] - [Costo]"},
    {"table": "_Medidas", "name": "Margen %", "expression": "DIVIDE([Margen], [Ventas], 0)"},
    {"table": "_Medidas", "name": "Ventas Budget", "expression": "SUM(FactPresupuesto[ImporteVentaBudget])"},
    {"table": "_Medidas", "name": "Ventas Forecast", "expression": "SUM(FactForecast[ImporteVentaForecast])"},
    {"table": "_Medidas", "name": "Ventas Budget vs Actual %", "expression": "CALCULATE([Ventas], 'Escenarios de Análisis'[Escenario] = \"Budget vs Actual %\")"},
]


def parse_bim(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    model = data.get("model", data)
    tables = []
    measures = []
    relationships = []

    for table in model.get("tables", []):
        t = {
            "name": table.get("name", ""),
            "description": table.get("description", ""),
            "columns": [],
        }
        for col in table.get("columns", []):
            t["columns"].append({
                "name": col.get("name", ""),
                "dataType": col.get("dataType", ""),
                "description": col.get("description", ""),
            })
        for measure in table.get("measures", []):
            expr = measure.get("expression", "")
            if isinstance(expr, list):
                expr = "\n".join(expr)
            measures.append({
                "table": t["name"],
                "name": measure.get("name", ""),
                "expression": expr,
                "description": measure.get("description", ""),
            })
        tables.append(t)

    for rel in model.get("relationships", []):
        relationships.append({
            "fromTable": rel.get("fromTable", ""),
            "fromColumn": rel.get("fromColumn", ""),
            "toTable": rel.get("toTable", ""),
            "toColumn": rel.get("toColumn", ""),
            "isActive": rel.get("isActive", True),
        })

    return {"tables": tables, "measures": measures, "relationships": relationships}


def parse_tmdl_folder(path: Path) -> Dict[str, Any]:
    tables: Dict[str, Dict[str, Any]] = {}
    measures: List[Dict[str, str]] = []
    relationships: List[Dict[str, str]] = []

    table_re = re.compile(r"^\s*table\s+'?([^'\n]+)'?", re.IGNORECASE)
    column_re = re.compile(r"^\s*column\s+'?([^'=\n]+)'?", re.IGNORECASE)
    measure_re = re.compile(r"^\s*measure\s+'?([^'=\n]+)'?\s*=\s*(.*)$", re.IGNORECASE)
    relationship_re = re.compile(r"^\s*relationship\s+'?([^'\n]+)'?", re.IGNORECASE)

    current_table = None
    for file in path.rglob("*.tmdl"):
        text = file.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            m = table_re.match(line)
            if m:
                current_table = m.group(1).strip()
                tables.setdefault(current_table, {"name": current_table, "description": "", "columns": []})
                continue
            m = column_re.match(line)
            if m and current_table:
                col = m.group(1).strip()
                tables[current_table]["columns"].append({"name": col, "dataType": "", "description": ""})
                continue
            m = measure_re.match(line)
            if m:
                measures.append({
                    "table": current_table or file.stem,
                    "name": m.group(1).strip(),
                    "expression": m.group(2).strip(),
                    "description": "",
                })
                continue
            m = relationship_re.match(line)
            if m:
                relationships.append({"name": m.group(1).strip()})

    return {"tables": list(tables.values()), "measures": measures, "relationships": relationships}


def canonical_model() -> Dict[str, Any]:
    tables = []
    for t in CANONICAL_TABLES:
        tables.append({
            "name": t["name"],
            "description": t["description"],
            "columns": [{"name": c, "dataType": "", "description": ""} for c in t["columns"]],
        })
    return {"tables": tables, "measures": CANONICAL_MEASURES, "relationships": []}


def md_escape(text: Any) -> str:
    return str(text or "").replace("|", "\\|").replace("\n", "<br>")


def render_markdown(model: Dict[str, Any], source: str) -> str:
    lines: List[str] = []
    lines.append("# Data Dictionary - Modelo Ventas Retail")
    lines.append("")
    lines.append(f"Fuente analizada: `{source}`")
    lines.append("")
    lines.append("## Tablas y columnas")
    lines.append("")

    for table in model.get("tables", []):
        lines.append(f"### {md_escape(table.get('name'))}")
        desc = table.get("description") or "Pendiente de descripción funcional."
        lines.append("")
        lines.append(f"{md_escape(desc)}")
        lines.append("")
        lines.append("| Columna | Tipo | Descripción |")
        lines.append("|---|---|---|")
        cols = table.get("columns") or []
        if not cols:
            lines.append("| Pendiente |  |  |")
        for col in cols:
            if isinstance(col, str):
                lines.append(f"| {md_escape(col)} |  | Pendiente |")
            else:
                lines.append(f"| {md_escape(col.get('name'))} | {md_escape(col.get('dataType'))} | {md_escape(col.get('description') or 'Pendiente')} |")
        lines.append("")

    lines.append("## Medidas")
    lines.append("")
    lines.append("| Tabla | Medida | Expresión | Descripción |")
    lines.append("|---|---|---|---|")
    measures = model.get("measures") or []
    if not measures:
        lines.append("| _Medidas | Pendiente |  | No se detectaron medidas automáticamente. |")
    for m in measures:
        lines.append(f"| {md_escape(m.get('table'))} | {md_escape(m.get('name'))} | `{md_escape(m.get('expression'))}` | {md_escape(m.get('description') or 'Pendiente')} |")
    lines.append("")

    lines.append("## Relaciones")
    lines.append("")
    rels = model.get("relationships") or []
    if rels:
        lines.append("| Desde | Hacia | Activa |")
        lines.append("|---|---|---|")
        for r in rels:
            if "fromTable" in r:
                src = f"{r.get('fromTable')}[{r.get('fromColumn')}]"
                dst = f"{r.get('toTable')}[{r.get('toColumn')}]"
                lines.append(f"| {md_escape(src)} | {md_escape(dst)} | {md_escape(r.get('isActive'))} |")
            else:
                lines.append(f"| {md_escape(r.get('name'))} |  |  |")
    else:
        lines.append("No se detectaron relaciones automáticamente. Documenta manualmente las relaciones críticas:")
        lines.append("")
        lines.append("- `DimFecha[Date] -> FactVentas[OrderDate]`")
        lines.append("- `DimProducto[ProductKey] -> FactVentas[ProductKey]`")
        lines.append("- `DimCliente[CustomerKey] -> FactVentas[CustomerKey]`")
        lines.append("- `DimGeografia[GeographyKey] -> DimCliente[GeographyKey]`")
        lines.append("- `DimGeografia[GeographyKey] -> FactVentas_Agg[GeographyKey]`")
    lines.append("")

    lines.append("## Validación humana")
    lines.append("")
    lines.append("Completa esta sección después de revisar el diccionario generado.")
    lines.append("")
    lines.append("| Pregunta | Respuesta |")
    lines.append("|---|---|")
    lines.append("| ¿Los nombres coinciden con las guías del curso? |  |")
    lines.append("| ¿Hay medidas sin descripción? |  |")
    lines.append("| ¿Hay columnas sensibles? |  |")
    lines.append("| ¿La RLS está documentada? |  |")
    lines.append("")
    return "\n".join(lines)


def load_model(input_path: Path) -> Dict[str, Any]:
    if input_path.is_file() and input_path.suffix.lower() == ".bim":
        return parse_bim(input_path)
    if input_path.is_dir():
        model = parse_tmdl_folder(input_path)
        if model["tables"] or model["measures"]:
            return model
    return canonical_model()


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera un Data Dictionary Markdown desde BIM o TMDL/PBIP.")
    parser.add_argument("--input", required=True, help="Ruta a archivo .bim o carpeta PBIP/TMDL")
    parser.add_argument("--out", required=True, help="Ruta de salida .md")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.out)
    model = load_model(input_path)
    markdown = render_markdown(model, str(input_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"Data Dictionary generado: {output_path}")


if __name__ == "__main__":
    main()
