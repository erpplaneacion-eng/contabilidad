# 📘 Guía Completa de Uso - Sistema de Proveedores

## 🎯 Resumen de Cambios Realizados

### ✅ Templates Creados
1. **proveedor_list.html** - Lista de proveedores (requiere login)
2. **proveedor_detail.html** - Detalle completo de un proveedor (requiere login)
3. **login.html** - Página de inicio de sesión para revisores

### ✅ Sistema de Autenticación
- Login para personal autorizado
- Protección de vistas administrativas
- Logout seguro

### ✅ Mejoras en el Formulario
- Lenguaje más amigable para proveedores
- Contexto claro y profesional
- Instrucciones útiles en cada sección

---

## 👥 ROLES Y ACCESOS

### 1️⃣ PROVEEDOR (Sin Login)
**Puede acceder a:**
- ✅ Formulario de registro: `http://127.0.0.1:8000/proveedores/registro/`
- ✅ Formulario de actualización: `http://127.0.0.1:8000/proveedores/actualizar/<id>/`
- ✅ Página de confirmación: `http://127.0.0.1:8000/proveedores/success/<id>/`

**NO puede acceder a:**
- ❌ Lista de proveedores
- ❌ Detalle de otros proveedores
- ❌ Panel de administración

---

### 2️⃣ REVISOR/ADMINISTRADOR (Con Login)
**Puede acceder a:**
- ✅ Login: `http://127.0.0.1:8000/login/`
- ✅ Lista de proveedores: `http://127.0.0.1:8000/proveedores/lista/`
- ✅ Detalle de proveedores: `http://127.0.0.1:8000/proveedores/detalle/<id>/`
- ✅ Panel admin: `http://127.0.0.1:8000/admin/`
- ✅ Todo lo que puede el proveedor

**Credenciales por defecto:**
```
Usuario: admin
Contraseña: admin123
```

---

## 🔄 FLUJOS DE USO

### 📝 FLUJO 1: Proveedor Nuevo Se Registra

```
1. Empresa envía link al proveedor
   └─ http://127.0.0.1:8000/proveedores/registro/

2. Proveedor abre el link
   └─ Ve: "Bienvenido - Formulario de Registro de Proveedores"

3. Proveedor completa el formulario
   ├─ Información de Su Empresa
   ├─ Personas de Contacto (opcional)
   ├─ Información Tributaria
   ├─ Sus Condiciones de Pago
   ├─ Documentos de Su Empresa
   └─ Representante Legal

4. Hace clic en "Completar Registro"

5. Sistema guarda todo

6. Proveedor ve confirmación
   └─ Con ID único para futuras actualizaciones
```

---

### 🔄 FLUJO 2: Proveedor Actualiza Sus Datos

```
1. Proveedor recibe link de actualización
   └─ http://127.0.0.1:8000/proveedores/actualizar/45/

2. Abre el link
   └─ Ve: "Actualizar Mis Datos como Proveedor"
   └─ Todos los campos PRE-LLENADOS

3. Modifica lo que necesite

4. Hace clic en "Actualizar Mis Datos"

5. Ve confirmación de actualización
```

---

### 👁️ FLUJO 3: Revisor Consulta Proveedores

```
1. Revisor accede al sistema
   └─ http://127.0.0.1:8000/login/

2. Ingresa credenciales
   Usuario: admin
   Contraseña: admin123

3. Sistema lo redirige automáticamente
   └─ http://127.0.0.1:8000/proveedores/lista/

4. Ve lista completa de proveedores
   ├─ Puede buscar
   ├─ Puede filtrar
   ├─ Ve estadísticas
   └─ 20 proveedores por página

5. Hace clic en "Ver Detalle" de un proveedor

6. Ve información completa:
   ├─ Datos generales
   ├─ Ubicación
   ├─ Contactos
   ├─ Impuestos
   ├─ Documentos (puede descargar)
   └─ Firma y sello

7. Opciones disponibles:
   ├─ Editar proveedor
   ├─ Ir al admin
   └─ Volver a la lista

8. Para cerrar sesión:
   └─ Clic en "Cerrar Sesión"
```

