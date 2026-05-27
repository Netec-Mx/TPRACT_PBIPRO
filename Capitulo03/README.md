# Ingeniería de Performance: Eficiencia de Carga y Respuesta de Consultas

## 1. Metadatos

| Atributo | Valor |
|---|---|
| **Duración estimada** | 119 minutos |
| **Complejidad** | Alta |
| **Nivel Bloom** | Crear |
| **Módulo** | 3 — Ingeniería de Performance |
| **Laboratorio previo requerido** | Lab 01-00-01 y Lab 02-00-01 |
| **Archivo de inicio** | `Lab03_Start.pbix` (proporcionado por el instructor) |
| **Archivo de solución** | `Lab03_Solution.pbix` |

---

## 2. Descripción General

En este laboratorio aplicarás una estrategia integral de optimización de rendimiento sobre un modelo Power BI de gran escala que contiene una tabla de hechos con millones de registros de transacciones de ventas retail. Trabajarás en tres fases sucesivas: primero diagnosticarás y corregirás cuellos de botella en el pipeline de Power Query asegurando Query Folding e implementando Incremental Refresh; luego analizarás medidas DAX con DAX Studio para identificar trabajo innecesario en el Formula Engine y las reescribirás aplicando patrones de optimización; finalmente implementarás una capa de agregaciones Import sobre la tabla de hechos para acelerar consultas de nivel resumen sin sacrificar la granularidad de detalle. Al completar el laboratorio habrás construido un modelo semántico de producción con rendimiento medible y documentado.

---

## 3. Objetivos de Aprendizaje

Al finalizar este laboratorio serás capaz de:

- [ ] **Diagnosticar** cuellos de botella en la carga de datos utilizando el Diagnóstico de consultas de Power Query y el Performance Analyzer de Power BI Desktop, identificando pasos que rompen el Query Folding.
- [ ] **Optimizar** pipelines de Power Query aplicando Query Folding, tipado temprano, eliminación de pasos innecesarios y configuración de Incremental Refresh para la tabla de hechos principal.
- [ ] **Analizar** el rendimiento de medidas DAX con DAX Studio (Server Timings y Query Plan), distinguiendo el trabajo del Storage Engine frente al Formula Engine.
- [ ] **Reescribir** medidas DAX costosas aplicando patrones de optimización: variables `VAR/RETURN`, `CALCULATE` con modificadores de filtro, `REMOVEFILTERS`/`KEEPFILTERS` y funciones de agregación nativas.
- [ ] **Implementar** una tabla de agregaciones sobre la tabla de hechos para resolver consultas de resumen sin acceder a la granularidad de detalle.

---

## 4. Prerrequisitos

### Conocimientos requeridos

| Área | Nivel mínimo |
|---|---|
| Power Query / lenguaje M | Intermedio — transformaciones encadenadas, tipos de datos, parámetros |
| Query Folding | Conceptual — saber cuándo ocurre y qué pasos lo rompen |
| DAX | Intermedio-avanzado — `CALCULATE`, iteradores `SUMX`/`AVERAGEX`, `VAR/RETURN` |
| DAX Studio | Básico — conectar a un modelo, ejecutar consultas, activar Server Timings |
| Laboratorios anteriores | Haber completado Lab 01 y Lab 02 o disponer de los archivos de solución |

### Acceso y herramientas

| Herramienta | Versión mínima | Estado requerido |
|---|---|---|
| Power BI Desktop | Junio 2024 o superior | Instalado y activado |
| DAX Studio | 3.1.x o superior | Instalado, conecta a Power BI Desktop |
| Tabular Editor 2 | 2.x | Instalado (opcional para verificar particiones) |
| SQL Server / Azure SQL | Cualquier edición con acceso al dataset de práctica | Accesible desde la máquina |
| VertiPaq Analyzer | Integrado en DAX Studio | Disponible vía DAX Studio |

> **Nota sobre el dataset:** El instructor proveerá la cadena de conexión al servidor SQL con la base de datos `SalesDW_Lab` que contiene la tabla `dbo.FactSales` con entre 5 y 10 millones de filas. Si el hardware tiene menos de 16 GB RAM, solicita al instructor la versión reducida de 1–2 millones de filas.

---

## 5. Entorno de Laboratorio

### Hardware recomendado

| Recurso | Mínimo | Recomendado |
|---|---|---|
| RAM | 16 GB | 32 GB |
| CPU | Intel i5 8ª gen / Ryzen 5 | Intel i7/i9 o Ryzen 7 |
| Almacenamiento libre | 10 GB SSD | 20 GB SSD |
| Pantalla | 1920×1080 | Dual monitor o 2K/4K |

### Configuración inicial del entorno

Antes de comenzar los ejercicios, ejecuta los siguientes pasos de preparación:

**Paso A — Verificar la conexión al servidor SQL:**

```powershell
# Desde PowerShell, verifica conectividad al servidor de práctica
Test-NetConnection -ComputerName "sql-lab-server" -Port 1433
```

**Paso B — Abrir el archivo de inicio:**

1. Abre Power BI Desktop.
2. Abre el archivo `Lab03_Start.pbix` proporcionado por el instructor.
3. Cuando se solicite, actualiza las credenciales de la fuente de datos con las proporcionadas en el aula.

**Paso C — Verificar que DAX Studio puede conectarse:**

1. Con `Lab03_Start.pbix` abierto en Power BI Desktop, abre DAX Studio.
2. En la pantalla de conexión selecciona **PBI / SSDT Model** y elige el modelo `Lab03_Start`.
3. Confirma que la conexión es exitosa y que aparece el listado de tablas en el panel izquierdo.

**Paso D — Anotar métricas de línea base:**

Antes de optimizar, registra los tiempos iniciales en la siguiente tabla (la completarás durante el laboratorio):

| Métrica | Valor inicial | Valor final |
|---|---|---|
| Tiempo de refresh completo (segundos) | _____ | _____ |
| Tiempo DAX — Medida `Ventas Brutas` (ms) | _____ | _____ |
| Tiempo DAX — Medida `Clientes Activos` (ms) | _____ | _____ |
| Tiempo DAX — Medida `Margen %` (ms) | _____ | _____ |
| Memoria modelo VertiPaq (MB) | _____ | _____ |

---

## 6. Procedimiento Paso a Paso

El laboratorio se divide en **tres fases** y **ocho pasos**:

| Fase | Pasos | Duración aprox. |
|---|---|---|
| **Fase 1:** Diagnóstico y optimización de Power Query | 1 – 3 | 40 min |
| **Fase 2:** Diagnóstico y optimización de medidas DAX | 4 – 6 | 45 min |
| **Fase 3:** Implementación de agregaciones | 7 – 8 | 34 min |

