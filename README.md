<div align="center">

# 📚 AIBERT — Microservicio de Recomendación

### *"Planificación inteligente, éxito estudiantil asegurado"*

---

### 🛠️ Stack Tecnológico

![Java](https://img.shields.io/badge/Java-21-007396?style=for-the-badge&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.4.3-6DB33F?style=for-the-badge&logo=spring-boot&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge&logo=mongodb&logoColor=white)

### ☁️ Infraestructura & Calidad

![Azure](https://img.shields.io/badge/Azure-Cloud-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Maven](https://img.shields.io/badge/Maven-Build-C71A36?style=for-the-badge&logo=apache-maven&logoColor=white)

### 🏗️ Arquitectura

![Hexagonal](https://img.shields.io/badge/Architecture-Hexagonal-blueviolet?style=for-the-badge)
![Clean Architecture](https://img.shields.io/badge/Clean-Architecture-blue?style=for-the-badge)
![REST API](https://img.shields.io/badge/REST-API-009688?style=for-the-badge)

</div>

---

## 📑 Tabla de Contenidos

1. [👤 Integrantes](#1--integrantes)
2. [🎯 Objetivo del Microservicio](#2--objetivo-del-microservicio)
3. [⚡ Funcionalidades Principales](#3--funcionalidades-principales)
4. [📋 Estrategia de Versionamiento y Branches](#4--manejo-de-estrategia-de-versionamiento-y-branches)
   - [4.1 Convenciones para crear ramas](#41-convenciones-para-crear-ramas)
   - [4.2 Convenciones para crear commits](#42-convenciones-para-crear-commits)
5. [⚙️ Tecnologías Utilizadas](#5--tecnologias-utilizadas)
6. [🧩 Funcionalidad](#6--funcionalidad)
7. [📊 Diagramas](#7--diagramas)
8. [⚠️ Manejo de Errores](#8--manejo-de-errores)
9. [🧪 Evidencia de Pruebas y Ejecución](#9--evidencia-de-las-pruebas-y-como-ejecutarlas)
10. [🗂️ Organización del Código](#10--codigo-de-la-implementacion-organizado-en-las-respectivas-carpetas)
11. [🚀 Ejecución del Proyecto](#11--ejecucion-del-proyecto)
12. [☁️ CI/CD y Despliegue en Azure](#12--evidencia-de-cicd-y-despliegue-en-azure)
13. [🤝 Contribuciones](#13--contribuciones)

---

## 1. 👤 Integrantes

- Equipo AIBERT (SuperOScholar)

## 2. 🎯 Objetivo del microservicio

El microservicio de Recomendación tiene como objetivo generar, gestionar y entregar planes diarios y recomendaciones de estudio para los estudiantes dentro de la plataforma AIBERT. Este servicio se encarga de conectar con motores de inteligencia artificial externa (como Gemini y Groq) para analizar el perfil, el historial de actividades y las tareas pendientes del estudiante, y así recomendar una planificación inteligente del tiempo. Además, se integra con otros microservicios como el de Perfiles y Planificación/Tareas para asegurar que los consejos sean consistentes, apoyando al usuario para evitar el agotamiento y mejorar su rendimiento.

---

## 3. ⚡ Funcionalidades principales

<div align="center">

<table>
  <thead>
    <tr>
      <th>💡 Funcionalidad</th>
      <th>Descripción</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Generación de Recomendaciones</strong></td>
      <td>Procesa información de contexto del estudiante para enviar un prompt a IA (Gemini/Groq) y generar entre 1 y 5 recomendaciones clave para el día.</td>
    </tr>
    <tr>
      <td><strong>Plan Diario de Tareas</strong></td>
      <td>Genera un resumen diario (Daily Plan) sugiriendo qué tareas realizar hoy y cuáles se pueden reprogramar.</td>
    </tr>
    <tr>
      <td><strong>Integración Multi-IA</strong></td>
      <td>Capacidad de conectar tanto con el modelo de Gemini como con la API de Groq, implementando resiliencia mediante Circuit Breaker.</td>
    </tr>
    <tr>
      <td><strong>Registro de Actividad Estudiantil</strong></td>
      <td>Manejo de historiales (Student Activity Log) para tener contexto a largo plazo sobre los hábitos del estudiante.</td>
    </tr>
    <tr>
      <td><strong>Integración vía Feign</strong></td>
      <td>Comunicación robusta y síncrona con Profile Service y Task Service para agrupar todos los datos necesarios antes de solicitar recomendaciones a la IA.</td>
    </tr>
  </tbody>
</table>

</div>


## 4. 📋 Manejo de Estrategia de versionamiento y branches

### Estrategia de Ramas (Git Flow)

### Ramas y propósito
- Manejaremos GitFlow, el modelo de ramificación para el control de versiones de Git

#### `main`
- **Propósito:** rama **estable** con la versión final (lista para demo/producción).
- **Reglas:**
    - Solo recibe merges desde `release/*` y `hotfix/*`.
    - Cada merge a `main` debe crear un **tag** SemVer (`vX.Y.Z`).
    - Rama **protegida**: PR obligatorio, 1–2 aprobaciones, checks de CI en verde.

#### `develop`
- **Propósito:** integración continua de trabajo; base de nuevas funcionalidades.
- **Reglas:**
    - Recibe merges desde `feature/*` y también desde `release/*` al finalizar un release.
    - Rama **protegida** similar a `main`.

#### `feature/*`
- **Propósito:** desarrollo de una funcionalidad, refactor o spike.
- **Base:** `develop`.
- **Cierre:** se fusiona a `develop` mediante **PR**


#### `release/*`
- **Propósito:** congelar cambios para estabilizar pruebas, textos y versiones previas al deploy.
- **Base:** `develop`.
- **Cierre:** merge a `main` (crear **tag** `vX.Y.Z`) **y** merge de vuelta a `develop`.
- **Ejemplo de nombre:**  
  `release/1.3.0`

#### `hotfix/*`
- **Propósito:** corregir un bug **crítico** detectado en `main`.
- **Base:** `main`.
- **Cierre:** merge a `main` (crear **tag** de **PATCH**) **y** merge a `develop` para mantener paridad.
- **Ejemplos de nombre:**  
  `hotfix/fix-resilience-bug`

---

### 4.1 Convenciones para **crear ramas**

#### `feature/*`
**Formato:**
```
feature/[nombre-funcionalidad]-AIBERT_[codigo-jira]
```

**Ejemplos:**
- `feature/add-groq-client-AIBERT-42`

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
**Ejemplo:** `release/1.3.0`

#### `hotfix/*`
**Formato:**
```
hotfix/[descripcion-breve-del-fix]
```

---

### 4.2 Convenciones para **crear commits**

#### **Formato:**
```
[codigo-jira] [tipo]: [descripción específica de la acción]
```

#### **Tipos de commit:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de errores
- `docs`: Cambios en documentación
- `refactor`: Refactorización de código

## 5. ⚙️ Tecnologías Utilizadas

| **Tecnología / Herramienta** | **Uso principal en el proyecto** |
|------------------------------|----------------------------------|
| **Java OpenJDK 21** | Lenguaje de programación base, aprovechando las últimas características como Virtual Threads. |
| **Spring Boot 3.4.x** | Framework base, exponiendo APIs REST y gestionando inyección de dependencias. |
| **Spring Web** | Exposición de endpoints REST (controladores HTTP) en la arquitectura hexagonal. |
| **Spring Cloud OpenFeign** | Creación declarativa de clientes REST para consumir el Profile Service y Task Service. |
| **Resilience4j** | Implementación de Circuit Breaker para tolerar fallos al llamar APIs externas como Gemini o Groq. |
| **Spring Security & JWT** | Autenticación y validación de tokens JWT en las solicitudes a la API. |
| **Spring Data MongoDB** | Conexión a la base de datos NoSQL mediante el patrón Repository y adaptadores. |
| **MongoDB Atlas** | Base de datos NoSQL en la nube para persistir logs de actividad estudiantil e historial de recomendaciones. |
| **Apache Maven** | Gestión de dependencias y empaquetado del proyecto. |
| **MapStruct & Lombok** | Generación de código boilerplate (getters, setters) y mapeo automático entre Entidades y DTOs. |
| **JUnit 5 & Mockito** | Framework de pruebas unitarias simulando dependencias (puertos, feign clients). |
| **JaCoCo** | Generación de reportes de cobertura de código. |
| **Swagger (OpenAPI 3)** | Documentación interactiva de la API (springdoc-openapi). |

## 6. 🧩 Funcionalidad

---

### 1️⃣ Generar Recomendación Diaria

Permite generar recomendaciones personalizadas llamando a la IA con el contexto del estudiante.

**Endpoint principal:**  
`POST /api/v1/recommendations`

---

### 📦 Estructura de la Solicitud (Request)

<div align="center">

| 🏷️ Campo | 🗃️ Tipo | ⚠️ Restricciones | 📝 Descripción |
|---|---|:---:|---|
| studentId | Long | Obligatorio | Identificador único del estudiante. |

</div>

---

### 📦 Estructura de la Respuesta (Response)

<div align="center">

| 🏷️ Campo | 🗃️ Tipo | 📝 Descripción |
|---|---|---|
| recommendations | List<String> | Lista de 1 a 5 recomendaciones accionables. |
| generatedAt | LocalDateTime | Fecha y hora en la que se generó la recomendación. |

</div>

---

### 2️⃣ Consultar Plan Diario

Genera y retorna un plan diario basado en el estado actual de las tareas del estudiante.

**Endpoint principal:**  
`GET /api/v1/recommendations/daily/{studentId}`

---

### 📦 Estructura de la Solicitud (Request)

<div align="center">

| 🏷️ Campo | 🗃️ Tipo | ⚠️ Restricciones | 📝 Descripción |
|---|---|:---:|---|
| studentId | Long | Obligatorio (Path) | Identificador del estudiante a consultar. |

</div>

---

### 📦 Estructura de la Respuesta (Response)

<div align="center">

| 🏷️ Campo | 🗃️ Tipo | 📝 Descripción |
|---|---|---|
| todayTasks | List<TaskDTO> | Lista de tareas planificadas para hoy. |
| reschedulableTasks | List<TaskDTO> | Lista de tareas que podrían ser reprogramadas si la carga es alta. |

</div>

---

## 7. 📊 Diagramas

Esta sección muestra los flujos de interacción entre componentes del microservicio mediante diagramas de secuencia.



### 🔁 Diagrama de Secuencia — `POST /api/v1/recommendations`

Flujo completo de generación de recomendaciones diarias para un estudiante: validación, consulta de historial, enriquecimiento de contexto con IA y persistencia del resultado.

<div align="center">

![Sequence POST recommendations](docs/images/sequence_recommendations_post.png)

</div>



### 🔁 Diagrama de Secuencia — `GET /api/v1/recommendations/daily/{studentId}`

Flujo de consulta del plan diario: obtención de tareas priorizadas, clasificación de sugeridas vs reprogramables, y cálculo de alertas de urgencia.

<div align="center">

![Sequence GET daily plan](docs/images/sequence_recommendations_daily_get.png)

</div>



### 🏗️ Arquitectura Hexagonal — Componentes clave

El microservicio de Recommendations separa sus responsabilidades:

- **Infraestructura In (REST Controllers):** `RecommendationController` recibe peticiones.
- **Aplicación (Use Cases):** `GenerateRecommendationUseCaseImpl`, `GenerateDailyPlanUseCaseImpl`.
- **Dominio:** `Recommendation`, `StudentActivityLog`.
- **Infraestructura Out (Adapters):**
  - `GeminiAdapter`, `GroqAdapter` para la IA externa.
  - `MongoRecommendationRepositoryAdapter` para persistencia.
  - `ProfileFeignClientAdapter`, `TaskFeignClientAdapter` para servicios hermanos.

## 8. ⚠️ Manejo de Errores

El backend implementa un **mecanismo centralizado de manejo de errores** que garantiza uniformidad y seguridad.

A través de un `GlobalExceptionHandler` (`@ControllerAdvice`), se capturan las excepciones de validación o del dominio de negocio (por ejemplo, `InsufficientHistoryException` cuando no hay suficientes datos para recomendar).

### 📊 Tipos de errores manejados

<div align="center">

| 🔢 **Código HTTP** | ⚠️ **Escenario** |
|:------------------:|:----------------|
| ![400](https://img.shields.io/badge/400-Bad_Request-red?style=flat) | Datos inválidos en la petición o IDs faltantes |
| ![404](https://img.shields.io/badge/404-Not_Found-orange?style=flat) | Recurso o estudiante no encontrado en servicios externos |
| ![409](https://img.shields.io/badge/409-Conflict-orange?style=flat) | Error de lógica de negocio (ej. historial insuficiente) |
| ![503](https://img.shields.io/badge/503-Service_Unavailable-critical?style=flat) | Proveedor de IA o servicio hermano caído (Circuit Breaker activo) |

</div>

## 9. 🧪 Evidencia de Pruebas y Ejecución

El proyecto incluye pruebas unitarias integrales.

### 🚀 Cómo ejecutar las pruebas

#### **1️⃣ Ejecutar todas las pruebas**
```bash
mvn clean test
```

#### **2️⃣ Generar reporte de cobertura con JaCoCo**
```bash
mvn clean test jacoco:report
```
El reporte HTML se generará en `target/site/jacoco/index.html`.

## 10. 🗂️ Organización del Código (Scaffolding)

El microservicio sigue una **arquitectura hexagonal (puertos y adaptadores)**:

```
recommendation-service/
│
├── 📁 src/
│   ├── 📁 main/
│   │   ├── 📁 java/com/aibert/dosw/
│   │   │   ├── 📁 application/                     # 🔵 CAPA DE APLICACIÓN (Casos de Uso)
│   │   │   │   ├── 📁 dto/
│   │   │   │   └── 📁 usecase/
│   │   │   │
│   │   │   ├── 📁 config/                          # ⚙️ CONFIGURACIONES (Seguridad)
│   │   │   │
│   │   │   ├── 📁 domain/                          # 🟢 CAPA DE DOMINIO
│   │   │   │   ├── 📁 exception/
│   │   │   │   ├── 📁 model/                       # Entidades puras
│   │   │   │   └── 📁 port/                        # Puertos In/Out
│   │   │   │
│   │   │   └── 📁 infrastructure/                  # 🟠 CAPA DE INFRAESTRUCTURA
│   │   │       └── 📁 adapters/
│   │   │           ├── 📁 in/rest/                 # Controladores y Manejo de Errores
│   │   │           └── 📁 out/                     # Persistencia, Feign, AI Clients
│   │   │               ├── 📁 api/gemini/          # Adaptadores a LLMs (Gemini, Groq)
│   │   │               ├── 📁 db/                  # Adaptadores MongoDB
│   │   │               └── 📁 feign/               # Clientes Feign
│   │   │
│   │   └── 📁 resources/                           # 📄 application.yml
│   │
│   └── 📁 test/                                    # 🧪 PRUEBAS UNITARIAS
│
└── 📄 pom.xml                                      # Configuración Maven
```

## 11. 🚀 Ejecución del Proyecto

### 📋 Prerrequisitos
- **Java 21**
- **Maven 3.8+**
- **Docker** (Opcional)

### 🛠️ Opción 1: Ejecución Local (Maven)

```bash
mvn spring-boot:run
```
📍 **URL Local:** `http://localhost:8080` (o el puerto configurado)  
📚 **Documentación API (Swagger):** `http://localhost:8080/swagger-ui.html`

### 🐳 Opción 2: Ejecución con Docker (Si se incluye Dockerfile)

```bash
docker-compose up --build -d
```

## 12. ☁️ CI/CD y Despliegue en Azure

El proyecto tiene capacidad para desplegarse mediante GitHub Actions hacia Azure App Service o un entorno contenedorizado en la nube.
Se definen perfiles como `dev` y `prod` en `application.yml` para gestionar la cadena de conexión de MongoDB y las keys de Gemini/Groq.

## 13. 🤝 Contribuciones

### Metodología
Se utiliza **Scrum** con iteraciones cortas, asegurando entregas continuas y mejora de valor. Las ramas principales son protegidas y todos los PRs deben cumplir validación estática (SonarQube) y ejecutar pipelines de CI.

<div align="center">

### 🏆 Proyecto AIBERT

![Course](https://img.shields.io/badge/Course-DOSW-orange?style=for-the-badge)
![Year](https://img.shields.io/badge/Year-2026-blue?style=for-the-badge)
