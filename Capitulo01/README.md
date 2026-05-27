---LAB_START---
LAB_ID: 01-00-01
---MARKDOWN---
# Optimización de la Capa Semántica: Reducción de Deuda Técnica y Memoria

## 1. Metadatos

| Atributo            | Valor                                                                 |
|---------------------|-----------------------------------------------------------------------|
| **Duración**        | 90 minutos                                                            |
| **Complejidad**     | Media                                                                 |
| **Nivel Bloom**     | Crear                                                                 |
| **Módulo**          | Módulo 1 — Optimización Semántica Avanzada                            |
| **Herramientas**    | Power BI Desktop, DAX Studio, VertiPaq Analyzer, Power Query (M), DAX |
| **Archivo inicial** | `Lab01_VentasRetail_DeudaTecnica.pbix`                                |
| **Archivo solución**| `Lab01_VentasRetail_Optimizado_SOLUCION.pbix`                         |

---

## 2. Descripción General

En este laboratorio recibirás un modelo semántico Power BI construido deliberadamente con deuda técnica: columnas calculadas innecesarias, medidas duplicadas, tipos de datos subóptimos, relaciones evitables y la opción *Auto date/time* activa. Utilizarás **DAX Studio** y **VertiPaq Analyzer** para diagnosticar y cuantificar cada problema, luego aplicarás un proceso estructurado de remediación en **Power Query**, el **editor de modelos** y el **editor DAX**. El laboratorio concluye con un benchmarking comparativo que valida una reducción de al menos el 30 % en el tamaño del modelo y una mejora medible en el tiempo de respuesta de consultas representativas.

---

## 3. Objetivos de Aprendizaje

Al finalizar este laboratorio serás capaz de:

- [ ] Identificar y cuantificar fuentes de deuda técnica (columnas de alta cardinalidad, medidas duplicadas, relaciones ineficientes) usando VertiPaq Analyzer y DMVs en DAX Studio.
- [ ] Aplicar técnicas de optimización de memoria en Power Query: conversión de tipos, eliminación de columnas y reducción de cardinalidad mediante dimensiones de referencia.
- [ ] Refactorizar medidas DAX redundantes en medidas base reutilizables utilizando `CALCULATE`, `DIVIDE` y variables `VAR`.
- [ ] Desactivar *Auto date/time* e implementar una dimensión de fechas única (`DimFecha`) para eliminar tablas ocultas redundantes.
- [ ] Validar el impacto de las optimizaciones comparando métricas de tamaño de modelo y rendimiento de consultas antes y después de cada intervención.

---

## 4. Prerrequisitos

### Conocimiento previo

| Área                        | Nivel requerido                                                              |
|-----------------------------|------------------------------------------------------------------------------|
| Modelado relacional Power BI | Intermedio — creación de tablas, relaciones y esquema estrella              |
| Tipos de datos Power BI      | Básico — diferencia entre texto, entero, decimal, fecha                     |
| DAX                          | Básico — medidas calculadas, columnas calculadas, diferencia entre ambas    |
| Power Query (M)              | Básico — transformaciones de tipo, columnas personalizadas                  |
| DAX Studio                   | Básico — instalación y conexión a Power BI Desktop                          |

### Acceso y archivos necesarios