---

### FASE 1: Diagnóstico y Optimización de Power Query

---

### Paso 1 — Diagnosticar el Pipeline de Power Query con Query Diagnostics

**Objetivo:** Identificar qué pasos de transformación en la consulta `FactSales` rompen el Query Folding y cuánto tiempo consumen, usando el Diagnóstico de consultas integrado en Power Query.

#### Instrucciones

1. En Power BI Desktop, ve a la pestaña **Inicio** → **Transformar datos** para abrir el Editor de Power Query.

2. En el panel izquierdo, selecciona la consulta **FactSales**.

3. Haz clic derecho sobre cualquier paso en el panel **Pasos aplicados** (excepto el último) y selecciona **Ver consulta nativa** (*View Native Query*).
   - Si la opción está disponible y muestra SQL, el folding está activo hasta ese punto.
   - Si la opción aparece en gris (*greyed out*), el folding está roto en ese paso o en uno anterior.
   - **Anota** en qué paso se rompe el folding por primera vez.

4. Ahora activa el diagnóstico formal. Ve a la pestaña **Herramientas** (*Tools*) en el Editor de Power Query → **Diagnóstico de consultas** → **Iniciar diagnóstico**.

   > Si la pestaña "Herramientas" no es visible, ve a **Ver** → **Diagnóstico de consultas** → **Iniciar diagnóstico**.

5. Con el diagnóstico activo, haz clic en **Actualizar vista previa** (*Refresh Preview*) en la consulta **FactSales**.

6. Detén el diagnóstico: **Herramientas** → **Diagnóstico de consultas** → **Detener diagnóstico**.

7. Power Query generará automáticamente dos consultas nuevas en el panel izquierdo:
   - `Diagnostics Summary` — resumen de pasos y tiempos.
   - `Diagnostics Detail` — detalle fila a fila.

8. Selecciona **Diagnostics Summary** y examina las columnas:
   - **Step** — nombre del paso.
   - **Duration (ms)** — tiempo de ejecución.
   - **Data Source Query** — si contiene SQL, el paso se plegó; si está vacío o contiene "Table.Buffer", el folding está roto.

9. Identifica y **anota** los tres pasos con mayor duración y si tienen SQL en la columna `Data Source Query`.

10. Cierra el panel de diagnóstico (puedes eliminar las consultas de diagnóstico generadas antes de continuar).

#### Resultado esperado

Deberías identificar al menos un paso (probablemente `Table.Buffer` o una transformación de texto) que rompe el folding y genera un tiempo de ejecución significativamente mayor que los pasos anteriores. El informe de diagnóstico mostrará ese paso sin SQL en la columna `Data Source Query`.

#### Verificación

- [ ] Puedes señalar con precisión en qué paso se rompe el Query Folding en la consulta `FactSales`.
- [ ] Tienes anotado el tiempo de ejecución del paso problemático en milisegundos.
- [ ] El paso anterior al problemático muestra SQL en `Data Source Query`.

---

### Paso 2 — Refactorizar la Consulta FactSales para Maximizar Query Folding

**Objetivo:** Reescribir la consulta `FactSales` en el editor avanzado para eliminar los pasos que rompen el folding, asegurar tipado temprano y reducir el número de columnas transferidas desde el origen.

#### Instrucciones

1. En el Editor de Power Query, selecciona la consulta **FactSales**.

2. Ve a **Inicio** → **Editor avanzado** (*Advanced Editor*) para ver el código M completo.

3. Examina el código actual. Probablemente encontrarás algo similar a esto (código problemático del archivo de inicio):

```m
let
    Source = Sql.Database("sql-lab-server", "SalesDW_Lab"),
    Fact = Source{[Schema="dbo", Item="FactSales"]}[Data],
    Filtered = Table.SelectRows(Fact, each [OrderDate] >= #datetime(2020,1,1,0,0,0)),
    Buffered = Table.Buffer(Filtered),
    AddedColumn = Table.AddColumn(Buffered, "YearMonth", 
                    each Text.From(Date.Year([OrderDate])) & "-" & 
                    Text.PadStart(Text.From(Date.Month([OrderDate])), 2, "0")),
    Typed = Table.TransformColumnTypes(AddedColumn, 
                {{"SalesAmount", type number}, {"Quantity", Int64.Type}}),
    AllColumns = Table.SelectColumns(Typed, 
                {"OrderDate", "CustomerID", "ProductID", "TerritoryID", 
                 "SalesAmount", "Quantity", "UnitPrice", "OrderNumber",
                 "YearMonth", "ShipDate", "DueDate", "RevisionNumber",
                 "CarrierTrackingNumber", "SalesPersonID"})
in
    AllColumns
```

4. **Identifica los problemas** en el código anterior:
   - `Table.Buffer(Filtered)` — rompe el folding forzando la descarga completa antes de continuar.
   - `Table.AddColumn` con funciones de texto (`Text.From`, `Text.PadStart`) — no se puede plegar a SQL.
   - `Table.SelectColumns` incluye columnas innecesarias (`CarrierTrackingNumber`, `RevisionNumber`, `ShipDate`, `DueDate`) que aumentan el volumen transferido.
   - El filtro de fecha usa un literal fijo en lugar de los parámetros de Incremental Refresh.

5. **Reemplaza** el código completo con la versión optimizada:

```m
let
    Source = Sql.Database("sql-lab-server", "SalesDW_Lab", 
                [Query = null, CreateNavigationProperties = true]),
    Fact = Source{[Schema="dbo", Item="FactSales"]}[Data],
    // Tipado temprano - permite al motor optimizar antes de filtrar
    Typed = Table.TransformColumnTypes(Fact, {
                {"OrderDate",   type datetime}, 
                {"SalesAmount", type number}, 
                {"Quantity",    Int64.Type},
                {"UnitPrice",   type number},
                {"CustomerID",  Int64.Type},
                {"ProductID",   Int64.Type},
                {"TerritoryID", Int64.Type}
            }),
    // Filtro incremental ANTES de cualquier transformación costosa
    // RangeStart y RangeEnd son parámetros que se definirán en el Paso 3
    Filtered = Table.SelectRows(Typed, 
                each [OrderDate] >= RangeStart and [OrderDate] < RangeEnd),
    // Proyección mínima: solo columnas necesarias para el modelo
    Selected = Table.SelectColumns(Filtered, {
                "OrderDate", "CustomerID", "ProductID", 
                "TerritoryID", "SalesAmount", "Quantity", "UnitPrice"
            })
in
    Selected
```

