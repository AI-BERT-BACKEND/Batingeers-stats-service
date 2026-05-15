<div align="center">

# AIBERT — Microservicio de Estadísticas Académicas

### *"Seguimiento académico inteligente para el éxito estudiantil"*

---

### Stack Tecnológico

![Java](https://img.shields.io/badge/Java-21-007396?style=for-the-badge&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.4.3-6DB33F?style=for-the-badge&logo=spring-boot&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Relacional-336791?style=for-the-badge&logo=postgresql&logoColor=white)

### Infraestructura & Calidad

![Azure](https://img.shields.io/badge/Azure-Cloud-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Maven](https://img.shields.io/badge/Maven-Build-C71A36?style=for-the-badge&logo=apache-maven&logoColor=white)

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

---

## 1. Integrantes

- Laura Valentina Santiago Márquez
- Juan Sebastian Murcia Yanquen
- Joshua David Quiroga Landazabal
- Juan Manuel Lopez Barrera

---

## 2. Objetivo del Microservicio

El microservicio de Estadísticas Académicas tiene como objetivo gestionar y exponer el rendimiento académico de los estudiantes dentro de la plataforma AIBERT. Este servicio centraliza el registro de calificaciones, el cálculo de promedios y el seguimiento del progreso académico a lo largo del tiempo. Además, se integra con un módulo de notificaciones por correo electrónico para mantener informados a los usuarios sobre cambios relevantes en su historial académico. El servicio opera sobre una base de datos relacional (PostgreSQL) y expone una API REST protegida mediante JWT, siguiendo los principios de arquitectura hexagonal.

---

## 3. Funcionalidades Principales

<div align="center">

<table>
  <thead>
    <tr>
      <th>Funcionalidad</th>
      <th>Descripción</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Registro de Calificaciones</strong></td>
      <td>Permite ingresar y actualizar notas académicas de los estudiantes mediante el DTO <code>GradeEntryDto</code>, validando la estructura antes de persistir.</td>
    </tr>
    <tr>
      <td><strong>Consulta de Estadísticas</strong></td>
      <td>Expone endpoints para obtener el rendimiento académico de un estudiante: promedios, historial de notas y métricas de desempeño.</td>
    </tr>
    <tr>
      <td><strong>Gestión de Usuarios</strong></td>
      <td>Administración del modelo de usuario asociado a las estadísticas, incluyendo su perfil académico y objetos de valor relacionados.</td>
    </tr>
    <tr>
      <td><strong>Notificaciones por Correo</strong></td>
      <td>Integración con un servicio de correo externo para enviar alertas o confirmaciones relacionadas con eventos académicos relevantes.</td>
    </tr>
    <tr>
      <td><strong>Autenticación y Autorización</strong></td>
      <td>Protección de los endpoints mediante Spring Security y validación de tokens JWT para garantizar acceso controlado a los datos académicos.</td>
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
- **Ejemplo:** `hotfix/fix-grade-calculation-bug`

---

### 4.1 Convenciones para crear ramas

#### `feature/*`
**Formato:**
```
feature/[nombre-funcionalidad]-AIBERT_[codigo-jira]
```

**Ejemplos:**
- `feature/grade-entry-endpoint-AIBERT-15`
- `feature/email-notification-service-AIBERT-22`

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
| **Java OpenJDK 21** | Lenguaje de programación base del microservicio. |
| **Spring Boot 3.4.3** | Framework base; expone la API REST y gestiona inyección de dependencias. |
| **Spring Web** | Exposición de endpoints REST mediante controladores HTTP. |
| **Spring Data JPA** | Acceso a la base de datos relacional mediante el patrón Repository y mapeo objeto-relacional. |
| **PostgreSQL** | Base de datos relacional para persistir calificaciones, usuarios y estadísticas académicas. |
| **Spring Security & JWT** | Autenticación y validación de tokens JWT en las solicitudes a la API. |
| **MapStruct & Lombok** | Mapeo automático entre entidades y DTOs, y reducción de código boilerplate. |
| **Springdoc OpenAPI 3** | Documentación interactiva de la API disponible en Swagger UI. |
| **Apache Maven** | Gestión de dependencias y empaquetado del proyecto. |
| **JUnit 5** | Framework de pruebas unitarias incluido vía `spring-boot-starter-test`. |
| **Mockito** | Librería de mocking para simular dependencias en las pruebas unitarias. |
| **Spring Boot Test** | Soporte de integración para pruebas de contexto Spring y slices de la aplicación. |
| **Docker** | Contenerización del microservicio para despliegue en Azure. |

---

## 6. Funcionalidad

### 1. Registro de Calificación

Permite registrar una nueva entrada de calificación para un estudiante.

**Endpoint:**
`POST /api/v1/stats/grades`

---

#### Estructura de la Solicitud (Request)

<div align="center">

| Campo | Tipo | Restricciones | Descripción |
|---|---|:---:|---|
| studentId | Long | Obligatorio | Identificador único del estudiante. |
| subject | String | Obligatorio | Nombre de la materia evaluada. |
| grade | Double | Obligatorio, 0.0–5.0 | Calificación obtenida. |
| period | String | Obligatorio | Período académico (ej. `2026-1`). |

</div>

---

#### Estructura de la Respuesta (Response)

<div align="center">

| Campo | Tipo | Descripción |
|---|---|---|
| id | Long | Identificador de la entrada registrada. |
| studentId | Long | Identificador del estudiante. |
| subject | String | Materia evaluada. |
| grade | Double | Calificación registrada. |
| period | String | Período académico. |
| createdAt | LocalDateTime | Fecha y hora del registro. |

</div>

---

### 2. Consulta de Estadísticas por Estudiante

Retorna el resumen de rendimiento académico de un estudiante en un período dado.

**Endpoint:**
`GET /api/v1/stats/{studentId}`

---

#### Estructura de la Solicitud (Request)

<div align="center">

| Campo | Tipo | Restricciones | Descripción |
|---|---|:---:|---|
| studentId | Long | Obligatorio (Path) | Identificador del estudiante a consultar. |
| period | String | Opcional (Query) | Filtra por período académico. |

</div>

---

#### Estructura de la Respuesta (Response)

<div align="center">

| Campo | Tipo | Descripción |
|---|---|---|
| studentId | Long | Identificador del estudiante. |
| averageGrade | Double | Promedio general del estudiante en el período. |
| grades | List\<GradeEntryDto\> | Listado de calificaciones por materia. |
| period | String | Período académico consultado. |

</div>

---

## 7. Diagramas

Esta sección muestra los flujos de interacción entre los componentes del microservicio.

### Diagrama de Secuencia — `POST /api/v1/stats/grades`

> *(Espacio reservado — agregar diagrama de secuencia del flujo de registro de calificación)*

---

### Diagrama de Secuencia — `GET /api/v1/stats/{studentId}`

> *(Espacio reservado — agregar diagrama de secuencia del flujo de consulta de estadísticas)*

---

### Arquitectura Hexagonal — Componentes Clave

> *(Espacio reservado — agregar diagrama de arquitectura hexagonal del microservicio)*

El microservicio de estadísticas separa sus responsabilidades de la siguiente manera:

- **Entrypoints (REST Controllers):** Reciben peticiones HTTP y delegan al caso de uso correspondiente.
- **Application (Use Cases & Services):** Orquestan la lógica de negocio; coordinan repositorios y servicios externos.
- **Domain:** Contiene las entidades puras (`User`, value objects) y las interfaces de puertos de entrada.
- **Infrastructure:**
  - `persistence/`: Adaptadores JPA para PostgreSQL (entidades, repositorios, mappers).
  - `external/email/`: Adaptador para el envío de notificaciones por correo.

---

## 8. Manejo de Errores

El microservicio implementa un **mecanismo centralizado de manejo de errores** a través de un `GlobalExceptionHandler` (`@ControllerAdvice`) ubicado en la capa `entrypoints/advice/`. Captura excepciones de validación y del dominio de negocio, garantizando respuestas uniformes y seguras.

### Tipos de errores manejados

<div align="center">

| **Código HTTP** | **Escenario** |
|:---:|:---|
| ![400](https://img.shields.io/badge/400-Bad_Request-red?style=flat) | Datos inválidos en la petición, campos obligatorios faltantes o formato incorrecto. |
| ![401](https://img.shields.io/badge/401-Unauthorized-orange?style=flat) | Token JWT ausente, inválido o expirado. |
| ![403](https://img.shields.io/badge/403-Forbidden-orange?style=flat) | El usuario autenticado no tiene permisos sobre el recurso solicitado. |
| ![404](https://img.shields.io/badge/404-Not_Found-orange?style=flat) | Estudiante o recurso académico no encontrado. |
| ![409](https://img.shields.io/badge/409-Conflict-yellow?style=flat) | Conflicto de negocio, por ejemplo, calificación ya registrada para el mismo período y materia. |
| ![500](https://img.shields.io/badge/500-Internal_Server_Error-critical?style=flat) | Error inesperado en el servidor. |

</div>

---

## 9. Evidencia de Pruebas y Ejecución

El proyecto incluye pruebas unitarias orientadas a validar los casos de uso y la lógica de negocio del microservicio.
https://aibert-stats-service-qa.yellowwave-cb2d91fc.centralus.azurecontainerapps.io/docs#/


### Cómo ejecutar las pruebas

#### 1. Ejecutar todas las pruebas

```bash
mvn clean test
```

#### 2. Generar reporte de cobertura con JaCoCo

```bash
mvn clean test jacoco:report
```

El reporte HTML se generará en `target/site/jacoco/index.html`.

> *(Espacio reservado — agregar capturas de pantalla o evidencia de pruebas ejecutadas)*

---

## 10. Organización del Código

El microservicio sigue una **arquitectura hexagonal (puertos y adaptadores)**:

```
batingeers-stats-service/
│
├── src/
│   ├── main/
│   │   ├── java/com/aibert/dosw/
│   │   │   ├── application/                        # CAPA DE APLICACIÓN
│   │   │   │   ├── dto/
│   │   │   │   │   ├── request/                    # DTOs de entrada (ej. GradeEntryDto)
│   │   │   │   │   └── response/                   # DTOs de salida
│   │   │   │   ├── mapper/                         # Mappers de aplicación
│   │   │   │   ├── service/                        # Servicios de aplicación
│   │   │   │   └── usecase/                        # Casos de uso
│   │   │   │       └── user/                       # Casos de uso relacionados con usuario
│   │   │   │
│   │   │   ├── config/                             # Configuraciones (Security, Swagger, etc.)
│   │   │   │
│   │   │   ├── domain/                             # CAPA DE DOMINIO
│   │   │   │   ├── exceptions/                     # Excepciones de dominio
│   │   │   │   ├── model/
│   │   │   │   │   ├── user/                       # Entidad User
│   │   │   │   │   └── valueObjects/               # Objetos de valor del dominio
│   │   │   │   └── ports/
│   │   │   │       └── in/                         # Puertos de entrada (interfaces de casos de uso)
│   │   │   │
│   │   │   ├── entrypoints/                        # CAPA DE ENTRADA (Infraestructura In)
│   │   │   │   ├── advice/                         # GlobalExceptionHandler
│   │   │   │   └── rest/
│   │   │   │       ├── controller/                 # Controladores REST
│   │   │   │       └── mapper/                     # Mappers de entrypoint
│   │   │   │
│   │   │   └── infrastructure/                     # CAPA DE INFRAESTRUCTURA
│   │   │       ├── adapters/
│   │   │       │   ├── adapter/                    # Adaptadores de puertos de salida
│   │   │       │   └── persistence/
│   │   │       │       ├── entity/                 # Entidades JPA
│   │   │       │       ├── mapper/                 # Mappers de persistencia
│   │   │       │       └── repository/             # Repositorios JPA (Spring Data)
│   │   │       └── external/
│   │   │           └── email/                      # Adaptador de envío de correos
│   │   │
│   │   └── resources/                              # application.yml / application-dev.yml
│   │
│   └── test/                                       # PRUEBAS UNITARIAS
│
└── pom.xml                                         # Configuración Maven
```

---

## 11. Ejecución del Proyecto

### Prerrequisitos

- **Java 21**
- **Maven 3.8+**
- **PostgreSQL** (instancia local o remota configurada en `application.yml`)
- **Docker** (opcional)

### Variables de Entorno requeridas

Antes de ejecutar el proyecto, asegúrate de definir las siguientes variables de entorno (o configurarlas en tu `application.yml`/`.env`):

| Variable | Descripción |
|---|---|
| `DB_URL` | URL de conexión a PostgreSQL |
| `DB_USERNAME` | Usuario de la base de datos |
| `DB_PASSWORD` | Contraseña de la base de datos |
| `JWT_SECRET` | Clave secreta para firma de tokens JWT |
| `MAIL_HOST` | Host del servidor SMTP |
| `MAIL_USERNAME` | Usuario de correo para notificaciones |
| `MAIL_PASSWORD` | Contraseña del correo |

### Opción 1: Ejecución Local (Maven)

```bash
mvn spring-boot:run
```

URL Local: `http://localhost:8080`
Documentación API (Swagger): `http://localhost:8080/swagger-ui/index.html`

### Opción 2: Ejecución con Docker

```bash
docker-compose up --build -d
```

---

## 12. CI/CD y Despliegue en Azure

El proyecto se despliega mediante **GitHub Actions** hacia **Azure App Service** o un entorno contenedorizado en la nube. El pipeline de CI/CD ejecuta las siguientes etapas:

1. Compilación y empaquetado con Maven.
2. Ejecución de pruebas unitarias.
3. Análisis estático de calidad con SonarQube.
4. Construcción de imagen Docker.
5. Push de la imagen al registro de contenedores de Azure.
6. Despliegue en Azure App Service o Azure Container Apps.

Se definen perfiles `dev` y `prod` en `application.yml` para gestionar cadenas de conexión a PostgreSQL y demás configuraciones de entorno.

> *(Espacio reservado — agregar capturas del pipeline de CI/CD y evidencia de despliegue en Azure)*

---

## 13. Contribuciones

### Metodología

Se utiliza **Scrum** con iteraciones cortas, asegurando entregas continuas y mejora de valor. Las ramas principales son protegidas y todos los PRs deben cumplir validación estática (SonarQube) y ejecutar los pipelines de CI antes de ser mergeados.

<div align="center">

### Proyecto AIBERT — Batingeers Stats Service

![Course](https://img.shields.io/badge/Course-DOSW-orange?style=for-the-badge)
![Year](https://img.shields.io/badge/Year-2026-blue?style=for-the-badge)

</div>
