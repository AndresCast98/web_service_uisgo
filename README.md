# Web Service - UIS Go 🚀

¡Hola! Bienvenido al repositorio del backend de **UIS Go**.

Este proyecto contiene toda la lógica del servidor (API) que da vida a la aplicación móvil y web. Aquí gestionamos desde la autenticación de usuarios hasta los chats y las actividades en tiempo real.

## 🛠️ ¿Qué tecnologías usamos?

El servicio está construido principalmente sobre **Python**, enfocado en rendimiento y facilidad de uso:

*   **FastAPI**: Nuestro framework principal (rápido y moderno).
*   **PostgreSQL**: Base de datos relacional.
*   **SQLAlchemy & Alembic**: Para manejar los modelos de datos y las migraciones de forma ordenada.
*   **Docker**: Listo para desplegarse en contenedores.

## ⚙️ Configuración Local

Si quieres correr este proyecto en tu máquina, sigue estos pasos sencillos:

### 1. Prepara el entorno
Lo ideal es crear un entorno virtual para no mezclar librerías:

```bash
# Crea el entorno
python -m venv venv

# Actívalo (Mac/Linux)
source venv/bin/activate

# O en Windows
venv\Scripts\activate
```

### 2. Instala las dependencias
Todas las librerías necesarias están en la carpeta `Backend`:

```bash
pip install -r Backend/requirements.txt
```

### 3. Base de Datos
Asegúrate de tener una instancia de PostgreSQL corriendo. El proyecto usa Alembic para crear las tablas:

```bash
# Ejecutar migraciones (estando en la raíz)
alembic upgrade head
```

### 4. ¡A correr!
Para iniciar el servidor de desarrollo:

```bash
cd Backend
uvicorn app.main:app --reload
```

La API debería estar disponible en `http://localhost:8000`. Puedes ver la documentación interactiva automática en `http://localhost:8000/docs`.

---
*Este repositorio contiene únicamente el código del Web Service. El cliente web/móvil se encuentra en su propio repositorio.*