6. Haz clic en **Listo** (*Done*).

   > **Nota:** Si `RangeStart` y `RangeEnd` no existen aún como parámetros, Power Query mostrará un error. Esto es esperado; los crearás en el Paso 3. Por ahora, si el error impide continuar, reemplaza temporalmente `RangeStart` por `#datetime(2020,1,1,0,0,0)` y `RangeEnd` por `#datetime(2025,1,1,0,0,0)` para validar el folding.

7. Haz clic derecho sobre el último paso **Selected** → **Ver consulta nativa**. Confirma que aparece una consulta SQL con `SELECT`, `WHERE` y los tipos de columna correctos.

8. La consulta SQL generada debe parecerse a:

```sql
SELECT 
    [OrderDate], [CustomerID], [ProductID], 
    [TerritoryID], [SalesAmount], [Quantity], [UnitPrice]
FROM [dbo].[FactSales]
WHERE [OrderDate] >= '2020-01-01 00:00:00' 
  AND [OrderDate] < '2025-01-01 00:00:00'
```

9. Verifica también que el paso **Typed** muestra SQL (el tipado temprano se plegó).

#### Resultado esperado

La consulta nativa visible muestra SQL completo con `SELECT` de solo 7 columnas y `WHERE` con el filtro de fecha. No hay `Table.Buffer` ni funciones de texto que fuercen procesamiento local. El tiempo de actualización de vista previa debería ser notablemente menor.

#### Verificación

- [ ] `View Native Query` en el paso `Selected` muestra SQL válido.
- [ ] El SQL generado contiene exactamente las 7 columnas seleccionadas.
- [ ] No hay `Table.Buffer` en el código M.
- [ ] La columna `YearMonth` fue eliminada (si se necesita, se puede crear como columna calculada en DAX a costo mínimo).

---

### Paso 3 — Configurar Incremental Refresh con Parámetros RangeStart y RangeEnd

**Objetivo:** Implementar la política de Incremental Refresh sobre `FactSales` para que en cada actualización solo se procesen los datos recientes, reduciendo drásticamente la ventana de refresh en producción.

#### Instrucciones

1. En el Editor de Power Query, crea los parámetros requeridos:
   - Ve a **Inicio** → **Administrar parámetros** → **Nuevo parámetro**.
   - Crea el primer parámetro con estos valores exactos:

   | Campo | Valor |
   |---|---|
   | Nombre | `RangeStart` |
   | Tipo | Date/Time |
   | Valor actual | `1/1/2020 12:00:00 AM` |

   - Crea el segundo parámetro:

   | Campo | Valor |
   |---|---|
   | Nombre | `RangeEnd` |
   | Tipo | Date/Time |
   | Valor actual | `1/1/2025 12:00:00 AM` |

   > **Crítico:** Los nombres deben ser exactamente `RangeStart` y `RangeEnd` (sensibles a mayúsculas). Power BI los reconoce automáticamente para la política de Incremental Refresh.

2. Haz clic en **Aceptar** y cierra el diálogo de parámetros.

3. Verifica que la consulta `FactSales` ya no muestra errores (ahora que los parámetros existen, el código M del Paso 2 es válido).

4. Haz clic en **Cerrar y aplicar** (*Close & Apply*) para volver a Power BI Desktop.

5. Espera a que se complete la carga de datos. **Anota el tiempo** que tarda en la tabla de métricas del Paso D.

6. Ahora configura la política de Incremental Refresh. En Power BI Desktop:
   - En el panel **Campos**, haz clic derecho sobre la tabla **FactSales**.
   - Selecciona **Actualización incremental** (*Incremental refresh*).

7. En el diálogo de Incremental Refresh, configura:

   | Configuración | Valor |
   |---|---|
   | Activar actualización incremental | ✅ Activado |
   | Archivar datos desde hace | 3 años |
   | Actualizar datos desde hace | 2 días |
   | Detectar cambios de datos | ❌ Desactivado (para este laboratorio) |
   | Solo actualizar períodos completos | ✅ Activado |

8. Haz clic en **Aplicar**.

9. Guarda el archivo `.pbix` con **Ctrl+S**.

   > **Nota pedagógica:** En un entorno de desarrollo local, el Incremental Refresh no crea particiones físicas visibles hasta que el modelo se publica en el Servicio Power BI y se ejecuta la primera actualización desde el servicio. Lo que has configurado es la *política* que se aplicará al publicar. Puedes verificar la configuración en Tabular Editor 2 si está disponible: abre el modelo externo desde TE2 y navega a `Tables > FactSales > Partitions`.

#### Resultado esperado

La política de Incremental Refresh está configurada. Power BI Desktop muestra un ícono especial junto a `FactSales` en el panel de campos indicando que tiene política de actualización incremental activa. El modelo carga correctamente con los datos del rango completo definido por los parámetros.

#### Verificación

- [ ] Los parámetros `RangeStart` y `RangeEnd` existen con tipo `Date/Time`.
- [ ] La consulta `FactSales` utiliza ambos parámetros en el filtro.
- [ ] La política de Incremental Refresh está configurada (3 años historial, 2 días actualización).
- [ ] El modelo carga sin errores.

---

### FASE 2: Diagnóstico y Optimización de Medidas DAX

---

### Paso 4 — Medir el Rendimiento Inicial con Performance Analyzer y DAX Studio

**Objetivo:** Establecer una línea base de rendimiento de las medidas DAX problemáticas usando Performance Analyzer en Power BI Desktop y Server Timings en DAX Studio.

#### Instrucciones

**Parte A — Performance Analyzer en Power BI Desktop:**

1. En Power BI Desktop, navega a la página del informe llamada **"Resumen de Ventas"** (debe existir en el archivo de inicio con al menos 4 visuales que usen las medidas principales).

2. Ve a la pestaña **Ver** (*View*) → **Analizador de rendimiento** (*Performance Analyzer*).

3. En el panel del Analizador de rendimiento, haz clic en **Iniciar grabación** (*Start recording*).

4. Haz clic en **Actualizar objetos visuales** (*Refresh visuals*) en la parte superior del panel.

5. Espera a que todos los visuales terminen de renderizar.

6. Haz clic en **Detener** (*Stop*).

7. Expande cada visual en el panel y anota los tiempos para:
   - **Consulta DAX** (*DAX query*) — tiempo que tardó el motor DAX.
   - **Otros** (*Other*) — tiempo en rendering y otros procesos.
   - Identifica el visual más lento.

8. Haz clic en **Copiar consulta** (*Copy query*) en el visual más lento. Esto copia la consulta DAX al portapapeles.

**Parte B — Server Timings en DAX Studio:**

9. Abre DAX Studio (debe estar conectado al modelo `Lab03_Start` como configuraste en el Paso C de preparación).

