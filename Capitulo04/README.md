# Gobierno de Datos y Despliegue: Gestión del Ciclo de Vida Analítico

## Metadatos

| Atributo | Valor |
|---|---|
| **Duración estimada** | 74 minutos |
| **Complejidad** | Media |
| **Nivel Bloom** | Crear |
| **Módulo** | 4 — Gobierno de Datos y Despliegue |
| **Versión del laboratorio** | 1.0 |

---

## Descripción General

En este laboratorio los participantes operacionalizan un ciclo de vida analítico completo dentro del Servicio Power BI. Comenzarán creando tres Workspaces (Dev, Test, Prod) conectados por un Deployment Pipeline con reglas de despliegue por ambiente, luego implementarán Row-Level Security dinámica en el modelo semántico y la validarán en el servicio. Posteriormente establecerán un flujo de control de versiones exportando el modelo `.bim` desde Tabular Editor hacia un repositorio Git, simulando un rollback ante un cambio no deseado. El laboratorio concluye aplicando endorsement, un glosario de datos básico y etiquetas de sensibilidad de Microsoft Purview, dejando el activo analítico listo para consumo empresarial gobernado.

---

## Objetivos de Aprendizaje

Al finalizar este laboratorio, serás capaz de:

- [ ] **Configurar** un Deployment Pipeline de tres etapas (Dev → Test → Prod) con reglas de despliegue que ajusten parámetros de conexión por ambiente.
- [ ] **Implementar** Row-Level Security dinámica usando `USERPRINCIPALNAME()` con una tabla de permisos y validar su funcionamiento con la función "Ver como rol".
- [ ] **Versionar** el modelo tabular exportando el archivo `.bim` en Git, realizar commits descriptivos y simular un proceso de rollback.
- [ ] **Aplicar** endorsement (Certificado), un glosario de datos básico y etiquetas de sensibilidad de Microsoft Purview al dataset publicado.

---

## Prerrequisitos

### Conocimiento previo
- Familiaridad con el Servicio Power BI: publicación de reportes y gestión de acceso en Workspaces.
- Conceptos básicos de Row-Level Security en Power BI Desktop.
- Conocimiento básico de Git: inicializar repositorio, `git add`, `git commit`, `git log`, `git checkout`.
- Haber completado los laboratorios anteriores **o** contar con el archivo de solución `Lab03_Solucion.pbix` provisto por el instructor.

### Acceso y licencias
| Requisito | Detalle |
|---|---|
| Licencia Power BI | Pro o Premium Per User (PPU) |
| Permisos en el tenant | Capacidad para crear Workspaces y habilitar Deployment Pipelines |
| Tabular Editor 2 | Versión 2.x (gratuita) instalada y funcional |
| Git | Versión 2.40 o superior, configurado con nombre y correo de usuario |
| Cuenta GitHub o repositorio local | Para alojar el repositorio del modelo tabular |

> **Nota importante:** Si el tenant no tiene habilitados los Deployment Pipelines para tu licencia, notifica al instructor. Se proporcionará una demostración alternativa para los pasos 1 y 2, y los participantes pueden continuar desde el paso 3 (RLS) con el archivo `.pbix` local.

---

## Entorno de Laboratorio

### Hardware mínimo requerido

| Componente | Mínimo | Recomendado |
|---|---|---|
| RAM | 16 GB | 32 GB |
| Procesador | Intel i5 8ª gen / Ryzen 5 | Intel i7/i9 o Ryzen 7 |
| Almacenamiento libre | 50 GB SSD | 100 GB SSD |
| Resolución | 1920×1080 | 2560×1440 (dual monitor) |
| Conexión a Internet | 10 Mbps | 25 Mbps o superior |

### Software requerido

| Herramienta | Versión mínima | Uso en este lab |
|---|---|---|
| Power BI Desktop | Junio 2024 o superior | Configuración de RLS y publicación |
| Power BI Service | Siempre actualizado | Deployment Pipelines, Endorsement |
| Tabular Editor 2 | 2.x (gratuita) | Exportación del archivo `.bim` |
| Git | 2.40+ | Control de versiones del modelo |
| GitHub Desktop *(opcional)* | 3.x | Interfaz visual para Git |
| Navegador web | Edge 120+ / Chrome 120+ | Acceso al Servicio Power BI |

### Configuración inicial del entorno

