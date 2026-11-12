# Migraciones de base de datos

La versión 5 inicializa tablas mediante SQLAlchemy `Base.metadata.create_all` al arrancar. Para producción con cambios de esquema frecuentes, incorporar Alembic y migraciones versionadas antes de modificar modelos existentes. No borres la base PostgreSQL para aplicar cambios.