10. En la barra de herramientas de DAX Studio, activa **Server Timings** haciendo clic en el ícono del cronómetro (o ve a **Advanced** → **Server Timings**).

11. También activa **Query Plan** desde el mismo menú **Advanced**.

12. Pega la consulta copiada del Performance Analyzer en el editor de DAX Studio.

13. Ejecuta la consulta con **F5**.

14. Examina la pestaña **Server Timings** en la parte inferior:
    - **Total** — tiempo total de ejecución.
    - **SE CPU** — tiempo de CPU del Storage Engine (paralelo, eficiente).
    - **FE** — tiempo del Formula Engine (secuencial, costoso).
    - **SE Queries** — número de consultas al Storage Engine.
    - **SE Cache** — cuántas consultas se resolvieron desde caché.

15. **Anota** los valores de FE y SE para las tres medidas principales.

16. Ahora ejecuta individualmente cada una de las medidas problemáticas del modelo. Copia y ejecuta en DAX Studio:

```dax
-- Medida 1: Ventas Brutas (versión actual del modelo)
EVALUATE
ROW(
    "Ventas Brutas", [Ventas Brutas],
    "Clientes Activos", [Clientes Activos],
    "Margen %", [Margen %]
)
```

17. Anota los tiempos en la tabla de métricas del Paso D de preparación.

#### Resultado esperado

El Performance Analyzer muestra tiempos de DAX Query superiores a 500ms en al menos uno de los visuales. En DAX Studio, el tiempo de Formula Engine (FE) es desproporcionadamente alto comparado con el Storage Engine (SE) en las medidas problemáticas, indicando trabajo que debería delegarse al SE.

#### Verificación

- [ ] Tienes registrados los tiempos de Performance Analyzer para todos los visuales de la página.
- [ ] DAX Studio muestra Server Timings con desglose FE vs SE.
- [ ] Identificaste al menos una medida donde FE > SE (indicador de ineficiencia).
- [ ] La tabla de métricas de línea base está completa.

---

### Paso 5 — Analizar y Reescribir Medidas DAX Ineficientes

**Objetivo:** Examinar el código DAX de las medidas problemáticas, entender por qué generan trabajo excesivo en el Formula Engine y reescribirlas aplicando patrones de optimización.

#### Instrucciones

1. En Power BI Desktop, ve al panel **Campos** y localiza la tabla **Measures** (o la tabla donde están las medidas).

2. Haz doble clic en la medida **Clientes Activos** para ver su código actual. Debería ser similar a:

```dax
Clientes Activos =
COUNTROWS (
    FILTER (
        VALUES ( 'Customer'[CustomerID] ),
        CALCULATE ( SUM ( FactSales[SalesAmount] ) ) > 0
    )
)
```

3. **Analiza el problema:** `FILTER` con `VALUES` itera sobre todos los clientes en el contexto, y para cada uno ejecuta un `CALCULATE(SUM(...))`. Esto fuerza al Formula Engine a materializar una tabla temporal y ejecutar múltiples consultas al Storage Engine. Es un patrón O(n) en el FE.

4. **Reescribe** la medida con el patrón optimizado. Selecciona la medida, borra el código y escribe:

```dax
Clientes Activos =
CALCULATE (
    DISTINCTCOUNT ( 'Customer'[CustomerID] ),
    FactSales[SalesAmount] > 0
)
```

   > **Por qué es mejor:** `CALCULATE` con un predicado de columna (`FactSales[SalesAmount] > 0`) se traduce en un filtro del Storage Engine directamente. `DISTINCTCOUNT` es una función nativa del SE. El FE apenas interviene.

5. Confirma el cambio haciendo clic en la marca de verificación (✓) o presionando **Enter** en la barra de fórmulas.

6. Ahora localiza la medida **Margen %** y examina su código actual:

```dax
Margen % =
DIVIDE (
    SUM ( FactSales[SalesAmount] ) - SUM ( FactSales[TotalCost] ),
    SUM ( FactSales[SalesAmount] )
)
```

   > **Problema:** Aunque este código no es terriblemente ineficiente, `SUM(FactSales[SalesAmount])` se evalúa **dos veces** — una para el numerador y otra para el denominador. En modelos grandes, cada evaluación genera una consulta al SE.

7. **Reescribe** usando variables para evitar la doble evaluación:

```dax
Margen % =
VAR Ventas = SUM ( FactSales[SalesAmount] )
VAR Costo  = SUM ( FactSales[TotalCost] )
RETURN
    DIVIDE ( Ventas - Costo, Ventas )
```

8. Localiza la medida **Ventas por Territorio (Top 5)** (o similar) que usa un patrón de ranking. El código actual probablemente es:

```dax
Ventas Top Territorios =
SUMX (
    FILTER (
        ALL ( 'Territory'[TerritoryName] ),
        RANKX ( ALL ( 'Territory'[TerritoryName] ), [Ventas Brutas] ) <= 5
    ),
    [Ventas Brutas]
)
```

   > **Problema:** `FILTER` con `RANKX` itera dos veces sobre la tabla de territorios y fuerza múltiples evaluaciones en el FE.

9. **Reescribe** con un patrón más eficiente usando `TOPN`:

```dax
Ventas Top Territorios =
SUMX (
    TOPN ( 5, ALL ( 'Territory'[TerritoryName] ), [Ventas Brutas], DESC ),
    [Ventas Brutas]
)
```

10. Ahora localiza la medida **% Ventas vs Total** que probablemente usa `ALL` de forma ineficiente:

```dax
% Ventas vs Total =
DIVIDE (
    [Ventas Brutas],
    CALCULATE ( [Ventas Brutas], ALL ( FactSales ) )
)
```

   > **Problema:** `ALL(FactSales)` elimina todos los filtros de la tabla de hechos, incluyendo los de dimensiones relacionadas. Puede producir resultados incorrectos en modelos con múltiples relaciones y es más costoso que `REMOVEFILTERS` específico.

11. **Reescribe** con `REMOVEFILTERS` explícito y `ALLSELECTED` para respetar filtros externos de slicers:

```dax
% Ventas vs Total =
DIVIDE (
    [Ventas Brutas],
    CALCULATE ( 
        [Ventas Brutas], 
        REMOVEFILTERS ( 'Product' ),
        REMOVEFILTERS ( 'Territory' ),
        REMOVEFILTERS ( 'Customer' )
    )
)
```

   > **Alternativa con ALLSELECTED** (para que respete filtros de página/slicer pero ignore el contexto del visual):

```dax
% Ventas vs Total (Relativo) =
DIVIDE (
    [Ventas Brutas],
    CALCULATE ( [Ventas Brutas], ALLSELECTED () )
)
```

12. Guarda el archivo con **Ctrl+S**.

#### Resultado esperado