- Power BI Desktop instalado (versión mínima junio 2024).
- DAX Studio 3.1.x o superior instalado y con conexión verificada a Power BI Desktop.
- Archivo de práctica `Lab01_VentasRetail_DeudaTecnica.pbix` descargado desde el repositorio del curso.
- Carpeta de trabajo local creada: `C:\LabPowerBI\Lab01\`.

---

## 5. Entorno de Laboratorio

### Hardware recomendado

| Componente     | Mínimo                        | Recomendado                    |
|----------------|-------------------------------|--------------------------------|
| RAM            | 16 GB                         | 32 GB                          |
| Procesador     | Intel i5 8ª gen / Ryzen 5     | Intel i7/i9 o Ryzen 7          |
| Almacenamiento | 50 GB libres en SSD           | 100 GB libres en SSD           |
| Pantalla       | 1920×1080                     | Monitor dual o 2K/4K           |

### Software requerido

| Herramienta          | Versión mínima     | Propósito en este lab                              |
|----------------------|--------------------|----------------------------------------------------|
| Power BI Desktop     | Junio 2024         | Editor principal del modelo semántico              |
| DAX Studio           | 3.1.x              | Consultas DMV, exportación VPAX, benchmarking      |
| VertiPaq Analyzer    | Integrado en DAX Studio | Análisis de memoria por columna y tabla       |
| Power Query (M)      | Incluido en PBI Desktop | Transformaciones de tipo y reducción de datos |
| Explorador de archivos / Notepad | — | Registro de métricas en archivo de bitácora   |

### Preparación del entorno

Ejecuta los siguientes pasos **antes** de iniciar los ejercicios:

**1. Crear carpeta de trabajo:**
```
md C:\LabPowerBI\Lab01
md C:\LabPowerBI\Lab01\Capturas
md C:\LabPowerBI\Lab01\VPAX
```

**2. Copiar archivo de práctica:**
```
copy <ruta_descarga>\Lab01_VentasRetail_DeudaTecnica.pbix C:\LabPowerBI\Lab01\
```

**3. Verificar conexión DAX Studio → Power BI Desktop:**
- Abre `Lab01_VentasRetail_DeudaTecnica.pbix` en Power BI Desktop.
- Abre DAX Studio → selecciona **PBI / SSDT Model** → confirma que aparece el modelo `Lab01_VentasRetail_DeudaTecnica`.

**4. Desactivar Auto date/time (configuración global):**
> Esta configuración se realizará también dentro del ejercicio, pero conviene verificarla antes.
> En Power BI Desktop: **Archivo → Opciones y configuración → Opciones → Carga de datos (global)** → desmarcar *"Auto date/time for new files"*.

---

## 6. Instrucciones Paso a Paso

---

### Paso 1 — Diagnóstico Inicial: Exportar y Analizar el VPAX

**Objetivo:** Establecer la línea base del modelo documentando tamaño total, columnas de mayor consumo y cardinalidades problemáticas antes de cualquier modificación.

#### Instrucciones

1. Con el archivo `Lab01_VentasRetail_DeudaTecnica.pbix` abierto en Power BI Desktop, abre **DAX Studio**.

2. En DAX Studio, conecta al modelo: menú **Home → Connect → PBI / SSDT Model** y selecciona `Lab01_VentasRetail_DeudaTecnica`.

3. Exporta el VPAX: menú **Advanced → Export Metrics (VertiPaq Analyzer)**. Guarda el archivo como:
   ```
   C:\LabPowerBI\Lab01\VPAX\Lab01_ANTES.vpax
   ```

4. Abre VertiPaq Analyzer: menú **Advanced → View Metrics** (si no se abre automáticamente, abre el archivo `.vpax` guardado).

5. En la pestaña **Summary**, registra en tu bitácora los siguientes valores:

   | Métrica                        | Valor inicial |
   |-------------------------------|---------------|
   | Tamaño total del modelo (MB)  | ___________   |
   | Número de tablas              | ___________   |
   | Número de columnas total      | ___________   |
   | Columnas calculadas (count)   | ___________   |

6. En la pestaña **Columns**, ordena por **Total Size** (descendente). Identifica y anota las **5 columnas de mayor tamaño**:

   | Tabla            | Columna              | Cardinalidad | Tipo de dato | Tamaño (KB) |
   |------------------|----------------------|--------------|--------------|-------------|
   | ___________      | ___________          | ___________  | ___________  | ___________ |
   | ___________      | ___________          | ___________  | ___________  | ___________ |
   | ___________      | ___________          | ___________  | ___________  | ___________ |
   | ___________      | ___________          | ___________  | ___________  | ___________ |
   | ___________      | ___________          | ___________  | ___________  | ___________ |

7. Filtra la vista de columnas para mostrar solo **columnas calculadas** (columna *Is Calculated = TRUE*). Anota cuántas existen y en qué tablas.

8. Ejecuta la siguiente consulta DMV en DAX Studio para identificar medidas con lógica potencialmente duplicada:

```DAX
SELECT
    [MEASUREGROUP_NAME]    AS [Tabla],
    [MEASURE_NAME]         AS [Medida],
    [EXPRESSION]           AS [Expresion DAX]
FROM $SYSTEM.MDSCHEMA_MEASURES
WHERE [MEASURE_IS_VISIBLE] = TRUE
ORDER BY [MEASUREGROUP_NAME], [MEASURE_NAME]
```

9. Revisa los resultados. Marca en la lista las medidas que parezcan calcular lo mismo con expresiones ligeramente distintas (por ejemplo, `Ventas_Total`, `Total Ventas`, `SumaVentas`).

10. Toma una captura de pantalla de la pestaña **Summary** de VertiPaq Analyzer y guárdala como:
    ```
    C:\LabPowerBI\Lab01\Capturas\01_VertiPaq_ANTES_Summary.png
    ```

#### Resultado Esperado

- Archivo `Lab01_ANTES.vpax` guardado correctamente.
- Bitácora con tamaño inicial del modelo, top 5 columnas por consumo y lista de medidas potencialmente duplicadas.
- Identificación de al menos: 1 columna DateTime con hora innecesaria, 1 columna de texto con cardinalidad > 10,000, y 2+ columnas calculadas materializadas.

#### Verificación

En DAX Studio, ejecuta:

```DAX
SELECT
    [TABLE_NAME]   AS [Tabla],
    [COLUMN_ID]    AS [Columna],
    [DICTIONARY_SIZE] AS [Tamanio_Diccionario_Bytes]
