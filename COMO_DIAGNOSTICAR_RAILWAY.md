# 🔍 Cómo Diagnosticar Problema de Correos en Railway

## 📋 Checklist Rápido

Sigue estos pasos EN ORDEN:

### ✅ PASO 1: Desplegar Cambios en Railway (2 min)

```bash
git add .
git commit -m "feat: agregar endpoint de diagnóstico de email"
git push
```

Espera 2-3 minutos a que Railway termine el despliegue.

---

### ✅ PASO 2: Verificar Configuración (1 min)

Abre en tu navegador:
```
https://tu-app.railway.app/test-email/
```

Reemplaza `tu-app.railway.app` con tu URL real de Railway.

**¿Qué verás?**

#### ✅ Si TODO está bien configurado:
```json
{
  "servidor": "Railway",
  "debug_mode": false,
  "configuracion": {
    "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
    "EMAIL_HOST": "smtp.gmail.com",
    "EMAIL_PORT": 587,
    "EMAIL_USE_TLS": true,
    "EMAIL_HOST_USER_configurado": true,
    "EMAIL_HOST_USER": "erp.planeacion@vallesolidario.com",
    "EMAIL_HOST_PASSWORD_configurado": true,
    "EMAIL_HOST_PASSWORD": "***ymco",
    "DEFAULT_FROM_EMAIL": "erp.planeacion@vallesolidario.com",
    "NOTIFICATION_EMAIL": "recepcionfacturaschvs@gmail.com"
  },
  "info": "Para enviar correo de prueba, agrega ?send=true a la URL"
}
```

**→ Si ves esto, ve al PASO 3** ✓

#### ❌ Si faltan variables:
```json
{
  "servidor": "Railway",
  "debug_mode": false,
  "configuracion": {
    "EMAIL_HOST_USER_configurado": false,
    "EMAIL_HOST_USER": "❌ NO CONFIGURADO",
    "EMAIL_HOST_PASSWORD_configurado": false,
    "EMAIL_HOST_PASSWORD": "❌ NO CONFIGURADO"
  },
  "error": "Variables de email NO configuradas en Railway",
  "solucion": "Agrega EMAIL_HOST_USER y EMAIL_HOST_PASSWORD en Railway Variables"
}
```

**→ Si ves esto, ve a SOLUCIÓN A** ⚠️

---

### ✅ PASO 3: Enviar Correo de Prueba (1 min)

Abre en tu navegador:
```
https://tu-app.railway.app/test-email/?send=true
```

**¿Qué verás?**

#### ✅ Si el correo se envió:
```json
{
  "servidor": "Railway",
  "configuracion": { ... },
  "enviando": "Intentando enviar a recepcionfacturaschvs@gmail.com...",
  "exito": true,
  "mensaje": "✅ Correo enviado exitosamente desde Railway"
}
```

**→ El problema está resuelto! Ve al PASO 4** ✓

#### ❌ Si el correo NO se envió:
```json
{
  "exito": false,
  "error": "[Errno 111] Connection refused",
  "tipo_error": "SMTPConnectError"
}
```

**→ Ve a SOLUCIÓN B** ⚠️

---

### ✅ PASO 4: Probar Formulario Real (2 min)

1. Ve a tu formulario de proveedores en Railway
2. Diligencia y envía el formulario
3. Verifica que llegue el correo a `recepcionfacturaschvs@gmail.com`

**Si el formulario funciona:**
- ✅ ¡Problema resuelto!
- Elimina el endpoint de diagnóstico (ver PASO 5)

**Si el formulario NO funciona:**
- Ve a Railway Logs y busca errores
- Ve a SOLUCIÓN C

---

### ✅ PASO 5: Eliminar Endpoint (IMPORTANTE - Después de verificar)

**Por seguridad, elimina este endpoint después de diagnosticar:**

1. Edita `contabiliadad/urls.py`
2. Comenta o elimina esta línea:
   ```python
   # path('test-email/', test_email_production, name='test_email_production'),
   ```
3. Commit y push:
   ```bash
   git add .
   git commit -m "chore: eliminar endpoint de diagnóstico"
   git push
   ```

---

## 🔧 SOLUCIONES

### SOLUCIÓN A: Configurar Variables en Railway

El problema es que Railway **no tiene las variables de email**.

