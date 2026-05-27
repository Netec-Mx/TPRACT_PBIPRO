# Escalabilidad de Lógica de Negocio: Implementación de Grupos de Cálculo

## 1. Metadatos

| Propiedad | Detalle |
|---|---|
| **Duración estimada** | 119 minutos |
| **Complejidad** | Alta |
| **Nivel Bloom** | Crear |
| **Módulo** | 2 — Grupos de Cálculo |
| **Laboratorio anterior requerido** | Lab 01 (modelo de ventas optimizado) |
| **Archivo de inicio** | `Lab02_Start.pbix` |
| **Archivo de solución** | `Lab02_Solution.pbix` |

---

## 2. Descripción General

En este laboratorio partirás de un modelo de ventas retail (Adventure Works extendido) que contiene decenas de medidas individuales de inteligencia de tiempo redundantes. Analizarás la lógica duplicada existente y la reemplazarás por dos Grupos de Cálculo implementados en Tabular Editor 2: un grupo de **Inteligencia de Tiempo** con 8 elementos (Current Period, YTD, QTD, MTD, PY, YoY Absolute, YoY %, Rolling 12M) y un grupo de **Escenarios de Análisis** (Actual, Budget, Forecast). Configurarás Format Strings dinámicos, la propiedad `Precedence` para la resolución de conflictos entre grupos, y validarás el comportamiento en visualizaciones con segmentadores y matrices. Al finalizar, el modelo tendrá una arquitectura de medidas limpia, mantenible y escalable.

---

## 3. Objetivos de Aprendizaje

Al completar este laboratorio serás capaz de:

- [ ] **Diseñar** la arquitectura de Grupos de Cálculo para centralizar la lógica de inteligencia de tiempo, eliminando la proliferación de medidas individuales redundantes.
- [ ] **Implementar** en Tabular Editor 2 un Grupo de Cálculo con 8 Calculation Items que incluyan expresiones DAX con `SELECTEDMEASURE()`, Format Strings dinámicos y ordinales correctos.
- [ ] **Configurar** la propiedad `Precedence` para gestionar correctamente la interacción entre el grupo de Inteligencia de Tiempo y el grupo de Escenarios de Análisis.
- [ ] **Integrar** los Grupos de Cálculo en visualizaciones Power BI mediante segmentadores de selección única y matrices, validando resultados en combinaciones de filtros complejos.
- [ ] **Ejecutar pruebas de regresión** para confirmar que las medidas base existentes no se ven afectadas negativamente por la introducción de los grupos.

---

## 4. Prerrequisitos

### Conocimiento previo

| Área | Nivel requerido |
|---|---|
| Funciones DAX de inteligencia de tiempo (`TOTALYTD`, `DATEADD`, `SAMEPERIODLASTYEAR`, `DATESMTD`, `DATESYTD`) | Sólido |
| Modelo de evaluación de filtros DAX y `CALCULATE` | Sólido |
| Modelo semántico tabular: tablas, relaciones, medidas explícitas | Intermedio |
| Tabular Editor 2 — navegación básica de la interfaz | Básico |
| Laboratorio 1 completado o archivo de solución `Lab01_Solution.pbix` disponible | Requerido |

### Acceso y licencias

- Power BI Desktop instalado (versión mínima junio 2024).
- Tabular Editor 2 instalado y registrado como herramienta externa en Power BI Desktop.
- Acceso de lectura/escritura al directorio de trabajo local (no se requiere licencia Pro para este laboratorio).
- Archivo `Lab02_Start.pbix` descargado desde el repositorio del curso.

> **⚠️ Nota sobre nivel de compatibilidad:** Los Grupos de Cálculo requieren nivel de compatibilidad **1500 o superior**. El archivo de inicio ya tiene este nivel configurado. Si trabajas con un modelo propio heredado, verifica en Tabular Editor: `Model Properties → Compatibility Level` y actualiza si es necesario antes de continuar.

---

## 5. Entorno de Laboratorio

### Hardware recomendado

| Componente | Mínimo | Recomendado |
|---|---|---|
| RAM | 16 GB | 32 GB |
| CPU | Intel Core i5 8ª gen | Intel Core i7/i9 o AMD Ryzen 7 |
| Almacenamiento libre | 10 GB SSD | 20 GB SSD |
| Pantalla | 1920×1080 | Dual monitor o 2K/4K |

### Software requerido

| Herramienta | Versión mínima | Rol en el laboratorio |
|---|---|---|
| Power BI Desktop | Junio 2024+ | Visualización y publicación |
| Tabular Editor 2 | 2.x (gratuito) | Creación de Grupos de Cálculo |
| DAX Studio | 3.1.x | Verificación de consultas DAX |
| Navegador web | Edge 120+ / Chrome 120+ | Referencia de documentación |

### Preparación del entorno

Ejecuta los siguientes pasos **antes** de comenzar el laboratorio:

**1. Verificar que Tabular Editor 2 aparece como herramienta externa:**

Abre Power BI Desktop → pestaña **Herramientas externas** → confirma que aparece el ícono de **Tabular Editor**.