FROM $SYSTEM.DISCOVER_STORAGE_TABLE_COLUMN_SEGMENTS
ORDER BY [DICTIONARY_SIZE] DESC
```

Confirma que los resultados coinciden con lo observado en VertiPaq Analyzer. Las columnas con diccionarios más grandes deben corresponder a las identificadas en el paso 6.

---

### Paso 2 — Optimización en Power Query: Tipos de Datos y Eliminación de Columnas

**Objetivo:** Reducir el tamaño del modelo eliminando columnas no utilizadas y convirtiendo tipos de datos subóptimos directamente en la capa de ingesta (Power Query), aplicando las transformaciones antes de que VertiPaq materialice los datos.

#### Instrucciones

1. En Power BI Desktop, abre el **Editor de Power Query**: menú **Inicio → Transformar datos**.

2. **Eliminar columnas no utilizadas en visualizaciones:**

   Selecciona la tabla `FactVentas`. Identifica las siguientes columnas que no aparecen en ningún visual ni son usadas por medidas (confirmado en el diagnóstico del Paso 1):
   - `OrderTimeStamp` (DateTime completo — la hora no se usa)
   - `ShipAddressFull` (texto concatenado de alta cardinalidad)
   - `InternalNotes` (texto libre, cardinalidad muy alta)
   - `ETLLoadID` (clave técnica de ETL, no de negocio)

   Para eliminarlas, haz clic derecho sobre cada columna → **Quitar columnas**. Alternativamente, usa el editor avanzado para agregar este paso en M:

   ```m
   #"Columnas eliminadas" = Table.RemoveColumns(
       #"Paso anterior",
       {"OrderTimeStamp", "ShipAddressFull", "InternalNotes", "ETLLoadID"}
   )
   ```

3. **Convertir DateTime a Date (reducir cardinalidad):**

   En la tabla `FactVentas`, localiza la columna `OrderDate` que tiene tipo `datetime`. Convierte a `date`:

   ```m
   #"OrderDate a Date" = Table.TransformColumns(
       #"Columnas eliminadas",
       {{"OrderDate", DateTime.Date, type date}}
   )
   ```

   Repite para `ShipDate` si también es datetime.

4. **Redondear decimales a precisión de negocio:**

   La columna `UnitPrice` tiene 6 decimales. El negocio trabaja con 2 decimales:

   ```m
   #"UnitPrice redondeado" = Table.TransformColumns(
       #"OrderDate a Date",
       {{"UnitPrice", each Number.Round(_, 2), type number}}
   )
   ```

5. **Convertir columna de texto a clave entera (DimCanal):**

   La tabla `FactVentas` contiene la columna `CanalVenta` (texto: "Online", "Tienda Física", "Distribuidor", etc.) con cardinalidad moderada pero repetida en millones de filas.

   a. Selecciona la tabla `DimCanal` (ya existe en el modelo). Verifica que tiene las columnas `CanalKey` (entero) y `CanalVenta` (texto).

   b. En la tabla `FactVentas`, verifica que existe la columna `CanalKey` (entero). Si la columna `CanalVenta` texto **también** existe en `FactVentas`, elimínala:

   ```m
   #"CanalVenta texto eliminado" = Table.RemoveColumns(
       #"UnitPrice redondeado",
       {"CanalVenta"}
   )
   ```

   c. Confirma que la relación `FactVentas[CanalKey] → DimCanal[CanalKey]` existe en el modelo (la verificarás en el Paso 3).

6. **Verificar tipos de datos en todas las tablas de dimensiones:**

   Revisa `DimProducto`, `DimCliente` y `DimGeografia`. Para cada columna de clave (terminada en `Key` o `ID`), asegúrate de que el tipo sea **Número entero** (`Int64.Type`), no texto. Corrige los que sean incorrectos:

   ```m
   #"Tipos corregidos DimProducto" = Table.TransformColumnTypes(
       Source,
       {
           {"ProductKey",  Int64.Type},
           {"CategoryKey", Int64.Type},
           {"SubcategoryKey", Int64.Type}
       }
   )
   ```

7. Haz clic en **Cerrar y aplicar**. Espera a que el modelo se recargue.

8. Toma captura del panel de campos mostrando las tablas y columnas resultantes:
   ```
   C:\LabPowerBI\Lab01\Capturas\02_PowerQuery_Post_Optimizacion.png
   ```

#### Resultado Esperado

- La tabla `FactVentas` no contiene las columnas `OrderTimeStamp`, `ShipAddressFull`, `InternalNotes`, `ETLLoadID` ni `CanalVenta` (texto).
- `OrderDate` y `ShipDate` son de tipo `date`, no `datetime`.
- `UnitPrice` tiene máximo 2 decimales.
- Todas las columnas `*Key` e `*ID` son de tipo entero en todas las tablas.
- El modelo recarga sin errores.

#### Verificación

En DAX Studio, ejecuta la siguiente consulta para confirmar que las columnas eliminadas ya no existen:

```DAX
SELECT
    [TABLE_NAME],
    [COLUMN_ID],
    [DATA_TYPE]
FROM $SYSTEM.DISCOVER_STORAGE_TABLE_COLUMNS
WHERE [TABLE_NAME] = 'FactVentas'
  AND [COLUMN_TYPE] = 'BASIC_DATA'
