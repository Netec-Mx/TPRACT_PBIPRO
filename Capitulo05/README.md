# Productividad Asistida por IA: Documentación Técnica y Generación de Insights

## Metadatos

| Campo | Detalle |
|---|---|
| **Duración estimada** | 74 minutos |
| **Complejidad** | Media |
| **Nivel Bloom** | Crear |
| **Módulo** | 5 — Productividad Asistida por IA |
| **Laboratorio previo requerido** | Lab 04 (modelo semántico desplegado en Power BI Service) |
| **Archivo de inicio** | `AdventureWorks_Lab04_Final.pbix` + `AdventureWorks_Lab04_Final.bim` |

---

## Descripción General

En este laboratorio integrarás tres dimensiones de IA aplicada al desarrollo Power BI: uso de **Copilot en Power BI Service** para generar narrativas e insights asistidos, **automatización de documentación técnica** del modelo semántico mediante Python y el archivo `.bim`, y **asistencia DAX con LLMs** para generar, revisar y refactorizar expresiones complejas. Trabajarás con el modelo semántico construido en los laboratorios anteriores (Adventure Works extendido) y producirás artefactos concretos: un documento Markdown con el diccionario de datos, un catálogo de medidas explicadas y un catálogo de prompts validados para uso futuro.

El principio rector del laboratorio es que **la IA resume y acelera, pero no sustituye la validación humana**. Cada output generado por IA será verificado contra los datos reales del modelo antes de considerarse válido.

---

## Objetivos de Aprendizaje

Al finalizar este laboratorio, serás capaz de:

- [ ] Activar y utilizar el panel de Copilot en Power BI Service para generar narrativas automáticas y evaluar críticamente su precisión frente a los datos del modelo.
- [ ] Ejecutar un script Python que parsea el archivo `.bim` exportado y genera automáticamente documentación técnica en formato Markdown (diccionario de datos, catálogo de medidas).
- [ ] Enriquecer la documentación generada realizando llamadas a la API de un LLM para producir descripciones en lenguaje natural de expresiones DAX complejas.
- [ ] Aplicar técnicas de prompt engineering específicas para DAX, validar las sugerencias recibidas con DAX Studio y documentar un catálogo de prompts efectivos reutilizables.

---

## Prerrequisitos

### Conocimientos previos

- Comprensión del modelo semántico Adventure Works desarrollado en Labs 1–4.
- Familiaridad básica con Python (lectura de JSON, llamadas HTTP/API).
- Conocimiento de expresiones DAX de nivel intermedio (contexto de filtro, CALCULATE, funciones de inteligencia de tiempo).
- Haber completado el Lab 04 o disponer del archivo de solución `AdventureWorks_Lab04_Final.pbix` publicado en Power BI Service.

### Acceso y licencias

| Recurso | Requisito |
|---|---|
| Power BI Service | Licencia **Pro** o **Premium Per User (PPU)** |
| Copilot en Power BI | Capacidad **Fabric F64+** o tenant con Copilot habilitado por el administrador |
| OpenAI API | Clave de API válida (GPT-3.5-turbo o superior) **o** acceso a Azure OpenAI **o** Ollama local con Llama 3/Mistral |
| Tabular Editor 2 (TE2) | Versión gratuita 2.x — suficiente para este laboratorio |
| Python 3.10+ | Con librerías `pandas`, `openai`, `json` instaladas |

> **⚠️ Nota importante:** Si Copilot no está disponible en tu tenant, el instructor proporcionará una grabación de demostración para la Parte A. Las Partes B y C no requieren Copilot y pueden completarse de forma independiente.

---

## Entorno de Laboratorio

### Hardware recomendado

| Componente | Mínimo | Recomendado |
|---|---|---|
| RAM | 16 GB | 32 GB |
| Procesador | Intel i5 8ª gen / Ryzen 5 | Intel i7/i9 o Ryzen 7 |
| Almacenamiento libre | 50 GB SSD | 100 GB SSD |
| Pantalla | 1920×1080 | Dual monitor o 2K/4K |
| Conectividad | 10 Mbps | 25 Mbps+ |

### Software requerido

| Herramienta | Versión | Propósito en este lab |
|---|---|---|
| Power BI Desktop | Junio 2024+ | Verificación local de medidas |
| Power BI Service | Siempre actualizado | Copilot, publicación |
| Python | 3.10+ | Automatización de documentación |
| Visual Studio Code | 1.85+ | Edición de scripts y Markdown |
| DAX Studio | 3.1.x+ | Validación de expresiones DAX |
| Tabular Editor 2 | 2.x | Exportación del archivo .bim |
| Navegador web | Edge/Chrome 120+ | Acceso a Power BI Service |

### Configuración inicial del entorno

**Paso 1 — Verificar instalación de Python y librerías:**

```bash
python --version
# Debe mostrar Python 3.10.x o superior

pip install openai pandas
# Si ya están instaladas, actualizarlas:
pip install --upgrade openai pandas
```

**Paso 2 — Crear la carpeta de trabajo del laboratorio:**

```bash
mkdir C:\LabAI
mkdir C:\LabAI\docs
mkdir C:\LabAI\scripts
mkdir C:\LabAI\prompts
```

**Paso 3 — Verificar acceso a la API de LLM (elegir una opción):**

*Opción A — OpenAI API:*
```bash
# Establecer la variable de entorno con tu API key
setx OPENAI_API_KEY "sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
# Verificar (abrir nueva terminal):
echo %OPENAI_API_KEY%
```

*Opción B — Ollama local (sin costo):*
```bash
# Descargar e instalar Ollama desde https://ollama.ai
ollama pull llama3
ollama serve
# El servidor queda disponible en http://localhost:11434
```

**Paso 4 — Exportar el archivo `.bim` desde Tabular Editor 2:**

1. Abrir Tabular Editor 2.
2. Ir a **File → Open → From Power BI Desktop** y seleccionar `AdventureWorks_Lab04_Final.pbix` (Power BI Desktop debe estar abierto con ese archivo).
3. En el menú **File → Save As**, seleccionar formato **Model.bim** y guardar en `C:\LabAI\AdventureWorks.bim`.

> **✅ Verificación:** El archivo `AdventureWorks.bim` debe tener un tamaño mayor a 50 KB y ser legible como JSON válido en VS Code.

---

## Pasos del Laboratorio

---

### Parte A — Copilot en Power BI Service: Narrativas e Insights Asistidos

**Duración estimada: 20 minutos**

---

#### Paso A.1 — Activar Copilot y explorar el panel

**Objetivo:** Verificar que Copilot está disponible en el workspace y familiarizarse con su interfaz antes de generar contenido.