> Si no aparece, descarga el instalador desde [https://github.com/TabularEditor/TabularEditor/releases](https://github.com/TabularEditor/TabularEditor/releases) y ejecuta `TabularEditor.Installer.msi`. Reinicia Power BI Desktop tras la instalación.

**2. Abrir el archivo de inicio:**

```
Archivo → Abrir → Lab02_Start.pbix
```

**3. Verificar el nivel de compatibilidad del modelo:**

En Power BI Desktop → Herramientas externas → **Tabular Editor** → en el panel izquierdo selecciona el nodo raíz `Model` → en el panel de propiedades confirma:

```
CompatibilityLevel = 1500 (o superior)
```

**4. Verificar que la tabla `Dim Fecha` está marcada como tabla de fechas:**

En Power BI Desktop → Vista de modelo → clic derecho sobre `Dim Fecha` → **Marcar como tabla de fechas** → columna: `Fecha`.

---

## 6. Instrucciones Paso a Paso

---

### Paso 1: Auditoría del Modelo — Análisis de Medidas Redundantes

**Objetivo:** Identificar y documentar las medidas de inteligencia de tiempo duplicadas en el modelo antes de reemplazarlas con Grupos de Cálculo.

**Instrucciones:**

1. Con `Lab02_Start.pbix` abierto en Power BI Desktop, ve a la **Vista de datos** (ícono de tabla en la barra lateral izquierda).

2. En el panel **Campos**, expande la tabla `_Medidas` (o la tabla donde estén agrupadas las medidas). Observa la lista completa de medidas disponibles.

3. Identifica y anota en la siguiente tabla de auditoría las medidas que siguen el patrón de inteligencia de tiempo. Busca prefijos o sufijos como `_YTD`, `_MTD`, `_PY`, `_YoY`, `_Rolling`:

   | Medida base | Variantes encontradas | Patrón DAX usado |
   |---|---|---|
   | `Importe Ventas` | `Ventas YTD`, `Ventas MTD`, `Ventas PY`, `Ventas YoY %` | `TOTALYTD`, `DATESMTD`, `SAMEPERIODLASTYEAR` |
   | `Cantidad Vendida` | `Cantidad YTD`, `Cantidad PY` | `TOTALYTD`, `SAMEPERIODLASTYEAR` |
   | `Margen Bruto` | `Margen YTD`, `Margen YoY %` | `TOTALYTD`, `DATEADD` |
   | *(añade las que encuentres)* | | |

4. Abre **Tabular Editor 2** desde la pestaña Herramientas externas.

5. En el panel izquierdo de Tabular Editor, expande **Tables → _Medidas**. Haz clic derecho sobre cualquier medida de inteligencia de tiempo (p. ej., `Ventas YTD`) y selecciona **Go to definition** para revisar su expresión DAX en el panel de edición.

6. Confirma que la lógica es idéntica entre medidas del mismo tipo (p. ej., todas las medidas `_YTD` usan `TOTALYTD` o `DATESYTD` con la misma columna de fecha). Esta redundancia es exactamente lo que eliminaremos.

**Resultado esperado:** Una lista documentada de al menos 12 medidas redundantes organizadas por tipo de cálculo (YTD, MTD, PY, YoY%). El modelo tiene entre 25 y 40 medidas en total; más del 50% son variantes derivadas de 3-4 medidas base.

**Verificación:** En Tabular Editor, el conteo de medidas en la tabla `_Medidas` debe ser visible en la barra de estado. Confirma que identificaste medidas con al menos 4 patrones distintos de inteligencia de tiempo.

---

### Paso 2: Crear el Grupo de Cálculo "Inteligencia de Tiempo" mediante Script C#

**Objetivo:** Implementar el Grupo de Cálculo principal con 8 elementos usando el Advanced Scripting de Tabular Editor para mayor precisión y reproducibilidad.

**Instrucciones:**

1. En Tabular Editor 2, ve al menú **Advanced Scripting** (o presiona `Ctrl+Shift+A` / usa el menú **Tools → Advanced Scripting**).

2. En el editor de scripts, **borra cualquier contenido existente** y pega el siguiente script completo:

```csharp
// ============================================================
// Lab 02 — Grupo de Cálculo: Inteligencia de Tiempo
// Tabular Editor 2 — Advanced Scripting (C#)
// ============================================================

// 1. Crear el grupo de cálculo
var cg = Model.AddCalculationGroup("Inteligencia de Tiempo");
cg.Description = "Grupo de cálculo para transformaciones de inteligencia de tiempo. Reemplaza medidas derivadas individuales.";
cg.Precedence = 50;

// 2. Agregar la columna visible del grupo
var col = cg.AddCalculationGroupColumn("Cálculo");
col.Description = "Selecciona el período o tipo de cálculo a aplicar.";

// ---- ELEMENTO 1: Current Period (valor base sin modificación) ----
var cp = cg.AddCalculationItem("Current Period");
cp.Expression = "SELECTEDMEASURE()";
cp.FormatStringExpression = "SELECTEDMEASUREFORMATSTRING()";
cp.Ordinal = 10;
cp.Description = "Devuelve el valor de la medida en el período actual sin modificación.";

// ---- ELEMENTO 2: YTD (Year-to-Date) ----
var ytd = cg.AddCalculationItem("YTD");
ytd.Expression = "CALCULATE( SELECTEDMEASURE(), DATESYTD('Dim Fecha'[Fecha]) )";
ytd.FormatStringExpression = "SELECTEDMEASUREFORMATSTRING()";
ytd.Ordinal = 20;
ytd.Description = "Acumulado del año hasta la fecha.";

// ---- ELEMENTO 3: QTD (Quarter-to-Date) ----
var qtd = cg.AddCalculationItem("QTD");
qtd.Expression = "CALCULATE( SELECTEDMEASURE(), DATESQTD('Dim Fecha'[Fecha]) )";
qtd.FormatStringExpression = "SELECTEDMEASUREFORMATSTRING()";
qtd.Ordinal = 30;
qtd.Description = "Acumulado del trimestre hasta la fecha.";

// ---- ELEMENTO 4: MTD (Month-to-Date) ----
var mtd = cg.AddCalculationItem("MTD");
mtd.Expression = "CALCULATE( SELECTEDMEASURE(), DATESMTD('Dim Fecha'[Fecha]) )";
mtd.FormatStringExpression = "SELECTEDMEASUREFORMATSTRING()";
mtd.Ordinal = 40;
mtd.Description = "Acumulado del mes hasta la fecha.";

// ---- ELEMENTO 5: PY (Previous Year — mismo período) ----
var py = cg.AddCalculationItem("PY");
py.Expression = "CALCULATE( SELECTEDMEASURE(), DATEADD('Dim Fecha'[Fecha], -1, YEAR) )";
py.FormatStringExpression = "SELECTEDMEASUREFORMATSTRING()";
py.Ordinal = 50;
py.Description = "Valor del mismo período del año anterior.";

// ---- ELEMENTO 6: YoY Absolute (diferencia absoluta vs año anterior) ----
var yoyAbs = cg.AddCalculationItem("YoY Absolute");
yoyAbs.Expression =
@"VAR _Current  = SELECTEDMEASURE()
VAR _Previous = CALCULATE( SELECTEDMEASURE(), DATEADD('Dim Fecha'[Fecha], -1, YEAR) )
RETURN
    _Current - _Previous";
yoyAbs.FormatStringExpression = "SELECTEDMEASUREFORMATSTRING()";
yoyAbs.Ordinal = 60;
yoyAbs.Description = "Diferencia absoluta entre el período actual y el mismo período del año anterior.";

// ---- ELEMENTO 7: YoY % (variación porcentual vs año anterior) ----
var yoyPct = cg.AddCalculationItem("YoY %");
yoyPct.Expression =
@"VAR _Current  = SELECTEDMEASURE()
VAR _Previous = CALCULATE( SELECTEDMEASURE(), DATEADD('Dim Fecha'[Fecha], -1, YEAR) )
RETURN
    DIVIDE( _Current - _Previous, ABS(_Previous) )";
yoyPct.FormatStringExpression = "\"#,##0.0%\"";
yoyPct.Ordinal = 70;
yoyPct.Description = "Variación porcentual respecto al mismo período del año anterior. Formato: porcentaje.";

// ---- ELEMENTO 8: Rolling 12M (ventana móvil de 12 meses) ----
var r12 = cg.AddCalculationItem("Rolling 12M");
r12.Expression =
@"VAR _MaxDate = MAX('Dim Fecha'[Fecha])
RETURN
    CALCULATE(
        SELECTEDMEASURE(),
        DATESINPERIOD('Dim Fecha'[Fecha], _MaxDate, -12, MONTH)
    )";
r12.FormatStringExpression = "SELECTEDMEASUREFORMATSTRING()";
r12.Ordinal = 80;
r12.Description = "Suma acumulada de los últimos 12 meses desde la fecha máxima del contexto.";

// ============================================================
// Guardar cambios en el modelo
// ============================================================
Model.SaveChanges();
Info("✅ Grupo de Cálculo 'Inteligencia de Tiempo' creado con 8 elementos.");
```

3. Haz clic en el botón **Run** (▶) o presiona `F5` para ejecutar el script.

4. Verifica que aparece el mensaje `✅ Grupo de Cálculo 'Inteligencia de Tiempo' creado con 8 elementos.` en la consola de salida.

5. En el panel izquierdo de Tabular Editor, expande el nodo **Calculation Groups**. Deberías ver la tabla `Inteligencia de Tiempo` con la columna `Cálculo` y los 8 elementos listados debajo.

6. **Guarda los cambios al modelo:** En Tabular Editor, menú **File → Save** (o `Ctrl+S`). Esto escribe los cambios al archivo `.pbix` abierto en Power BI Desktop.

7. Regresa a Power BI Desktop. Aparecerá un diálogo indicando que el modelo fue modificado externamente. Haz clic en **Actualizar ahora** para cargar los cambios.

**Resultado esperado:** En el panel **Campos** de Power BI Desktop aparece una nueva tabla llamada `Inteligencia de Tiempo` con un campo `Cálculo`. Al expandirla, se listan los 8 elementos: Current Period, YTD, QTD, MTD, PY, YoY Absolute, YoY %, Rolling 12M.

**Verificación:** En Power BI Desktop, crea una **Tarjeta** temporal y arrastra el campo `Inteligencia de Tiempo[Cálculo]` a Valores. No mostrará un número (es un campo de texto), pero confirma que el campo existe y es reconocido por el modelo sin errores.

---

### Paso 3: Configurar Format Strings Dinámicos y Validar Ordinales

**Objetivo:** Revisar y ajustar manualmente las propiedades de cada Calculation Item en la interfaz de Tabular Editor para confirmar que los Format Strings son correctos y los ordinales producen el orden esperado.

**Instrucciones:**

1. En Tabular Editor 2, expande **Calculation Groups → Inteligencia de Tiempo → Cálculo**.

2. Selecciona el elemento **YoY %**. En el panel de propiedades (derecha), verifica:
   - `Format String Expression`: debe contener `"#,##0.0%"` (con comillas dobles escapadas).
   - `Ordinal`: debe ser `70`.

3. Selecciona el elemento **YoY Absolute**. Verifica:
   - `Format String Expression`: `SELECTEDMEASUREFORMATSTRING()` — hereda el formato de la medida base.
   - `Ordinal`: `60`.

4. Selecciona el elemento **Current Period**. Verifica:
   - `Expression`: `SELECTEDMEASURE()` — sin modificación.
   - `Ordinal`: `10` — aparecerá primero en la lista.

5. Selecciona el nodo raíz **Inteligencia de Tiempo** (la tabla del grupo). En el panel de propiedades verifica:
   - `Precedence`: `50`.

6. **Ajuste de Format String para YoY Absolute con signo explícito:** Haz doble clic en el campo `Format String Expression` del elemento `YoY Absolute` y actualiza el valor a:

```
IF( SELECTEDMEASURE() >= 0, SELECTEDMEASUREFORMATSTRING(), SELECTEDMEASUREFORMATSTRING() )
```

> **Nota pedagógica:** Para la mayoría de medidas monetarias, heredar el formato base es suficiente. El signo negativo se manejará automáticamente por el formato de la medida base (p. ej., `#,##0.00 €`). No se requiere lógica adicional en este caso.

7. Guarda los cambios: **File → Save** (`Ctrl+S`) en Tabular Editor.

8. Regresa a Power BI Desktop y acepta la actualización del modelo.

**Resultado esperado:** Los 8 elementos están ordenados de la siguiente forma al expandir el campo `Cálculo` en un segmentador: Current Period → YTD → QTD → MTD → PY → YoY Absolute → YoY % → Rolling 12M.

**Verificación:** 
- Crea un **Segmentador** en una página en blanco del informe.
- Arrastra `Inteligencia de Tiempo[Cálculo]` al segmentador.
- Confirma que los 8 elementos aparecen en el orden definido por los ordinales.
- Asegúrate de que el segmentador está configurado en **Selección única** (en el panel de formato del segmentador → Controles de selección → desactiva "Selección múltiple").

---

### Paso 4: Crear una Visualización de Validación para el Grupo de Inteligencia de Tiempo

**Objetivo:** Construir una matriz que permita validar visualmente que cada Calculation Item produce el resultado correcto para la medida `Importe Ventas`.

**Instrucciones:**

1. En Power BI Desktop, crea una nueva página en el informe y nómbrala **"Validación - Time Intelligence"**.

2. Inserta una **Matriz** en la página.

3. Configura la matriz con los siguientes campos:
   - **Filas:** `Dim Fecha[Año]` y `Dim Fecha[Nombre Mes]`
   - **Columnas:** `Inteligencia de Tiempo[Cálculo]`
   - **Valores:** `[Importe Ventas]` (medida base)

4. Aplica un filtro de página para mostrar solo los años 2022 y 2023 (o los dos años más recientes disponibles en el dataset).

5. Expande la matriz para ver el nivel de mes dentro de un año (p. ej., 2023 → Enero, Febrero, ...).

6. Valida manualmente los siguientes valores para el mes de **Marzo 2023** (o el mes equivalente disponible):

   | Elemento | Comportamiento esperado |
   |---|---|
   | **Current Period** | Ventas de marzo 2023 únicamente |
   | **YTD** | Suma de ventas Enero + Febrero + Marzo 2023 |
   | **QTD** | Suma de ventas Enero + Febrero + Marzo 2023 (Q1) |
   | **MTD** | Igual a Current Period (mes completo en contexto) |
   | **PY** | Ventas de marzo 2022 |
   | **YoY Absolute** | Ventas Mar 2023 − Ventas Mar 2022 |
   | **YoY %** | (Mar 2023 − Mar 2022) / \|Mar 2022\| en formato % |
   | **Rolling 12M** | Suma de ventas Abr 2022 a Mar 2023 |

7. Para verificar **YoY %**, comprueba que el formato de celda muestra `%` (p. ej., `12.5%`) y no un decimal (p. ej., `0.125`).

8. Para verificar **Rolling 12M**, crea una medida de verificación temporal en DAX Studio:

```dax
-- Pega en DAX Studio (conectado al modelo abierto en Power BI Desktop)
EVALUATE
SUMMARIZECOLUMNS(
    'Dim Fecha'[Año],
    'Dim Fecha'[Nombre Mes Corto],
    "Importe Ventas", [Importe Ventas],
    "Rolling 12M Verificacion",
        CALCULATE(
            [Importe Ventas],
            DATESINPERIOD('Dim Fecha'[Fecha], DATE(2023,3,31), -12, MONTH)
        )
)
ORDER BY 'Dim Fecha'[Año], 'Dim Fecha'[Nombre Mes Corto]
```

> Ejecuta esta consulta en DAX Studio (conectado al modelo local) para obtener el valor de referencia y compararlo con el que muestra la matriz.

**Resultado esperado:** La matriz muestra 8 columnas con valores coherentes. El elemento `YoY %` muestra formato de porcentaje. Los valores de `YTD` son acumulativos (crecen mes a mes dentro del año). El valor `Rolling 12M` para diciembre es igual a `YTD` del mismo año si el año está completo.

**Verificación:** Selecciona el elemento **YTD** en el segmentador creado en el Paso 3. El visual de matriz debe filtrar para mostrar solo la columna YTD, y el valor del mes de diciembre debe coincidir con el total anual de `Importe Ventas`.

---

### Paso 5: Implementar el Grupo de Cálculo "Escenarios de Análisis"

**Objetivo:** Crear un segundo Grupo de Cálculo para análisis de escenarios (Actual, Budget, Forecast) con la propiedad `Precedence` correctamente configurada para interactuar con el grupo de Inteligencia de Tiempo.

**Instrucciones:**

1. Regresa a **Tabular Editor 2** (si lo cerraste, ábrelo de nuevo desde Herramientas externas en Power BI Desktop).

2. Ve a **Tools → Advanced Scripting** y pega el siguiente script:

```csharp
// ============================================================
// Lab 02 — Grupo de Cálculo: Escenarios de Análisis
// Precedencia mayor que Inteligencia de Tiempo (50)
// para que la conversión de escenario ocurra DESPUÉS del
// cálculo del período de tiempo.
// ============================================================

var cg2 = Model.AddCalculationGroup("Escenarios de Análisis");
cg2.Description = "Grupo de cálculo para seleccionar la versión de datos: Real, Presupuesto o Forecast.";
cg2.Precedence = 100; // Mayor que Inteligencia de Tiempo (50)

var col2 = cg2.AddCalculationGroupColumn("Escenario");
col2.Description = "Selecciona la versión de datos a visualizar.";

// ---- ELEMENTO 1: Actual (datos reales — comportamiento por defecto) ----
var actual = cg2.AddCalculationItem("Actual");
actual.Expression = "SELECTEDMEASURE()";
actual.FormatStringExpression = "SELECTEDMEASUREFORMATSTRING()";
actual.Ordinal = 10;
actual.Description = "Datos reales del período seleccionado.";

// ---- ELEMENTO 2: Budget (datos de presupuesto) ----
var budget = cg2.AddCalculationItem("Budget");
budget.Expression =
@"VAR _MeasureName = SELECTEDMEASURENAME()
VAR _Result =
    SWITCH(
        _MeasureName,
        ""Importe Ventas"",
            CALCULATE(
                [Importe Ventas Budget],
                ALLEXCEPT('Dim Fecha', 'Dim Fecha'[Año], 'Dim Fecha'[Mes Numero])
            ),
        ""Cantidad Vendida"",
            CALCULATE(
                [Cantidad Budget],
                ALLEXCEPT('Dim Fecha', 'Dim Fecha'[Año], 'Dim Fecha'[Mes Numero])
            ),
        SELECTEDMEASURE()  -- fallback para medidas sin versión Budget
    )
RETURN _Result";
budget.FormatStringExpression = "SELECTEDMEASUREFORMATSTRING()";
budget.Ordinal = 20;
budget.Description = "Datos de presupuesto. Usa SELECTEDMEASURENAME() para enrutar a la medida de Budget correspondiente.";

// ---- ELEMENTO 3: Forecast (proyección) ----
var forecast = cg2.AddCalculationItem("Forecast");
forecast.Expression =
@"VAR _MeasureName = SELECTEDMEASURENAME()
VAR _HasForecast =
    ISSELECTEDMEASURE([Importe Ventas]) ||
    ISSELECTEDMEASURE([Cantidad Vendida])
RETURN
    IF(
        _HasForecast,
        CALCULATE(
            SELECTEDMEASURE(),
            USERELATIONSHIP('Dim Fecha'[Fecha], 'Fact Forecast'[Fecha Forecast])
        ),
        SELECTEDMEASURE()
    )";
forecast.FormatStringExpression = "SELECTEDMEASUREFORMATSTRING()";
forecast.Ordinal = 30;
forecast.Description = "Proyección forecast. Activa una relación inactiva con la tabla Fact Forecast.";

// ---- ELEMENTO 4: Budget vs Actual % ----
var bva = cg2.AddCalculationItem("Budget vs Actual %");
bva.Expression =
@"VAR _Actual = SELECTEDMEASURE()
VAR _Budget =
    SWITCH(
        SELECTEDMEASURENAME(),
        ""Importe Ventas"", [Importe Ventas Budget],
        ""Cantidad Vendida"", [Cantidad Budget],
        BLANK()
    )
RETURN
    DIVIDE( _Actual - _Budget, ABS(_Budget) )";
bva.FormatStringExpression = "\"#,##0.0%\"";
bva.Ordinal = 40;
bva.Description = "Variación porcentual entre el valor real y el presupuesto. Formato: porcentaje.";

Model.SaveChanges();
Info("✅ Grupo de Cálculo 'Escenarios de Análisis' creado con 4 elementos. Precedencia: 100.");
```

3. Ejecuta el script con **F5** y confirma el mensaje de éxito.

4. Guarda los cambios: **File → Save** (`Ctrl+S`) en Tabular Editor.

5. Regresa a Power BI Desktop y acepta la actualización del modelo.

6. Confirma en el panel **Campos** que aparece la tabla `Escenarios de Análisis` con el campo `Escenario` y sus 4 elementos.

> **Nota sobre el modelo de datos:** El script de `Budget` y `Forecast` hace referencia a medidas (`[Importe Ventas Budget]`, `[Cantidad Budget]`) y una tabla (`Fact Forecast`) que ya existen en el archivo `Lab02_Start.pbix`. Si ves errores de referencia, verifica los nombres exactos de las medidas en el panel Campos y ajusta las cadenas en el script.

**Resultado esperado:** Dos Grupos de Cálculo en el modelo: `Inteligencia de Tiempo` (Precedencia 50) y `Escenarios de Análisis` (Precedencia 100). En el panel Campos, ambas tablas son visibles con sus respectivos campos.

**Verificación:** En Tabular Editor, selecciona el nodo `Escenarios de Análisis` y confirma `Precedence = 100`. Selecciona `Inteligencia de Tiempo` y confirma `Precedence = 50`. La diferencia de precedencia garantiza que la lógica de inteligencia de tiempo se aplica primero y el escenario se superpone después.

---

### Paso 6: Validar la Interacción entre Grupos de Cálculo (Composición)

**Objetivo:** Verificar que la combinación simultánea de un elemento de Inteligencia de Tiempo con un elemento de Escenarios produce resultados semánticamente correctos.

**Instrucciones:**

1. En Power BI Desktop, crea una nueva página llamada **"Validación - Composición de Grupos"**.

2. Inserta dos **Segmentadores** en la página:
   - **Segmentador 1:** `Inteligencia de Tiempo[Cálculo]` — Selección única activada.
   - **Segmentador 2:** `Escenarios de Análisis[Escenario]` — Selección única activada.

3. Inserta una **Tabla** con los siguientes campos:
   - `Dim Fecha[Año]`
   - `Dim Fecha[Nombre Mes]`
   - `[Importe Ventas]`

4. Prueba las siguientes combinaciones y registra los resultados:

   | Inteligencia de Tiempo | Escenario | Resultado esperado |
   |---|---|---|
   | Current Period | Actual | Ventas reales del período |
   | YTD | Actual | Ventas reales acumuladas del año |
   | Current Period | Budget | Presupuesto del período |
   | YTD | Budget | Presupuesto acumulado del año |
   | YoY % | Actual | Variación % real vs año anterior |
   | Current Period | Budget vs Actual % | Desviación % real vs presupuesto del período |

5. Para la combinación **YTD + Budget**: el valor esperado es el presupuesto acumulado año a la fecha. Verifica que el valor sea coherente (menor que el presupuesto anual total, mayor que el de un solo mes).

6. Para la combinación **YoY % + Budget**: el resultado debería mostrar la variación del presupuesto respecto al presupuesto del año anterior. Documenta si este comportamiento es el deseado para tu organización o si requiere lógica adicional con `ISSELECTEDMEASURE()`.

7. Añade una **Tarjeta** que muestre el elemento seleccionado con la siguiente medida de soporte (créala en Power BI Desktop):

```dax
Elemento Seleccionado TI = 
SELECTEDVALUE('Inteligencia de Tiempo'[Cálculo], "Ninguno")
```

```dax
Escenario Seleccionado = 
SELECTEDVALUE('Escenarios de Análisis'[Escenario], "Ninguno")
```

**Resultado esperado:** Las combinaciones de los dos grupos producen resultados lógicamente consistentes. La tarjeta refleja en tiempo real el elemento activo de cada grupo. No se producen errores de cálculo circular ni valores en blanco inesperados.

**Verificación:** Selecciona **YTD + Budget**. El valor de `Importe Ventas` en la tabla debe ser acumulativo (el valor de diciembre debe ser mayor que el de enero). Selecciona **Current Period + Budget vs Actual %**. Los valores deben ser porcentajes (con el símbolo `%` visible en las celdas).

---

### Paso 7: Implementar Lógica Condicional con ISSELECTEDMEASURE() y Prueba de Regresión

**Objetivo:** Agregar lógica condicional al elemento `YoY %` para que solo actúe sobre medidas de tipo monetario/cantidad, y ejecutar pruebas de regresión para confirmar que las medidas base no se ven afectadas.

**Instrucciones:**

1. Regresa a **Tabular Editor 2** y navega a **Calculation Groups → Inteligencia de Tiempo → Cálculo → YoY %**.

2. Actualiza la expresión del elemento `YoY %` con la siguiente versión que incluye lógica condicional:

```dax
VAR _IsApplicable =
    ISSELECTEDMEASURE( [Importe Ventas] ) ||
    ISSELECTEDMEASURE( [Cantidad Vendida] ) ||
    ISSELECTEDMEASURE( [Margen Bruto] ) ||
    ISSELECTEDMEASURE( [Costo Total] )
VAR _Current  = SELECTEDMEASURE()
VAR _Previous = CALCULATE( SELECTEDMEASURE(), DATEADD('Dim Fecha'[Fecha], -1, YEAR) )
RETURN
    IF(
        _IsApplicable,
        DIVIDE( _Current - _Previous, ABS(_Previous) ),
        SELECTEDMEASURE()  -- devuelve el valor sin modificar para medidas no aplicables
    )
```

3. Guarda los cambios en Tabular Editor (`Ctrl+S`) y actualiza en Power BI Desktop.

4. **Prueba de regresión — Parte A (medidas base sin filtro de grupo):**

   Crea una página nueva llamada **"Prueba de Regresión"**.
   
   Inserta una tabla con:
   - `Dim Fecha[Año]`
   - `[Importe Ventas]`
   - `[Cantidad Vendida]`
   - `[Margen Bruto]`
   
   **Sin ningún segmentador de Grupos de Cálculo activo**, verifica que los valores son idénticos a los que existían antes de implementar los grupos. Los Grupos de Cálculo no deben afectar los visuals que no incluyen el campo `[Cálculo]` o `[Escenario]`.

5. **Prueba de regresión — Parte B (medidas base con elemento Current Period):**

   Añade el segmentador `Inteligencia de Tiempo[Cálculo]` a la página y selecciona **Current Period**.
   
   Los valores de `[Importe Ventas]`, `[Cantidad Vendida]` y `[Margen Bruto]` deben ser **idénticos** a los de la Parte A. El elemento `Current Period` devuelve `SELECTEDMEASURE()` sin modificación.

6. **Prueba de regresión — Parte C (medida no listada en ISSELECTEDMEASURE):**

   Añade al visual una medida que **no** esté en la lista de `_IsApplicable`, por ejemplo `[% Margen]` (si existe en el modelo). Selecciona el elemento **YoY %** en el segmentador.
   
   El resultado para `[% Margen]` debe ser el valor sin modificar (el `IF` devuelve `SELECTEDMEASURE()`), mientras que `[Importe Ventas]` sí muestra la variación porcentual.

7. Documenta los resultados en la siguiente tabla de regresión:

   | Medida | Current Period = Valor Base? | YoY % aplica lógica? | Sin grupo activo = Valor Base? |
   |---|---|---|---|
   | `[Importe Ventas]` | ✅ | ✅ | ✅ |
   | `[Cantidad Vendida]` | ✅ | ✅ | ✅ |
   | `[Margen Bruto]` | ✅ | ✅ | ✅ |
   | `[% Margen]` | ✅ | ❌ (devuelve valor base) | ✅ |

**Resultado esperado:** Las medidas base no se ven afectadas cuando no hay elementos de Grupos de Cálculo activos. El elemento `Current Period` es transparente. El elemento `YoY %` solo aplica la lógica de variación a las medidas listadas en `ISSELECTEDMEASURE()`.

**Verificación:** Compara los totales anuales de `[Importe Ventas]` en la página de regresión (sin grupo activo) con los valores que tenías documentados antes del laboratorio. Deben ser idénticos al centavo.

---

### Paso 8: Integración Final en el Informe y Configuración de Segmentadores

**Objetivo:** Construir una página de informe ejecutivo que integre ambos Grupos de Cálculo de forma profesional con segmentadores configurados correctamente.

**Instrucciones:**

1. Crea una nueva página llamada **"Dashboard Ejecutivo"**.

2. Añade los siguientes elementos al lienzo:

   **Panel de control (parte superior):**
   - Segmentador `Inteligencia de Tiempo[Cálculo]` — estilo: Lista, Selección única activada, título: "Período de Análisis".
   - Segmentador `Escenarios de Análisis[Escenario]` — estilo: Lista, Selección única activada, título: "Versión de Datos".
   - Segmentador `Dim Fecha[Año]` — estilo: Menú desplegable.

   **Visualizaciones principales:**
   - **Gráfico de barras agrupadas:** Eje X = `Dim Fecha[Nombre Mes]`, Valores = `[Importe Ventas]`, `[Margen Bruto]`.
   - **Tarjeta KPI:** Valor = `[Importe Ventas]`, Objetivo = `[Importe Ventas Budget]` (si está disponible como medida).
   - **Matriz de rendimiento por categoría:** Filas = `Dim Producto[Categoría]`, Columnas = `Inteligencia de Tiempo[Cálculo]`, Valores = `[Importe Ventas]`.

3. Configura el segmentador de `Inteligencia de Tiempo[Cálculo]` para que **Current Period** sea la selección predeterminada (clic en "Current Period" y luego en el ícono de marcador de posición predeterminado en el panel de formato del segmentador, si está disponible, o usa un marcador de Power BI).

4. Crea un **Marcador** llamado `"Vista YTD"` con la selección YTD activa en el segmentador de Inteligencia de Tiempo y Actual en Escenarios. Crea otro marcador `"Vista Budget vs Actual"` con Current Period + Budget vs Actual %.

5. Añade dos **Botones** en la parte superior del lienzo vinculados a estos marcadores para permitir navegación rápida entre vistas.

6. Aplica formato condicional a la columna `YoY %` en la matriz:
   - En el panel de formato del visual → Formato condicional → Color de fondo.
   - Regla: si el valor es < 0 → rojo claro (`#FFE0E0`), si el valor es > 0 → verde claro (`#E0FFE0`).

**Resultado esperado:** Una página de informe ejecutivo funcional donde el usuario puede seleccionar el tipo de análisis temporal y la versión de datos de forma independiente, y todas las visualizaciones responden coherentemente a ambas selecciones.

**Verificación:** 
- Selecciona **YTD + Actual**: el gráfico de barras muestra valores crecientes mes a mes (acumulación correcta).
- Selecciona **Current Period + Budget vs Actual %**: la matriz muestra porcentajes con formato `%` y colores condicionales.
- Haz clic en el botón `"Vista YTD"`: los segmentadores cambian automáticamente a la configuración correcta.

---

## 7. Validación y Pruebas Finales

### Lista de verificación de completitud

Ejecuta las siguientes comprobaciones antes de considerar el laboratorio completado:

| # | Verificación | Método | ✅/❌ |
|---|---|---|---|
| 1 | El modelo contiene el grupo `Inteligencia de Tiempo` con exactamente 8 elementos | Tabular Editor → Calculation Groups | |
| 2 | El grupo `Inteligencia de Tiempo` tiene `Precedence = 50` | Tabular Editor → propiedades del grupo | |
| 3 | El elemento `YoY %` tiene `FormatStringExpression = "#,##0.0%"` | Tabular Editor → propiedades del ítem | |
| 4 | Los ordinales están en múltiplos de 10 (10, 20, 30... 80) | Tabular Editor → cada ítem | |
| 5 | El modelo contiene el grupo `Escenarios de Análisis` con 4 elementos | Tabular Editor → Calculation Groups | |
| 6 | El grupo `Escenarios de Análisis` tiene `Precedence = 100` | Tabular Editor → propiedades del grupo | |
| 7 | Las medidas base muestran valores idénticos sin grupos activos | Página "Prueba de Regresión" | |
| 8 | La combinación YTD + Budget produce valores acumulativos de presupuesto | Página "Validación - Composición" | |
| 9 | El elemento `YoY %` no modifica medidas no listadas en `ISSELECTEDMEASURE()` | Página "Prueba de Regresión" — Parte C | |
| 10 | El Dashboard Ejecutivo responde correctamente a ambos segmentadores | Página "Dashboard Ejecutivo" | |

### Consulta de validación en DAX Studio

Abre DAX Studio, conéctate al modelo local (Power BI Desktop) y ejecuta la siguiente consulta para validar los 8 elementos del grupo de Inteligencia de Tiempo:

```dax
-- Validación: todos los elementos del grupo Inteligencia de Tiempo
EVALUATE
SELECTCOLUMNS(
    'Inteligencia de Tiempo',
    "Elemento", 'Inteligencia de Tiempo'[Cálculo]
)
ORDER BY 'Inteligencia de Tiempo'[Cálculo]
```

**Resultado esperado:** 8 filas con los nombres: Budget vs Actual % *(no, ese es del otro grupo)* — los 8 elementos de Inteligencia de Tiempo en orden alfabético.

```dax
-- Validación cruzada: YTD vs suma manual para el año 2023
EVALUATE
ROW(
    "Ventas 2023 Total",
        CALCULATE( [Importe Ventas], 'Dim Fecha'[Año] = 2023 ),
    "Ventas YTD Dic 2023",
        CALCULATE(
            [Importe Ventas],
            DATESYTD('Dim Fecha'[Fecha]),
            'Dim Fecha'[Año] = 2023,
            'Dim Fecha'[Mes Numero] = 12
        )
)
```

Ambos valores deben ser **idénticos** — confirma que el elemento YTD del grupo produce el mismo resultado que la función `DATESYTD` directa.

---

## 8. Solución de Problemas

### Problema 1: Los Calculation Items No Aparecen en Power BI Desktop Después de Guardar en Tabular Editor

**Síntoma:** Después de ejecutar el script en Tabular Editor y guardar (`Ctrl+S`), al regresar a Power BI Desktop no aparece la tabla `Inteligencia de Tiempo` en el panel de Campos. O aparece el diálogo de actualización pero los campos no se reflejan correctamente.

**Causa:** Power BI Desktop no recargó automáticamente los metadatos del modelo, o el archivo `.pbix` estaba en un estado bloqueado durante la escritura de Tabular Editor. Esto ocurre con frecuencia cuando hay una consulta DAX en ejecución o un visual actualizándose en el momento del guardado.

**Solución:**
1. En Power BI Desktop, ve a **Vista → Actualizar** o cierra y vuelve a abrir el archivo `.pbix`.
2. Si el problema persiste, en Tabular Editor verifica que el modelo se guardó correctamente: **File → Save** y confirma que no hay errores en la barra de estado.
3. Alternativa: usa **File → Save to file** en Tabular Editor para guardar como un archivo `.bim` separado, luego importa los cambios manualmente.
4. Verifica que no hay otro proceso (como DAX Studio) conectado al modelo en modo exclusivo, ya que puede bloquear la escritura.
5. Como último recurso, cierra completamente Power BI Desktop y Tabular Editor, reabre el `.pbix` y vuelve a ejecutar el script.

---

### Problema 2: Error de Referencia Circular o Valores en Blanco Inesperados al Combinar Dos Grupos de Cálculo

**Síntoma:** Al seleccionar simultáneamente un elemento de `Inteligencia de Tiempo` y un elemento de `Escenarios de Análisis`, algunos visuals muestran `(En blanco)` o un error `A circular dependency was detected`. Esto ocurre especialmente con la combinación **YoY % + Budget**.

**Causa:** La combinación de dos Grupos de Cálculo con `SELECTEDMEASURE()` puede crear dependencias circulares cuando el elemento de mayor precedencia intenta evaluar `SELECTEDMEASURE()` y este a su vez contiene una referencia al elemento del grupo de menor precedencia. Adicionalmente, si el elemento `Budget` hace referencia a medidas explícitas (`[Importe Ventas Budget]`) que no existen en el modelo o tienen un nombre incorrecto, el resultado es `BLANK()`.

**Solución:**
1. **Para dependencias circulares:** Revisa la expresión del elemento de mayor precedencia (`Escenarios de Análisis`). Si contiene `SELECTEDMEASURE()` y el grupo de menor precedencia también usa `SELECTEDMEASURE()` con una función que modifica el contexto de filtro de la misma tabla de fechas, puede haber conflicto. Solución: en el elemento `Budget`, usa `CALCULATE( SELECTEDMEASURE(), ... )` con modificadores de filtro explícitos en lugar de referencias cruzadas a otros grupos.
2. **Para valores en blanco:** En Tabular Editor, verifica los nombres exactos de las medidas referenciadas. En el script del elemento `Budget`, las cadenas `"Importe Ventas Budget"` y `"Cantidad Budget"` deben coincidir exactamente (incluyendo mayúsculas y espacios) con los nombres de las medidas en el modelo. Usa el panel de Campos en Power BI Desktop para confirmar los nombres exactos.
3. **Diagnóstico con DAX Studio:** Conecta DAX Studio al modelo y ejecuta:

```dax
-- Diagnóstico: evaluar Budget en contexto específico
EVALUATE
CALCULATETABLE(
    ROW( "Budget Test", [Importe Ventas Budget] ),
    'Dim Fecha'[Año] = 2023
)
```

Si esta consulta devuelve `BLANK()`, el problema está en la medida base `[Importe Ventas Budget]`, no en el Grupo de Cálculo.

4. **Para la combinación YoY % + Budget (comportamiento por diseño):** Documenta explícitamente que esta combinación puede no ser semánticamente válida para tu organización (variación YoY del presupuesto). Considera usar `ISSELECTEDMEASURE()` en el elemento `YoY %` para devolver `BLANK()` o un mensaje de texto cuando el escenario activo es `Budget` o `Forecast`.

---

## 9. Limpieza del Entorno

Antes de cerrar el laboratorio, realiza las siguientes acciones:

1. **Guardar el archivo final:**
   ```
   Power BI Desktop → Archivo → Guardar como → Lab02_Completado_[TuNombre].pbix
   ```

2. **Eliminar medidas redundantes (opcional — solo si el instructor lo indica):**
   En Tabular Editor, selecciona las medidas individuales de inteligencia de tiempo que ahora están reemplazadas por los Grupos de Cálculo (p. ej., `Ventas YTD`, `Ventas MTD`, `Ventas PY`). Haz clic derecho → **Delete**. Guarda los cambios.
   
   > ⚠️ **Precaución:** Solo elimina medidas si has confirmado que ningún visual existente las referencia directamente. Usa la función **Analyze in Excel** o revisa el panel de **Performance Analyzer** para identificar referencias activas antes de eliminar.

3. **Cerrar DAX Studio** si está abierto para liberar la conexión al modelo.

4. **Cerrar Tabular Editor** para evitar conflictos de escritura concurrente con Power BI Desktop.

5. **Archivar el script C# utilizado:**
   Guarda los scripts de Advanced Scripting en archivos `.cs` separados:
   - `Lab02_Script_TimeIntelligence_CG.cs`
   - `Lab02_Script_AnalysisScenarios_CG.cs`
   
   Estos scripts son reutilizables en otros modelos del proyecto.

6. **Documentar los grupos creados** en el catálogo semántico del equipo (archivo `Catalogo_Semantico.xlsx` o equivalente):

   | Grupo | Elementos | Precedencia | Medidas base aplicables |
   |---|---|---|---|
   | Inteligencia de Tiempo | 8 (Current Period → Rolling 12M) | 50 | Todas las medidas numéricas |
   | Escenarios de Análisis | 4 (Actual, Budget, Forecast, Budget vs Actual %) | 100 | Importe Ventas, Cantidad Vendida |

---

## 10. Resumen y Próximos Pasos

### Conceptos Clave Aplicados

En este laboratorio implementaste una arquitectura de **Grupos de Cálculo** que transforma la escalabilidad del modelo semántico:

| Concepto | Implementación realizada |
|---|---|
| **SELECTEDMEASURE()** | Función central en todos los Calculation Items; actúa como proxy de la medida activa en contexto |
| **FormatStringExpression** | Heredado con `SELECTEDMEASUREFORMATSTRING()` para medidas acumulativas; explícito (`"#,##0.0%"`) para porcentajes |
| **Ordinal** | Controla el orden de presentación en segmentadores y ejes de matrices |
| **Precedence** | `50` para Inteligencia de Tiempo (se aplica primero); `100` para Escenarios (se aplica después) |
| **ISSELECTEDMEASURE()** | Lógica condicional en `YoY %` para limitar la transformación a medidas aplicables |
| **SELECTEDMEASURENAME()** | Enrutamiento en el elemento `Budget` para seleccionar la medida de presupuesto correcta |
| **Pruebas de regresión** | Verificación sistemática de que las medidas base no se ven afectadas |

### Impacto en el Modelo

El modelo pasó de **~35 medidas individuales** (con alta redundancia) a una arquitectura donde:
- Las medidas base son **3-5 medidas fundamentales** (`Importe Ventas`, `Margen Bruto`, `Cantidad Vendida`, etc.).
- La lógica de inteligencia de tiempo está centralizada en **8 Calculation Items** reutilizables.
- La lógica de escenarios está centralizada en **4 Calculation Items** adicionales.
- Cualquier nueva medida base automáticamente hereda todas las transformaciones de los grupos sin crear medidas derivadas adicionales.

### Próximos Pasos

- **Lab 03:** El modelo con los Grupos de Cálculo implementados será la base para las técnicas de optimización de performance. Analizarás el impacto de los Grupos de Cálculo en el rendimiento del motor VertiPaq usando DAX Studio y VertiPaq Analyzer.
- **Extensión opcional:** Implementa un tercer Grupo de Cálculo de **Conversión de Moneda** con elementos `Moneda Local`, `USD (TC Actual)` y `USD (TC Promedio)`, asignando una precedencia de `150` para que se aplique como última capa sobre los grupos existentes.
- **Documentación:** Añade descripciones detalladas a cada Calculation Item en Tabular Editor (campo `Description`) para facilitar el onboarding de nuevos desarrolladores al modelo.

### Recursos de Referencia

| Recurso | URL |
|---|---|
| Calculation Groups — Microsoft Learn | https://learn.microsoft.com/analysis-services/tabular-models/calculation-groups |
| SELECTEDMEASURE() — DAX Guide | https://dax.guide/selectedmeasure/ |
| ISSELECTEDMEASURE() — DAX Guide | https://dax.guide/isselectedmeasure/ |
| Introduction to Calculation Groups — SQLBI | https://www.sqlbi.com/articles/calculation-groups/ |
| Tabular Editor 2 — Calculation Groups Docs | https://docs.tabulareditor.com/te2/Calculation-Groups.html |
| Dynamic Format Strings — Power BI | https://learn.microsoft.com/power-bi/transform-model/dynamic-format-strings |

---