ORDER BY [TABLE_NAME], [COLUMN_ID]
```

Confirma que `ShipAddressFull`, `InternalNotes`, `ETLLoadID` y `CanalVenta` **no aparecen** en los resultados.

---

### Paso 3 — Optimización del Modelo: Relaciones, Auto Date/Time y DimFecha

**Objetivo:** Eliminar relaciones innecesarias o ineficientes, desactivar *Auto date/time* para suprimir tablas de fecha ocultas redundantes, y validar que la `DimFecha` única está correctamente configurada.

#### Instrucciones

1. **Desactivar Auto date/time en el archivo actual:**

   En Power BI Desktop: **Archivo → Opciones y configuración → Opciones → pestaña "Archivo actual" → Carga de datos** → desmarcar **"Auto date/time"**.

   > ⚠️ **Importante:** Esto debe hacerse tanto en la configuración *global* como en la del *archivo actual*. La configuración global afecta nuevos archivos; la del archivo actual afecta el modelo abierto.

   Haz clic en **Aceptar** y espera a que el modelo se actualice.

2. **Verificar eliminación de tablas de fecha ocultas:**

   En DAX Studio, ejecuta:

   ```DAX
   SELECT
       [TABLE_NAME],
       [TABLE_IS_PRIVATE]
   FROM $SYSTEM.TMSCHEMA_TABLES
   ORDER BY [TABLE_IS_PRIVATE] DESC, [TABLE_NAME]
   ```

   Las tablas con `TABLE_IS_PRIVATE = TRUE` son las tablas auto date/time. Después de desactivar la opción, al recargar el modelo, estas tablas deben desaparecer o reducirse significativamente.

3. **Revisar y corregir relaciones Many-to-Many evitables:**

   En la vista de **Modelo** de Power BI Desktop, identifica relaciones marcadas con el símbolo `*` en ambos extremos (Many-to-Many). El modelo de práctica tiene una relación M:M entre `FactVentas` y `DimPromocion`.

   Esta relación existe porque `FactVentas` tiene una columna `PromocionCodigo` (texto) que no es única en `DimPromocion`. Solución:

   a. En `DimPromocion`, verifica que existe `PromocionKey` (entero, único).

   b. En Power Query, en `FactVentas`, verifica que existe `PromocionKey` (entero). Si no existe, crea una combinación (merge) con `DimPromocion` para obtener la clave:

   ```m
   #"Merge Promocion" = Table.NestedJoin(
       #"Paso anterior",
       {"PromocionCodigo"},
       DimPromocion,
       {"PromocionCodigo"},
       "DimPromocion",
       JoinKind.LeftOuter
   ),
   #"PromocionKey expandido" = Table.ExpandTableColumn(
       #"Merge Promocion",
       "DimPromocion",
       {"PromocionKey"},
       {"PromocionKey"}
   ),
   #"PromocionCodigo eliminado" = Table.RemoveColumns(
       #"PromocionKey expandido",
       {"PromocionCodigo"}
   )
   ```

   c. Elimina la relación M:M existente en la vista de Modelo.

   d. Crea una nueva relación: `FactVentas[PromocionKey] → DimPromocion[PromocionKey]` (Many-to-One, dirección de filtro única: de dimensión a hecho).

4. **Verificar relaciones bidireccionales innecesarias:**

   En la vista de Modelo, identifica relaciones con dirección de filtro **Ambas** (bidireccional). Evalúa cada una:
   - Si la bidireccionalidad es necesaria para la lógica de negocio (p. ej., rol de seguridad), consérvala documentada.
   - Si fue configurada "por defecto" sin análisis, cámbiala a **Dirección única** (de dimensión a hecho).

   En el modelo de práctica, la relación `DimGeografia ↔ DimCliente` es bidireccional sin justificación. Cámbiala a dirección única: `DimGeografia → DimCliente`.

5. **Validar DimFecha:**

   Confirma que la tabla `DimFecha` contiene al menos las columnas:
   - `DateKey` (entero, formato YYYYMMDD — clave de relación)
   - `Date` (tipo date)
   - `Year` (entero)
   - `QuarterNumber` (entero)
   - `MonthNumber` (entero)
   - `MonthName` (texto — cardinalidad 12)
   - `DayOfWeek` (entero)
   - `IsWeekend` (booleano)

   > ✅ **Buena práctica:** Evita columnas concatenadas como `"2024-Q1"` o `"Ene 2024"` como texto. Usa columnas separadas y define jerarquías en el modelo.

   Verifica que `FactVentas[OrderDate]` tiene una relación activa con `DimFecha[Date]` (o `DimFecha[DateKey]` si usas clave entera).

6. Guarda el archivo: **Ctrl + S**.

#### Resultado Esperado

- *Auto date/time* desactivado; las tablas privadas de fecha ya no aparecen en la consulta DMV.
- La relación `FactVentas ↔ DimPromocion` es Many-to-One con dirección de filtro única.
- La relación `DimGeografia ↔ DimCliente` tiene dirección única.
- `DimFecha` está correctamente relacionada con `FactVentas[OrderDate]`.

#### Verificación

En la vista de Modelo, confirma visualmente:
- Ninguna relación muestra `*` en ambos extremos.
- Las flechas de filtro apuntan desde dimensiones hacia hechos (excepto casos documentados).

En DAX Studio, verifica que no quedan tablas privadas:

```DAX
SELECT [TABLE_NAME], [TABLE_IS_PRIVATE]
FROM $SYSTEM.TMSCHEMA_TABLES
WHERE [TABLE_IS_PRIVATE] = TRUE
```

El resultado debe estar vacío o contener únicamente tablas privadas justificadas.

---

### Paso 4 — Refactorización DAX: Eliminar Columnas Calculadas y Consolidar Medidas

**Objetivo:** Convertir columnas calculadas materializadas en medidas calculadas a demanda, y consolidar medidas redundantes en un conjunto de medidas base reutilizables con convenciones de nomenclatura claras.

#### Instrucciones

1. **Identificar y eliminar columnas calculadas innecesarias:**

   En la vista de **Datos** de Power BI Desktop, navega a la tabla `FactVentas`. Identifica las siguientes columnas calculadas (icono de función `fx`):
   - `Margen` = `FactVentas[ImporteVenta] - FactVentas[ImporteCosto]`
   - `Margen%` = `DIVIDE(FactVentas[Margen], FactVentas[ImporteVenta])`
   - `VentasConIVA` = `FactVentas[ImporteVenta] * 1.21`

   Estas columnas se materializan fila por fila y ocupan memoria. Deben convertirse en medidas.

   Para eliminar cada columna calculada: selecciona la columna → clic derecho → **Eliminar columna**. Confirma la eliminación.

2. **Crear tabla de medidas centralizada:**

   Crea una tabla vacía dedicada a medidas (buena práctica de organización):

   En Power BI Desktop: **Modelado → Nueva tabla**:

   ```DAX
   _Medidas = DATATABLE("Placeholder", STRING, {{""}})
   ```

   Oculta la columna `Placeholder`: clic derecho sobre la columna → **Ocultar en vista de informe**.

3. **Crear medidas base reutilizables:**

   En la tabla `_Medidas`, crea las siguientes medidas. Usa **Modelado → Nueva medida**:

   ```DAX
   Ventas =
   SUM(FactVentas[ImporteVenta])
   ```

   ```DAX
   Costo =
   SUM(FactVentas[ImporteCosto])
   ```

   ```DAX
   Unidades =
   SUM(FactVentas[Cantidad])
   ```

4. **Crear medidas derivadas que referencian las medidas base:**

   ```DAX
   Margen =
   [Ventas] - [Costo]
   ```

   ```DAX
   Margen % =
   DIVIDE([Margen], [Ventas], 0)
   ```

   ```DAX
   Ventas Con IVA =
   VAR _tasaIVA = 0.21
   RETURN
       [Ventas] * (1 + _tasaIVA)
   ```

   ```DAX
   Ticket Promedio =
   DIVIDE([Ventas], [Unidades], 0)
   ```

5. **Identificar y eliminar medidas duplicadas:**

   Basándote en la lista obtenida en el Paso 1 (consulta DMV), localiza las medidas redundantes. El modelo de práctica contiene:

   | Medida redundante a eliminar | Medida base equivalente |
   |------------------------------|-------------------------|
   | `Ventas_Total`               | `Ventas`                |
   | `Total Ventas`               | `Ventas`                |
   | `SumaVentas`                 | `Ventas`                |
   | `Margen Bruto`               | `Margen`                |
   | `PorcentajeMargen`           | `Margen %`              |

   Para cada medida redundante: selecciona la medida en el panel de campos → clic derecho → **Eliminar del modelo**.

   > ⚠️ **Antes de eliminar:** Verifica en la vista de **Informe** que ningún visual usa la medida redundante. Si algún visual la usa, actualiza el visual para usar la medida base equivalente antes de eliminar.

6. **Organizar medidas en carpetas de visualización:**

   Selecciona cada medida en el panel de campos. En el panel de **Propiedades** (panel derecho), asigna la carpeta de visualización:

   | Medida           | Carpeta de visualización |
   |------------------|--------------------------|
   | `Ventas`         | `Ventas\Base`            |
   | `Costo`          | `Ventas\Base`            |
   | `Unidades`       | `Ventas\Base`            |
   | `Margen`         | `Rentabilidad`           |
   | `Margen %`       | `Rentabilidad`           |
   | `Ventas Con IVA` | `Ventas\Derivadas`       |
   | `Ticket Promedio`| `Ventas\Derivadas`       |

7. **Ocultar columnas técnicas:**

   En la vista de Modelo, oculta las siguientes columnas (clic derecho → **Ocultar en vista de informe**):
   - Todas las columnas `*Key` e `*ID` en tablas de hechos y dimensiones.
   - La columna `Placeholder` de la tabla `_Medidas`.
   - Columnas de ordenación (p. ej., `MonthNumber` si se usa solo para ordenar `MonthName`).

8. Guarda el archivo: **Ctrl + S**.

#### Resultado Esperado

- Las columnas calculadas `Margen`, `Margen%` y `VentasConIVA` ya no existen en `FactVentas`.
- Existe la tabla `_Medidas` con al menos 7 medidas organizadas en carpetas.
- Las medidas redundantes (`Ventas_Total`, `Total Ventas`, `SumaVentas`, `Margen Bruto`, `PorcentajeMargen`) han sido eliminadas.
- Las columnas técnicas están ocultas en la vista de informe.

#### Verificación

Ejecuta en DAX Studio para confirmar el conteo de medidas actual:

```DAX
SELECT
    COUNT([MEASURE_NAME]) AS [Total_Medidas],
    [MEASUREGROUP_NAME]   AS [Tabla]
