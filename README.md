# Informe Técnico: Microservicio CRUD de Canciones

## Datos Generales
- **Materia:** Aplicaciones Web Avanzadas
- **Carrera:** Ingeniería en Software
- **Nombre del estudiante:** [Tu nombre aquí]
- **Fecha:** [Fecha de entrega]
- **Tema:** Microservicio con CRUD de Canciones desplegado en AWS ECR

## 1. Configuración Inicial
- **Base de datos:** Amazon DynamoDB (NoSQL)
- **Framework:** FastAPI
- **Contenarización:** Docker
- **Despliegue:** AWS ECR + ECS

## 2. Arquitectura y Mejores Prácticas Implementadas

### 2.1. Estructura del proyecto (Actualizada)
```
crud-canciones/
├── app/
│   ├── __init__.py          # Inicialización del paquete
│   ├── main.py              # Aplicación FastAPI principal
│   ├── models.py            # Modelos de datos DynamoDB
│   ├── schemas.py           # Esquemas Pydantic para validación
│   ├── database.py          # Configuración y conexión DynamoDB
│   ├── crud.py              # Operaciones CRUD
│   └── config.py            # Configuración de la aplicación
├── Dockerfile               # Configuración Docker optimizada
├── docker-compose.yml       # Orquestación de contenedores
├── requirements.txt         # Dependencias Python
├── .env.example            # Variables de entorno de ejemplo
├── .gitignore              # Archivos ignorados por Git
├── create_table.py         # Script para crear tabla DynamoDB
└── README.md               # Documentación del proyecto
```

### 2.2. Mejores Prácticas Implementadas

#### a. **Gestión de Configuración**
- Variables de entorno para configuración
- Archivo `.env.example` como plantilla
- Clase `Settings` con Pydantic para validación de configuración
- Separación de configuración por ambiente

#### b. **Validación de Datos**
- Esquemas Pydantic con validaciones robustas
- Documentación automática de API con ejemplos
- Manejo de errores tipificado

#### c. **Logging y Monitoreo**
- Sistema de logging configurado
- Health checks implementados
- Métricas de aplicación

#### d. **Seguridad**
- Usuario no-root en Docker
- Variables de entorno para credenciales
- CORS configurado apropiadamente

#### e. **Desarrollo y Despliegue**
- Docker multi-etapa optimizado
- Docker Compose para desarrollo local
- Scripts de automatización

## 3. Implementación Técnica Detallada

### 3.1. Modelos de Datos (models.py)
```python
class DynamoDBSong(BaseModel):
    id: str = Field(..., description="Unique song identifier (UUID)")
    name: str = Field(..., min_length=1, max_length=200)
    path: str = Field(..., description="Song file path or URL")
    plays: int = Field(default=0, ge=0)
```

### 3.2. Esquemas de Validación (schemas.py)
```python
class SongCreate(SongBase):
    """Schema for creating a new song"""
    
class SongUpdate(BaseModel):
    """Schema for updating an existing song"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    path: Optional[str] = Field(None)
    plays: Optional[int] = Field(None, ge=0)

class SongResponse(SongBase):
    """Schema for song response with ID"""
    id: str = Field(..., description="Unique song identifier")
```

### 3.3. Configuración de Base de Datos (database.py)
```python
class DynamoDBConfig:
    """DynamoDB configuration and connection manager"""
    
    def __init__(self):
        self.region_name = os.getenv('AWS_REGION', 'us-east-1')
        self.table_name = os.getenv('DYNAMODB_TABLE_NAME', 'TBL_SONG')
    
    @property
    def table(self):
        """Get DynamoDB table with error handling"""
        # Implementación con manejo de errores y logging
```

### 3.4. Operaciones CRUD Asíncronas (crud.py)
```python
class SongCRUD:
    """Song CRUD operations with async support"""
    
    async def get_all_songs(self) -> List[Dict[str, Any]]:
        """Get all songs with pagination support"""
    
    async def create_song(self, song_data: SongCreate) -> Dict[str, Any]:
        """Create song"""
    
    async def update_song(self, song_id: str, song_data: SongUpdate) -> Optional[Dict[str, Any]]:
        """Partial update support"""
    
    async def delete_song(self, song_id: str) -> Optional[Dict[str, Any]]:
        """Soft delete with return of deleted item"""
```

