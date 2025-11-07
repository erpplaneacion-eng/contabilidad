"""
Configuración de Gunicorn para la aplicación de contabilidad.
Este archivo optimiza el rendimiento y evita timeouts en operaciones largas.
"""

import multiprocessing
import os

# Dirección y puerto de escucha
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Número de workers (procesos)
# Railway/Heroku recomiendan: 2-4 workers para aplicaciones pequeñas/medianas
workers = int(os.getenv('WEB_CONCURRENCY', '2'))

# Tipo de worker (sync es el más compatible con Django)
worker_class = 'sync'

# Timeout de workers (en segundos)
# Aumentado a 120 segundos para permitir operaciones de correo más lentas
# Nota: con threading, la mayoría de requests responderán rápido
timeout = 120

# Timeout para graceful shutdown
graceful_timeout = 30

# Keep-alive para conexiones
keepalive = 5

# Logging
accesslog = '-'  # Log a stdout
errorlog = '-'   # Log a stderr
loglevel = 'info'

# Preload de la aplicación (mejora el uso de memoria)
preload_app = True

# Número máximo de requests por worker antes de reiniciarlo
# Esto ayuda a liberar memoria
max_requests = 1000
max_requests_jitter = 50

# Configuración de threads por worker (opcional, para operaciones I/O)
# threads = 2
