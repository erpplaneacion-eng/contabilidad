# Supplier Registration/Update Form - Django Application

This README outlines the fields and structure for a Django-based web application to handle supplier registration and update forms, based on the Excel file `FORMATO PROVEEDORES ACTUALIZADO JULIO 2024 V2 (1).xls`.

The form is titled "SOLICITUD DE VINCULACIÓN O ACTUALIZACIÓN DE DATOS" (Request for Linking or Data Update) and includes sections for general information, contacts, taxes, payment conditions, and required documents.

## Form Sections and Fields

### 1. General Information (INFORMACIÓN GENERAL)
- **Fecha Diligenciamiento** (Date of Completion): Date field (DateField in Django)
- **Nombre o Razón Social** (Name or Business Name): Text field (CharField, max_length=200)
- **Naturaleza Jurídica** (Legal Nature): Select field (ChoiceField) - Options: Persona Natural, Persona Jurídica, etc. (to be defined)
- **Tipo de identificación** (Type of Identification): Select field (ChoiceField) - Options: Cédula de Ciudadanía, NIT, Pasaporte, etc.
- **No de identificación** (ID Number): Text field (CharField, max_length=20)
- **Dirección** (Address): Text field (CharField, max_length=200)
- **Teléfono** (Phone): Text field (CharField, max_length=20)
- **Celular** (Cell Phone): Text field (CharField, max_length=20)
- **País** (Country): Select field (ChoiceField) - Options: Colombia, etc. (expand as needed)
- **Departamento** (Department): Select field (ChoiceField) - Options: Antioquia, Bogotá, etc.
- **Ciudad** (City): Text field (CharField, max_length=100)

### 2. Other Contacts (OTROS CONTACTOS)
Two sets of contact fields (can be modeled as related models or inline forms).

For each contact:
- **Nombre y Apellidos** (Name and Surname): Text field (CharField, max_length=200)
- **Cargo** (Position): Text field (CharField, max_length=100)
- **Dirección** (Address): Text field (CharField, max_length=200)
- **Correo Electrónico** (Email): Email field (EmailField)
- **Ciudad** (City): Text field (CharField, max_length=100)
- **Teléfono** (Phone): Text field (CharField, max_length=20)
- **Celular** (Cell Phone): Text field (CharField, max_length=20)

### 3. Taxes (IMPUESTOS DE INDUSTRIA Y COMERCIO / RETENCIÓN EN LA FUENTE)
For each tax type (Rte Fte por compras, Rte Fte por servicios, etc.), include:
- **SI/NO** (Yes/No): Boolean field (BooleanField)
- **PORCENTAJE** (Percentage): Decimal field (DecimalField, max_digits=5, decimal_places=2)
- **Código Act. Econ. (CIIU)**: Text field (CharField, max_length=10)
- **Tarifa** (Rate): Decimal field (DecimalField, max_digits=5, decimal_places=2)
- **Municipio** (Municipality): Text field (CharField, max_length=100)
- **Si es exento indicar el número y fecha de resolución** (If exempt, indicate resolution number and date): Text field (CharField, max_length=200)

Tax Types:
- Rete Fte por compras (Withholding for purchases)
- Rete Fte por servicios (Withholding for services)
- Rete Fte por transporte (Withholding for transportation)
- Rete Fte por otro concepto (Withholding for other concepts) - Include a text field for specification

### 4. Payment Conditions (CONDICIONES DE PAGO)
- **Código** (Code): Select field (ChoiceField) - Options:
  - 001: Contado (Cash)
  - 008: Crédito 8 Días (8-day Credit)
  - 010: Crédito 10 Días (10-day Credit)
  - 015: Crédito 15 Días (15-day Credit)
  - 030: Crédito 30 Días (30-day Credit)
  - 045: Crédito 45 Días (45-day Credit)
  - 060: Crédito 60 Días (60-day Credit)
  - Otro (Other): Include a text field for custom description

### 5. Required Documents (DOCUMENTOS REQUERIDOS)
- **Fotocopia del RUT**: File upload field (FileField) or Boolean for confirmation
- **Solicitud de vinculación o actualización de datos**: File upload or Boolean
- **Certificado de Cámara y Comercio (No más de 30 días)**: File upload or Boolean
- **Certificación Bancaria**: File upload or Boolean
- **Fotocopia C.C. Representante Legal**: File upload or Boolean
- **Autorización para Recolección, Consulta, Tratamiento de Datos**: File upload or Boolean

### 6. Signature and Approval
- **Firma del Representante legal** (Signature of Legal Representative): Image upload (ImageField) or text
- **Datos del Representante Legal** (Legal Representative Data): Text field (CharField, max_length=200)
- **Firma del Representante legal** (Signature): Image upload or text
- **Sello** (Seal): Image upload (ImageField)

## Additional Notes
- Dates like "Fecha actualizacion" (45474, 45498) are Excel serial dates; convert to actual dates in Django (e.g., using datetime.fromordinal).
- For file uploads, use Django's FileField and handle storage appropriately.
- Consider using Django forms with ModelForm for database integration.
- Validate fields such as email, phone numbers, and percentages.
- For multi-contact and multi-tax sections, use inline formsets or related models.

This specification can be used to build a Django model, forms, and views for the application.