### 3.5. API Principal con Mejores Prácticas (main.py)
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup and shutdown logic

app = FastAPI(
    title="Songs CRUD API",
    description="A RESTful API for managing songs using Amazon DynamoDB",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware configuration
app.add_middleware(CORSMiddleware, ...)

# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handling"""
```

## 4. Configuración Docker Optimizada

### 4.1. Dockerfile con Mejores Prácticas
```dockerfile
FROM python:3.11-slim

# Environment variables for optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Security: non-root user
RUN adduser --disabled-password --gecos '' --uid 1001 appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### 4.2. Docker Compose para Desarrollo
```yaml
version: '3.8'
services:
  songs-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AWS_REGION=${AWS_REGION:-us-east-1}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
```

## 5. Scripts de Automatización

### 5.1. Creación de Tabla DynamoDB
```bash
python create_table.py
```

### 5.2. Construcción y Despliegue Docker
```bash
docker-compose up --build
```

## 6. Testing y Validación

### 6.1. Endpoints Disponibles
- `GET /` - Health check básico
- `GET /health` - Health check detallado
- `GET /songs` - Obtener todas las canciones
- `POST /songs` - Crear nueva canción
- `GET /songs/{song_id}` - Obtener canción por ID
- `PUT /songs/{song_id}` - Actualizar canción
- `DELETE /songs/{song_id}` - Eliminar canción

## 6. Despliegue en AWS (ECR + ECS)

### 6.1. Preparación de Imagen Docker
```bash
# Construir imagen
docker build -t songs-api .

# Etiquetar para ECR
docker tag songs-api:latest 202533529057.dkr.ecr.us-east-1.amazonaws.com/songs-api:latest
```

### 6.2. Subida a ECR
```bash
# Login a ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 202533529057.dkr.ecr.us-east-1.amazonaws.com

# Push imagen
docker push 202533529057.dkr.ecr.us-east-1.amazonaws.com/songs-api:latest
```

### 6.3. Configuración ECS
- **Cluster:** Fargate
- **Task Definition:** Con imagen ECR
- **Service:** Con configuración de red pública
- **Variables de entorno:** AWS credentials y configuración

## 7. Variables de Entorno Requeridas

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
DYNAMODB_TABLE_NAME=TBL_SONG

# Application Configuration
APP_NAME=Songs CRUD API
LOG_LEVEL=INFO
DEBUG=false
```

## 9. Estructura de Datos DynamoDB

### Tabla: TBL_SONG
- **Partition Key:** `id` (String) - UUID
- **Attributes:**
  - `name` (String) - Nombre de la canción
  - `path` (String) - Ruta del archivo
  - `plays` (Number) - Número de reproducciones

## 10. Conclusiones

### Mejoras Implementadas:
✅ **Arquitectura limpia** con separación de responsabilidades  
✅ **Validación robusta** con Pydantic schemas  
✅ **Manejo de errores** centralizado y tipificado  
✅ **Logging estructurado** para debugging y monitoreo  
✅ **Configuración por variables de entorno**  
✅ **Docker optimizado** con usuario no-root y health checks  
✅ **Documentación automática** de la API  
✅ **Scripts de automatización** para desarrollo y despliegue  
✅ **Operaciones asíncronas** para mejor rendimiento  
✅ **Actualización parcial** (PATCH-style updates)  

### Beneficios Obtenidos:
- **Mantenibilidad:** Código organizado y bien documentado
- **Escalabilidad:** Arquitectura preparada para crecimiento
- **Seguridad:** Mejores prácticas de seguridad implementadas
- **Observabilidad:** Logging y health checks integrados
- **Desarrollo:** Scripts y herramientas para desarrollo eficiente

El microservicio implementa las mejores prácticas de la industria para APIs RESTful con FastAPI y DynamoDB, proporcionando una base sólida para producción.