Las cuatro medidas han sido reescritas. El código es más conciso y delega más trabajo al Storage Engine. En el siguiente paso verificarás la mejora de rendimiento con DAX Studio.

#### Verificación

- [ ] `Clientes Activos` usa `DISTINCTCOUNT` con predicado de columna, no `FILTER(VALUES(...))`.
- [ ] `Margen %` usa variables `VAR` para evitar doble evaluación.
- [ ] `Ventas Top Territorios` usa `TOPN` en lugar de `FILTER(ALL(...), RANKX(...))`.
- [ ] `% Ventas vs Total` usa `REMOVEFILTERS` explícito o `ALLSELECTED`.
- [ ] Todas las medidas se guardan sin errores de sintaxis.

---

### Paso 6 — Verificar la Mejora de Rendimiento DAX con DAX Studio

**Objetivo:** Medir el impacto de las reescrituras DAX comparando los tiempos de Server Timings antes y después, y documentar la mejora obtenida.

#### Instrucciones

1. Regresa a DAX Studio (debe seguir conectado al modelo).

2. Limpia la caché del motor antes de medir para obtener tiempos reales (sin caché):
   - En DAX Studio, ve a **Advanced** → **Clear Cache** → **Clear Cache and Run**.

   > **Alternativa:** Usa el botón **Run** con la opción **Clear Cache on Run** habilitada en la barra de herramientas.

3. Ejecuta nuevamente la consulta de benchmark:

```dax
EVALUATE
ROW(
    "Ventas Brutas",          [Ventas Brutas],
    "Clientes Activos",       [Clientes Activos],
    "Margen %",               [Margen %],
    "Ventas Top Territorios", [Ventas Top Territorios]
)
```

4. Observa la pestaña **Server Timings**. Compara:
   - El tiempo total vs el tiempo registrado en el Paso 4.
   - La proporción FE/SE: debería haber bajado significativamente para `Clientes Activos` y `Ventas Top Territorios`.

5. Para una comparación más precisa, ejecuta cada medida por separado y anota los tiempos:

```dax
-- Test individual: Clientes Activos
EVALUATE
SUMMARIZECOLUMNS (
    'Territory'[TerritoryName],
    "Clientes Activos", [Clientes Activos]
)
```

```dax
-- Test individual: Margen % por Producto
EVALUATE
SUMMARIZECOLUMNS (
    'Product'[ProductCategory],
    "Margen %", [Margen %]
)
```

6. Completa la columna **Valor final** en la tabla de métricas del Paso D.

7. Calcula el porcentaje de mejora: `((Inicial - Final) / Inicial) × 100`.

8. Ahora examina el **Query Plan** para la medida `Clientes Activos` optimizada:
   - En la pestaña **Query Plan**, busca operaciones `VertiPaq Scan` — estas son del Storage Engine (eficiente).
   - Busca operaciones `Lookup` o `Join` en el FE — si hay pocas o ninguna, la optimización fue exitosa.

9. Regresa a Power BI Desktop, activa el **Performance Analyzer** y actualiza los visuales de la página **"Resumen de Ventas"**.
   - Compara los nuevos tiempos de DAX Query con los registrados en el Paso 4.

10. Exporta el resultado del Performance Analyzer: haz clic en **Exportar** (*Export*) en el panel del analizador y guarda el archivo JSON como `Lab03_PerfAnalyzer_Optimized.json`.

#### Resultado esperado

Los tiempos de `Clientes Activos` deberían haber mejorado entre un 40% y un 80% (dependiendo del volumen de datos). `Margen %` mostrará una mejora más modesta pero consistente. El ratio FE/SE total habrá mejorado. El Performance Analyzer mostrará tiempos de DAX Query menores en los visuales afectados.

#### Verificación

- [ ] Los Server Timings muestran reducción en tiempo FE para `Clientes Activos`.
- [ ] El Query Plan de `Clientes Activos` muestra principalmente operaciones `VertiPaq Scan`.
- [ ] La tabla de métricas tiene valores iniciales y finales completos.
- [ ] El archivo `Lab03_PerfAnalyzer_Optimized.json` está guardado.

---

### FASE 3: Implementación de Agregaciones

---

### Paso 7 — Crear la Tabla de Agregaciones en Power Query

**Objetivo:** Construir una tabla de agregaciones precalculadas (`FactSales_Agg`) que resuma las ventas por mes y categoría de producto, para que Power BI pueda resolver consultas de nivel resumen sin acceder a la granularidad de detalle de `FactSales`.

#### Instrucciones

1. En Power BI Desktop, ve a **Inicio** → **Transformar datos** para abrir el Editor de Power Query.

2. Crea una nueva consulta basada en la fuente SQL. Ve a **Inicio** → **Nueva fuente** → **SQL Server**.

3. Conecta al mismo servidor `sql-lab-server` y base de datos `SalesDW_Lab`.

4. En lugar de navegar a una tabla, selecciona **Instrucción SQL avanzada** y escribe:

```sql
SELECT 
    YEAR(fs.OrderDate)           AS OrderYear,
    MONTH(fs.OrderDate)          AS OrderMonth,
    DATEFROMPARTS(
        YEAR(fs.OrderDate), 
        MONTH(fs.OrderDate), 1)  AS OrderMonthDate,
    p.ProductCategoryKey,
    t.SalesTerritoryKey,
    SUM(fs.SalesAmount)          AS TotalSalesAmount,
    SUM(fs.Quantity)             AS TotalQuantity,
    SUM(fs.TotalCost)            AS TotalCost,
    COUNT(DISTINCT fs.CustomerID) AS UniqueCustomers,
    COUNT(*)                     AS TransactionCount
FROM dbo.FactSales fs
    INNER JOIN dbo.DimProduct p 
        ON fs.ProductID = p.ProductKey
    INNER JOIN dbo.DimSalesTerritory t 
        ON fs.TerritoryID = t.SalesTerritoryKey
GROUP BY 
    YEAR(fs.OrderDate),
    MONTH(fs.OrderDate),
    DATEFROMPARTS(YEAR(fs.OrderDate), MONTH(fs.OrderDate), 1),
    p.ProductCategoryKey,
    t.SalesTerritoryKey
```

5. Haz clic en **Aceptar**. Power Query ejecutará la consulta SQL y mostrará los datos agregados.

6. En el panel **Pasos aplicados**, renombra el paso `Source` a `AggSource` para claridad.

7. Aplica tipado explícito a todas las columnas:

```m
// En el Editor Avanzado, el código completo debería ser:
let
    AggSource = Sql.Database("sql-lab-server", "SalesDW_Lab", 
                    [Query = "SELECT YEAR(fs.OrderDate) AS OrderYear,
                              MONTH(fs.OrderDate) AS OrderMonth,
                              DATEFROMPARTS(YEAR(fs.OrderDate), MONTH(fs.OrderDate), 1) AS OrderMonthDate,
                              p.ProductCategoryKey,
                              t.SalesTerritoryKey,
                              SUM(fs.SalesAmount) AS TotalSalesAmount,
                              SUM(fs.Quantity) AS TotalQuantity,
                              SUM(fs.TotalCost) AS TotalCost,
                              COUNT(DISTINCT fs.CustomerID) AS UniqueCustomers,
                              COUNT(*) AS TransactionCount
                              FROM dbo.FactSales fs
                              INNER JOIN dbo.DimProduct p ON fs.ProductID = p.ProductKey
                              INNER JOIN dbo.DimSalesTerritory t ON fs.TerritoryID = t.SalesTerritoryKey
                              GROUP BY YEAR(fs.OrderDate), MONTH(fs.OrderDate),
                              DATEFROMPARTS(YEAR(fs.OrderDate), MONTH(fs.OrderDate), 1),
                              p.ProductCategoryKey, t.SalesTerritoryKey"]),
    Typed = Table.TransformColumnTypes(AggSource, {
                {"OrderYear",         Int64.Type},
                {"OrderMonth",        Int64.Type},
                {"OrderMonthDate",    type date},
                {"ProductCategoryKey",Int64.Type},
                {"SalesTerritoryKey", Int64.Type},
                {"TotalSalesAmount",  type number},
                {"TotalQuantity",     Int64.Type},
                {"TotalCost",         type number},
                {"UniqueCustomers",   Int64.Type},
                {"TransactionCount",  Int64.Type}
            })
in
    Typed
```

8. Renombra la consulta a `FactSales_Agg` haciendo doble clic en su nombre en el panel izquierdo.

9. Verifica que la tabla tiene significativamente menos filas que `FactSales` (debería tener miles de filas vs millones).

10. Haz clic en **Cerrar y aplicar**.

11. Establece el **modo de almacenamiento** de `FactSales_Agg` como **Import**:
    - En Power BI Desktop, en el panel de campos, haz clic derecho sobre `FactSales_Agg`.
    - Selecciona **Modo de almacenamiento** (*Storage mode*) → **Importar** (*Import*).
    - Confirma el cambio si se solicita.

12. Crea las relaciones necesarias en la vista de modelo:
    - `FactSales_Agg[ProductCategoryKey]` → `DimProductCategory[ProductCategoryKey]` (muchos a uno)
    - `FactSales_Agg[SalesTerritoryKey]` → `DimSalesTerritory[SalesTerritoryKey]` (muchos a uno)
    - `FactSales_Agg[OrderMonthDate]` → `DimDate[DateKey]` (muchos a uno, si la tabla de fechas tiene granularidad mensual o superior)

#### Resultado esperado

La tabla `FactSales_Agg` está cargada en modo Import con datos precalculados por mes, categoría y territorio. Tiene entre 1,000 y 10,000 filas (dependiendo del rango de fechas y número de categorías/territorios). Las relaciones con las dimensiones están establecidas correctamente.

#### Verificación

- [ ] `FactSales_Agg` aparece en el modelo con modo de almacenamiento Import.
- [ ] La tabla tiene las 10 columnas tipadas correctamente.
- [ ] Las relaciones con `DimProductCategory`, `DimSalesTerritory` y `DimDate` están activas.
- [ ] El número de filas de `FactSales_Agg` es órdenes de magnitud menor que `FactSales`.

---

### Paso 8 — Configurar la Capa de Agregaciones y Verificar su Uso

**Objetivo:** Mapear `FactSales_Agg` como tabla de agregaciones de `FactSales` en Power BI Desktop, y verificar con DAX Studio que las consultas de nivel resumen se resuelven desde la agregación sin acceder a los datos de detalle.

#### Instrucciones

1. En Power BI Desktop, en la **Vista de modelo** (*Model view*), selecciona la tabla `FactSales_Agg`.

2. En la cinta de opciones, ve a **Herramientas de tabla** (*Table tools*) → **Administrar agregaciones** (*Manage aggregations*).

   > Si no ves esta opción, haz clic derecho sobre la tabla `FactSales_Agg` en el panel de campos → **Administrar agregaciones**.

3. Se abrirá el diálogo de administración de agregaciones. Configura los mapeos columna por columna:

   | Columna de FactSales_Agg | Resumen | Tabla de detalle | Columna de detalle |
   |---|---|---|---|
   | `TotalSalesAmount` | Suma | `FactSales` | `SalesAmount` |
   | `TotalQuantity` | Suma | `FactSales` | `Quantity` |
   | `TotalCost` | Suma | `FactSales` | `TotalCost` |
   | `UniqueCustomers` | Contar filas de tabla | `FactSales` | *(tabla)* |
   | `TransactionCount` | Contar filas de tabla | `FactSales` | *(tabla)* |
   | `ProductCategoryKey` | Agrupar por | `FactSales` | `ProductID` |
   | `SalesTerritoryKey` | Agrupar por | `FactSales` | `TerritoryID` |
   | `OrderMonthDate` | Agrupar por | `FactSales` | `OrderDate` |

4. Haz clic en **Aplicar todo** (*Apply all*).

5. Verifica que `FactSales_Agg` ahora aparece en el panel de campos con un ícono especial (rayo o similar) indicando que es una tabla de agregaciones oculta.

   > Power BI automáticamente ocultará la tabla de agregaciones de los usuarios finales; solo es visible para el motor de consultas.

6. Ahora **verifica que las agregaciones se usan correctamente** con DAX Studio:

   En DAX Studio, ejecuta una consulta que debería resolverse desde la agregación (nivel de categoría de producto y mes):

```dax
-- Esta consulta DEBE resolverse desde FactSales_Agg, no desde FactSales
EVALUATE
SUMMARIZECOLUMNS (
    'DimProductCategory'[EnglishProductCategoryName],
    'DimDate'[CalendarYear],
    "Ventas Totales", SUM ( FactSales[SalesAmount] ),
    "Costo Total",    SUM ( FactSales[TotalCost] )
)
ORDER BY 
    'DimDate'[CalendarYear],
    [Ventas Totales] DESC
```

7. Antes de ejecutar, asegúrate de tener **Server Timings** activo y **Clear Cache** habilitado.

8. Ejecuta la consulta y examina:
   - En **Server Timings**: busca en las consultas SE si aparece `FactSales_Agg` en lugar de `FactSales`. Si la agregación funciona, verás consultas al SE sobre `FactSales_Agg`.
   - El tiempo total debería ser significativamente menor que si la misma consulta accediera a `FactSales` directamente.