---

## 🖼️ PANTALLAS DEL SISTEMA

### 1. Formulario de Registro (Proveedor)
```
┌─────────────────────────────────────────────┐
│  🤝 Bienvenido - Formulario de Registro    │
│  Queremos conocerlo mejor...               │
├─────────────────────────────────────────────┤
│                                             │
│  ℹ️ Información de Su Empresa              │
│  Por favor ingrese los datos principales   │
│                                             │
│  📋 Personas de Contacto (Opcional)        │
│  Puede agregar contactos adicionales...    │
│                                             │
│  🧾 Información Tributaria                 │
│  Indique retenciones aplicables...         │
│                                             │
│  💳 Sus Condiciones de Pago                │
│  Política de pago preferida...             │
│                                             │
│  📄 Documentos de Su Empresa               │
│  Adjunte documentos necesarios...          │
│                                             │
│  ✍️ Representante Legal                    │
│  Datos del representante autorizado...     │
│                                             │
│  ✅ [Completar Registro]  [Limpiar]       │
│                                             │
│  🔒 Sus datos están protegidos             │
└─────────────────────────────────────────────┘
```

### 2. Login (Revisor)
```
┌─────────────────────────────────────────────┐
│        🔐 Panel de Revisión                │
│   Sistema de Gestión de Proveedores        │
├─────────────────────────────────────────────┤
│                                             │
│  👤 Usuario:  [________________]           │
│                                             │
│  🔒 Contraseña: [________________]         │
│                                             │
│         [🔑 Iniciar Sesión]               │
│                                             │
│  ⚠️ Acceso solo para personal autorizado  │
│                                             │
│  ← Volver al formulario de proveedores    │
└─────────────────────────────────────────────┘
```

### 3. Lista de Proveedores (Revisor)
```
┌─────────────────────────────────────────────┐
│  📋 Proveedores Registrados                │
│  [+ Nuevo]  [🚪 Cerrar Sesión]            │
├─────────────────────────────────────────────┤
│  📊 Total Proveedores: 45                  │
├─────────────────────────────────────────────┤
│                                             │
│  ID | NIT      | Razón Social | Ciudad     │
│  45 | 900123.. | ACME Corp    | Bogotá     │
│      [👁️ Ver] [✏️ Editar] [⚙️ Admin]      │
│  44 | 800234.. | ABC SA       | Cali       │
│      [👁️ Ver] [✏️ Editar] [⚙️ Admin]      │
│  ...                                        │
│                                             │
│  [◀️ Anterior] Página 1 de 3 [Siguiente ▶️]│
└─────────────────────────────────────────────┘
```

### 4. Detalle de Proveedor (Revisor)
```
┌─────────────────────────────────────────────┐
│  🏢 ACME Corporation                       │
│  [✏️ Editar] [◀️ Volver]                   │
├─────────────────────────────────────────────┤
│                                             │
│  ℹ️ Información General                    │
│  ID: 45                                     │
│  NIT: 900123456-7                          │
│  Tipo: Persona Jurídica                    │
│                                             │
│  📍 Ubicación y Contacto                   │
│  Dirección: Calle 10 #20-30                │
│  Ciudad: Bogotá, Cundinamarca              │
│  ☎️ 601-1234567  📱 3001234567            │
│                                             │
│  📇 Contactos Adicionales (2)              │
│  • Juan Pérez - Gerente                    │
│    📧 juan@acme.com ☎️ 3002345678         │
│  • María López - Contadora                 │
│    📧 maria@acme.com ☎️ 3003456789        │
│                                             │
│  🧾 Impuestos y Retenciones                │
│  Compras: ✅ Sí - 2.5%                    │
│  Servicios: ✅ Sí - 4.0%                  │
│                                             │
│  📄 Documentos (6)                         │
│  📎 RUT                                    │
│  📎 Cámara de Comercio                     │
│  📎 Certificación Bancaria                 │
│  ...                                        │
│                                             │
│  ✍️ Representante Legal                    │
│  Juan Carlos Pérez                         │
│  🖼️ [Firma]  🖼️ [Sello]                   │
└─────────────────────────────────────────────┘
```