Antes de comenzar, verifica que Git esté configurado con tu identidad. Abre una terminal (PowerShell o Git Bash) y ejecuta:

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu.correo@empresa.com"
git config --list | grep user
```

Crea la carpeta de trabajo para este laboratorio:

```bash
mkdir C:\Labs\Lab04
cd C:\Labs\Lab04
mkdir repo-modelo-ventas
```

Verifica que Tabular Editor 2 esté accesible desde Power BI Desktop:
1. Abre Power BI Desktop.
2. Ve a **Archivo → Opciones y configuración → Opciones → Vista previa de características**.
3. Confirma que "Herramientas externas" esté habilitado.
4. En la pestaña **Herramientas externas** de la cinta, debe aparecer **Tabular Editor**.

---

## Instrucciones Paso a Paso

---

### Paso 1: Crear Workspaces y Configurar el Deployment Pipeline

**Objetivo:** Establecer los tres ambientes de trabajo (Dev, Test, Prod) en el Servicio Power BI y conectarlos mediante un Deployment Pipeline con reglas de implementación por ambiente.

**Tiempo estimado:** 15 minutos

#### Instrucciones

**1.1 — Crear los tres Workspaces**

1. Abre el Servicio Power BI en el navegador (`https://app.powerbi.com`) e inicia sesión con tu cuenta Pro/PPU.
2. En el panel izquierdo, haz clic en **Workspaces → + Nuevo workspace**.
3. Crea el primer workspace con la siguiente configuración:
   - **Nombre:** `Lab04-Ventas-Dev`
   - **Descripción:** `Ambiente de desarrollo — Lab 04`
   - **Licencia:** Pro (o Premium Per User según disponibilidad)
   - Haz clic en **Guardar**.
4. Repite el proceso para crear:
   - `Lab04-Ventas-Test` (descripción: `Ambiente de pruebas/UAT — Lab 04`)
   - `Lab04-Ventas-Prod` (descripción: `Ambiente de producción — Lab 04`)

> Deberías ver los tres workspaces listados en el panel lateral izquierdo.

**1.2 — Publicar el modelo en el workspace Dev**

1. Abre Power BI Desktop con el archivo `Lab03_Solucion.pbix` (o el archivo provisto por el instructor).
2. Ve a **Inicio → Publicar**.
3. Selecciona el workspace **`Lab04-Ventas-Dev`** y haz clic en **Seleccionar**.
4. Espera a que la publicación finalice. Haz clic en el enlace para abrir el reporte en el servicio y confirma que se publicó correctamente.

**1.3 — Crear el Deployment Pipeline**

1. En el Servicio Power BI, haz clic en **Deployment Pipelines** en el panel izquierdo (ícono de tres círculos conectados).
   - Si no aparece el ícono, ve a `https://app.powerbi.com/deploymentpipelines`.
2. Haz clic en **+ Crear un pipeline**.
3. Asigna el nombre: `Pipeline-Ventas-Lab04` y haz clic en **Crear**.
4. Se mostrará la vista de tres etapas (Desarrollo, Pruebas, Producción). Asigna los workspaces:
   - **Desarrollo:** Haz clic en **Asignar un área de trabajo** → selecciona `Lab04-Ventas-Dev` → **Asignar**.
   - **Pruebas:** Haz clic en **Asignar un área de trabajo** → selecciona `Lab04-Ventas-Test` → **Asignar**.
   - **Producción:** Haz clic en **Asignar un área de trabajo** → selecciona `Lab04-Ventas-Prod` → **Asignar**.

**1.4 — Configurar Reglas de Implementación**

1. En la vista del pipeline, haz clic en el ícono de engranaje (**⚙**) junto a la etapa **Pruebas**.
2. Selecciona **Reglas de implementación**.
3. Verás el dataset publicado (`Lab03_Solucion` o el nombre de tu modelo). Haz clic en él para expandir las reglas disponibles.
4. En la sección **Parámetros**, si el modelo tiene un parámetro `EnvironmentName`, configúralo:
   - **Nombre del parámetro:** `EnvironmentName`
   - **Valor en Pruebas:** `TEST`
   - Haz clic en **Guardar**.
5. Repite el proceso para la etapa **Producción**:
   - Haz clic en el engranaje (**⚙**) de **Producción → Reglas de implementación**.
   - Configura `EnvironmentName` = `PROD`.
   - Haz clic en **Guardar**.

> **Nota:** Si el modelo no tiene el parámetro `EnvironmentName`, puedes crear una regla de origen de datos cambiando la cadena de conexión del servidor. Para efectos de este laboratorio, documenta la interfaz y confirma que entiendes el mecanismo.

**1.5 — Desplegar de Dev a Test**

1. En la vista del pipeline, ubica la etapa **Desarrollo** y haz clic en el botón **Implementar en Pruebas** (flecha hacia la derecha).
2. En el cuadro de diálogo, revisa los artefactos que se desplegarán (dataset y reporte).
3. Haz clic en **Implementar**.
4. Espera a que el despliegue finalice. Deberías ver una marca de verificación verde.
5. Repite el proceso: haz clic en **Implementar en Producción** desde la etapa de Pruebas.

**Salida esperada:**
- Los tres workspaces contienen el dataset y el reporte.
- El pipeline muestra las tres etapas en verde sin diferencias de artefactos.
- Las reglas de implementación están guardadas con valores distintos por ambiente.

**Verificación:**
```
✅ Pipeline-Ventas-Lab04 creado y visible en Deployment Pipelines.
✅ Tres workspaces asignados (Dev, Test, Prod).
✅ Dataset y reporte presentes en los tres workspaces.
✅ Reglas de implementación configuradas para parámetro EnvironmentName.
```

---

### Paso 2: Implementar Row-Level Security Dinámica

**Objetivo:** Configurar RLS dinámica en Power BI Desktop usando `USERPRINCIPALNAME()` con una tabla de permisos, publicar los roles al servicio y validar el acceso con "Ver como rol".

