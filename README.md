# WhatsApp Contactos

Este proyecto es una API desarrollada con **FastAPI** para gestionar contactos y chats de WhatsApp. Incluye funcionalidades para manejar cuentas, etiquetas, y la asociación de estas con los chats.

## Características

- Gestión de cuentas de usuario.
- Creación y asignación de etiquetas a chats.
- Base de datos configurada con **PostgreSQL**.
- Migraciones de base de datos gestionadas con **Alembic**.
- Configuración de variables de entorno mediante **dotenv**.

## Requisitos previos

Asegúrate de tener instalados los siguientes componentes:

- Python 3.8 o superior
- PostgreSQL
- Git

## Instalación

1. Crea y activa un entorno virtual:

   ```
   python3 -m venv venv
   Source venv/bin/activate
   ```


2. Instala las dependencias:

   ```
   pip install -r requirements.txt
   ```

3. Configura las variables de entorno:

Crea un archivo .env en la raíz del proyecto con el siguiente contenido (ajusta según tu configuración):

   ```
   DATABASE_URL=postgresql://usuario:contraseña@localhost/nombre_base_datos
   API_KEY=tu_contraseña_segura
   ```

4. Realiza las migraciones de la base de datos:

   ```
   alembic upgrade head
   ```

5. Inicia el servidor de desarrollo:

   ```
   uvicorn app.main:app --reload
   ```