FROM $SYSTEM.MDSCHEMA_MEASURES
WHERE [MEASURE_IS_VISIBLE] = TRUE
GROUP BY [MEASUREGROUP_NAME]
ORDER BY [Tabla]
```

Verifica que el total de medidas es menor que el inicial (medidas redundantes eliminadas) y que `_Medidas` aparece como tabla contenedora principal.

Adicionalmente, crea un visual de tabla en el informe con `DimProducto[ProductName]` y las medidas `[Ventas]`, `[Margen]`, `[Margen %]`. Confirma que los valores son consistentes con los reportes originales (compara con capturas del estado inicial).

---

### Paso 5 — Benchmarking Comparativo: Antes vs. Después

**Objetivo:** Cuantificar el impacto total de las optimizaciones aplicadas exportando un nuevo VPAX, comparando métricas de tamaño y ejecutando consultas de benchmark para medir la mejora en tiempo de respuesta.

#### Instrucciones

1. **Exportar VPAX del modelo optimizado:**

   En DAX Studio (reconecta al modelo actualizado si es necesario): **Advanced → Export Metrics (VertiPaq Analyzer)**. Guarda como:
   ```
   C:\LabPowerBI\Lab01\VPAX\Lab01_DESPUES.vpax
   ```

2. **Comparar métricas de tamaño:**

   Abre ambos archivos VPAX en VertiPaq Analyzer y completa la tabla comparativa en tu bitácora:

   | Métrica                           | Antes        | Después      | Reducción (%) |
   |-----------------------------------|--------------|--------------|---------------|
   | Tamaño total del modelo (MB)      | ___________  | ___________  | ___________   |
   | Número de columnas                | ___________  | ___________  | ___________   |
   | Número de columnas calculadas     | ___________  | ___________  | ___________   |
   | Número de medidas                 | ___________  | ___________  | ___________   |
   | Tamaño FactVentas (MB)            | ___________  | ___________  | ___________   |
   | Tablas privadas (auto date/time)  | ___________  | ___________  | ___________   |

   > 🎯 **Meta:** Reducción de tamaño total ≥ 30 %. Si no se alcanza, revisa si quedan columnas calculadas o si *Auto date/time* fue desactivado correctamente en el archivo actual.

3. **Ejecutar consultas de benchmark:**

   En DAX Studio, ejecuta las siguientes consultas de benchmark. Para cada una, usa **Query → Run** y registra el tiempo en **Server Timings** (habilita con **Home → Server Timings**).

   **Consulta de benchmark 1 — Ventas por categoría y año:**
   ```DAX
   EVALUATE
   SUMMARIZECOLUMNS(
       DimProducto[Category],
       DimFecha[Year],
       "Ventas",    [Ventas],
       "Margen",    [Margen],
       "Margen %",  [Margen %]
   )
   ORDER BY DimFecha[Year], DimProducto[Category]
   ```

   **Consulta de benchmark 2 — Top 10 clientes por ventas:**
   ```DAX
   EVALUATE
   TOPN(
       10,
       SUMMARIZECOLUMNS(
           DimCliente[CustomerName],
           "Ventas", [Ventas]
       ),
       [Ventas], DESC
   )
   ```

   **Consulta de benchmark 3 — Ventas mensuales del último año:**
   ```DAX
   EVALUATE
   CALCULATETABLE(
       SUMMARIZECOLUMNS(
           DimFecha[Year],
           DimFecha[MonthNumber],
           DimFecha[MonthName],
           "Ventas",   [Ventas],
           "Unidades", [Unidades]
       ),
       DimFecha[Year] = YEAR(TODAY()) - 1
   )
   ORDER BY DimFecha[MonthNumber]
   ```

   Registra los tiempos en tu bitácora:

   | Consulta       | Tiempo ANTES (ms) | Tiempo DESPUÉS (ms) | Mejora (%) |
   |----------------|-------------------|---------------------|------------|
   | Benchmark 1    | ___________       | ___________         | ___________|
   | Benchmark 2    | ___________       | ___________         | ___________|
   | Benchmark 3    | ___________       | ___________         | ___________|

   > **Nota:** Si no tienes los tiempos "ANTES" porque no los mediste en el Paso 1, usa el archivo `Lab01_VentasRetail_DeudaTecnica.pbix` original (sin modificar) en una segunda instancia de Power BI Desktop para obtener los tiempos de referencia.

4. **Guardar el archivo final optimizado:**

   Guarda el archivo con un nombre que distinga la versión optimizada:
   ```
   C:\LabPowerBI\Lab01\Lab01_VentasRetail_Optimizado.pbix
   ```

5. Toma captura final de VertiPaq Analyzer (pestaña Summary del modelo optimizado):
   ```
   C:\LabPowerBI\Lab01\Capturas\05_VertiPaq_DESPUES_Summary.png
   ```

#### Resultado Esperado

- Archivo `Lab01_DESPUES.vpax` guardado.
- Tabla comparativa completa en la bitácora con reducción ≥ 30 % en tamaño total.
- Las tres consultas de benchmark muestran tiempos iguales o menores al estado inicial.
- Archivo `Lab01_VentasRetail_Optimizado.pbix` guardado en la carpeta de trabajo.

#### Verificación

En VertiPaq Analyzer, pestaña **Columns** del archivo DESPUES, confirma:
- Ninguna columna de tipo `Calculated` con tamaño > 1 MB (las columnas calculadas eliminadas no deben aparecer).
- La columna `OrderDate` muestra tipo `Date` (no `DateTime`).
- Las columnas `ShipAddressFull`, `InternalNotes`, `ETLLoadID` no existen.

---

## 7. Validación y Pruebas

Al completar todos los pasos, realiza las siguientes verificaciones finales para confirmar que el laboratorio fue completado exitosamente:

### Lista de verificación de completitud

| # | Verificación                                                                 | Estado |
|---|------------------------------------------------------------------------------|--------|
| 1 | Archivo `Lab01_ANTES.vpax` existe en `C:\LabPowerBI\Lab01\VPAX\`            | ☐      |
| 2 | Archivo `Lab01_DESPUES.vpax` existe en `C:\LabPowerBI\Lab01\VPAX\`          | ☐      |
| 3 | Reducción de tamaño de modelo ≥ 30 %                                         | ☐      |
| 4 | *Auto date/time* desactivado — sin tablas privadas en consulta DMV           | ☐      |
| 5 | Columnas calculadas `Margen`, `Margen%`, `VentasConIVA` eliminadas de `FactVentas` | ☐ |
| 6 | Medidas redundantes eliminadas (mínimo 5 medidas duplicadas removidas)       | ☐      |
| 7 | Tabla `_Medidas` con carpetas de visualización configuradas                  | ☐      |
| 8 | Relación `FactVentas ↔ DimPromocion` es Many-to-One (no M:M)                | ☐      |
| 9 | Relación `DimGeografia ↔ DimCliente` tiene dirección de filtro única         | ☐      |
| 10| Consultas de benchmark ejecutadas con tiempos registrados                    | ☐      |
| 11| Archivo `Lab01_VentasRetail_Optimizado.pbix` guardado                        | ☐      |

### Prueba de integridad de datos

Ejecuta en DAX Studio para confirmar que las medidas base producen resultados correctos:

```DAX
EVALUATE
ROW(
    "Total Ventas",    [Ventas],
    "Total Costo",     [Costo],
    "Total Margen",    [Margen],
    "Margen Pct",      [Margen %],
    "Total Unidades",  [Unidades]
)
```

Compara los totales con los valores del modelo original (antes de optimizar). Los totales de `Ventas`, `Costo` y `Unidades` deben ser **idénticos**. Si difieren, revisa que no se hayan eliminado columnas de datos fuente por error en el Paso 2.

---

## 8. Solución de Problemas

### Problema 1: El modelo no reduce tamaño después de desactivar Auto date/time

**Síntoma:** Después de desactivar *Auto date/time* y recargar el modelo, VertiPaq Analyzer sigue mostrando tablas privadas y el tamaño del modelo no disminuye significativamente.

**Causa:** La opción *Auto date/time* fue desactivada en la configuración **global** (nuevos archivos) pero no en la configuración del **archivo actual**. Ambas configuraciones son independientes y deben desactivarse por separado.

**Solución:**
1. En Power BI Desktop, ve a **Archivo → Opciones y configuración → Opciones**.
2. En el panel izquierdo, bajo la sección **ARCHIVO ACTUAL** (no Global), selecciona **Carga de datos**.
3. Desmarca **"Auto date/time"** en esta sección específica del archivo actual.
4. Haz clic en **Aceptar**.
5. Cierra y vuelve a abrir el archivo PBIX (o usa **Inicio → Actualizar**).
6. Reconecta DAX Studio y vuelve a ejecutar la consulta DMV de tablas privadas para confirmar la eliminación.

---

### Problema 2: Los visuals del informe muestran error después de eliminar medidas redundantes

**Síntoma:** Al eliminar las medidas redundantes (`Ventas_Total`, `Total Ventas`, etc.), algunos visuals del informe muestran el mensaje *"No se puede mostrar el objeto visual"* o campos marcados con un signo de advertencia amarillo.

**Causa:** Uno o más visuals del informe referenciaban directamente las medidas eliminadas. Al eliminar la medida sin actualizar primero el visual, la referencia queda rota.

**Solución:**
1. Antes de eliminar cualquier medida redundante, navega a cada página del informe y revisa el panel de **Campos** de cada visual.
2. Si un visual usa `Ventas_Total`, reemplaza ese campo por la medida base `Ventas` arrastrando la nueva medida al visual y eliminando la referencia antigua.
3. Una vez confirmado que ningún visual usa la medida redundante, procede a eliminarla.
4. Si ya eliminaste la medida y el visual está roto: ve a la vista de **Informe**, selecciona el visual afectado, en el panel de Campos verás el campo marcado con ⚠️ — elimina ese campo del visual y agrega la medida base equivalente.
5. Para prevenir este problema en el futuro, usa la función **Analizar en Excel** o la vista de **Árbol de dependencias** (disponible en Tabular Editor) para identificar todas las dependencias de una medida antes de eliminarla.

---

## 9. Limpieza del Entorno

Una vez completado el laboratorio y validados todos los puntos de la lista de verificación:

1. **Cerrar conexiones de DAX Studio:**
   En DAX Studio, cierra la conexión activa: **File → Disconnect** o cierra la ventana de DAX Studio.

2. **Conservar archivos de trabajo:**
   Los siguientes archivos son necesarios para el **Lab 02** (Grupos de Cálculo):
   - `C:\LabPowerBI\Lab01\Lab01_VentasRetail_Optimizado.pbix` ← **Este archivo es la entrada del Lab 02**
   - `C:\LabPowerBI\Lab01\VPAX\Lab01_ANTES.vpax`
   - `C:\LabPowerBI\Lab01\VPAX\Lab01_DESPUES.vpax`

3. **Archivar el modelo con deuda técnica original:**
   ```
   copy C:\LabPowerBI\Lab01\Lab01_VentasRetail_DeudaTecnica.pbix
        C:\LabPowerBI\Lab01\Archivados\Lab01_VentasRetail_DeudaTecnica_ORIGINAL.pbix
   ```

4. **Cerrar Power BI Desktop** si no continuarás con el siguiente laboratorio en esta sesión.

5. **Opcional — Limpiar archivos temporales de Power BI:**
   Power BI Desktop crea archivos de caché en `%LOCALAPPDATA%\Microsoft\Power BI Desktop\`. Si el disco está bajo en espacio, puedes limpiar la subcarpeta `TempSaves`, pero **no elimines** la carpeta `AnalysisServicesWorkspaces` mientras Power BI Desktop esté abierto.

---

## 10. Resumen

### Lo que aprendiste en este laboratorio

En este laboratorio aplicaste un proceso completo de diagnóstico y remediación de deuda técnica en un modelo semántico Power BI:

1. **Diagnóstico con VertiPaq Analyzer y DMVs:** Aprendiste a exportar un archivo VPAX y a interpretar las métricas de tamaño, cardinalidad y columnas calculadas para priorizar intervenciones con impacto real.

2. **Optimización en Power Query:** Aplicaste las transformaciones en el origen correcto — la capa de ingesta — para que VertiPaq nunca materialice datos innecesarios: eliminación de columnas, conversión de DateTime a Date, redondeo de decimales y sustitución de texto por claves enteras.

3. **Gobernanza del modelo:** Desactivaste *Auto date/time*, corregiste relaciones M:M y bidireccionales innecesarias, y validaste la integridad de la `DimFecha` única — tres acciones con alto impacto en tamaño y claridad semántica.

4. **Refactorización DAX:** Convertiste columnas calculadas materializadas en medidas calculadas a demanda, consolidaste medidas redundantes en medidas base con `CALCULATE`, `DIVIDE` y `VAR`, y organizaste el modelo con carpetas de visualización y convenciones de nomenclatura.

5. **Benchmarking comparativo:** Cuantificaste el impacto de cada optimización con métricas objetivas (tamaño VPAX y tiempos de consulta), estableciendo la práctica de medir antes y después como estándar de trabajo.

### Conexión con los próximos laboratorios

El archivo `Lab01_VentasRetail_Optimizado.pbix` generado en este laboratorio es la base del **Lab 02**, donde implementarás **Grupos de Cálculo** sobre las medidas base creadas aquí para centralizar lógica de inteligencia de tiempo y comparación de períodos, eliminando la necesidad de crear decenas de medidas derivadas adicionales.

### Recursos de referencia

| Recurso | URL |
|---------|-----|
| Técnicas de reducción de datos para modelos Import en Power BI | https://learn.microsoft.com/power-bi/guidance/import-modeling-data-reduction |
| Diseño de esquema estrella para Power BI | https://learn.microsoft.com/power-bi/guidance/star-schema |
| VertiPaq (almacenamiento columnar) en Analysis Services | https://learn.microsoft.com/analysis-services/tabular/vertipaq |
| Auto date/time en Power BI Desktop | https://learn.microsoft.com/power-bi/transform-model/desktop-auto-date-time |
| Agregaciones avanzadas en Power BI | https://learn.microsoft.com/power-bi/transform-model/aggregations-advanced |
| VertiPaq Analyzer (SQLBI) | https://www.sqlbi.com/tools/vertipaq-analyzer/ |
| Optimizing DAX (SQLBI) | https://www.sqlbi.com/articles/optimizing-dax/ |

---

> **Nota para el instructor:** Si algún participante no alcanza la reducción del 30 % en tamaño, verifique primero si *Auto date/time* fue desactivado correctamente en el **archivo actual** (no solo en global). Esta es la causa más frecuente de reducción insuficiente. En segundo lugar, verifique que las columnas calculadas fueron eliminadas del modelo y no solo ocultadas.

---
LAB_END---