**Tiempo estimado:** 18 minutos

#### Instrucciones

**2.1 — Crear la tabla de permisos de seguridad**

1. Abre Power BI Desktop con el archivo `Lab03_Solucion.pbix`.
2. Ve a la vista **Datos** (ícono de tabla en el panel izquierdo).
3. En la pestaña **Inicio**, haz clic en **Especificar datos** para crear una tabla manual.
4. Crea la siguiente tabla con el nombre `SeguridadUsuarios`:

| UserPrincipalName | Region |
|---|---|
| `usuario1@tudominio.com` | Norte |
| `usuario2@tudominio.com` | Sur |
| `usuario3@tudominio.com` | Centro |
| `tu.correo@tudominio.com` | Norte |

> **Importante:** Reemplaza `tudominio.com` con el dominio real de tu tenant. Incluye tu propio correo electrónico asignado a una región para poder probar el acceso.

5. Haz clic en **Cargar**.

**2.2 — Crear la relación entre la tabla de permisos y el modelo**

1. Ve a la vista **Modelo** (ícono de diagrama).
2. Verifica que exista una columna `Region` en la tabla de hechos o en la tabla de dimensión geográfica (por ejemplo, `DimGeografia[Region]`).
3. Crea una relación entre:
   - `SeguridadUsuarios[Region]` → `DimGeografia[Region]`
   - Cardinalidad: **Muchos a uno** (muchos usuarios → una región)
   - Dirección del filtro cruzado: **Ambos** (para que el filtro de seguridad se propague hacia la tabla de hechos)
4. Haz clic en **Aceptar** para guardar la relación.

**2.3 — Configurar el rol de RLS dinámico**

1. Ve a la pestaña **Modelado** en la cinta.
2. Haz clic en **Administrar roles**.
3. Haz clic en **+ Nuevo rol** y nómbralo: `AccesoRegional`.
4. En el panel de tablas, selecciona la tabla **`SeguridadUsuarios`**.
5. En el campo de expresión DAX del filtro de tabla, escribe:

```dax
[UserPrincipalName] = USERPRINCIPALNAME()
```

6. Haz clic en el ícono de verificación (✓) para validar la expresión. Debe aparecer un mensaje de éxito.
7. Haz clic en **Guardar**.

> **Explicación:** Cuando un usuario accede al reporte, Power BI evalúa `USERPRINCIPALNAME()` con el correo del usuario autenticado. La tabla `SeguridadUsuarios` filtra a ese usuario específico y, a través de la relación, propaga el filtro de región hacia todas las tablas conectadas.

**2.4 — Probar el rol localmente con "Ver como"**

1. Con el rol `AccesoRegional` creado, haz clic en **Ver como** en la pestaña **Modelado**.
2. Selecciona **Otro usuario** e ingresa: `usuario1@tudominio.com`.
3. Activa el rol **`AccesoRegional`**.
4. Haz clic en **Aceptar**.
5. Navega a la vista de **Informe** y verifica que los datos muestran únicamente la región **Norte**.
6. Repite la prueba con `usuario2@tudominio.com` y confirma que solo aparece la región **Sur**.
7. Haz clic en **Detener ver como** para salir del modo de prueba.

**2.5 — Publicar el modelo con RLS al workspace Dev**

1. Guarda el archivo `.pbix` (`Ctrl + S`).
2. Ve a **Inicio → Publicar**.
3. Selecciona **`Lab04-Ventas-Dev`** y haz clic en **Seleccionar**.
4. Cuando se pregunte si deseas reemplazar el dataset existente, selecciona **Reemplazar**.
5. Espera a que la publicación finalice.

**2.6 — Validar RLS en el Servicio Power BI**

1. En el Servicio Power BI, navega al workspace **`Lab04-Ventas-Dev`**.
2. Ubica el **dataset** (no el reporte). Haz clic en los tres puntos (**…**) junto al dataset.
3. Selecciona **Seguridad**.
4. En la página de seguridad del dataset, verás el rol **`AccesoRegional`** listado.
5. Agrega tu propio correo electrónico al rol `AccesoRegional` en el campo **Miembros del rol**.
6. Haz clic en **Agregar → Guardar**.
7. Regresa al workspace, abre el reporte y verifica que solo ves los datos de tu región asignada en la tabla `SeguridadUsuarios`.
8. Para probar con otro usuario (si tienes una cuenta de prueba disponible), usa la opción **Probar como rol** en la página de seguridad del dataset.

**Salida esperada:**
- El rol `AccesoRegional` aparece en la configuración de seguridad del dataset en el servicio.
- Al abrir el reporte como tu usuario, los datos están filtrados a la región asignada en `SeguridadUsuarios`.
- Las pruebas con "Ver como" en Desktop confirman el filtrado correcto por usuario.

**Verificación:**
```
✅ Tabla SeguridadUsuarios creada con al menos 4 registros.
✅ Relación SeguridadUsuarios[Region] → DimGeografia[Region] creada con filtro bidireccional.
✅ Rol AccesoRegional con expresión USERPRINCIPALNAME() guardado.
✅ Prueba local "Ver como" muestra datos filtrados correctamente.
✅ Dataset publicado en Lab04-Ventas-Dev con rol visible en la configuración de seguridad.
```

