# Configuración del entorno — Ingeniería de Datos en Power BI Pro

Completa esta configuración **una sola vez** antes de iniciar el Capítulo 01. La ruta principal del taller usa archivos CSV locales y Power BI Desktop/Service. SQL Server es **recomendado solo para la demostración técnica acotada del Capítulo 03**; no es obligatorio para completar todo el curso.

> Al final de este documento encontrarás la **matriz de requisitos por laboratorio** (sección 8): qué necesitas, qué entra y qué sale en cada capítulo.

---

## 1. Estructura de carpetas

En el Github del curso se encuentra la carpeta `LabPowerBI` con esta estructura. Descargar la carpeta y extraerla en `C:\` para obtener la carpeta `C:\LabPowerBI\` con todo organizado. No es necesario crear la estructura manualmente.

Estructura de carpetas:

```text
C:\LabPowerBI\
├── AllFiles\              ← Tiene 9 archivos .CSV de datos del paquete
│   ├── FactVentas.csv
│   ├── DimFecha.csv
│   ├── DimProducto.csv
│   ├── DimCliente.csv
│   ├── DimGeografia.csv
│   ├── DimCanal.csv
│   ├── DimPromocion.csv
│   ├── FactPresupuesto.csv
│   └── FactForecast.csv
├── Lab01\                 ← trabajo del Capítulo 01 (+ subcarpetas Capturas\ y VPAX\)
├── Lab02\                 ← trabajo del Capítulo 02
├── Lab03\                 ← trabajo del Capítulo 03
├── Lab04\                 ← trabajo del Capítulo 04 (+ repo Git)
└── Lab05\                 ← trabajo del Capítulo 05 (+ scripts\)
```

---

## 2. Power BI Desktop (obligatorio)

1. Instala la versión más reciente desde [Microsoft Store](https://aka.ms/pbidesktopstore) o el [instalador independiente](https://www.microsoft.com/download/details.aspx?id=58494).
2. Verifica la versión en **Ayuda → Acerca de**. Usa una versión publicada en los **últimos 3 meses** (Calculation Groups nativos, DAX Query View y Smart Narrative requieren versiones recientes).

---

## 3. DAX Studio (recomendado — Cap01 y Cap03)

1. Descarga e instala desde [daxstudio.org](https://daxstudio.org/) (gratuito y de código abierto).
2. Confirma que aparece en **Power BI Desktop → pestaña Herramientas externas → DAX Studio**.
3. Se usa para: VertiPaq Analyzer y consultas DMV (Cap01), Server Timings y medición de consultas (Cap03).

---

## 4. Power BI Service y licencias (Cap04 y publicación)

Se requiere licencia de Power BI Pro para publicar a un workspace, crear workspaces manuales y usar alertas de datos. Para Deployment Pipelines se necesita un workspace en Fabric/Premium/PPU según el tenant. Para Copilot en Power BI, el tenant debe estar habilitado y tener capacidad compatible (Fabric/Premium).

---

## 5. Python 3.10+ (recomendado — Cap05)

```powershell
python --version
python -m venv C:\LabPowerBI\Lab05\.venv
C:\LabPowerBI\Lab05\.venv\Scripts\Activate.ps1
pip install requests pandas python-dotenv
```

- Marca **"Add Python to PATH"** durante la instalación.

---

## 7. Tabular Editor y SQL Server

- **Tabular Editor 2/3** (opcional): alternativa para crear Calculation Groups (Cap02) y para exportar `VentasRetail.bim` (Cap04/Cap05). Descárgalo desde [github.com/TabularEditor](https://github.com/TabularEditor/TabularEditor/releases). En esta versión **ya no es obligatorio**, porque los grupos de cálculo se crean desde Power BI Desktop.
- **SQL Server / Azure SQL** (recomendado solo para Cap03): se usa para una demostración controlada de **Query Folding** e **Incremental Refresh**. No convierte el curso a SQL Server y no reemplaza los CSV del modelo principal.

Preparación sugerida antes de la sesión:

1. Instala SQL Server Developer, SQL Server Express o prepara una Azure SQL Database.
2. Confirma que puedes conectarte con SQL Server Management Studio o Azure Data Studio.
3. Mantén `FactVentas.csv` en `C:\LabPowerBI\AllFiles\FactVentas.csv`.
4. En el Capítulo 03 ejecuta los scripts incluidos en `Capitulo03\sql\` para crear la base `PBIPRO_Lab` y cargar `dbo.FactVentas`.

Si un alumno no tiene SQL Server, usa la **Ruta B — Contingencia con CSV** del Capítulo 03. El curso no se detiene.

---

## 8. Matriz de requisitos por laboratorio

Esta es la referencia rápida de **qué necesitas, qué entra y qué sale** en cada capítulo.

| Cap. | Archivo de ENTRADA | Archivo de SALIDA | Datos (CSV) | Herramientas imprescindibles | Servicio/extra |
|---|---|---|---|---|---|
| **01** | `Lab01_VentasRetail_DeudaTecnica.pbix` | `Lab01_VentasRetail_Optimizado.pbix` | (los del PBIX inicial) | Power BI Desktop, **DAX Studio**, VertiPaq Analyzer | — |
| **02** | salida Cap01 → `Lab02_Start.pbix` | `Lab02_VentasRetail_DAX_CalculationGroups.pbix` | + `FactPresupuesto.csv`, `FactForecast.csv` | Power BI Desktop (Calculation Groups), DAX Query View | Tabular Editor (opcional) |
| **03** | salida Cap02 → `Lab03_Start.pbix` | `Lab03_VentasRetail_Performance.pbix` | mismos del Cap02 | Power BI Desktop, Power Query Diagnostics, Performance Analyzer, **DAX Studio** | SQL Server recomendado para demo acotada; Ruta B con CSV disponible |
| **04** | salida Cap03 → `Lab04_Start.pbix` | `Lab04_VentasRetail_Gobierno_DevOps.pbix` | mismos del Cap03 | Power BI Desktop, **Power BI Service**, Git | Deployment Pipelines / Power Automate (según tenant) |
| **05** | `Lab04_VentasRetail_Gobierno_DevOps.pbix` | `Lab05_VentasRetail_IA_Documentacion.pbix` | mismos del Cap04 | Power BI Desktop, DAX Query View, Smart Narrative, **Python** | Copilot (opcional) |

> **Regla de oro de continuidad:** cada capítulo parte de una **copia renombrada** del archivo de salida del anterior. Nunca edites el archivo de salida del capítulo previo directamente; cópialo, renómbralo y trabaja sobre la copia.

---

## 9. Checklist antes de iniciar el Capítulo 01

- [ ] Carpeta `C:\LabPowerBI\AllFiles` creada con los 9 CSV.
- [ ] Carpetas `Lab01` … `Lab05` creadas.
- [ ] Power BI Desktop instalado, actualizado y con Auto date/time desactivado en global.
- [ ] DAX Studio instalado y visible en Herramientas externas.
- [ ] Git y VS Code instalados (para Cap04–05).
- [ ] Python 3.10+ instalado (para Cap05).
- [ ] Confirmaste si tu tenant tiene Power BI Service, Deployment Pipelines y Copilot; si no, usarás las rutas alternativas documentadas.
- [ ] Archivo `Lab01_VentasRetail_DeudaTecnica.pbix` disponible en `C:\LabPowerBI\Lab01\`.

---

## 10. Validación rápida de los CSV

Antes de construir el modelo, confirma que `AllFiles` contiene los archivos y que no están bloqueados:

```powershell
Get-ChildItem C:\LabPowerBI\AllFiles\*.csv | Select-Object Name, Length
```

Debes ver **nueve** archivos CSV, incluidos `FactPresupuesto.csv` y `FactForecast.csv`.



























































# Configuración del entorno — Ingeniería de Datos en Power BI Pro

Completa esta configuración **una sola vez** antes de iniciar el Capítulo 01. Este documento prepara una máquina virtual o equipo Windows para ejecutar los cinco laboratorios del taller.

La ruta principal del curso usa **CSV locales + Power BI Desktop + Power BI Service**. SQL Server se usa únicamente como demostración técnica acotada en el Capítulo 03 para **Query Folding** e **Incremental Refresh**. No reemplaza el modelo principal basado en CSV.

---

## 1. Alcance del entorno

Este setup cubre los componentes requeridos o recomendados para todos los laboratorios:

| Componente | Uso principal |
|---|---|
| Power BI Desktop | Desarrollo de modelo, Power Query, DAX, visuales, RLS, PBIP y publicación. |
| Power BI Service | Publicación, workspaces, Deployment Pipelines, RLS en servicio, alertas y Power Automate. |
| VS Code | Edición de Markdown, scripts, archivos `.dax`, `.json`, `.bim`, `.tmdl` y documentación. |
| Python 3.13 | Generación de diccionarios técnicos y automatización local en Capítulo 05. |
| DAX Studio | VertiPaq Analyzer, DMVs, Server Timings y validación de consultas DAX. |
| Tabular Editor 2 o 3 | Calculation Groups, revisión avanzada del modelo y exportación BIM. |
| PowerShell | Preparación de carpetas, instalación, validaciones y ejecución de scripts. |
| Git | Versionamiento local del proyecto PBIP y documentación en Capítulo 04. |
| SQL Server | Solo demostración acotada de Query Folding e Incremental Refresh en Capítulo 03. |
| Navegador Edge| Acceso a Power BI Service, Power Automate y Copilot Chat básico. |

---

## 2. Requisitos mínimos de la máquina

| Recurso | Recomendado |
|---|---|
| Sistema operativo | Windows 10/11 de 64 bits o Windows Server compatible. |
| CPU | 2 vCPU mínimo, 4 vCPU recomendado. |
| Memoria | 8 GB mínimo, 16 GB recomendado. |
| Disco libre | 15 GB mínimo, 25 GB recomendado si se instala SQL Server. |
| Red | Acceso a internet para instalación, Power BI Service y Power Automate. |
| Permisos | Administrador local recomendado para instalar DAX Studio, SQL Server y herramientas externas. |
| Cuenta | Cuenta corporativa o de laboratorio con Power BI Pro/PPU/Fabric Trial según el capítulo. |

---

## 3. Estructura de carpetas

Descarga la carpeta `LabPowerBI` del repositorio del curso y extráela directamente en `C:\` para obtener:

```text
C:\LabPowerBI\
├── AllFiles\
|   ├── SQLBackup\
|           └── PBIPRO_Lab.bak
│   ├── FactVentas.csv
│   ├── DimFecha.csv
│   ├── DimProducto.csv
│   ├── DimCliente.csv
│   ├── DimGeografia.csv
│   ├── DimCanal.csv
│   ├── DimPromocion.csv
│   ├── FactPresupuesto.csv
│   └── FactForecast.csv
├── Lab01\
|       └── Lab01_VentasRetail_DeudaTecnica.pbix (archivo inicial del Capítulo 01)
├── Lab02\
├── Lab03\
├── Lab04\
└── Lab05\
```

> **Importante:** `FactPresupuesto.csv` y `FactForecast.csv` se usan a partir del Capítulo 02. Si el paquete recibido no los incluye, valida con el instructor antes de iniciar ese capítulo o genera/importa esas tablas siguiendo la guía del Capítulo 02.

---

## 4. Instalación rápida desde PowerShell con WinGet

Abre **PowerShell como administrador** y valida que WinGet esté disponible:

```powershell
winget --version
```

Instala las herramientas base:

```powershell
winget install --id Microsoft.PowerBI -e --source winget --accept-package-agreements --accept-source-agreements
winget install --id Microsoft.VisualStudioCode -e --source winget --accept-package-agreements --accept-source-agreements
winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements
winget install --id DaxStudio.DaxStudio -e --source winget --accept-package-agreements --accept-source-agreements
winget install --id TabularEditor.TabularEditor.2 -e --source winget --accept-package-agreements --accept-source-agreements
winget install --id Microsoft.SQLServer.2022.Developer -e --source winget --accept-package-agreements --accept-source-agreements
winget install --id Microsoft.SQLServerManagementStudio -e --source winget --accept-package-agreements --accept-source-agreements
```

> **Nota:** para que DAX Studio y Tabular Editor aparezcan correctamente en **Power BI Desktop → Herramientas externas**, conviene instalarlos con PowerShell ejecutado como administrador. Si después de instalar no aparecen, reinicia Power BI Desktop.

>[!IMPORTANT]
> Restaurar `PBIPRO_Lab.bak` en SQL Server.

---

## 5. Validación rápida de herramientas instaladas

Cierra y vuelve a abrir PowerShell. Luego ejecuta:

```powershell
python --version
py --version
git --version
code --version
```

Power BI Desktop, DAX Studio y Tabular Editor se validan visualmente:

1. Abre Power BI Desktop.
2. Verifica **Ayuda → Acerca de**.
3. Verifica que exista la pestaña **Herramientas externas**.
4. Confirma que aparecen:
   - DAX Studio.
   - Tabular Editor.

---

## 6. Power BI Service, licencias y tenant

Para los capítulos 04 y 05 se requiere acceso al servicio:

| Funcionalidad | Requisito |
|---|---|
| Publicar desde Power BI Desktop | Power BI Pro, PPU o licencia/capacidad asignada por el instructor. |
| Crear workspaces | Permiso habilitado en el tenant. |
| Deployment Pipelines | Fabric/Premium/PPU compatible según configuración del tenant. |
| RLS en Service | Modelo publicado + usuarios/grupos asignados al rol. |
| Alertas de datos | Dashboard tile tipo card, KPI o gauge en Power BI Service. |
| Power Automate | Permisos para crear flujo en el entorno asignado. |
| Copilot Chat básico | Puede usarse como apoyo externo para redacción y validación, sin asumir Copilot integrado en Power BI. |

---

## 7. Checklist antes de iniciar el Capítulo 01

- [ ] `C:\LabPowerBI\` existe.
- [ ] `C:\LabPowerBI\AllFiles\` contiene los CSV requeridos.
- [ ] `Lab01` a `Lab05` existen.
- [ ] Power BI Desktop está instalado y actualizado.
- [ ] DAX Studio está instalado y visible en Herramientas externas.
- [ ] Tabular Editor está instalado y visible en Herramientas externas.
- [ ] Git está instalado y configurado.
- [ ] VS Code está instalado.
- [ ] Python 3.13 está instalado y disponible en PowerShell.
- [ ] `Lab01_VentasRetail_DeudaTecnica.pbix` está disponible en `C:\LabPowerBI\Lab01\`.

---

## 15. Recursos de referencia

| Recurso | URL |
|---|---|
| Power BI Desktop | https://learn.microsoft.com/power-bi/fundamentals/desktop-get-the-desktop |
| DAX Query View | https://learn.microsoft.com/power-bi/transform-model/dax-query-view |
| Power BI Projects PBIP | https://learn.microsoft.com/power-bi/developer/projects/projects-overview |
| Incremental Refresh | https://learn.microsoft.com/power-bi/connect-data/incremental-refresh-configure |
| DAX Studio | https://daxstudio.org/ |
| Tabular Editor | https://docs.tabulareditor.com/ |
| Git for Windows | https://git-scm.com/install/windows |
| Python en Windows | https://learn.microsoft.com/windows/dev-environment/python/ |
| VS Code en Windows | https://code.visualstudio.com/docs/setup/windows |
| SQL Server | https://www.microsoft.com/sql-server/sql-server-downloads |
| SSMS | https://learn.microsoft.com/ssms/install/install |