**Pasos:**

1. Ve a [railway.app](https://railway.app)
2. Selecciona tu proyecto
3. Haz clic en tu servicio web
4. Ve a **"Variables"**
5. Agrega estas variables (clic en "+ New Variable" para cada una):

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=erp.planeacion@vallesolidario.com
EMAIL_HOST_PASSWORD=nyczispxalvsymco
DEFAULT_FROM_EMAIL=erp.planeacion@vallesolidario.com
NOTIFICATION_EMAIL=recepcionfacturaschvs@gmail.com
```

6. Haz clic en **"Save"** o **"Deploy"**
7. Espera 2-3 minutos al redespliegue
8. **Vuelve al PASO 2** para verificar

---

### SOLUCIÓN B: Errores de Conexión SMTP

Si ves errores como:
- `Connection refused`
- `Connection timed out`
- `[Errno 111]`
- `SMTPConnectError`

**Posibles causas:**

#### 1. App Password incorrecto
- Ve a [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
- Genera un nuevo App Password
- Actualiza `EMAIL_HOST_PASSWORD` en Railway

#### 2. Railway bloquea puerto 587 (RARO)
- Prueba puerto 465 con SSL:
  ```bash
  EMAIL_PORT=465
  EMAIL_USE_TLS=False
  EMAIL_USE_SSL=True
  ```

#### 3. Gmail bloqueó el acceso
- Revisa [myaccount.google.com/notifications](https://myaccount.google.com/notifications)
- Busca alertas de seguridad
- Aprueba el acceso desde Railway

---

### SOLUCIÓN C: Formulario No Envía Pero Endpoint Sí

Si el endpoint `/test-email/?send=true` funciona pero el formulario no:

**Problema:** El thread se está muriendo antes de enviar.

**Solución 1: Revisar logs**

```bash
# En Railway Dashboard → Deployments → View Logs
# Busca estas líneas:
Thread de notificación iniciado para proveedor X
Correo enviado exitosamente
```

Si ves "Thread iniciado" pero NO "Correo enviado", el thread murió.

**Solución 2: Usar timeout más largo**

Edita `proveedores/views.py` y agrega un pequeño delay para forzar que el thread termine:

```python
thread = threading.Thread(...)
thread.start()
thread.join(timeout=5)  # Esperar máximo 5 segundos
```

**Solución 3: Cambiar a sincrónico temporalmente**

Si nada funciona, haz el envío sincrónico (bloqueante) solo para probar:

En `proveedores/views.py`:
```python
# Comentar todo el bloque de threading
# thread = threading.Thread(...)
# ...

# Usar directamente (bloqueante):
enviar_notificacion_async(proveedor.pk, url_proveedor)
```

Si esto funciona, el problema es threading con Gunicorn.

---

## 📊 Tabla de Diagnóstico

| Síntoma | Causa Probable | Solución |
|---------|----------------|----------|
| `/test-email/` muestra variables NO configuradas | Faltan variables en Railway | SOLUCIÓN A |
| `/test-email/?send=true` da error de conexión | App Password o puerto | SOLUCIÓN B |
| `/test-email/?send=true` funciona, formulario no | Thread muere antes de enviar | SOLUCIÓN C |
| Local funciona, Railway no | Variables no configuradas | SOLUCIÓN A |

---

## 🚨 Si Nada Funciona

Contacta con:
1. Copia la salida completa de `/test-email/?send=true`
2. Copia los logs de Railway cuando envías el formulario
3. Verifica que las 8 variables de email estén en Railway

---

## 📝 Comandos Útiles

```bash
# Ver logs de Railway en tiempo real
railway logs --follow

# Ver solo errores de email
railway logs | grep -i "correo\|email\|thread\|notificacion"

# Ver últimas 100 líneas
railway logs --tail 100

# Filtrar por fecha
railway logs --since 1h  # Última hora
```

---

## ✅ Verificación Final

Después de solucionar:

- [ ] `/test-email/` muestra todas las variables configuradas
- [ ] `/test-email/?send=true` envía correo exitosamente
- [ ] Formulario de proveedor envía correo
- [ ] Correo llega a `recepcionfacturaschvs@gmail.com`
- [ ] Endpoint de diagnóstico eliminado (por seguridad)

---

**Última actualización:** 2025-11-07