9. Ahora ejecuta una consulta de **detalle** que NO puede resolverse desde la agregación (nivel de cliente individual):

```dax
-- Esta consulta DEBE ir a FactSales (detalle), no puede usar la agregación
EVALUATE
SUMMARIZECOLUMNS (
    'Customer'[CustomerID],
    'Customer'[FullName],
    "Ventas Cliente", SUM ( FactSales[SalesAmount] )
)
ORDER BY [Ventas Cliente] DESC
```

10. Compara los tiempos de ambas consultas. La primera (nivel categoría/mes) debería ser entre 5x y 20x más rápida que la segunda (nivel cliente).

11. Usa **VertiPaq Analyzer** en DAX Studio para verificar el impacto en memoria:
    - En DAX Studio, ve a **Advanced** → **View Metrics** o abre VertiPaq Analyzer.
    - Compara el tamaño en memoria de `FactSales` vs `FactSales_Agg`.
    - Documenta el tamaño de ambas tablas en MB.

12. Guarda el archivo final como `Lab03_Completed.pbix`.

#### Resultado esperado

Las consultas de nivel resumen (por categoría, mes, territorio) se resuelven desde `FactSales_Agg` en Import, con tiempos de respuesta notablemente menores. Las consultas de detalle (por cliente individual, por transacción) siguen accediendo a `FactSales`. VertiPaq Analyzer confirma que `FactSales_Agg` ocupa una fracción del espacio de `FactSales`.

#### Verificación

- [ ] Los mapeos de agregación están configurados para todas las columnas métricas y de agrupación.
- [ ] `FactSales_Agg` aparece con ícono de tabla de agregaciones en el panel de campos.
- [ ] DAX Studio Server Timings muestra consultas a `FactSales_Agg` para la consulta de nivel categoría/mes.
- [ ] La consulta de nivel categoría es al menos 3x más rápida que la de nivel cliente.
- [ ] El tamaño de `FactSales_Agg` en VertiPaq Analyzer es menor al 5% del tamaño de `FactSales`.

---

## 7. Validación y Pruebas Finales

Completa las siguientes verificaciones integrales antes de dar el laboratorio por concluido:

### 7.1 Checklist de Query Folding

```m
// Abre el Editor de Power Query y verifica:
// 1. Haz clic derecho en el último paso de FactSales → "Ver consulta nativa"
// 2. Debe mostrar SQL con SELECT de 7 columnas y WHERE con fechas
// 3. NO debe haber Table.Buffer en el código M
// 4. Los parámetros RangeStart y RangeEnd deben existir con tipo DateTime
```

### 7.2 Prueba de Medidas DAX Optimizadas

Ejecuta en DAX Studio la siguiente batería de pruebas y verifica que los resultados son correctos (no solo rápidos):

```dax
-- Prueba de corrección: los valores deben coincidir con los del modelo original
EVALUATE
ROW(
    "Clientes Activos (debe ser > 0)",    [Clientes Activos],
    "Margen % (debe estar entre 0 y 1)",  [Margen %],
    "Top Territorios (debe ser > 0)",     [Ventas Top Territorios],
    "% vs Total (debe ser 1.0 sin filtro)",[% Ventas vs Total]
)
```

### 7.3 Prueba de Agregaciones

```dax
-- Prueba A: Consulta que DEBE usar agregación (rápida)
EVALUATE
SUMMARIZECOLUMNS(
    'DimProductCategory'[EnglishProductCategoryName],
    "Ventas", SUM(FactSales[SalesAmount])
)

-- Prueba B: Consulta que NO puede usar agregación (más lenta, esperado)
EVALUATE
SUMMARIZECOLUMNS(
    'Customer'[CustomerID],
    "Ventas", SUM(FactSales[SalesAmount])
)
```

La Prueba A debe ser al menos **3 veces más rápida** que la Prueba B.

### 7.4 Tabla de Métricas Completa

Completa y entrega la siguiente tabla al instructor:

| Métrica | Valor inicial | Valor final | Mejora % |
|---|---|---|---|
| Tiempo de refresh completo (seg) | _____ | _____ | _____ |
| Tiempo DAX — `Ventas Brutas` (ms) | _____ | _____ | _____ |
| Tiempo DAX — `Clientes Activos` (ms) | _____ | _____ | _____ |
| Tiempo DAX — `Margen %` (ms) | _____ | _____ | _____ |
| Consulta resumen categoría/mes (ms) | N/A | _____ | N/A |
| Consulta detalle cliente (ms) | N/A | _____ | N/A |
| Memoria modelo total (MB) | _____ | _____ | _____ |
| Tamaño `FactSales` en VertiPaq (MB) | _____ | _____ | _____ |
| Tamaño `FactSales_Agg` en VertiPaq (MB) | N/A | _____ | N/A |

---

## 8. Solución de Problemas

### Problema 1: `View Native Query` aparece en gris y no se puede verificar el Query Folding

**Síntomas:**
- Al hacer clic derecho en cualquier paso de la consulta `FactSales`, la opción **Ver consulta nativa** está deshabilitada (en gris).
- El Diagnóstico de consultas muestra columnas `Data Source Query` vacías para todos los pasos.
- Los tiempos de refresh son muy altos incluso con pocos datos.

**Causa:**
El conector utilizado no soporta Query Folding de forma nativa, o bien existe un paso que rompe el folding antes del punto que se está inspeccionando. Los conectores que comúnmente no soportan folding incluyen archivos Excel, CSV, carpetas y algunos conectores web. Adicionalmente, funciones como `Table.Buffer()`, `List.Generate()`, o transformaciones de texto aplicadas antes del filtro de fecha pueden romper la cadena de plegado.

**Solución:**
1. Verifica que el conector sea SQL Server (`Sql.Database`), no un archivo local. Si el dataset de práctica está en un archivo CSV por limitaciones del entorno, el folding no será posible — en este caso, simula el ejercicio de diagnóstico con los datos de diagnóstico que muestra el Query Diagnostics y enfoca los pasos de optimización en minimizar columnas y filas descargadas.
2. Revisa el código M en el Editor Avanzado y busca cualquier función que no sea una transformación simple de tipo, filtro de columna o proyección. Mueve el `Table.SelectColumns` y el filtro de fecha lo más cerca posible del paso `Source`, antes de cualquier transformación adicional.
3. Si el origen es SQL Server pero el folding sigue sin funcionar, verifica que el usuario de base de datos tiene permisos `SELECT` y que no hay vistas con `NOLOCK` u otras hints que confundan al conector.

---

### Problema 2: Las consultas en DAX Studio no muestran uso de `FactSales_Agg` en Server Timings después de configurar las agregaciones