---

### Paso 3: Control de Versiones del Modelo Tabular con Git

**Objetivo:** Exportar el modelo tabular como archivo `.bim` desde Tabular Editor, inicializar un repositorio Git, realizar commits descriptivos y simular un proceso de rollback ante un cambio no deseado.

**Tiempo estimado:** 20 minutos

#### Instrucciones

**3.1 — Exportar el modelo como archivo .bim desde Tabular Editor**

1. Con el archivo `Lab03_Solucion.pbix` abierto en Power BI Desktop, ve a la pestaña **Herramientas externas** en la cinta.
2. Haz clic en **Tabular Editor** para abrirlo. Tabular Editor se conectará automáticamente al modelo activo en Power BI Desktop.
3. En Tabular Editor, ve a **File → Save to folder…**
   - Si esta opción no está disponible en TE2, usa **File → Save As…** y guarda como archivo `.bim`.
4. Navega a la carpeta: `C:\Labs\Lab04\repo-modelo-ventas\`
5. Guarda el archivo con el nombre: `modelo-ventas.bim`
6. Cierra Tabular Editor.

> **Alternativa con Save As:** En TE2, ve a **File → Save As**, selecciona la carpeta `C:\Labs\Lab04\repo-modelo-ventas\` y guarda como `modelo-ventas.bim`. El archivo `.bim` es JSON legible que representa toda la estructura del modelo tabular.

**3.2 — Inicializar el repositorio Git**

1. Abre una terminal (PowerShell o Git Bash).
2. Navega a la carpeta del repositorio:

```bash
cd C:\Labs\Lab04\repo-modelo-ventas
```

3. Inicializa el repositorio Git:

```bash
git init
```

4. Crea un archivo `.gitignore` para excluir archivos temporales:

```bash
# En PowerShell:
@"
*.pbix
*.pbip
~*
.DS_Store
Thumbs.db
"@ | Out-File -FilePath .gitignore -Encoding utf8
```

5. Crea un archivo `README.md` básico:

```bash
@"
# Modelo Semántico: Ventas Retail

## Descripción
Modelo tabular para análisis de ventas retail (Adventure Works extendido).

## Estructura
- modelo-ventas.bim: Definición completa del modelo tabular (exportado desde Tabular Editor)

## Historial de versiones
Ver commits de Git para el historial completo de cambios.

## Responsable
Desarrollador: [Tu Nombre]
Última actualización: $(Get-Date -Format 'yyyy-MM-dd')
"@ | Out-File -FilePath README.md -Encoding utf8
```

**3.3 — Realizar el primer commit (versión base)**

1. Agrega todos los archivos al área de staging:

```bash
git add .
```

2. Verifica qué archivos se están incluyendo:

```bash
git status
```

Deberías ver:
```
Changes to be committed:
  new file:   .gitignore
  new file:   README.md
  new file:   modelo-ventas.bim
```

3. Realiza el primer commit con un mensaje descriptivo:

```bash
git commit -m "feat: versión inicial del modelo semántico de ventas con RLS dinámica

- Modelo exportado desde Lab03 con optimizaciones de rendimiento
- Tabla SeguridadUsuarios para RLS dinámica con USERPRINCIPALNAME()
- Rol AccesoRegional configurado y validado
- Grupos de cálculo de inteligencia de tiempo incluidos"
```

**3.4 — Simular un cambio no deseado y realizar rollback**

1. Abre el archivo `modelo-ventas.bim` en Visual Studio Code:

```bash
code modelo-ventas.bim
```

2. Busca (Ctrl+F) el nombre de una medida existente en el modelo (por ejemplo, `"Total Ventas"` o `"Sales Amount"`).
3. Cambia el nombre de esa medida a `"MEDIDA_BORRADA_POR_ERROR"` y guarda el archivo (`Ctrl+S`).

4. Regresa a la terminal y verifica el cambio:

```bash
git diff modelo-ventas.bim
```

Deberías ver las líneas modificadas en rojo (eliminadas) y verde (agregadas).

5. Realiza un commit del cambio erróneo para simular que fue confirmado accidentalmente:

```bash
git add modelo-ventas.bim
git commit -m "bug: renombrado accidental de medida Total Ventas (ERROR)"
```

6. Verifica el historial de commits:

```bash
git log --oneline
```

Deberías ver algo como:
```
a3f2c1d (HEAD -> main) bug: renombrado accidental de medida Total Ventas (ERROR)
b8e4a2f feat: versión inicial del modelo semántico de ventas con RLS dinámica
```

7. **Simula el rollback** al commit anterior usando el hash del primer commit (reemplaza `b8e4a2f` con el hash real de tu primer commit):

```bash
# Opción 1: Revertir el último commit manteniendo el historial (recomendado en equipos)
git revert HEAD --no-edit

