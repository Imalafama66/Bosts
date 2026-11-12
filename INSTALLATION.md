# Instalación local

1. Instala Python 3.12.
2. Crea un entorno virtual: `python -m venv .venv`.
3. Actívalo e instala dependencias: `pip install -r requirements.txt`.
4. Copia `.env.example` a `.env` y configura `SECRET_KEY` con un secreto aleatorio de al menos 32 caracteres.
5. Ejecuta `uvicorn main:app --reload`.
6. Abre `http://127.0.0.1:8000`.

La base local predeterminada es SQLite (`ghostbots.db`).
