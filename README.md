<div align="center">

# AIBERT — Microservicio de Estadísticas Académicas

### *"Seguimiento académico inteligente para el éxito estudiantil"*

---

### Stack Tecnológico

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Relacional-336791?style=for-the-badge&logo=postgresql&logoColor=white)

### Infraestructura & Calidad

![Azure](https://img.shields.io/badge/Azure-Cloud-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-CC0000?style=for-the-badge&logo=sqlalchemy&logoColor=white)

### Arquitectura

![Hexagonal](https://img.shields.io/badge/Architecture-Hexagonal-blueviolet?style=for-the-badge)
![Clean Architecture](https://img.shields.io/badge/Clean-Architecture-blue?style=for-the-badge)
![REST API](https://img.shields.io/badge/REST-API-009688?style=for-the-badge)

</div>

---

## Tabla de Contenidos

1. [Integrantes](#1-integrantes)
2. [Objetivo del Microservicio](#2-objetivo-del-microservicio)
3. [Funcionalidades Principales](#3-funcionalidades-principales)
4. [Estrategia de Versionamiento y Branches](#4-estrategia-de-versionamiento-y-branches)
   - [4.1 Convenciones para crear ramas](#41-convenciones-para-crear-ramas)
   - [4.2 Convenciones para crear commits](#42-convenciones-para-crear-commits)
5. [Tecnologías Utilizadas](#5-tecnologías-utilizadas)
6. [Funcionalidad](#6-funcionalidad)
7. [Diagramas](#7-diagramas)
8. [Manejo de Errores](#8-manejo-de-errores)
9. [Evidencia de Pruebas y Ejecución](#9-evidencia-de-pruebas-y-ejecución)
10. [Organización del Código](#10-organización-del-código)
11. [Ejecución del Proyecto](#11-ejecución-del-proyecto)
12. [CI/CD y Despliegue en Azure](#12-cicd-y-despliegue-en-azure)
13. [Contribuciones](#13-contribuciones)
14. [Referencia de API — Endpoints](#14-referencia-de-api--endpoints)

---

## 1. Integrantes

- Laura Valentina Santiago Márquez
- Juan Sebastian Murcia Yanquen
- Joshua David Quiroga Landazabal
- Juan Manuel Lopez Barrera

---

## 2. Objetivo del Microservicio

El microservicio de Estadísticas Académicas es el responsable de calcular, consolidar y exponer el rendimiento académico de los estudiantes dentro de la plataforma AIBERT. Provee dos funcionalidades principales: un **dashboard general** con el promedio ponderado, el porcentaje de tareas completadas y el listado de materias del semestre activo (AIB-31), y una vista de **detalle por materia** con notas por corte, nota proyectada, tareas asociadas y evolución histórica del rendimiento (AIB-32).

El servicio está construido con **FastAPI** y **SQLAlchemy** sobre **PostgreSQL**, y se comunica con `academic-service` y `task-service` mediante **HTTPx** para enriquecer las respuestas con datos académicos y de tareas. Todos los endpoints están protegidos mediante JWT y la API está documentada con OpenAPI 3 (Swagger disponible en `/docs`).

---

## 3. Funcionalidades Principales

<div align="center">

<table>
  <thead>
    <tr>
      <th>Funcionalidad</th>
      <th>Código</th>
      <th>Descripción</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Dashboard de Estadísticas Académicas</strong></td>
      <td>AIB-31</td>
      <td>Retorna el promedio ponderado actual (<code>currentGPA</code>), porcentaje de tareas completadas (<code>completionRate</code>) y el listado de materias del semestre activo con su nota y estado académico.</td>
    </tr>
    <tr>
      <td><strong>Estadísticas y Evolución por Materia</strong></td>
      <td>AIB-32</td>
      <td>Retorna el detalle de una materia: notas por corte con su peso porcentual, nota proyectada asumiendo cero en cortes sin nota, tareas asociadas con su estado, y la curva de evolución semanal del rendimiento.</td>
    </tr>
    <tr>
      <td><strong>Integración con Servicios Externos</strong></td>
      <td>—</td>
      <td>Consulta <code>academic-service</code> para obtener materias, créditos y docentes, y <code>task-service</code> para obtener tareas y calcular <code>completionRate</code>, usando HTTPx como cliente HTTP.</td>
    </tr>
    <tr>
      <td><strong>Autenticación y Autorización</strong></td>
      <td>—</td>
      <td>Protección de los endpoints mediante JWT; el <code>userId</code> se extrae automáticamente del token activo sin necesidad de enviarlo en el cuerpo o en la URL.</td>
    </tr>
  </tbody>
</table>

</div>

---

## 4. Estrategia de Versionamiento y Branches

### Estrategia de Ramas (Git Flow)

Se utiliza **GitFlow** como modelo de ramificación para el control de versiones.

#### `main`
- **Propósito:** Rama estable con la versión final (lista para demo/producción).
- **Reglas:**
  - Solo recibe merges desde `release/*` y `hotfix/*`.
  - Cada merge a `main` debe crear un **tag** SemVer (`vX.Y.Z`).
  - Rama **protegida**: PR obligatorio, 1–2 aprobaciones, checks de CI en verde.

#### `develop`
- **Propósito:** Integración continua de trabajo; base de nuevas funcionalidades.
- **Reglas:**
  - Recibe merges desde `feature/*` y también desde `release/*` al finalizar un release.
  - Rama **protegida** similar a `main`.

#### `feature/*`
- **Propósito:** Desarrollo de una funcionalidad, refactor o spike.
- **Base:** `develop`.
- **Cierre:** Se fusiona a `develop` mediante **PR**.

#### `release/*`
- **Propósito:** Congelar cambios para estabilizar pruebas y versiones previas al deploy.
- **Base:** `develop`.
- **Cierre:** Merge a `main` (crear **tag** `vX.Y.Z`) **y** merge de vuelta a `develop`.
- **Ejemplo:** `release/1.0.0`

#### `hotfix/*`
- **Propósito:** Corregir un bug **crítico** detectado en `main`.
- **Base:** `main`.
- **Cierre:** Merge a `main` (crear **tag** de **PATCH**) **y** merge a `develop` para mantener paridad.
- **Ejemplo:** `hotfix/fix-gpa-calculation-bug`

---

### 4.1 Convenciones para crear ramas

#### `feature/*`
**Formato:**
```
feature/[nombre-funcionalidad]-AIBERT_[codigo-jira]
```

**Ejemplos:**
- `feature/dashboard-stats-endpoint-AIBERT-31`
- `feature/subject-evolution-endpoint-AIBERT-32`

**Reglas de nomenclatura:**
- Usar **kebab-case** (palabras separadas por guiones)
- Máximo 50 caracteres en total
- Descripción clara y específica de la funcionalidad
- Código de Jira obligatorio para trazabilidad

#### `release/*`
**Formato:**
```
release/[version]
```
**Ejemplo:** `release/1.0.0`

#### `hotfix/*`
**Formato:**
```
hotfix/[descripcion-breve-del-fix]
```

---

### 4.2 Convenciones para crear commits

#### **Formato:**
```
[codigo-jira] [tipo]: [descripción específica de la acción]
```

#### **Tipos de commit:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de errores
- `docs`: Cambios en documentación
- `refactor`: Refactorización de código
- `style`: Cambios de formato o estilo (sin lógica)
- `test`: Adición o modificación de pruebas
- `chore`: Tareas de mantenimiento (dependencias, configuración)

---

## 5. Tecnologías Utilizadas

| **Tecnología / Herramienta** | **Uso principal en el proyecto** |
|------------------------------|----------------------------------|
| **Python 3.11** | Lenguaje de programación base del microservicio. |
| **FastAPI** | Framework web; expone los endpoints REST y genera automáticamente la documentación OpenAPI 3 en `/docs`. |
| **Pydantic v2** | Validación y serialización de los esquemas de entrada y salida (request/response models). |
| **SQLAlchemy** | ORM para el acceso a PostgreSQL, siguiendo el patrón Repository en la capa de infraestructura. |
| **PostgreSQL** | Base de datos relacional para persistir snapshots de estadísticas académicas. |
| **HTTPx** | Cliente HTTP asíncrono para la comunicación con `academic-service` y `task-service`. |
| **JWT (python-jose)** | Autenticación y extracción del `userId` desde el token Bearer en cada solicitud. |
| **pytest** | Framework de pruebas unitarias e de integración. |
| **pytest-asyncio** | Soporte para pruebas de endpoints y servicios asíncronos con FastAPI. |
| **httpx (TestClient)** | Cliente de pruebas HTTP para los tests de integración de los routers FastAPI. |
| **Docker** | Contenerización del microservicio para despliegue en Azure Container Apps. |

---

## 6. Funcionalidad

### 1. Ver Dashboard de Estadísticas Académicas (AIB-31)

Retorna el resumen del rendimiento académico del estudiante: promedio ponderado del semestre activo, porcentaje de tareas completadas y listado de materias con su nota y estado.

**Endpoint:** `GET /api/v1/stats/dashboard`

**Autenticación:** `Authorization: Bearer <JWT>` — el `userId` se extrae automáticamente del token.

---

#### Estructura de la Solicitud (Request)

<div align="center">

| Campo | Tipo | Origen | Descripción |
|---|---|:---:|---|
| userId | UUID | JWT (automático) | Identificador del estudiante autenticado. No se envía en la URL. |

</div>

---

#### Estructura de la Respuesta (Response)

<div align="center">

| Campo | Tipo | Descripción |
|---|---|---|
| currentGPA | Integer | Promedio ponderado actual del semestre (usa créditos de cada materia como peso). |
| completionRate | Float | Porcentaje de tareas completadas: `completadas / totales × 100`. Calculado consultando `task-service`. |
| subjectList | List\[SubjectSummary\] | Listado de materias del semestre activo, ordenado de mayor a menor nota. |
| subjectList[].subjectId | UUID | Identificador único de la materia. |
| subjectList[].subjectName | String | Nombre de la materia, obtenido desde `academic-service`. |
| subjectList[].credits | Integer | Créditos académicos de la materia, usados para el cálculo del promedio ponderado. |
| subjectList[].currentGrade | Float | Nota actual de la materia (escala 0.0 – 5.0). |
| subjectList[].academicStatus | String | Estado académico: `Aprobada`, `En riesgo` o `Sin información`. |
| subjectList[].teacherName | String \| null | Nombre del docente asociado a la materia (puede ser nulo). |

</div>

**Reglas de negocio:**
- **RN-01:** El promedio ponderado usa los créditos de cada materia como factor de peso.
- **RN-02:** Solo se incluyen materias del semestre activo en el cálculo.

---

### 2. Ver Estadísticas y Evolución por Materia (AIB-32)

Retorna el detalle analítico de una materia: notas por corte evaluativo con su peso, nota proyectada, tareas asociadas y la curva de evolución del rendimiento semana a semana.

**Endpoint:** `GET /api/v1/stats/subjects/{subject_id}`

**Autenticación:** `Authorization: Bearer <JWT>` — el `userId` se extrae automáticamente del token.

---

#### Estructura de la Solicitud (Request)

<div align="center">

| Campo | Tipo | Origen | Descripción |
|---|---|:---:|---|
| subject_id | UUID | Path (obligatorio) | Identificador de la materia. Debe pertenecer al estudiante autenticado. |
| userId | UUID | JWT (automático) | Identificador del estudiante autenticado. No se envía en la URL. |

</div>

---

#### Estructura de la Respuesta (Response)

<div align="center">

**gradesByPeriod** — Notas por corte evaluativo:

| Campo | Tipo | Descripción |
|---|---|---|
| gradesByPeriod[].periodId | UUID | Identificador único del corte evaluativo. |
| gradesByPeriod[].periodName | String | Nombre del corte (ej. `Corte 1`, `Corte 2`, `Corte final`). |
| gradesByPeriod[].weightPercentage | Float | Peso porcentual del corte. La suma de todos los cortes debe ser 100. |
| gradesByPeriod[].obtainedGrade | Float \| null | Nota obtenida en el corte (0.0 – 5.0). Nulo si aún no hay nota registrada. |
| gradesByPeriod[].contribution | Float | Aporte del corte a la nota final: `obtainedGrade × weightPercentage`. |
| gradesByPeriod[].projectedGrade | Float | Nota proyectada final, asumiendo cero en cortes sin nota registrada. |

**relatedTasks** — Tareas de la materia, ordenadas por fecha de entrega descendente (desde `task-service`):

| Campo | Tipo | Descripción |
|---|---|---|
| relatedTasks[].taskId | UUID | Identificador de la tarea en `task-service`. |
| relatedTasks[].taskName | String | Nombre de la tarea. |
| relatedTasks[].dueDate | date | Fecha límite de entrega (formato `YYYY-MM-DD`). |
| relatedTasks[].status | String | Estado de la tarea: `Pendiente`, `Completada` o `Vencida`. |
| relatedTasks[].priority | String \| null | Prioridad de la tarea: `Alta`, `Media` o `Baja`. Puede ser nulo. |
| relatedTasks[].estimatedHours | Float \| null | Horas estimadas para completar la tarea. Puede ser nulo. |

**gradeEvolution** — Evolución acumulada de la nota semana a semana:

| Campo | Tipo | Descripción |
|---|---|---|
| gradeEvolution[].week | Integer | Número de semana académica dentro del semestre. |
| gradeEvolution[].accumulatedGrade | Float | Nota acumulada hasta esa semana (0.0 – 5.0). |
| gradeEvolution[].registeredDate | date | Fecha en que se registró el punto de evolución (formato `YYYY-MM-DD`). |

</div>

**Reglas de negocio:**
- **RN-01:** `projectedGrade` = suma de `(obtainedGrade × weightPercentage)` para los cortes ya registrados.
- **RN-02:** `gradeEvolution` solo se devuelve si hay mínimo 2 cortes con nota registrada.

---

## 7. Diagramas

### Diagrama de Secuencia — View Dashboard (AIB-31)

<div align="center">

<img width="8192" height="6207" alt="View Dashboard Sequence Diagram - stats" src="https://github.com/user-attachments/assets/24ec1311-8c93-4de6-be6b-f48e286f18e1" />
</div>

---

### Diagrama de Secuencia — View Stats and Progress (AIB-32)

<div align="center">

<img width="8191" height="5450" alt="View stats and progress Sequence Diagram - stats" src="https://github.com/user-attachments/assets/808b441e-29b4-4cf7-be18-89ee2fe87979" />

</div>

---

### Diagrama de Secuencia — View Gamification Progress

<div align="center">

<img width="8192" height="5588" alt="Gamification progress Sequence Diagram - stats" src="https://github.com/user-attachments/assets/f0ca09a1-b430-47f1-a6aa-48672bb83f6c" />
</div>

---

### Diagrama de Clases — Dominio

El dominio tiene tres contextos: **Dashboard** (resumen general del usuario con GPA, tareas y materias), **Gamification** (perfil de puntos y badges), y **Stats** (estadísticas detalladas por materia con historial de notas y proyecciones).

<div align="center">

![DiagramaDeClasesDominioStats.jpeg](docs/uml/diagramas/DiagramaDeClasesDominioStats.jpeg)

</div>

---

### Diagrama de Entidad Relación

Dos tablas principales: `dashboard_snapshots` (snapshot general del usuario) y `subject_snapshots` (detalle por materia), relacionadas 1 a muchos. Ambas usan JSONB para datos complejos anidados.

<div align="center">

![DiagramaER.jpeg](docs/uml/diagramas/DiagramaER.jpeg)

</div>

---

### Diagrama de Componentes

El flujo va: `User → Stats Router → Use Cases → (SQLAlchemy Repository → Stats DB)` y `(HTTPx Client → academic-service, task-service, gamification-service)`.

<div align="center">

![DiagramaDeComponentesEspecificos.jpeg](docs/uml/diagramas/DiagramaDeComponentesEspecificos.jpeg)

</div>

---

## 8. Manejo de Errores

El microservicio implementa un **mecanismo centralizado de manejo de errores** mediante exception handlers de FastAPI (`@app.exception_handler`). Captura excepciones de validación (Pydantic) y de dominio de negocio, garantizando respuestas uniformes y seguras.

### Tipos de errores manejados

<div align="center">

| **Código HTTP** | **Escenario** |
|:---:|:---|
| ![400](https://img.shields.io/badge/400-Bad_Request-red?style=flat) | UUID inválido, formato de fecha incorrecto o campo obligatorio faltante. |
| ![401](https://img.shields.io/badge/401-Unauthorized-orange?style=flat) | Token JWT ausente, inválido o expirado. |
| ![403](https://img.shields.io/badge/403-Forbidden-orange?style=flat) | La materia solicitada no pertenece al estudiante autenticado. |
| ![404](https://img.shields.io/badge/404-Not_Found-orange?style=flat) | Estudiante o materia no encontrada en los servicios consultados. |
| ![503](https://img.shields.io/badge/503-Service_Unavailable-critical?style=flat) | `academic-service` o `task-service` no responde. |
| ![500](https://img.shields.io/badge/500-Internal_Server_Error-critical?style=flat) | Error inesperado en el servidor. |

</div>

---

## 9. Evidencia de Pruebas y Ejecución

El proyecto incluye pruebas unitarias con **pytest** orientadas a validar los casos de uso, la lógica de cálculo (GPA ponderado, nota proyectada, `completionRate`) y los routers FastAPI.

**Swagger desplegado (QA):**
https://aibert-stats-service-qa.yellowwave-cb2d91fc.centralus.azurecontainerapps.io/docs#/

### Escenarios de prueba relevantes

| Escenario | Tipo | Resultado esperado |
|---|---|---|
| Dashboard con materias registradas | Unitario | `currentGPA` calculado con créditos como peso; `subjectList` ordenado de mayor a menor nota. |
| Dashboard sin materias en semestre activo | Unitario | `subjectList` vacío, `currentGPA = 0`, `completionRate = 0.0`. |
| Dashboard con `task-service` no disponible | Integración | HTTP 503, mensaje de servicio no disponible. |
| Detalle de materia con todos los cortes registrados | Unitario | `projectedGrade` = suma real de contribuciones; `gradeEvolution` retorna puntos. |
| Detalle de materia con menos de 2 cortes con nota | Unitario | `gradeEvolution` retorna lista vacía (RN-02). |
| Detalle de materia con cortes sin nota | Unitario | `obtainedGrade = null`; `projectedGrade` asume 0 en esos cortes. |
| Materia que no pertenece al estudiante autenticado | Integración | HTTP 403 Forbidden. |
| Token JWT ausente o expirado | Integración | HTTP 401 Unauthorized. |

### Cómo ejecutar las pruebas

#### 1. Instalar dependencias de prueba

```bash
pip install pytest pytest-asyncio httpx
```

#### 2. Ejecutar todas las pruebas

```bash
pytest
```

#### 3. Ejecutar con reporte de cobertura

```bash
pytest --cov=app --cov-report=html
```

El reporte HTML se generará en `htmlcov/index.html`.

> *(Espacio reservado — agregar capturas de pantalla o evidencia de pruebas ejecutadas)*

---

## 10. Organización del Código

El microservicio sigue una **arquitectura hexagonal (puertos y adaptadores)**:

```
batingeers-stats-service/
│
├── app/
│   ├── application/                        # CAPA DE APLICACIÓN
│   │   ├── dto/
│   │   │   ├── request/                    # Schemas Pydantic de entrada
│   │   │   └── response/                   # Schemas Pydantic de salida
│   │   ├── mapper/                         # Conversión entre modelos de dominio y DTOs
│   │   ├── service/                        # Servicios de aplicación (orquestadores)
│   │   └── use_case/                       # Casos de uso (AIB-31, AIB-32)
│   │
│   ├── config/                             # Configuraciones (JWT, DB, HTTPx clients)
│   │
│   ├── domain/                             # CAPA DE DOMINIO
│   │   ├── exceptions/                     # Excepciones de dominio
│   │   ├── model/                          # Entidades y value objects puros
│   │   └── ports/
│   │       └── in_/                        # Interfaces de puertos de entrada (contratos de casos de uso)
│   │
│   ├── entrypoints/                        # CAPA DE ENTRADA
│   │   ├── exception_handler/              # Handlers globales de excepciones FastAPI
│   │   └── rest/
│   │       ├── router/                     # Routers FastAPI (stats_router.py)
│   │       └── mapper/                     # Mappers de entrypoint
│   │
│   └── infrastructure/                     # CAPA DE INFRAESTRUCTURA
│       ├── adapters/
│       │   ├── adapter/                    # Implementaciones de puertos de salida
│       │   └── persistence/
│       │       ├── entity/                 # Modelos SQLAlchemy
│       │       ├── mapper/                 # Mappers de persistencia
│       │       └── repository/             # Repositorios (SQLAlchemy)
│       └── external/
│           ├── academic_client.py          # HTTPx client → academic-service
│           └── task_client.py              # HTTPx client → task-service
│
├── tests/                                  # PRUEBAS (pytest)
│   ├── unit/                               # Pruebas unitarias de casos de uso
│   └── integration/                        # Pruebas de integración de routers
│
├── docs/
│   ├── openapi.yaml                        # Especificación OpenAPI 3 del servicio
│   └── requests.http                       # Peticiones HTTP de prueba
│
├── main.py                                 # Punto de entrada de la aplicación FastAPI
├── requirements.txt                        # Dependencias del proyecto
└── Dockerfile                              # Imagen Docker del servicio
```

---

## 11. Ejecución del Proyecto

### Prerrequisitos

- **Python 3.11+**
- **PostgreSQL** (instancia local o remota)
- **Docker** (opcional)

### Variables de Entorno requeridas

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | URL de conexión a PostgreSQL (ej. `postgresql+asyncpg://user:pass@host/db`) |
| `JWT_SECRET` | Clave secreta para validación de tokens JWT |
| `ACADEMIC_SERVICE_URL` | URL base de `academic-service` |
| `TASK_SERVICE_URL` | URL base de `task-service` |

### Opción 1: Ejecución Local

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

URL Local: `http://localhost:8000`
Documentación API (Swagger): `http://localhost:8000/docs`

### Opción 2: Ejecución con Docker

```bash
docker-compose up --build -d
```

---

## 12. CI/CD y Despliegue en Azure

El proyecto se despliega mediante **GitHub Actions** hacia **Azure Container Apps**. El pipeline de CI/CD ejecuta las siguientes etapas:

1. Instalación de dependencias Python.
2. Ejecución de pruebas con `pytest`.
3. Análisis estático con `ruff` y `mypy`.
4. Construcción de imagen Docker.
5. Push de la imagen al Azure Container Registry.
6. Despliegue en Azure Container Apps.

Se utilizan variables de entorno por ambiente (`dev`, `qa`, `prod`) configuradas en los secrets de GitHub Actions para gestionar las URLs de servicios externos y la cadena de conexión a PostgreSQL.

> *(Espacio reservado — agregar capturas del pipeline de CI/CD y evidencia de despliegue en Azure)*

---

## 13. Contribuciones

### Metodología

Se utiliza **Scrum** con iteraciones cortas, asegurando entregas continuas y mejora de valor. Las ramas principales son protegidas y todos los PRs deben pasar el pipeline de CI (pruebas + análisis estático) antes de ser mergeados.

<div align="center">

### Proyecto AIBERT — Batingeers Stats Service

![Course](https://img.shields.io/badge/Course-DOSW-orange?style=for-the-badge)
![Year](https://img.shields.io/badge/Year-2026-blue?style=for-the-badge)

</div>

---

## 14. Referencia de API — Endpoints

Esta sección es la referencia rápida de los contratos del microservicio, orientada a la integración con otros servicios de la plataforma AIBERT.

> Documentación interactiva completa (QA): https://aibert-stats-service-qa.yellowwave-cb2d91fc.centralus.azurecontainerapps.io/docs#/
> Especificación OpenAPI: [`docs/openapi.yaml`](docs/openapi.yaml)

---

### `GET /api/v1/stats/dashboard`

**Descripción:** Dashboard de estadísticas académicas del estudiante autenticado (AIB-31).

**Headers requeridos:**

| Header | Valor |
|---|---|
| `Authorization` | `Bearer <JWT>` |

**Entrada:** No requiere parámetros en URL ni cuerpo. El `userId` se extrae del JWT.

**Salida — HTTP 200:**

```json
{
  "currentGPA": 4,
  "completionRate": 75.5,
  "subjectList": [
    {
      "subjectId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "subjectName": "Cálculo Diferencial",
      "credits": 4,
      "currentGrade": 4.2,
      "academicStatus": "Aprobada",
      "teacherName": "Juan García"
    },
    {
      "subjectId": "7cb9e2a1-8821-4312-c4de-3d874f77bfe9",
      "subjectName": "Estructuras de Datos",
      "credits": 3,
      "currentGrade": 2.8,
      "academicStatus": "En riesgo",
      "teacherName": null
    }
  ]
}
```

| Campo | Tipo | Notas |
|---|---|---|
| `currentGPA` | `integer` | Promedio ponderado por créditos. Solo materias del semestre activo. |
| `completionRate` | `float` | `completadas / totales × 100`. Dato obtenido de `task-service`. |
| `subjectList[].subjectId` | `uuid` | |
| `subjectList[].subjectName` | `string` | Dato obtenido de `academic-service`. |
| `subjectList[].credits` | `integer` | |
| `subjectList[].currentGrade` | `float` | Escala 0.0 – 5.0. |
| `subjectList[].academicStatus` | `string` | `"Aprobada"` \| `"En riesgo"` \| `"Sin información"` |
| `subjectList[].teacherName` | `string \| null` | |

**Errores posibles:** `401`, `404`, `503`.

---

### `GET /api/v1/stats/subjects/{subject_id}`

**Descripción:** Detalle de estadísticas y evolución de una materia (AIB-32).

**Headers requeridos:**

| Header | Valor |
|---|---|
| `Authorization` | `Bearer <JWT>` |

**Parámetros de ruta:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `subject_id` | `uuid` | Identificador de la materia. Debe pertenecer al estudiante autenticado. |

**Salida — HTTP 200:**

```json
{
  "gradesByPeriod": [
    {
      "periodId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "periodName": "Corte 1",
      "weightPercentage": 30.0,
      "obtainedGrade": 4.0,
      "contribution": 1.2,
      "projectedGrade": 3.5
    },
    {
      "periodId": "9ab12cd3-4567-89ef-ghij-1234567890kl",
      "periodName": "Corte 2",
      "weightPercentage": 30.0,
      "obtainedGrade": null,
      "contribution": 0.0,
      "projectedGrade": 3.5
    },
    {
      "periodId": "7de34fg5-6789-01hi-jklm-2345678901no",
      "periodName": "Corte final",
      "weightPercentage": 40.0,
      "obtainedGrade": null,
      "contribution": 0.0,
      "projectedGrade": 3.5
    }
  ],
  "relatedTasks": [
    {
      "taskId": "1ab2cd34-ef56-7890-abcd-ef1234567890",
      "taskName": "Taller de integrales",
      "dueDate": "2026-05-20",
      "status": "Pendiente",
      "priority": "Alta",
      "estimatedHours": 3.0
    }
  ],
  "gradeEvolution": [
    {
      "week": 4,
      "accumulatedGrade": 4.0,
      "registeredDate": "2026-03-14"
    }
  ]
}
```

| Campo | Tipo | Notas |
|---|---|---|
| `gradesByPeriod[].periodId` | `uuid` | |
| `gradesByPeriod[].periodName` | `string` | |
| `gradesByPeriod[].weightPercentage` | `float` | Suma de todos los cortes = 100. |
| `gradesByPeriod[].obtainedGrade` | `float \| null` | 0.0 – 5.0. Nulo si no hay nota registrada. |
| `gradesByPeriod[].contribution` | `float` | `obtainedGrade × weightPercentage`. |
| `gradesByPeriod[].projectedGrade` | `float` | Proyección asumiendo 0 en cortes sin nota. |
| `relatedTasks[].taskId` | `uuid` | Dato obtenido de `task-service`. |
| `relatedTasks[].taskName` | `string` | |
| `relatedTasks[].dueDate` | `date` | Formato `YYYY-MM-DD`. |
| `relatedTasks[].status` | `string` | `"Pendiente"` \| `"Completada"` \| `"Vencida"` |
| `relatedTasks[].priority` | `string \| null` | `"Alta"` \| `"Media"` \| `"Baja"` |
| `relatedTasks[].estimatedHours` | `float \| null` | |
| `gradeEvolution[].week` | `integer` | Número de semana en el semestre. |
| `gradeEvolution[].accumulatedGrade` | `float` | 0.0 – 5.0. |
| `gradeEvolution[].registeredDate` | `date` | Formato `YYYY-MM-DD`. |

**Errores posibles:** `401`, `403`, `404`, `503`.