# Opción 2: Ver el estado del archivo en el commit anterior sin modificar el historial
git show b8e4a2f:modelo-ventas.bim > modelo-ventas-restaurado.bim
```

8. Si usaste `git revert`, verifica que el archivo fue restaurado:

```bash
git log --oneline
git diff HEAD~1 HEAD
```

9. Documenta el proceso en el `README.md`:

```bash
# Agrega una línea al README sobre el proceso de rollback
Add-Content -Path README.md -Value "`n## Proceso de Rollback`nUsar 'git revert <hash>' para revertir cambios no deseados manteniendo el historial completo."
git add README.md
git commit -m "docs: documentar proceso de rollback en README"
```

**3.5 — (Opcional) Subir el repositorio a GitHub**

Si tienes una cuenta de GitHub y deseas practicar el flujo remoto:

```bash
# Crea un repositorio en GitHub llamado "modelo-ventas-lab04" (hazlo desde la interfaz web)
# Luego conecta el repositorio local:
git remote add origin https://github.com/TU_USUARIO/modelo-ventas-lab04.git
git branch -M main
git push -u origin main
```

**Salida esperada:**
- Carpeta `C:\Labs\Lab04\repo-modelo-ventas\` con `.gitignore`, `README.md` y `modelo-ventas.bim`.
- Al menos 3 commits en el historial de Git.
- El proceso de `git revert` restauró el archivo a su estado correcto.

**Verificación:**
```bash
# Ejecuta este comando para verificar el estado final del repositorio:
git log --oneline --graph
```

```
✅ Repositorio Git inicializado con .gitignore y README.md.
✅ Archivo modelo-ventas.bim exportado desde Tabular Editor y versionado.
✅ Al menos 2 commits significativos con mensajes descriptivos.
✅ Proceso de rollback ejecutado exitosamente con git revert.
✅ git log muestra historial completo de cambios.
```

---

### Paso 4: Endorsement, Glosario de Datos y Etiquetas de Sensibilidad

**Objetivo:** Certificar el dataset como activo gobernado en el Servicio Power BI, crear un glosario de datos básico y aplicar etiquetas de sensibilidad de Microsoft Purview al dataset con información sensible.

**Tiempo estimado:** 15 minutos

#### Instrucciones

**4.1 — Aplicar Endorsement al Dataset**

1. En el Servicio Power BI, navega al workspace **`Lab04-Ventas-Prod`**.
2. Ubica el dataset del modelo de ventas. Haz clic en los tres puntos (**…**) junto al dataset.
3. Selecciona **Configuración**.
4. En la página de configuración del dataset, desplázate hacia abajo hasta encontrar la sección **Endorsement and discovery** (Aprobación y detección).
5. Haz clic en **Configurar**.
6. Selecciona la opción **Certificado** (Certified).
   - Si no tienes permisos de certificación en el tenant, selecciona **Promovido** (Promoted) como alternativa.
   - Agrega una descripción: `Modelo semántico de ventas retail validado por el equipo de Analytics. Incluye RLS dinámica por región y grupos de cálculo de inteligencia de tiempo.`
7. Haz clic en **Aplicar**.

> **Nota:** La opción "Certificado" puede requerir permisos de administrador del tenant o de certificador designado. Si no está disponible, usa "Promovido" y documenta la diferencia con el instructor.

**4.2 — Configurar la descripción del dataset y metadatos de descubrimiento**

1. En la misma página de configuración del dataset, busca la sección **Descripción del conjunto de datos**.
2. Agrega la siguiente descripción detallada:

```
Modelo semántico de ventas retail basado en Adventure Works extendido.
Contiene datos de transacciones de ventas, clientes, productos y geografía.

GOBERNANZA:
- Propietario de datos: Equipo de Analytics Corporativo
- Clasificación: Uso interno — Confidencial
- Frecuencia de actualización: Diaria (6:00 AM UTC)
- Última certificación: [Fecha actual]

SEGURIDAD:
- RLS dinámica activa por región geográfica
- Acceso controlado mediante roles en el servicio

CONTACTO: analytics@tuempresa.com
```

3. En la sección **Solicitar acceso**, activa la opción y proporciona instrucciones: `Contactar a analytics@tuempresa.com para solicitar acceso al dataset.`
4. Haz clic en **Aplicar** o **Guardar**.

**4.3 — Crear un Glosario de Datos Básico**

Para este laboratorio, el glosario de datos se documentará como un archivo Markdown en el repositorio Git. En entornos empresariales, esto se complementaría con Microsoft Purview Data Catalog.

1. Regresa a la terminal y navega al repositorio:

```bash
cd C:\Labs\Lab04\repo-modelo-ventas
```

2. Crea el archivo del glosario:

```bash
code glosario-datos.md
```

3. Agrega el siguiente contenido al archivo (ajusta los nombres de medidas según tu modelo real):

```markdown
# Glosario de Datos — Modelo de Ventas Retail

## Tablas Principales

### FactVentas
| Campo | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| OrderKey | Integer | Identificador único de orden | 12345 |
| OrderDate | Date | Fecha de la transacción de venta | 2024-03-15 |
| CustomerKey | Integer | FK hacia DimCliente | 4821 |
| ProductKey | Integer | FK hacia DimProducto | 217 |
| SalesAmount | Decimal | Monto total de venta en USD | 1,250.00 |
| Quantity | Integer | Unidades vendidas | 3 |