---

## 🚀 CÓMO INICIAR EL SISTEMA

```bash
# 1. Activar entorno virtual
venv\Scripts\activate

# 2. Iniciar servidor
python manage.py runserver

# 3. Acceder en el navegador
# Para proveedores: http://127.0.0.1:8000/
# Para revisores: http://127.0.0.1:8000/login/
```

---

## 📧 CÓMO COMPARTIR CON PROVEEDORES

### Opción 1: Email
```
Asunto: Registro de Proveedor - [Nombre Empresa]

Estimado proveedor,

Para completar su vinculación con nuestra empresa, por favor
complete el siguiente formulario de registro:

🔗 http://[su-dominio]/proveedores/registro/

El proceso toma aproximadamente 10 minutos.

Una vez registrado, recibirá un ID que podrá usar para
actualizar su información en cualquier momento.

Saludos,
Departamento de Compras
```

### Opción 2: WhatsApp
```
Hola! 👋

Para registrarse como proveedor, complete este formulario:

🔗 http://[su-dominio]/proveedores/registro/

Toma solo 10 minutos ⏱️

¿Necesita ayuda? Responda este mensaje.
```

---

## 🔐 SEGURIDAD

### URLs Públicas (sin login):
- ✅ `/proveedores/registro/` - Formulario de registro
- ✅ `/proveedores/actualizar/<id>/` - Actualizar datos
- ✅ `/proveedores/success/<id>/` - Confirmación

### URLs Protegidas (requieren login):
- 🔒 `/proveedores/lista/` - Lista de proveedores
- 🔒 `/proveedores/detalle/<id>/` - Detalle de proveedor
- 🔒 `/admin/` - Panel de administración

Si alguien intenta acceder a una URL protegida sin login:
```
Usuario no autenticado accede a /proveedores/lista/
         ↓
Sistema lo redirige a /login/
         ↓
Después de login exitoso, lo lleva a /proveedores/lista/
```

---

## 📊 DATOS QUE SE RECOPILAN

### Del Proveedor:
1. Información General (12 campos)
2. Contactos Adicionales (0-5 contactos, 7 campos c/u)
3. Impuestos (hasta 10 registros, 8 campos c/u)
4. Condiciones de Pago (2 campos)
5. Documentos (6 archivos)
6. Representante Legal (3 campos)

### Total aproximado:
- **Campos de texto**: ~50
- **Archivos**: ~8 (imágenes y PDFs)
- **Relaciones**: Contactos, Impuestos, Documentos

---

## ❓ PREGUNTAS FRECUENTES

### P: ¿Los proveedores necesitan crear cuenta?
**R:** No, pueden llenar el formulario directamente sin registro.

### P: ¿Cómo actualiza un proveedor sus datos?
**R:** Con el ID que reciben al registrarse, acceden a `/proveedores/actualizar/<id>/`

### P: ¿Quién puede ver la lista de proveedores?
**R:** Solo usuarios autenticados (admin/revisores).

### P: ¿Se pueden exportar los datos?
**R:** Sí, desde el panel admin (`/admin/`) se puede exportar a CSV.

### P: ¿Los archivos están seguros?
**R:** Sí, se guardan en `media/` con nombres únicos y solo usuarios autenticados pueden acceder vía URLs directas.

---

## 🎓 PRÓXIMOS PASOS RECOMENDADOS

1. **Probar el formulario** como proveedor
2. **Iniciar sesión** como revisor y ver la lista
3. **Personalizar** colores y logos en `static/css/style.css`
4. **Configurar email** para enviar notificaciones automáticas
5. **Agregar búsqueda** en la lista de proveedores
6. **Desplegar** en un servidor de producción

---

¡El sistema está listo para usar! 🎉