**Instrucciones:**

1. Abrir el navegador y navegar a `https://app.powerbi.com`.
2. Seleccionar el **Workspace** habilitado para Copilot (el instructor indicará el nombre específico; generalmente contiene "Lab05" o "Copilot-Enabled").
3. Abrir el reporte `AdventureWorks_Lab04_Final` publicado en ese workspace.
4. En la cinta superior del reporte, hacer clic en el ícono de **Copilot** (ícono de chispa/estrella). Si no aparece, verificar con el instructor que el workspace tiene capacidad habilitada.
5. Observar el panel lateral de Copilot que se despliega a la derecha. Identificar:
   - El campo de entrada de texto (prompt).
   - Las sugerencias de acciones rápidas.
   - El historial de conversación.

**Salida esperada:** Panel de Copilot visible y activo con el mensaje de bienvenida de Fabric Copilot.

**Verificación:** El panel muestra opciones como "Summarize this page", "Suggest a visual" o similares en inglés/español según la configuración del tenant.

---

#### Paso A.2 — Generar una narrativa automática de página

**Objetivo:** Usar Copilot para producir un resumen ejecutivo de la página principal del reporte y evaluar su precisión.

**Instrucciones:**

1. Navegar a la página **"Resumen Ejecutivo"** del reporte (o la página principal con KPIs de ventas).
2. En el panel de Copilot, escribir el siguiente prompt:

   ```
   Resume las tendencias de Ventas Totales y Margen Bruto del último trimestre disponible, 
   destacando las regiones con mayor crecimiento y cualquier anomalía relevante. 
   Usa solo los datos visibles en esta página.
   ```

3. Presionar **Enter** y esperar la respuesta (10–30 segundos).
4. Leer la narrativa generada con atención crítica.
5. Abrir una hoja de cálculo Excel en blanco o el bloc de notas y registrar:
   - **Dato 1 de la narrativa:** (copiarlo textualmente)
   - **Valor real en el reporte:** (leerlo directamente de la visualización)
   - **¿Coincide?** Sí / No / Parcialmente
6. Repetir la verificación para al menos **3 afirmaciones numéricas** de la narrativa.

**Salida esperada:** Una narrativa de 3–5 párrafos con cifras específicas de ventas, márgenes y variaciones regionales.

**Verificación:** Completar la tabla de validación con mínimo 3 filas. Al menos 2 de las 3 afirmaciones deben ser verificables directamente en el reporte. Documentar cualquier discrepancia encontrada.

> **💡 Reflexión crítica:** Las discrepancias pueden ocurrir por contextos de filtro que Copilot no interpreta correctamente, por redondeos, o por inferencias incorrectas. Esto es esperado y parte del aprendizaje.

---

#### Paso A.3 — Crear una visualización asistida por lenguaje natural

**Objetivo:** Usar Copilot para agregar una nueva visualización al reporte mediante descripción en lenguaje natural.

**Instrucciones:**

1. En el panel de Copilot, escribir:

   ```
   Crea un gráfico de líneas que muestre la evolución mensual de Ventas YoY % 
   por categoría de producto para los últimos 12 meses.
   ```

2. Copilot propondrá una visualización. Hacer clic en **"Add to report"** o **"Agregar al reporte"** si la propuesta es apropiada.
3. Si la visualización no usa las medidas correctas (por ejemplo, usa una columna en lugar de la medida `[Ventas YoY %]`), documentar el problema en tu bitácora.
4. Ajustar manualmente la visualización si es necesario para que use la medida DAX correcta.
5. Guardar el reporte.

**Salida esperada:** Una nueva visualización en el reporte canvas, posiblemente con ajustes manuales aplicados.

**Verificación:** La visualización muestra datos coherentes con los valores de la medida `[Ventas YoY %]` verificados en DAX Studio o en otras visualizaciones del reporte.

---

#### Paso A.4 — Documentar hallazgos de Copilot

**Objetivo:** Consolidar una evaluación crítica estructurada de las capacidades y limitaciones de Copilot observadas.

**Instrucciones:**

1. Crear el archivo `C:\LabAI\docs\evaluacion_copilot.md` en VS Code.
2. Usar la siguiente plantilla y completarla con tus observaciones reales:

```markdown
# Evaluación de Copilot en Power BI Service
**Fecha:** YYYY-MM-DD
**Reporte:** AdventureWorks_Lab04_Final
**Workspace:** [nombre del workspace]

## Narrativa Generada — Validación

| Afirmación de Copilot | Valor en reporte | ¿Preciso? | Observación |
|---|---|---|---|
| [copiar texto] | [valor real] | Sí/No/Parcial | [nota] |
| [copiar texto] | [valor real] | Sí/No/Parcial | [nota] |
| [copiar texto] | [valor real] | Sí/No/Parcial | [nota] |

## Visualización Asistida

- **Prompt usado:** [texto del prompt]
- **Resultado inicial:** [descripción de lo que Copilot propuso]
- **Ajustes manuales requeridos:** [descripción]
- **Evaluación:** [útil / requiere mucho ajuste / no apto para producción]

## Casos de Uso de Alto Valor Identificados

1. [caso de uso donde Copilot fue útil]
2. [otro caso de uso]

## Limitaciones Identificadas

1. [limitación observada]
2. [otra limitación]

## Criterios de Validación Recomendados

- Siempre verificar afirmaciones numéricas contra la fuente de datos.
- [agregar criterio propio]
```

3. Guardar el archivo.

**Salida esperada:** Archivo `evaluacion_copilot.md` completo con datos reales del laboratorio.

**Verificación:** El archivo existe en `C:\LabAI\docs\` y contiene al menos 3 filas en la tabla de validación con valores reales (no placeholders).

---

### Parte B — Automatización de Documentación Técnica con Python

**Duración estimada: 28 minutos**

---

#### Paso B.1 — Explorar la estructura del archivo `.bim`

**Objetivo:** Comprender la estructura JSON del archivo `.bim` para identificar los elementos que se documentarán.

**Instrucciones:**

1. Abrir VS Code y abrir el archivo `C:\LabAI\AdventureWorks.bim`.
2. Usar `Ctrl+Shift+P` → "Format Document" para formatear el JSON.
3. Explorar la estructura y localizar los siguientes elementos (usar `Ctrl+F` para buscar):
   - `"tables"` — lista de tablas del modelo.
   - `"measures"` — dentro de cada tabla, las medidas DAX.
   - `"columns"` — columnas de cada tabla.
   - `"relationships"` — relaciones entre tablas.
   - `"calculationGroups"` — grupos de cálculo (si existen del Lab 2).
4. Anotar la ruta JSON de las medidas: `model.tables[n].measures[m].expression`.

**Salida esperada:** Comprensión de la jerarquía JSON: `model → tables → [measures, columns, relationships]`.

**Verificación:** Puedes identificar al menos 5 medidas DAX en el archivo `.bim` con sus expresiones completas.

---

#### Paso B.2 — Crear el script de extracción de metadatos

**Objetivo:** Desarrollar un script Python que parsea el `.bim` y genera un documento Markdown con el diccionario de datos completo.

**Instrucciones:**

1. Crear el archivo `C:\LabAI\scripts\generar_documentacion.py` en VS Code.
2. Copiar y completar el siguiente script:

```python
#!/usr/bin/env python3
"""
Script: generar_documentacion.py
Propósito: Parsear archivo .bim de Power BI y generar documentación Markdown
Lab: 05-00-01 - Productividad Asistida por IA
"""