**Síntomas:**
- Después de configurar los mapeos de agregación en el Paso 8, las consultas de nivel categoría/mes siguen siendo lentas.
- En los Server Timings de DAX Studio, todas las consultas SE referencian `FactSales` y no `FactSales_Agg`.
- Los tiempos de la consulta de resumen y la de detalle son similares (no hay diferencia de velocidad).

**Causa:**
Las agregaciones en Power BI tienen requisitos estrictos para activarse automáticamente. Los motivos más comunes por los que no se activan son: (a) la consulta DAX incluye columnas o filtros que no están cubiertos por los mapeos de agregación definidos, (b) los tipos de datos entre la columna de la tabla de agregaciones y la columna de detalle no coinciden exactamente, (c) la relación entre `FactSales_Agg` y las dimensiones no está establecida o tiene la dirección incorrecta, o (d) la tabla `FactSales_Agg` no está en modo Import (si está en DirectQuery, no funciona como agregación).

**Solución:**
1. **Verifica el modo de almacenamiento:** En la Vista de modelo, selecciona `FactSales_Agg` y confirma en el panel de propiedades que el modo es **Import**. Si no lo es, cámbialo y vuelve a cargar los datos.
2. **Revisa los tipos de datos:** Abre el Editor de Power Query y compara los tipos de `ProductCategoryKey` en `FactSales_Agg` (debe ser `Int64`) con el tipo de la columna relacionada en `DimProductCategory`. Deben coincidir exactamente.
3. **Verifica los mapeos:** Ve a **Administrar agregaciones** en `FactSales_Agg` y confirma que cada columna de agrupación (`ProductCategoryKey`, `SalesTerritoryKey`, `OrderMonthDate`) está mapeada con la acción **Agrupar por** y apunta a la columna correcta en `FactSales`. Las columnas métricas (`TotalSalesAmount`) deben estar mapeadas con **Suma** a `SalesAmount`.
4. **Prueba con una consulta mínima:** Ejecuta en DAX Studio `EVALUATE SUMMARIZECOLUMNS('DimProductCategory'[ProductCategoryKey], "V", SUM(FactSales[SalesAmount]))` — esta es la consulta más simple posible que debería activar la agregación. Si esta funciona pero otras no, el problema está en las columnas adicionales de las consultas más complejas.

---

## 9. Limpieza del Entorno

Al finalizar el laboratorio, realiza las siguientes acciones de limpieza:

1. **Cierra DAX Studio** correctamente para liberar la conexión al modelo.

2. **Elimina las consultas de diagnóstico** generadas en el Paso 1 si aún existen en el Editor de Power Query:
   - Abre el Editor de Power Query.
   - Busca y elimina `Diagnostics Summary` y `Diagnostics Detail` si existen.
   - Haz clic en **Cerrar y aplicar**.

3. **Guarda el archivo final** como `Lab03_Completed_[TuNombre].pbix`.

4. **Documenta tus resultados** en la tabla de métricas y guarda el archivo JSON del Performance Analyzer exportado en el Paso 6.

5. **No publiques** el archivo al Servicio Power BI en este momento — la publicación se realizará en el Lab 04.

6. Si usaste una clave de API compartida u otros recursos del instructor durante el laboratorio, confirma con el instructor que ya no los necesitas.

---

## 10. Resumen

### Lo que construiste en este laboratorio

En este laboratorio aplicaste un ciclo completo de ingeniería de performance sobre un modelo Power BI de escala empresarial:

**Fase 1 — Pipeline de Power Query:**
- Diagnosticaste cuellos de botella usando Query Diagnostics e identificaste pasos que rompen el Query Folding.
- Refactorizaste la consulta `FactSales` para maximizar el trabajo realizado en el servidor SQL: tipado temprano, proyección mínima y eliminación de `Table.Buffer`.
- Configuraste la política de Incremental Refresh con los parámetros `RangeStart`/`RangeEnd` para reducir la ventana de refresh en producción.

**Fase 2 — Medidas DAX:**
- Estableciste una línea base de rendimiento con Performance Analyzer y DAX Studio Server Timings.
- Reescribiste cuatro medidas ineficientes aplicando patrones concretos: `DISTINCTCOUNT` con predicado de columna, variables `VAR/RETURN`, `TOPN` en lugar de `FILTER+RANKX`, y `REMOVEFILTERS`/`ALLSELECTED` explícitos.
- Verificaste la mejora de rendimiento y documentaste el porcentaje de mejora por medida.

**Fase 3 — Capa de Agregaciones:**
- Creaste la tabla `FactSales_Agg` con datos precalculados por mes, categoría y territorio.
- Configuraste los mapeos de agregación para que Power BI resuelva automáticamente consultas de nivel resumen desde la tabla comprimida en Import.
- Verificaste con DAX Studio que las consultas de nivel resumen usan la agregación y son significativamente más rápidas que las consultas de detalle.

### Principios clave aplicados

| Principio | Implementación en este lab |
|---|---|
| **Query Folding** | Tipado temprano, proyección mínima, eliminación de `Table.Buffer` |
| **Incremental Refresh** | Parámetros `RangeStart`/`RangeEnd`, política 3 años / 2 días |
| **SE > FE en DAX** | `DISTINCTCOUNT` con predicado, `TOPN`, `REMOVEFILTERS` explícito |
| **Variables DAX** | `VAR/RETURN` para evitar doble evaluación en `Margen %` |
| **Agregaciones** | Tabla Import precalculada con mapeos automáticos |

### Recursos de referencia

| Recurso | URL |
|---|---|
| Optimización de rendimiento en Power BI (Microsoft Learn) | https://learn.microsoft.com/power-bi/guidance/power-bi-performance-best-practices |
| Fundamentos de Query Folding (Microsoft Learn) | https://learn.microsoft.com/power-query/query-folding-basics |
| Incremental Refresh — Visión general | https://learn.microsoft.com/power-bi/connect-data/incremental-refresh-overview |
| Agregaciones avanzadas en Power BI | https://learn.microsoft.com/power-bi/transform-model/aggregations-advanced |
| DAX Studio — Server Timings y Query Plan | https://daxstudio.org/documentation/server-timings/ |
| Analizador de rendimiento en Power BI Desktop | https://learn.microsoft.com/power-bi/create-reports/desktop-performance-analyzer |
| Patrones DAX — SQLBI | https://www.daxpatterns.com |

### Próximos pasos

El modelo optimizado generado en este laboratorio (`Lab03_Completed.pbix`) será el punto de partida del **Lab 04**, donde implementarás Deployment Pipelines y estrategias de gobierno de datos en el Servicio Power BI para llevar este modelo optimizado a producción de forma controlada y reproducible.

---
