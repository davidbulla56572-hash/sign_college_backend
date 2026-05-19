# Project Context

## Product
Sistema inteligente de evaluación de aspirantes docentes.

## Main actors
- Aspirante
- Administrador

## Core flows in scope
1. Login
2. Registro de aspirante
3. Carga de CV PDF/DOCX
4. Extracción IA de datos del CV
5. Edición del formato de hoja de vida
6. Envío de postulación
7. Consulta de estado y resultados
8. Dashboard administrador

## Main entities
- Usuario
- Convocatoria
- Postulacion
- ItemHojaVida
- SoporteItem
- ReglaEvaluacion

## Important backend implications
- One user should not duplicate a postulation for the same convocatoria
- CV upload, extraction, and editable persistence are separate concerns
- Evaluation logic must remain isolated and testable
- The system needs role-aware access for aspirants and admins