import json
import os
from datetime import datetime

# ── Configuración ──────────────────────────────────────────────────────────────
BIM_FILE = r"C:\LabAI\AdventureWorks.bim"
OUTPUT_DIR = r"C:\LabAI\docs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "diccionario_datos.md")

# ── Carga del archivo .bim ─────────────────────────────────────────────────────
def cargar_bim(ruta: str) -> dict:
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

# ── Generadores de secciones Markdown ─────────────────────────────────────────
def generar_encabezado(nombre_modelo: str) -> str:
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""# Diccionario de Datos — {nombre_modelo}

> **Generado automáticamente:** {fecha}  
> **Fuente:** Archivo .bim exportado desde Tabular Editor 2  
> **Advertencia:** Revisar y validar antes de publicar en repositorio oficial.

---

"""

def generar_seccion_tablas(tablas: list) -> str:
    sb = ["## Tablas del Modelo\n\n"]
    sb.append("| Tabla | Tipo | N.° Columnas | N.° Medidas | Descripción |\n")
    sb.append("|---|---|---|---|---|\n")
    for tabla in tablas:
        nombre = tabla.get("name", "N/A")
        tipo = "Calculation Group" if tabla.get("calculationGroup") else "Regular"
        n_cols = len(tabla.get("columns", []))
        n_meds = len(tabla.get("measures", []))
        desc = tabla.get("description", "*(sin descripción)*")
        sb.append(f"| {nombre} | {tipo} | {n_cols} | {n_meds} | {desc} |\n")
    sb.append("\n")
    return "".join(sb)

def generar_seccion_columnas(tablas: list) -> str:
    sb = ["## Columnas por Tabla\n\n"]
    for tabla in tablas:
        nombre_tabla = tabla.get("name", "N/A")
        columnas = tabla.get("columns", [])
        if not columnas:
            continue
        sb.append(f"### Tabla: {nombre_tabla}\n\n")
        sb.append("| Columna | Tipo de Dato | Formato | Oculta | Descripción |\n")
        sb.append("|---|---|---|---|---|\n")
        for col in columnas:
            # Omitir columnas de tipo RowNumber (internas)
            if col.get("type") == "rowNumber":
                continue
            col_nombre = col.get("name", "N/A")
            col_tipo = col.get("dataType", "N/A")
            col_formato = col.get("formatString", "")
            col_oculta = "Sí" if col.get("isHidden", False) else "No"
            col_desc = col.get("description", "*(sin descripción)*")
            sb.append(f"| {col_nombre} | {col_tipo} | {col_formato} | {col_oculta} | {col_desc} |\n")
        sb.append("\n")
    return "".join(sb)

def generar_seccion_medidas(tablas: list) -> str:
    sb = ["## Catálogo de Medidas DAX\n\n"]
    total_medidas = 0
    for tabla in tablas:
        nombre_tabla = tabla.get("name", "N/A")
        medidas = tabla.get("measures", [])
        if not medidas:
            continue
        sb.append(f"### Tabla: {nombre_tabla}\n\n")
        for medida in medidas:
            total_medidas += 1
            m_nombre = medida.get("name", "N/A")
            m_expr = medida.get("expression", "N/A")
            m_formato = medida.get("formatString", "")
            m_carpeta = medida.get("displayFolder", "")
            m_desc = medida.get("description", "*(sin descripción — pendiente de documentar)*")
            m_oculta = "Sí" if medida.get("isHidden", False) else "No"
            sb.append(f"#### {m_nombre}\n\n")
            sb.append(f"- **Tabla:** {nombre_tabla}\n")
            sb.append(f"- **Carpeta de exhibición:** {m_carpeta if m_carpeta else '*(raíz)*'}\n")
            sb.append(f"- **Formato:** {m_formato if m_formato else '*(predeterminado)*'}\n")
            sb.append(f"- **Oculta:** {m_oculta}\n")
            sb.append(f"- **Descripción:** {m_desc}\n\n")
            sb.append("```DAX\n")
            sb.append(m_expr.strip() if isinstance(m_expr, str) else str(m_expr))
            sb.append("\n```\n\n")
            sb.append("---\n\n")
    sb.insert(1, f"> **Total de medidas documentadas:** {total_medidas}\n\n")
    return "".join(sb)

def generar_seccion_relaciones(relaciones: list) -> str:
    sb = ["## Relaciones del Modelo\n\n"]
    sb.append("| # | Tabla Origen | Columna Origen | Tabla Destino | Columna Destino | Cardinalidad | Activa |\n")
    sb.append("|---|---|---|---|---|---|---|\n")
    for i, rel in enumerate(relaciones, 1):
        origen_tabla = rel.get("fromTable", "N/A")
        origen_col = rel.get("fromColumn", "N/A")
        destino_tabla = rel.get("toTable", "N/A")
        destino_col = rel.get("toColumn", "N/A")
        cardinalidad = rel.get("fromCardinality", "many") + "→" + rel.get("toCardinality", "one")
        activa = "Sí" if rel.get("isActive", True) else "No"
        sb.append(f"| {i} | {origen_tabla} | {origen_col} | {destino_tabla} | {destino_col} | {cardinalidad} | {activa} |\n")
    sb.append("\n")
    return "".join(sb)

# ── Función principal ──────────────────────────────────────────────────────────
def main():
    print(f"[INFO] Cargando archivo .bim: {BIM_FILE}")
    bim = cargar_bim(BIM_FILE)
    
    # Navegar a la estructura del modelo
    modelo = bim.get("model", bim)  # Algunos .bim tienen nivel "model", otros no
    nombre_modelo = bim.get("name", "AdventureWorks")
    tablas = modelo.get("tables", [])
    relaciones = modelo.get("relationships", [])
    
    print(f"[INFO] Tablas encontradas: {len(tablas)}")
    print(f"[INFO] Relaciones encontradas: {len(relaciones)}")
    
    # Generar documento Markdown
    contenido = []
    contenido.append(generar_encabezado(nombre_modelo))
    contenido.append(generar_seccion_tablas(tablas))
    contenido.append(generar_seccion_relaciones(relaciones))
    contenido.append(generar_seccion_columnas(tablas))
    contenido.append(generar_seccion_medidas(tablas))
    
    documento = "".join(contenido)
    
    # Guardar el documento
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(documento)
    
    print(f"[OK] Documentación generada: {OUTPUT_FILE}")
    print(f"[INFO] Tamaño del documento: {len(documento):,} caracteres")

if __name__ == "__main__":
    main()
```

3. Guardar el archivo.
4. Ejecutar el script desde la terminal:

```bash
cd C:\LabAI\scripts
python generar_documentacion.py
```

**Salida esperada:**
```
[INFO] Cargando archivo .bim: C:\LabAI\AdventureWorks.bim
[INFO] Tablas encontradas: 8
[INFO] Relaciones encontradas: 7
[OK] Documentación generada: C:\LabAI\docs\diccionario_datos.md
[INFO] Tamaño del documento: 45,230 caracteres
```
*(Los números variarán según el modelo real)*

**Verificación:** Abrir `C:\LabAI\docs\diccionario_datos.md` en VS Code y confirmar que:
- La sección "Tablas del Modelo" lista todas las tablas del modelo.
- Al menos una medida DAX aparece con su expresión completa en bloque de código.
- La sección de relaciones tiene al menos 5 filas.

---

#### Paso B.3 — Enriquecer la documentación con descripciones generadas por LLM

**Objetivo:** Extender el script para llamar a la API de un LLM y generar descripciones en lenguaje natural de las medidas DAX más complejas.

**Instrucciones:**

1. Crear el archivo `C:\LabAI\scripts\enriquecer_medidas.py`:

```python
#!/usr/bin/env python3
"""
Script: enriquecer_medidas.py
Propósito: Usar LLM para generar descripciones en lenguaje natural de medidas DAX
Lab: 05-00-01 - Productividad Asistida por IA
"""

import json
import os
import time

# ── Configuración ──────────────────────────────────────────────────────────────
BIM_FILE = r"C:\LabAI\AdventureWorks.bim"
OUTPUT_FILE = r"C:\LabAI\docs\catalogo_medidas_enriquecido.md"
GLOSARIO_FILE = r"C:\LabAI\docs\glosario_negocio.txt"

# Configuración del LLM — elegir una opción:
# Opción A: OpenAI API
USE_OPENAI = True  # Cambiar a False para usar Ollama
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-3.5-turbo"

# Opción B: Ollama local
OLLAMA_BASE_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"

# Controles de costo y velocidad
MAX_MEDIDAS_A_PROCESAR = 10   # Limitar para el laboratorio (evitar costos excesivos)
DELAY_ENTRE_LLAMADAS = 1      # Segundos entre llamadas a la API

# ── Glosario de negocio (contexto para el LLM) ────────────────────────────────
GLOSARIO_DEFAULT = """
Glosario del modelo Adventure Works:
- Ventas: Total de ingresos netos por ventas de productos, después de descuentos.
- Margen Bruto: Diferencia entre Ventas y Costo de Ventas.
- Calendario: Tabla de fechas marcada como tabla de fechas en el modelo.
- Producto: Tabla de dimensión con jerarquía Categoría > Subcategoría > Producto.
- Cliente: Tabla de dimensión con información demográfica y geográfica.
- YoY: Year over Year — comparación interanual.
- MTD/QTD/YTD: Month/Quarter/Year To Date — acumulados de período.
- [Ventas]: Medida base que suma el campo SalesAmount de la tabla FactSales.
"""

# ── Función de llamada al LLM ──────────────────────────────────────────────────
def llamar_llm(prompt: str) -> str:
    """Llama al LLM configurado y retorna la respuesta como string."""
    if USE_OPENAI:
        return llamar_openai(prompt)
    else:
        return llamar_ollama(prompt)

def llamar_openai(prompt: str) -> str:
    """Llama a la API de OpenAI."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un experto en Power BI y DAX. Tu tarea es explicar "
                        "expresiones DAX en lenguaje claro para analistas de negocio. "
                        "Usa SOLO el glosario y contexto proporcionado. "
                        "No inventes KPIs ni supuestos que no estén en el prompt. "
                        "Si falta información, indícalo explícitamente."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.2  # Baja temperatura para respuestas más deterministas
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERROR en llamada OpenAI: {e}]"