### DimCliente
| Campo | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| CustomerKey | Integer | Identificador único del cliente | 4821 |
| CustomerName | String | Nombre completo del cliente | Juan Pérez |
| Region | String | Región geográfica asignada | Norte |

## Medidas Principales

| Medida | Descripción | Fórmula Simplificada |
|---|---|---|
| Total Ventas | Suma del monto de ventas del período seleccionado | SUM(FactVentas[SalesAmount]) |
| Ventas YTD | Ventas acumuladas desde inicio del año fiscal | TOTALYTD([Total Ventas], ...) |
| Variación vs Año Anterior | Diferencia porcentual vs mismo período del año previo | ([Total Ventas] - [Ventas AA]) / [Ventas AA] |

## Reglas de Negocio
- Las ventas con estado "Cancelado" se excluyen de todos los cálculos.
- El año fiscal comienza el 1 de julio.
- La región "Sin Asignar" agrupa transacciones sin geografía definida.

## Clasificación de Sensibilidad
- **SalesAmount, CustomerName:** Confidencial — Uso Interno
- **CustomerEmail, PhoneNumber:** Confidencial — PII (Información Personal Identificable)
```

4. Guarda el archivo y haz commit:

```bash
git add glosario-datos.md
git commit -m "docs: agregar glosario de datos con definiciones de tablas, medidas y reglas de negocio"
```

**4.4 — Aplicar Etiquetas de Sensibilidad de Microsoft Purview**

1. En el Servicio Power BI, navega al workspace **`Lab04-Ventas-Prod`**.
2. Haz clic en los tres puntos (**…**) junto al dataset y selecciona **Configuración**.
3. En la sección **Etiqueta de sensibilidad** (Sensitivity label), haz clic en el menú desplegable.
4. Selecciona la etiqueta apropiada según las disponibles en tu tenant:
   - **Confidencial / Uso Interno** (si existe)
   - **General** (si es la única disponible)
   - **Confidential - All Employees** (nomenclatura común en tenants empresariales)
5. Haz clic en **Aplicar**.

> **Nota:** Las etiquetas disponibles dependen de la configuración de Microsoft Purview en tu tenant. Si no hay etiquetas configuradas, documenta el proceso que seguirías y notifica al instructor.

6. Verifica que la etiqueta aparece junto al nombre del dataset en el workspace (un ícono de escudo o la etiqueta de texto).

7. **Verificar propagación de etiquetas:** Descarga el dataset como Excel (desde el reporte, usa **Exportar → Exportar a Excel**) y verifica que el archivo Excel descargado muestra la etiqueta de sensibilidad en las propiedades del documento.

**4.5 — Desplegar la versión final certificada**

1. Regresa al Deployment Pipeline `Pipeline-Ventas-Lab04`.
2. Dado que aplicaste cambios al workspace Prod directamente (endorsement y etiquetas), verifica que el pipeline no muestra diferencias de artefactos críticas.
3. Si realizaste cambios en el modelo (RLS, etc.) y los publicaste en Dev, despliega nuevamente de Dev → Test → Prod usando el pipeline.
4. Tras el despliegue final, verifica en el workspace Prod que:
   - El dataset tiene el badge de "Certificado" o "Promovido".
   - La etiqueta de sensibilidad está aplicada.
   - El rol `AccesoRegional` está presente en la configuración de seguridad.

**Salida esperada:**
- Dataset en `Lab04-Ventas-Prod` con badge de endorsement visible.
- Descripción detallada del dataset con información de gobernanza.
- Etiqueta de sensibilidad aplicada al dataset.
- Archivo `glosario-datos.md` en el repositorio Git con definiciones de términos clave.

**Verificación:**
```
✅ Dataset en Lab04-Ventas-Prod muestra badge "Certificado" o "Promovido".
✅ Descripción del dataset incluye información de propietario, clasificación y contacto.
✅ Etiqueta de sensibilidad aplicada y visible en el workspace.
✅ glosario-datos.md commiteado en el repositorio Git.
✅ Configuración "Solicitar acceso" activa con instrucciones de contacto.
```

---

## Validación y Pruebas Finales

Ejecuta la siguiente lista de verificación completa antes de considerar el laboratorio terminado:

### Lista de Verificación del Deployment Pipeline

```
□ Pipeline-Ventas-Lab04 existe y tiene los tres workspaces asignados correctamente.
□ Las reglas de implementación están configuradas (EnvironmentName por ambiente).
□ El dataset y reporte están presentes en los tres workspaces (Dev, Test, Prod).
□ No hay diferencias de artefactos pendientes entre etapas (o las diferencias son intencionales).
```

### Lista de Verificación de RLS

```
□ Tabla SeguridadUsuarios existe en el modelo con columnas UserPrincipalName y Region.
□ Relación bidireccional entre SeguridadUsuarios[Region] y DimGeografia[Region].
□ Rol AccesoRegional con expresión [UserPrincipalName] = USERPRINCIPALNAME() validada.
□ Prueba "Ver como" en Desktop muestra datos filtrados por región correctamente.
□ Rol visible en la configuración de seguridad del dataset en el servicio.
```

### Lista de Verificación de Control de Versiones

```
□ Repositorio Git inicializado en C:\Labs\Lab04\repo-modelo-ventas\.
□ Archivo modelo-ventas.bim exportado desde Tabular Editor y commiteado.
□ Al menos 3 commits con mensajes descriptivos en el historial.
□ Proceso de rollback ejecutado con git revert exitosamente.
□ git log --oneline muestra historial completo y coherente.
```

### Lista de Verificación de Gobierno y Certificación

```
□ Dataset en Lab04-Ventas-Prod con endorsement (Certificado o Promovido).
□ Descripción del dataset con metadatos de gobernanza completos.
□ Etiqueta de sensibilidad aplicada al dataset.
□ Glosario de datos (glosario-datos.md) en el repositorio Git.
□ Configuración de acceso bajo demanda activa.
```

### Prueba de Integración Final

Ejecuta este flujo completo para validar que todos los componentes funcionan juntos:

1. Realiza un cambio menor en el modelo en Power BI Desktop (por ejemplo, agrega una descripción a una medida).
2. Publica en `Lab04-Ventas-Dev`.
3. Exporta el nuevo `.bim` desde Tabular Editor y haz commit en Git.
4. Usa el Deployment Pipeline para desplegar de Dev → Test → Prod.
5. Verifica que el endorsement y la etiqueta de sensibilidad se mantienen en Prod.
6. Confirma que la RLS sigue funcionando abriendo el reporte como tu usuario.

---

## Solución de Problemas

### Problema 1: El Deployment Pipeline no aparece en el panel lateral o no se puede crear

**Síntomas:**
- El ícono de "Deployment Pipelines" no aparece en el panel izquierdo del Servicio Power BI.
- Al intentar crear un pipeline, aparece el mensaje: *"Esta característica no está disponible con tu licencia actual"* o similar.
- Los workspaces no pueden asignarse al pipeline.

**Causa:**
Los Deployment Pipelines requieren que el workspace esté en una capacidad Premium o que el usuario tenga licencia Premium Per User (PPU). Con licencia Pro estándar y workspaces en capacidad compartida, esta característica no está disponible. Adicionalmente, el administrador del tenant puede haber deshabilitado la característica en la configuración del portal de administración.

**Solución:**
1. Verifica tu tipo de licencia: en el Servicio Power BI, haz clic en tu avatar (esquina superior derecha) → **Mi cuenta**. Confirma si tienes licencia Pro, PPU o Premium.
2. Si tienes PPU, asegúrate de que los workspaces `Lab04-Ventas-Dev`, `Lab04-Ventas-Test` y `Lab04-Ventas-Prod` estén configurados con licencia PPU (en la configuración del workspace, la licencia debe ser "Premium per user").
3. Si el problema persiste, contacta al administrador del tenant para verificar que en el **Portal de Administración → Configuración del inquilino → Deployment Pipelines** la característica esté habilitada para tu grupo de usuarios.
4. **Alternativa para el laboratorio:** Si la característica no está disponible, documenta el proceso con capturas de pantalla de la demostración del instructor y continúa con los pasos 2, 3 y 4 del laboratorio que no requieren Deployment Pipelines.

---

### Problema 2: La RLS dinámica no filtra datos o muestra un error al abrir el reporte

**Síntomas:**
- Al abrir el reporte en el servicio con tu usuario, se muestran **todos los datos** sin filtrar por región (RLS no aplica).
- O bien, aparece el error: *"No tienes acceso a este contenido"* o *"Error al evaluar el filtro de seguridad a nivel de fila"*.
- En la prueba "Ver como" en Desktop, la expresión DAX devuelve un error de validación.

**Causa:**
Existen tres causas comunes: (A) El usuario no fue agregado como miembro del rol `AccesoRegional` en la configuración de seguridad del dataset en el servicio — sin esta asignación, la RLS no se aplica. (B) La dirección del filtro cruzado de la relación entre `SeguridadUsuarios` y `DimGeografia` no es bidireccional, por lo que el filtro no se propaga a la tabla de hechos. (C) El valor en la columna `SeguridadUsuarios[UserPrincipalName]` no coincide exactamente con el UPN del usuario (diferencia de mayúsculas/minúsculas, dominio incorrecto o espacios en blanco).

**Solución:**
1. **Verificar la asignación del rol en el servicio:** En el Servicio Power BI, ve al dataset → tres puntos → **Seguridad**. Confirma que tu correo electrónico aparece bajo el rol `AccesoRegional`. Si no está, agrégalo y guarda.
2. **Verificar la dirección de la relación:** En Power BI Desktop, ve a la vista **Modelo**, haz doble clic en la relación entre `SeguridadUsuarios` y `DimGeografia`. Confirma que la **dirección del filtro cruzado** está configurada como **Ambos**. Si está en "Único", cámbiala a "Ambos" y republica el modelo.
3. **Verificar el valor del UPN:** Abre la tabla `SeguridadUsuarios` en la vista de Datos y confirma que el correo electrónico en `[UserPrincipalName]` coincide exactamente con tu correo de inicio de sesión en Power BI (incluyendo dominio). Puedes usar esta medida de diagnóstico para verificar qué devuelve `USERPRINCIPALNAME()`:
   ```dax
   Debug_UPN = USERPRINCIPALNAME()
   ```
   Agrega esta medida a un visual de tarjeta en el reporte y usa "Ver como → Otro usuario" con tu correo para ver el valor exacto que devuelve la función.
4. Después de corregir cualquiera de los puntos anteriores, guarda, republica el modelo y vuelve a probar.

---

## Limpieza del Entorno

Al finalizar el laboratorio, realiza las siguientes acciones para liberar recursos y dejar el entorno ordenado:

### En el Servicio Power BI

```
1. Navega al workspace Lab04-Ventas-Dev.
   - Si deseas conservar el trabajo: deja el workspace tal como está.
   - Si deseas limpiar: haz clic en Configuración del workspace → Eliminar workspace.

