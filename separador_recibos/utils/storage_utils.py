"""
Utilidades para manejar archivos tanto en almacenamiento local como remoto (Cloudinary)
"""
import os
import tempfile
import logging
from django.core.files.storage import default_storage
from django.core.files.base import File

logger = logging.getLogger(__name__)


class StorageHelper:
    """Helper para manejar archivos en diferentes tipos de storage backends"""

    @staticmethod
    def es_storage_local():
        """Verifica si el storage backend es local (FileSystemStorage)"""
        from django.core.files.storage import FileSystemStorage
        return isinstance(default_storage, FileSystemStorage)

    @staticmethod
    def obtener_path_archivo(file_field):
        """
        Obtiene la ruta local de un archivo, descargándolo temporalmente si es necesario.

        Args:
            file_field: Campo FileField o ImageField de Django

        Returns:
            tuple: (ruta_local, es_temporal)
                - ruta_local: Path absoluto al archivo
                - es_temporal: True si el archivo fue descargado temporalmente
        """
        if not file_field:
            raise ValueError("El campo de archivo está vacío")

        # Si es storage local, retornar path directamente
        if StorageHelper.es_storage_local():
            return (file_field.path, False)

        # Si es storage remoto (Cloudinary), descargar temporalmente
        logger.info(f"Descargando archivo remoto: {file_field.name}")

        # Crear archivo temporal con la misma extensión
        ext = os.path.splitext(file_field.name)[1]
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)

        try:
            # Leer contenido del archivo remoto de forma incremental
            file_field.open('rb')
            try:
                for chunk in file_field.chunks():
                    temp_file.write(chunk)
            finally:
                file_field.close()

            temp_file.flush()
            temp_file.close()
            logger.info(f"Archivo descargado temporalmente a: {temp_file.name}")
            return (temp_file.name, True)

        except Exception as e:
            # Si hay error, eliminar archivo temporal
            temp_file.close()
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            raise Exception(f"Error descargando archivo remoto: {str(e)}")

    @staticmethod
    def limpiar_archivo_temporal(path, es_temporal):
        """
        Elimina un archivo temporal si es necesario.

        Args:
            path: Ruta del archivo
            es_temporal: Si el archivo es temporal (debe eliminarse)
        """
        if es_temporal and path and os.path.exists(path):
            try:
                os.unlink(path)
                logger.info(f"Archivo temporal eliminado: {path}")
            except Exception as e:
                logger.warning(f"Error eliminando archivo temporal {path}: {str(e)}")


def obtener_path_local(file_field):
    """
    Función de conveniencia para obtener path local de un archivo.
    Usa context manager para limpiar automáticamente.

    Uso:
        path_local, es_temp = obtener_path_local(archivo)
        try:
            # usar path_local
        finally:
            StorageHelper.limpiar_archivo_temporal(path_local, es_temp)
    """
    return StorageHelper.obtener_path_archivo(file_field)
