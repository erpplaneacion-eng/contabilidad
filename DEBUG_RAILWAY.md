# 🔍 DEBUG: Correos Funcionan Local pero NO en Railway

## ✅ Estado Actual

- ✅ Local funciona perfectamente (test_email_config.py)
- ✅ Local funciona con proveedores (test_notificacion_proveedor.py)
- ❌ Railway NO envía correos al diligenciar formulario

## 🎯 Posibles Causas

### 1. Variables de entorno NO configuradas en Railway ⭐ (MÁS PROBABLE)

Railway puede tener valores por defecto vacíos o diferentes.

**Verificar:**
```bash
# En Railway Dashboard:
Variables → Revisar que TODAS estas existan:

EMAIL_HOST_USER=erp.planeacion@vallesolidario.com
EMAIL_HOST_PASSWORD=nyczispxalvsymco
DEFAULT_FROM_EMAIL=erp.planeacion@vallesolidario.com
NOTIFICATION_EMAIL=recepcionfacturaschvs@gmail.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

### 2. Threading no funciona correctamente con Gunicorn preload

En `gunicorn_config.py` tenemos `preload_app = True`, lo cual puede causar problemas con threading.

**Solución:** Desactivar preload temporalmente

### 3. Gunicorn worker muere antes de enviar el correo

Si el thread tarda más de lo esperado, el worker puede terminar.

**Solución:** Aumentar graceful_timeout

### 4. Railway bloquea puerto 587 saliente (POCO PROBABLE)

Railway podría estar bloqueando SMTP.

**Verificar:** Crear endpoint de prueba

## 🔧 Plan de Acción

### PASO 1: Crear Endpoint de Diagnóstico (5 min)

Vamos a crear un endpoint especial en tu app que:
- Muestre las variables de entorno
- Intente enviar un correo de prueba
- Registre todo en logs

### PASO 2: Verificar Variables en Railway (2 min)

Revisar que todas las variables de email existan.

### PASO 3: Ajustar Gunicorn si es necesario (3 min)

Modificar configuración para que threading funcione mejor.

## 📝 Comandos Útiles

```bash
# Ver logs en tiempo real de Railway
railway logs --follow

# Ver solo errores
railway logs | grep -i error

# Ver logs de email
railway logs | grep -i "correo\|email\|notificacion"
```

---

Vamos a empezar creando el endpoint de diagnóstico...