2. Repite para Lab04-Ventas-Test y Lab04-Ventas-Prod si decides eliminarlos.

3. En Deployment Pipelines, si eliminas los workspaces, el pipeline quedará sin asignaciones.
   Puedes eliminarlo desde la vista del pipeline → menú de tres puntos → Eliminar pipeline.
```

> **Recomendación:** Conserva los workspaces y el pipeline si continuarás con el Lab 05, ya que el modelo certificado en Prod será utilizado en el siguiente laboratorio.

### En el equipo local

```bash
# Conserva el repositorio Git para referencia futura.
# Si deseas limpiar archivos temporales:
cd C:\Labs\Lab04
# Elimina solo archivos temporales si los hay:
Remove-Item -Path ".\*.tmp" -ErrorAction SilentlyContinue
```

### Verificación de limpieza

```
□ Workspaces eliminados o conservados según decisión documentada.
□ Pipeline eliminado si los workspaces fueron eliminados.
□ Repositorio Git en C:\Labs\Lab04\repo-modelo-ventas\ conservado para referencia.
□ Archivos temporales eliminados del equipo local.
```

---

## Resumen

En este laboratorio implementaste un ciclo de vida analítico completo con gobernanza empresarial en Power BI. Los conceptos y habilidades adquiridos se resumen a continuación:

| Componente | Lo que implementaste | Valor empresarial |
|---|---|---|
| **Deployment Pipeline** | 3 ambientes (Dev/Test/Prod) con reglas de implementación | Promueve activos con confianza y trazabilidad; elimina errores manuales de configuración |
| **RLS Dinámica** | Rol `AccesoRegional` con `USERPRINCIPALNAME()` y tabla de permisos | Seguridad granular sin multiplicar reportes; un solo modelo sirve a múltiples perfiles de acceso |
| **Control de Versiones Git** | Exportación `.bim`, commits descriptivos, proceso de rollback | Trazabilidad de cambios, recuperación ante errores y colaboración en equipo |
| **Endorsement y Glosario** | Badge "Certificado", descripción de gobernanza, glosario en Git | Confianza del consumidor en los datos; reducción de "shadow analytics" |
| **Etiquetas de Sensibilidad** | Microsoft Purview aplicado al dataset | Cumplimiento regulatorio y protección de datos en exportaciones |

### Conexión con el Marco de Gobierno de Datos

El flujo implementado en este laboratorio refleja directamente el "DevOps ligero" descrito en la lección teórica:

```
Commit (Git) → Validación → Despliegue (Pipeline) → Certificación → Consumo gobernado
```

Cada etapa tiene controles: el pipeline con reglas de implementación elimina la configuración manual por ambiente; la RLS dinámica centraliza la seguridad en el modelo; el versionado Git proporciona auditoría y capacidad de rollback; el endorsement y las etiquetas comunican la confiabilidad y clasificación del activo a toda la organización.

### Recursos Adicionales

| Recurso | URL |
|---|---|
| Documentación oficial: Deployment Pipelines | https://learn.microsoft.com/power-bi/create-reports/deployment-pipelines-overview |
| Row-Level Security en Power BI | https://learn.microsoft.com/power-bi/enterprise/service-admin-rls |
| Protección de datos y etiquetas de sensibilidad | https://learn.microsoft.com/power-bi/enterprise/service-security-data-protection-overview |
| Endorsement de datasets y dataflows | https://learn.microsoft.com/power-bi/collaborate-share/service-endorsement-overview |
| Registro de actividad y auditoría | https://learn.microsoft.com/power-bi/enterprise/service-admin-auditing |
| pbi-tools para control de versiones | https://github.com/pbi-tools/pbi-tools |
| Tabular Editor — documentación oficial | https://docs.tabulareditor.com/ |
| REST API de Power BI | https://learn.microsoft.com/rest/api/power-bi/ |

---

*Lab 04-00-01 — Gobierno de Datos y Despliegue: Gestión del Ciclo de Vida Analítico | Versión 1.0*