def llamar_ollama(prompt: str) -> str:
    """Llama a Ollama local."""
    import urllib.request
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }).encode("utf-8")
    try:
        req = urllib.request.Request(
            OLLAMA_BASE_URL,
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            resultado = json.loads(resp.read().decode("utf-8"))
            return resultado.get("response", "[Sin respuesta]").strip()
    except Exception as e:
        return f"[ERROR en llamada Ollama: {e}]"

# ── Construcción del prompt para una medida ───────────────────────────────────
def construir_prompt(nombre: str, expresion: str, glosario: str) -> str:
    return f"""Glosario del modelo:
{glosario}

Medida DAX a explicar:
Nombre: {nombre}
Expresión:
```DAX
{expresion}
```

Tarea: Explica en 2-3 frases qué calcula esta medida, qué contexto de filtro utiliza 
y cuándo sería útil para un analista de negocio.

Formato de respuesta requerido:
- **Descripción:** [explicación en lenguaje natural]
- **Contexto de filtro:** [cómo interactúa con filtros/segmentadores]
- **Caso de uso:** [cuándo usar esta medida]

Restricciones: No cambies nombres técnicos. No inventes supuestos fuera del glosario."""

# ── Función principal ──────────────────────────────────────────────────────────
def main():
    # Cargar glosario
    if os.path.exists(GLOSARIO_FILE):
        with open(GLOSARIO_FILE, "r", encoding="utf-8") as f:
            glosario = f.read()
        print(f"[INFO] Glosario cargado desde: {GLOSARIO_FILE}")
    else:
        glosario = GLOSARIO_DEFAULT
        print("[INFO] Usando glosario predeterminado del script")
    
    # Cargar .bim
    with open(BIM_FILE, "r", encoding="utf-8") as f:
        bim = json.load(f)
    
    modelo = bim.get("model", bim)
    tablas = modelo.get("tables", [])
    
    # Recopilar todas las medidas
    todas_medidas = []
    for tabla in tablas:
        for medida in tabla.get("measures", []):
            todas_medidas.append({
                "tabla": tabla.get("name", "N/A"),
                "nombre": medida.get("name", "N/A"),
                "expresion": medida.get("expression", ""),
                "carpeta": medida.get("displayFolder", ""),
            })
    
    print(f"[INFO] Total de medidas en el modelo: {len(todas_medidas)}")
    
    # Seleccionar medidas más complejas (criterio: longitud de expresión)
    medidas_complejas = sorted(
        [m for m in todas_medidas if len(m.get("expresion", "")) > 50],
        key=lambda x: len(x.get("expresion", "")),
        reverse=True
    )[:MAX_MEDIDAS_A_PROCESAR]
    
    print(f"[INFO] Procesando las {len(medidas_complejas)} medidas más complejas...")
    
    # Generar documento enriquecido
    lineas = [
        "# Catálogo de Medidas DAX — Descripciones Generadas por IA\n\n",
        "> **Nota:** Las descripciones fueron generadas por un LLM. ",
        "Deben ser revisadas por un desarrollador Power BI antes de publicarse.\n\n",
        f"> **Modelo LLM usado:** {'OpenAI ' + OPENAI_MODEL if USE_OPENAI else 'Ollama ' + OLLAMA_MODEL}\n\n",
        "---\n\n"
    ]
    
    for i, medida in enumerate(medidas_complejas, 1):
        print(f"[{i}/{len(medidas_complejas)}] Procesando: {medida['nombre']}...")
        
        prompt = construir_prompt(medida["nombre"], medida["expresion"], glosario)
        descripcion_ia = llamar_llm(prompt)
        
        lineas.append(f"## {medida['nombre']}\n\n")
        lineas.append(f"- **Tabla:** {medida['tabla']}\n")
        lineas.append(f"- **Carpeta:** {medida['carpeta'] if medida['carpeta'] else '*(raíz)*'}\n\n")
        lineas.append("### Expresión DAX\n\n")
        lineas.append("```DAX\n")
        lineas.append(medida["expresion"].strip())
        lineas.append("\n```\n\n")
        lineas.append("### Descripción Generada por IA\n\n")
        lineas.append(descripcion_ia)
        lineas.append("\n\n")
        lineas.append("### Validación\n\n")
        lineas.append("- [ ] Revisado por desarrollador DAX\n")
        lineas.append("- [ ] Validado contra datos reales en DAX Studio\n")
        lineas.append("- [ ] Aprobado para publicación\n\n")
        lineas.append("---\n\n")
        
        # Pausa entre llamadas para respetar rate limits
        if i < len(medidas_complejas):
            time.sleep(DELAY_ENTRE_LLAMADAS)
    
    # Guardar documento
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.writelines(lineas)
    
    print(f"\n[OK] Catálogo enriquecido generado: {OUTPUT_FILE}")
    print(f"[INFO] Medidas procesadas: {len(medidas_complejas)}")
    print(f"[AVISO] Revisar y validar todas las descripciones antes de publicar.")

if __name__ == "__main__":
    main()
```

2. Guardar el archivo.
3. Ejecutar el script:

```bash
python C:\LabAI\scripts\enriquecer_medidas.py
```

4. Monitorear la salida en consola. Cada medida procesada mostrará su número de progreso.

**Salida esperada:**
```
[INFO] Usando glosario predeterminado del script
[INFO] Total de medidas en el modelo: 24
[INFO] Procesando las 10 medidas más complejas...
[1/10] Procesando: Ventas YoY %...
[2/10] Procesando: Margen Bruto Acumulado YTD...
...
[OK] Catálogo enriquecido generado: C:\LabAI\docs\catalogo_medidas_enriquecido.md
[INFO] Medidas procesadas: 10
[AVISO] Revisar y validar todas las descripciones antes de publicar.
```

**Verificación:** Abrir `catalogo_medidas_enriquecido.md` en VS Code y confirmar que:
- Cada medida tiene una sección "Descripción Generada por IA" con contenido real (no errores).
- El formato de respuesta del LLM incluye los tres campos: Descripción, Contexto de filtro, Caso de uso.
- Las casillas de validación `[ ]` están presentes y sin marcar (pendientes de revisión humana).

---

#### Paso B.4 — Validar una descripción generada con DAX Studio

**Objetivo:** Establecer el flujo de validación humana comprobando que la descripción de IA para la medida `Ventas YoY %` es semánticamente correcta.

**Instrucciones:**

1. Abrir DAX Studio y conectarlo al modelo (Power BI Desktop abierto con `AdventureWorks_Lab04_Final.pbix`).
2. Ejecutar la siguiente consulta DAX para obtener valores de referencia:

```DAX
EVALUATE
SUMMARIZECOLUMNS(
    'Calendario'[Año],
    'Calendario'[NombreMes],
    "Ventas_Actual", [Ventas],
    "Ventas_YoY_Pct", [Ventas YoY %]
)
ORDER BY 'Calendario'[Año] DESC, 'Calendario'[NombreMes]
```

3. Revisar los resultados y confirmar que:
   - `Ventas_YoY_Pct` es `NULL` para el primer año del dataset (no hay año anterior).
   - Los valores son porcentajes decimales (p. ej., 0.12 = 12%).
   - El cálculo es coherente con la descripción generada por el LLM.

4. Abrir `catalogo_medidas_enriquecido.md` y localizar la entrada de `Ventas YoY %`.
5. En la sección "Validación", marcar las casillas según corresponda:
   - `[x] Revisado por desarrollador DAX` — si la descripción es correcta.
   - `[x] Validado contra datos reales en DAX Studio` — después de ejecutar la consulta.
6. Si la descripción del LLM es incorrecta o incompleta, agregar una nota de corrección debajo de la descripción.

**Salida esperada:** Consulta DAX ejecutada con resultados numéricos, y al menos una entrada en el catálogo con las casillas de validación marcadas.

**Verificación:** El archivo `catalogo_medidas_enriquecido.md` tiene al menos una medida con `[x]` en las casillas de revisión y validación.

---

### Parte C — Asistencia DAX con IA y Catálogo de Prompts

**Duración estimada: 26 minutos**

---

#### Paso C.1 — Practicar prompt engineering para generación de DAX

**Objetivo:** Aprender a construir prompts efectivos para solicitar medidas DAX a un LLM, incluyendo el contexto del modelo necesario para obtener respuestas correctas.

**Instrucciones:**

1. Abrir el navegador y acceder a la interfaz del LLM que estés usando (ChatGPT, Azure OpenAI Playground, o la interfaz web de Ollama si aplica).
2. **Experimento 1 — Prompt sin contexto (ejemplo de lo que NO hacer):**
   
   Enviar este prompt y observar la respuesta:
   ```
   Escribe una medida DAX para calcular las ventas del trimestre anterior.
   ```
   
   Anotar en tu bitácora: ¿La respuesta es genérica? ¿Usa nombres de tablas/columnas que no existen en tu modelo?

3. **Experimento 2 — Prompt con contexto estructurado (template correcto):**

   Enviar este prompt completo:
   ```
   ## Contexto del modelo Power BI
   
   Modelo: Adventure Works (ventas retail)
   
   Tablas relevantes:
   - FactSales: columnas SalesAmount (decimal), OrderDate (date), ProductKey (int), CustomerKey (int)
   - Calendario: tabla de fechas marcada, columnas Fecha (date), Año (int), Trimestre (int), Mes (int)
   - Producto: ProductKey (int), NombreProducto (text), Categoría (text), Subcategoría (text)
   
   Medidas existentes:
   - [Ventas] = SUMX(FactSales, FactSales[SalesAmount])
   
   Relaciones:
   - FactSales[OrderDate] → Calendario[Fecha] (muchos a uno, activa)
   - FactSales[ProductKey] → Producto[ProductKey] (muchos a uno, activa)
   
   ## Tarea
   
   Crea una medida DAX llamada "Ventas Trimestre Anterior" que calcule el total de ventas 
   del trimestre calendario inmediatamente anterior al período seleccionado en el reporte.
   
   ## Restricciones
   - Usa solo las tablas y columnas descritas arriba.
   - No uses funciones obsoletas de DAX.
   - Si necesitas una función de inteligencia de tiempo, úsala correctamente con la tabla de fechas marcada.
   - Agrega comentarios en el DAX para explicar cada paso.
   
   ## Formato de respuesta
   1. Expresión DAX completa con comentarios.
   2. Explicación de 2-3 frases de cómo funciona.
   3. Advertencias o supuestos que debo verificar.
   ```

4. Copiar la medida DAX generada por el LLM.

**Salida esperada:** Una expresión DAX estructurada, probablemente usando `CALCULATE`, `PREVIOUSQUARTER` o `DATEADD` con referencia correcta a la tabla `Calendario`.

**Verificación:** La expresión generada referencia la tabla `Calendario` (no `Date` u otro nombre genérico) y usa `[Ventas]` como medida base.

---

#### Paso C.2 — Validar la medida generada en DAX Studio

**Objetivo:** Establecer el flujo de validación obligatorio para cualquier DAX generado por IA antes de incorporarlo al modelo.

**Instrucciones:**

1. En DAX Studio (conectado al modelo), ejecutar la medida generada como consulta de prueba:

```DAX
-- Reemplazar [EXPRESION_GENERADA] con el DAX del LLM
EVALUATE
SUMMARIZECOLUMNS(
    'Calendario'[Año],
    'Calendario'[Trimestre],
    "Ventas_Actual", [Ventas],
    "Ventas_Q_Anterior", 
    CALCULATE(
        [Ventas],
        PREVIOUSQUARTER('Calendario'[Fecha])
        -- O la expresión que el LLM haya generado
    )
)
ORDER BY 'Calendario'[Año] DESC, 'Calendario'[Trimestre] DESC
```

2. Verificar los resultados:
   - ¿El Q1 de cada año muestra las ventas del Q4 del año anterior en la columna "Ventas_Q_Anterior"?
   - ¿Los valores son coherentes con los datos esperados?
   - ¿Hay valores NULL inesperados?

3. Si la medida funciona correctamente, agregarla al modelo en Power BI Desktop:
   - En Power BI Desktop, ir a la vista de **Datos** o **Modelo**.
   - Seleccionar la tabla `FactSales`.
   - Ir a **Modelado → Nueva medida** y pegar la expresión validada.
   - Guardar el archivo `.pbix`.

4. Si la medida tiene errores, usar el siguiente prompt de corrección:

```
La medida DAX que generaste produce el siguiente error/resultado incorrecto:
[DESCRIBIR EL ERROR O RESULTADO INCORRECTO]

El resultado esperado es:
[DESCRIBIR QUÉ DEBERÍA MOSTRAR]

¿Puedes corregir la expresión? Mantén las mismas restricciones del prompt anterior.
```

**Salida esperada:** Medida validada con resultados correctos en DAX Studio, o iteración de corrección documentada.

**Verificación:** La consulta en DAX Studio retorna filas con valores numéricos en ambas columnas (Ventas_Actual y Ventas_Q_Anterior) para al menos los últimos 4 trimestres del dataset.

---

#### Paso C.3 — Construir el catálogo de prompts efectivos

**Objetivo:** Documentar un catálogo reutilizable de prompts validados para las tareas DAX más comunes en el entorno de trabajo.

**Instrucciones:**

1. Crear el archivo `C:\LabAI\prompts\catalogo_prompts_dax.md` en VS Code.
2. Usar la siguiente estructura y completar con los prompts usados en este laboratorio más los que diseñes:

```markdown
# Catálogo de Prompts para Asistencia DAX con IA

> **Versión:** 1.0  
> **Autor:** [Tu nombre]  
> **Fecha:** YYYY-MM-DD  
> **Modelo LLM probado:** GPT-3.5-turbo / Llama 3 (indicar cuál usaste)

---

## Estructura Recomendada de Prompt DAX

Todo prompt efectivo para DAX debe incluir:
1. **Contexto del modelo** — tablas, columnas relevantes, medidas existentes, relaciones.
2. **Tarea específica** — qué calcular, con qué nombre, en qué tabla.
3. **Restricciones** — nombres exactos a usar, funciones a evitar, supuestos.
4. **Formato de respuesta** — DAX con comentarios + explicación + advertencias.

---

## Prompt 01 — Generación de Medida Nueva

**Caso de uso:** Crear una medida DAX desde cero con contexto del modelo.  
**Efectividad observada:** Alta / Media / Baja *(completar después de probar)*  
**Validado en DAX Studio:** Sí / No

### Template

```
## Contexto del modelo Power BI
[DESCRIBIR TABLAS, COLUMNAS Y MEDIDAS RELEVANTES]

## Tarea
Crea una medida DAX llamada "[NOMBRE]" que calcule [DESCRIPCIÓN DEL CÁLCULO].

## Restricciones
- Usa solo las tablas y columnas descritas.
- [RESTRICCIONES ADICIONALES]

## Formato de respuesta
1. Expresión DAX con comentarios.
2. Explicación de 2-3 frases.
3. Advertencias o supuestos a verificar.
```

---

## Prompt 02 — Explicación de Medida Existente

**Caso de uso:** Generar descripción en lenguaje natural para documentación.  
**Efectividad observada:** [completar]  
**Validado:** [completar]

### Template

```
## Glosario del modelo
[INSERTAR GLOSARIO]

## Medida a explicar
Nombre: [NOMBRE]
Expresión DAX:
```DAX
[EXPRESION]
```

## Tarea
Explica en 2-3 frases qué calcula esta medida, qué contexto de filtro utiliza 
y cuándo sería útil para un analista de negocio.

## Restricciones
- No inventes supuestos fuera del glosario.
- No cambies nombres técnicos.
- Si falta información, indícalo.

## Formato
- **Descripción:** 
- **Contexto de filtro:** 
- **Caso de uso:** 
```

---

## Prompt 03 — Refactorización de DAX

**Caso de uso:** Mejorar rendimiento o legibilidad de una medida existente.  
**Efectividad observada:** [completar]  
**Validado:** [completar]

### Template

```
## Contexto
[DESCRIBIR EL MODELO]

## Medida actual (con problema identificado)
```DAX
[EXPRESION ACTUAL]
```

## Problema identificado
[DESCRIBIR: rendimiento lento / difícil de mantener / usa funciones obsoletas / etc.]

## Tarea
Refactoriza esta medida para [OBJETIVO: mejorar rendimiento / aumentar legibilidad / etc.].
Mantén el mismo resultado semántico.

## Restricciones
- El resultado debe ser idéntico al original.
- Usa variables (VAR) para mejorar legibilidad si aplica.
- No cambies el nombre de la medida.

## Formato
1. Medida refactorizada con comentarios explicando los cambios.
2. Lista de cambios realizados y justificación.
3. Cómo verificar que el resultado es idéntico.
```

---

## Prompt 04 — Diagnóstico de Error DAX

**Caso de uso:** Identificar y corregir errores en expresiones DAX.  
**Efectividad observada:** [completar]  
**Validado:** [completar]

### Template

```
## Contexto del modelo
[DESCRIBIR TABLAS Y RELACIONES RELEVANTES]

## Medida con error
```DAX
[EXPRESION CON ERROR]
```

## Error o comportamiento incorrecto
[DESCRIBIR: mensaje de error / resultado inesperado / valores NULL donde no deberían estar]

## Resultado esperado
[DESCRIBIR QUÉ DEBERÍA CALCULAR]

## Tarea
Identifica la causa del error y proporciona la versión corregida.

## Formato
1. Diagnóstico del problema (causa raíz).
2. Expresión DAX corregida.
3. Explicación del cambio realizado.
```

---

## Registro de Prompts Usados en Este Laboratorio

| # | Tarea | Prompt usado | Resultado | ¿Requirió iteración? |
|---|---|---|---|---|
| 1 | Ventas Trimestre Anterior | Prompt 01 | [resultado] | Sí/No |
| 2 | Explicar Ventas YoY % | Prompt 02 | [resultado] | Sí/No |
| ... | ... | ... | ... | ... |

---

## Lecciones Aprendidas

### Qué funciona bien
- [observación 1]
- [observación 2]

### Qué no funciona bien
- [limitación 1]
- [limitación 2]

### Mejores prácticas identificadas
1. Siempre incluir el contexto del modelo (tablas y columnas exactas).
2. [agregar práctica propia]
3. [agregar práctica propia]
```

3. Completar el catálogo con los prompts y resultados reales del laboratorio.
4. Guardar el archivo.

**Salida esperada:** Archivo `catalogo_prompts_dax.md` con al menos 2 prompts documentados y el registro de prompts usados en el laboratorio.

**Verificación:** El catálogo tiene el campo "Efectividad observada" y "Validado en DAX Studio" completados con valores reales (no placeholders) para al menos 2 prompts.

---

## Validación y Pruebas del Laboratorio

Al finalizar los tres bloques, ejecutar la siguiente lista de verificación completa:

### Lista de verificación final

| # | Verificación | Criterio de éxito | Estado |
|---|---|---|---|
| 1 | Archivo `evaluacion_copilot.md` existe | Mínimo 3 afirmaciones validadas en tabla | `[ ]` |
| 2 | Script `generar_documentacion.py` ejecuta sin errores | Archivo `diccionario_datos.md` generado con tablas, columnas y medidas | `[ ]` |
| 3 | Script `enriquecer_medidas.py` ejecuta sin errores | Archivo `catalogo_medidas_enriquecido.md` con ≥5 medidas y descripciones de IA | `[ ]` |
| 4 | Validación en DAX Studio completada | Al menos 1 medida con casillas `[x]` en el catálogo enriquecido | `[ ]` |
| 5 | Medida "Ventas Trimestre Anterior" generada por LLM | Medida validada en DAX Studio y agregada al modelo `.pbix` | `[ ]` |
| 6 | Catálogo de prompts creado | Mínimo 2 prompts documentados con efectividad y estado de validación | `[ ]` |
| 7 | Estructura de carpetas correcta | `C:\LabAI\docs\`, `C:\LabAI\scripts\`, `C:\LabAI\prompts\` con archivos correspondientes | `[ ]` |

### Prueba de integridad de la documentación generada

Ejecutar en terminal para verificar que todos los archivos existen y tienen contenido:

```bash
for %f in (
  "C:\LabAI\docs\diccionario_datos.md"
  "C:\LabAI\docs\catalogo_medidas_enriquecido.md"
  "C:\LabAI\docs\evaluacion_copilot.md"
  "C:\LabAI\prompts\catalogo_prompts_dax.md"
) do (
  if exist %f (
    echo [OK] Existe: %f
  ) else (
    echo [FALTA] No encontrado: %f
  )
)
```

**Resultado esperado:** Cuatro líneas `[OK]` sin ninguna `[FALTA]`.

---

## Solución de Problemas

### Problema 1 — El script Python falla con `KeyError` o `JSONDecodeError` al parsear el `.bim`

**Síntomas:**
- El script `generar_documentacion.py` termina con un traceback mostrando `KeyError: 'tables'` o `json.decoder.JSONDecodeError`.
- El archivo `diccionario_datos.md` no se genera o está vacío.

**Causa:**
La estructura JSON del archivo `.bim` puede variar según la versión de Tabular Editor y el nivel de compatibilidad del modelo. Algunos archivos `.bim` tienen la estructura `{ "model": { "tables": [...] } }` mientras que otros (especialmente modelos PBIP) tienen `{ "tables": [...] }` directamente en la raíz. Adicionalmente, si el archivo fue exportado con codificación diferente a UTF-8, el parser de JSON puede fallar.

**Solución:**
1. Abrir el archivo `.bim` en VS Code y verificar la estructura de primer nivel:
   ```bash
   # En PowerShell, ver las primeras 5 líneas del archivo:
   Get-Content "C:\LabAI\AdventureWorks.bim" -TotalCount 5
   ```
2. Si la raíz del JSON tiene `"tables"` directamente (sin clave `"model"`), modificar la línea en el script:
   ```python
   # Cambiar esta línea en generar_documentacion.py:
   modelo = bim.get("model", bim)
   # Por esta si el .bim tiene estructura plana:
   modelo = bim  # sin nivel "model"
   ```
3. Si el error es de codificación, exportar nuevamente desde Tabular Editor 2 asegurándose de que VS Code muestra "UTF-8" en la barra de estado inferior al abrir el archivo.
4. Volver a ejecutar el script.

---

### Problema 2 — Las llamadas a la API del LLM retornan errores de autenticación o rate limit

**Síntomas:**
- El script `enriquecer_medidas.py` muestra mensajes como `[ERROR en llamada OpenAI: Error code: 401 - Unauthorized]` o `[ERROR en llamada OpenAI: Error code: 429 - Too Many Requests]`.
- Algunas medidas en el catálogo tienen la descripción `[ERROR en llamada OpenAI: ...]` en lugar de texto generado.

**Causa:**
El error 401 indica que la API key no está configurada correctamente o ha expirado. El error 429 indica que se ha superado el límite de solicitudes por minuto (rate limit) de la cuenta gratuita o de prueba de OpenAI.

**Solución:**
*Para error 401 (autenticación):*
1. Verificar que la variable de entorno está configurada correctamente:
   ```bash
   # En una nueva terminal (después de ejecutar setx):
   echo %OPENAI_API_KEY%
   # Debe mostrar tu API key, no una cadena vacía
   ```
2. Si está vacía, establecerla directamente en el script de forma temporal:
   ```python
   # En enriquecer_medidas.py, línea de configuración:
   OPENAI_API_KEY = "sk-TUAPIKEY"  # Solo para pruebas, no versionar este valor
   ```
3. Alternativamente, cambiar a Ollama local (`USE_OPENAI = False`) si está disponible.

*Para error 429 (rate limit):*
1. Aumentar el valor de `DELAY_ENTRE_LLAMADAS` en el script:
   ```python
   DELAY_ENTRE_LLAMADAS = 5  # Aumentar de 1 a 5 segundos
   ```
2. Reducir `MAX_MEDIDAS_A_PROCESAR` a 5 para el laboratorio:
   ```python
   MAX_MEDIDAS_A_PROCESAR = 5
   ```
3. Si el problema persiste, usar la opción de Ollama local que no tiene rate limits.

---

## Limpieza del Entorno

> **Nota:** Conservar los archivos de documentación generados ya que son entregables del laboratorio. Solo eliminar archivos temporales y cachés.

**Paso 1 — Verificar y versionar los entregables:**

```bash
# Listar todos los entregables del laboratorio
dir C:\LabAI\docs\
dir C:\LabAI\prompts\
```

**Paso 2 — Si se usó una API key temporal en el script, removerla:**

```python
# Asegurarse de que el archivo enriquecer_medidas.py NO tenga la API key hardcodeada
# Debe usar: OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
```

**Paso 3 — Comprimir los entregables para entrega:**

```bash
# Crear archivo ZIP con todos los entregables del laboratorio
powershell Compress-Archive -Path "C:\LabAI\*" -DestinationPath "C:\LabAI_Lab05_Entregables.zip"
```

**Paso 4 — Si se usó Ollama local, detener el servicio:**

```bash
# Verificar si Ollama está corriendo
tasklist | findstr ollama
# Si aparece en la lista, cerrarlo desde la bandeja del sistema o:
taskkill /IM ollama.exe /F
```

**Paso 5 — Cerrar conexiones de DAX Studio:**

- En DAX Studio, ir a **File → Close** para cerrar la conexión con Power BI Desktop.
- Guardar el archivo `.pbix` con la nueva medida "Ventas Trimestre Anterior" agregada.

---

## Resumen

En este laboratorio has construido un flujo de trabajo completo de productividad asistida por IA para el desarrollo Power BI, articulado en tres dimensiones:

**Copilot en Power BI Service:** Experimentaste de primera mano cómo las narrativas generadas automáticamente pueden acelerar la comunicación de insights, pero también identificaste la necesidad de validar cada afirmación numérica contra los datos reales. La evaluación crítica no es opcional; es parte del flujo de trabajo profesional.

**Automatización de documentación:** Construiste scripts Python reutilizables que parsean el archivo `.bim` y producen documentación estructurada en Markdown, enriquecida con descripciones generadas por LLM. Este enfoque transforma la documentación de una tarea manual y esporádica a un proceso automatizable y versionable en Git.

**Asistencia DAX con IA:** Aprendiste que la calidad del output del LLM es directamente proporcional a la calidad del contexto que le proporcionas. Los prompts con estructura (Contexto + Tarea + Restricciones + Formato) producen resultados significativamente más precisos y útiles que las preguntas genéricas. El catálogo de prompts que construiste es un activo reutilizable para tu trabajo diario.

El principio fundamental que atraviesa todo el laboratorio: **la IA resume y acelera, pero la validación humana es obligatoria**. Las casillas de verificación en el catálogo de medidas no son decorativas; representan el contrato de calidad que separa un output de IA de un artefacto técnico confiable.

### Recursos Adicionales

| Recurso | URL |
|---|---|
| Copilot en Microsoft Fabric — Documentación oficial | https://learn.microsoft.com/fabric/get-started/copilot-fabric-overview |
| Power BI REST API — Datasets | https://learn.microsoft.com/rest/api/power-bi/datasets/get-dataset-in-group |
| XMLA Endpoints en Power BI Premium | https://learn.microsoft.com/power-bi/enterprise/service-premium-connect-tools |
| Tabular Editor 3 — Scripting avanzado | https://docs.tabulareditor.com/te3/Advanced/Scripting.html |
| OpenAI API — Documentación Python | https://platform.openai.com/docs/libraries/python-library |
| Ollama — LLMs locales gratuitos | https://ollama.ai |
| Smart Narrative Visual en Power BI | https://learn.microsoft.com/power-bi/visuals/power-bi-visualization-smart-narrative |
| Key Influencers Visual | https://learn.microsoft.com/power-bi/visuals/power-bi-visualization-influencers |
| Power BI Project (PBIP) — Control de versiones | https://learn.microsoft.com/power-bi/developer/projects/projects-overview |

---
*Lab 05-00-01 — Versión 1.0 | Curso: Optimización Avanzada y Gobierno de Modelos Semánticos en Power BI*
