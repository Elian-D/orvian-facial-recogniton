# Orvian Facial Recognition API

Microservicio de reconocimiento facial construido con **FastAPI** y **face_recognition** (dlib). Forma parte del ecosistema Orvian (Fase 13) y es consumido por el backend Laravel vía HTTP en el puerto **8001**.

---

## Tabla de contenidos

- [Arquitectura y rol](#arquitectura-y-rol)
- [Requisitos](#requisitos)
- [Variables de entorno](#variables-de-entorno)
- [Ejecución](#ejecución)
  - [Con Docker (recomendado)](#con-docker-recomendado)
  - [Local sin Docker](#local-sin-docker)
- [Endpoints](#endpoints)
  - [GET /health](#get-health)
  - [POST /api/v1/enroll/](#post-apiv1enroll)
  - [POST /api/v1/verify/](#post-apiv1verify)
- [Flujo de datos](#flujo-de-datos)
- [Tests](#tests)
- [Estructura del proyecto](#estructura-del-proyecto)

---

## Arquitectura y rol

Este servicio **no almacena ningún dato**. Su única responsabilidad es:

1. **Enrollment** — detectar una cara en la imagen enviada y devolver su encoding (vector de 128 floats).
2. **Verification** — recibir una imagen desconocida + una lista de encodings conocidos (que el cliente guarda en su propia BD), y devolver quién coincide.

El cliente (Laravel) es responsable de persistir los encodings y de enviarlos en cada petición de verificación.

```
Laravel Backend
    │
    │ HTTP (port 8001)
    ▼
Orvian Facial Recognition API
    │
    ├── /enroll  → devuelve encoding[]
    └── /verify  → recibe encodings[], devuelve match
```

---

## Requisitos

| Herramienta | Versión mínima |
|-------------|----------------|
| Python      | 3.11           |
| Docker      | 24+            |
| Docker Compose | v2          |

> Las dependencias nativas de dlib (cmake, OpenBLAS, LAPACK) se instalan automáticamente en el Dockerfile.

---

## Variables de entorno

Copia `.env.example` a `.env` y ajusta los valores:

```bash
cp .env.example .env
```

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `API_KEY` | Clave secreta que deben incluir los clientes en el header `X-API-Key` | — (requerido) |
| `ALLOWED_ORIGINS` | JSON array con los orígenes CORS permitidos | `["http://localhost","http://localhost:8000"]` |
| `FACE_DETECTION_MODEL` | Modelo de detección: `hog` (CPU, rápido) o `cnn` (GPU, más preciso) | `hog` |
| `FACE_ENCODING_MODEL` | Modelo de encoding: `large` (128D, preciso) o `small` (5D, rápido) | `large` |
| `TOLERANCE` | Distancia máxima para considerar un match (0.0–1.0, menor = más estricto) | `0.6` |
| `MAX_IMAGE_SIZE` | Tamaño máximo de imagen en bytes | `5242880` (5 MB) |
| `REDIS_HOST` | Host de Redis | `redis` |
| `REDIS_PORT` | Puerto de Redis | `6379` |
| `REDIS_DB` | Base de datos de Redis | `0` |

> Redis está configurado como dependencia en docker-compose, reservado para caching futuro.

---

## Ejecución

### Con Docker (recomendado)

```bash
# Construir e iniciar el servicio (API + Redis)
docker-compose up --build

# En background
docker-compose up --build -d

# Ver logs
docker-compose logs -f facial-api

# Detener
docker-compose down
```

La API queda disponible en `http://localhost:8001`.

### Local sin Docker

```bash
# Instalar dependencias del sistema (Ubuntu/Debian)
sudo apt-get install build-essential cmake libopenblas-dev liblapack-dev

# Crear entorno virtual e instalar dependencias Python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copiar y configurar variables de entorno
cp .env.example .env

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

---

## Endpoints

Todos los endpoints protegidos requieren el header:
```
X-API-Key: <tu API_KEY>
```

---

### GET /health

Verifica que el servicio esté funcionando. No requiere autenticación.

**Respuesta:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### POST /api/v1/enroll/

Registra la cara de un estudiante y devuelve su encoding para que el cliente lo almacene.

**Content-Type:** `multipart/form-data`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `student_id` | int | ID único del estudiante |
| `school_id` | int | ID de la institución |
| `image` | file | Foto del rostro (JPEG o PNG, máx. 5 MB) |

**Requisito:** la imagen debe contener exactamente **1 cara**.

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "student_id": 123,
  "encoding": [0.123, -0.456, "... 128 floats"],
  "faces_detected": 1,
  "message": "Face enrolled successfully"
}
```

**Errores posibles:**

| Código | Motivo |
|--------|--------|
| 403 | API key inválida o ausente |
| 413 | Imagen mayor a 5 MB |
| 415 | Archivo no es una imagen |
| 200 `success: false` | No se detectó ninguna cara o se detectaron múltiples |

---

### POST /api/v1/verify/

Identifica quién aparece en una imagen comparándola contra encodings conocidos.

**Content-Type:** `multipart/form-data`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `school_id` | int | ID de la institución |
| `known_encodings` | string (JSON) | Array de encodings conocidos (ver formato abajo) |
| `image` | file | Foto a identificar (JPEG o PNG, máx. 5 MB) |

**Formato de `known_encodings`:**
```json
[
  {"id": 1, "name": "Juan Pérez", "encoding": [0.123, -0.456, "... 128 floats"]},
  {"id": 2, "name": "María García", "encoding": ["... 128 floats"]}
]
```

**Respuesta con match (200):**
```json
{
  "success": true,
  "matched": true,
  "student_id": 1,
  "student_name": "Juan Pérez",
  "confidence": 95.5,
  "distance": 0.045,
  "faces_detected": 1,
  "message": "Match found"
}
```

**Respuesta sin match (200):**
```json
{
  "success": true,
  "matched": false,
  "student_id": null,
  "student_name": null,
  "confidence": null,
  "distance": null,
  "faces_detected": 1,
  "message": "No match found"
}
```

**Lógica de matching:**
- Se calcula la distancia euclidiana entre el encoding de la imagen y cada encoding conocido.
- Si la distancia mínima es `≤ TOLERANCE (0.6)`, hay match.
- `confidence = (1 - distance) × 100`

---

## Flujo de datos

### Enrollment

```
1. Cliente sube imagen del estudiante
2. Validación de imagen (tamaño y tipo)
3. Detección de cara (HOG)
4. Validar exactamente 1 cara
5. Generar encoding (128D ResNet)
6. Devolver encoding → cliente lo guarda en su BD
```

### Verification

```
1. Cliente sube imagen desconocida + array de encodings conocidos
2. Validación de imagen
3. Detección de cara
4. Generar encoding de la cara detectada
5. Comparar contra todos los encodings conocidos (distancia euclidiana)
6. Devolver el mejor match si distancia ≤ tolerancia
```

---

## Tests

```bash
pytest tests/
```

Los tests usan mocks para la librería `face_recognition`, por lo que no requieren imágenes reales ni GPU.

Cobertura actual:
- `tests/test_face_detection.py` — detección de caras, cara única, cara más grande
- `tests/test_face_matching.py` — comparación de encodings, cálculo de confianza, mejor match, lista vacía

---

## Estructura del proyecto

```
orvian-facial-recogniton/
├── app/
│   ├── main.py                  # Inicialización de FastAPI y CORS
│   ├── config.py                # Variables de entorno con Pydantic Settings
│   ├── models/
│   │   └── schemas.py           # Modelos de request/response (Pydantic)
│   ├── routers/
│   │   ├── health.py            # GET /health
│   │   ├── enroll.py            # POST /api/v1/enroll/
│   │   └── verify.py            # POST /api/v1/verify/
│   ├── services/
│   │   ├── face_detection.py    # Detección de caras con dlib/HOG
│   │   ├── face_encoding.py     # Generación de embeddings 128D
│   │   └── face_matching.py     # Comparación y distancia euclidiana
│   └── utils/
│       └── image_processing.py  # Validación de imágenes
├── tests/
│   ├── test_face_detection.py
│   └── test_face_matching.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```
