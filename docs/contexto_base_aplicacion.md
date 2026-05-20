# Contexto Base de la Aplicación
## Sistema Inteligente de Evaluación de Aspirantes Docentes

## 1. Propósito de este documento

Este documento consolida el contexto integral de la aplicación y debe ser tomado como la base principal para todo lo que se diseñe, implemente, documente o evolucione en el proyecto. Su propósito es unificar en un solo lugar la visión funcional, técnica, conceptual, arquitectónica y operativa del sistema, de manera que cualquier decisión futura mantenga coherencia con el alcance y dirección definidos.

Este archivo debe servir como referencia madre para:

- arquitectura de software,
- desarrollo frontend,
- desarrollo backend,
- diseño de base de datos,
- integración de inteligencia artificial,
- documentación técnica,
- backlog técnico,
- criterios de calidad,
- definición de fases,
- uso de skills de desarrollo con ChatGPT.

---

## 2. Nombre del proyecto

**Sistema Inteligente de Evaluación de Aspirantes Docentes**

---

## 3. Contexto del problema

Los procesos de selección de aspirantes docentes suelen implicar revisión manual de hojas de vida, validación de soportes, interpretación de experiencia académica y profesional, y aplicación de reglas de evaluación definidas por cada convocatoria. Este proceso puede ser lento, repetitivo, propenso a errores y difícil de estandarizar cuando se realiza de forma manual.

La aplicación busca resolver este problema mediante una plataforma web que permita:

- registrar aspirantes,
- recibir hojas de vida en PDF o DOCX,
- extraer información automáticamente usando IA,
- estructurar la información en un formato editable,
- aplicar reglas de evaluación configurables,
- calcular puntajes,
- mostrar resultados y estado de la postulación,
- facilitar la gestión del proceso por parte de un administrador.

---

## 4. Objetivo general

Construir una aplicación web que automatice y estandarice el proceso de evaluación de aspirantes docentes, permitiendo una gestión eficiente de convocatorias, extracción de información documental, validación de datos, cálculo automático de puntajes y visualización de resultados para aspirantes y administradores.

---

## 5. Objetivos específicos

- Permitir el registro e inicio de sesión de usuarios.
- Diferenciar permisos entre aspirantes y administradores.
- Permitir la creación y gestión de convocatorias.
- Facilitar la carga de hojas de vida en formato PDF o DOCX.
- Integrar un módulo de inteligencia artificial para extracción automática de datos.
- Permitir la edición manual de la información extraída.
- Gestionar soportes documentales asociados a cada ítem de hoja de vida.
- Aplicar reglas de evaluación configurables por convocatoria.
- Calcular el puntaje total de cada postulación.
- Mostrar al aspirante el estado de su proceso.
- Mostrar al administrador dashboards y listados de resultados.
- Mantener trazabilidad y coherencia entre datos, reglas y resultados.

---

## 6. Visión del producto

La visión del producto es construir una plataforma académica robusta, clara y escalable que sirva como apoyo al proceso de selección docente, reduciendo carga operativa, aumentando consistencia en la evaluación y proporcionando una experiencia ordenada tanto para el aspirante como para el administrador.

El sistema no debe ser un prototipo desordenado orientado solo a la entrega; debe sentar bases reales de arquitectura, modularidad y calidad para permitir crecimiento, mantenimiento y evolución.

---

## 7. Alcance funcional del sistema

## 7.1 Funcionalidades para aspirante
- Registrarse en el sistema.
- Iniciar sesión.
- Cargar su hoja de vida.
- Visualizar los datos extraídos automáticamente.
- Editar y completar manualmente su información.
- Adjuntar soportes por ítem.
- Guardar y enviar su postulación.
- Consultar estado de la postulación.
- Consultar resultados y puntaje.

## 7.2 Funcionalidades para administrador
- Iniciar sesión.
- Crear convocatorias.
- Definir o configurar reglas de evaluación.
- Visualizar postulaciones recibidas.
- Consultar ranking o listado de aspirantes.
- Filtrar por estado.
- Ver detalle de postulaciones.
- Ver soportes documentales.
- Consultar resultados por aspirante y por convocatoria.

## 7.3 Funcionalidades del sistema
- Procesar documentos con IA.
- Extraer datos estructurados.
- Aplicar reglas de evaluación.
- Calcular puntajes automáticamente.
- Mantener consistencia entre convocatorias, reglas y resultados.

---

## 8. Roles del sistema

### Aspirante
Usuario que se postula a una convocatoria docente. Su interacción principal está centrada en el registro, carga de hoja de vida, edición de datos, envío de postulación y consulta de estado y resultados.

### Administrador
Usuario con permisos de gestión sobre convocatorias, evaluación y visualización del proceso. Tiene acceso a funcionalidades administrativas y a la gestión de resultados.

---

## 9. Metodología de trabajo definida

El proyecto se enmarca en un enfoque ágil tipo **Scrumban**, combinando elementos de Scrum y Kanban.

### Scrum
- Sprints de duración corta.
- Planeación por entregas.
- Revisión y retrospectiva.
- Product backlog priorizado.

### Kanban
- Flujo visual de tareas.
- Trabajo por columnas.
- Seguimiento continuo.
- Control de trabajo en progreso.

Este enfoque busca equilibrar disciplina de entrega con flexibilidad de ejecución.

---

## 10. Stack tecnológico oficial

## 10.1 Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- React Router DOM
- Formik
- Yup
- Zustand
- TanStack Query
- Axios
- React Toastify
- React Dropzone
- clsx
- tailwind-merge

## 10.2 Backend
- FastAPI
- Python 3.11+
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- passlib / bcrypt
- python-jose o PyJWT
- httpx
- pytest

## 10.3 Integración de IA
- Gemini API o un proveedor equivalente desacoplado desde una capa de integración.

## 10.4 Gestión y soporte
- Git
- GitHub
- GitHub Projects o tablero Kanban
- Markdown para documentación
- Skills especializados para desarrollo con ChatGPT

---

## 11. Regla central de diseño del proyecto

Todo el proyecto debe construirse con esta regla como principio obligatorio:

> Se debe utilizar primero el ecosistema de librerías y herramientas definidas antes de crear lógica personalizada nueva.

Esto significa que no se debe reinventar lo que ya resuelven bien librerías maduras del stack.

### En frontend, usar prioritariamente:
- Formik para formularios
- Yup para validación
- Zustand para estado global ligero
- TanStack Query para datos remotos
- Axios para comunicación HTTP
- React Toastify para notificaciones
- React Dropzone para carga de archivos
- Tailwind para estilos
- clsx y tailwind-merge para composición de clases

### En backend, usar prioritariamente:
- FastAPI para API REST y dependencias
- Pydantic para validación y settings
- SQLAlchemy para persistencia
- Alembic para migraciones
- herramientas estándar del ecosistema JWT para autenticación

---

## 12. Principios arquitectónicos

- Separación clara de responsabilidades.
- Arquitectura desacoplada entre frontend y backend.
- Modularidad por dominio o feature.
- Reutilización antes que duplicación.
- Validación en cliente y servidor.
- Contratos API bien definidos.
- Preparación para escalar.
- Integraciones externas desacopladas.
- Calidad estructural por encima de velocidad improvisada.

---

## 13. Arquitectura general del sistema

La aplicación se construirá bajo una arquitectura cliente-servidor desacoplada.

### Frontend
Aplicación SPA construida en React, encargada de la experiencia del usuario, formularios, navegación, visualización de estados y consumo de la API.

### Backend
API REST construida con FastAPI, encargada de:
- autenticación,
- lógica de negocio,
- acceso a base de datos,
- orquestación de la integración con IA,
- evaluación por reglas,
- exposición de datos al frontend.

### Base de datos
PostgreSQL como base de datos relacional principal.

### Módulo IA
Servicio integrado desde backend para procesar hojas de vida y devolver datos estructurados.

### Motor de reglas
Servicio de negocio que calcula puntajes a partir de reglas configurables por convocatoria.

---

## 14. Modelo conceptual del dominio

El dominio principal del sistema gira alrededor de estos conceptos:

- Usuario
- Aspirante
- Administrador
- Convocatoria
- Postulación
- Hoja de vida estructurada
- Ítem de hoja de vida
- Soporte documental
- Regla de evaluación
- Resultado o puntaje
- Estado de postulación

Estos conceptos deben guiar tanto el modelo de datos como la estructura del software.

---

## 15. Entidades principales del sistema

### Usuario
Representa cualquier persona autenticada dentro del sistema.

Campos esperados:
- id_usuario
- nombre
- apellido
- cedula
- email
- telefono
- municipio
- departamento
- pais
- rol
- password_hash
- activo
- fecha_registro
- fecha_actualizacion

### Convocatoria
Representa cada proceso de selección docente.

Campos esperados:
- id_convocatoria
- titulo
- descripcion
- fecha_inicio
- fecha_cierre
- activa
- creado_por
- fecha_creacion
- fecha_actualizacion

### Postulacion
Representa la relación entre aspirante y convocatoria.

Campos esperados:
- id_postulacion
- id_usuario
- id_convocatoria
- estado
- puntaje_total
- url_cv_original
- observaciones_admin
- fecha_envio
- fecha_evaluacion
- fecha_creacion
- fecha_actualizacion

### ItemHojaVida
Representa cada ítem estructurado de la hoja de vida.

Campos esperados:
- id_item
- id_postulacion
- tipo_item
- descripcion
- institucion
- fecha_inicio
- fecha_fin
- cantidad
- puntaje_asignado
- validado
- fecha_creacion

### SoporteItem
Representa documentos de soporte asociados a cada ítem.

Campos esperados:
- id_soporte
- id_item
- nombre_archivo
- url_archivo
- tipo_archivo
- tamanio_bytes
- fecha_carga

### ReglaEvaluacion
Representa la configuración de puntaje por tipo de ítem dentro de una convocatoria.

Campos esperados:
- id_regla
- id_convocatoria
- tipo_item
- descripcion_regla
- puntaje_unitario
- maximo_acumulable
- unidad

---

## 16. Relaciones principales del modelo

- Un Usuario puede tener muchas Postulaciones.
- Un Administrador crea muchas Convocatorias.
- Una Convocatoria tiene muchas Postulaciones.
- Una Convocatoria tiene muchas Reglas de Evaluación.
- Una Postulación tiene muchos Items de Hoja de Vida.
- Un Item de Hoja de Vida puede tener muchos Soportes.

Además, debe existir una restricción para evitar que un usuario se postule más de una vez a la misma convocatoria.

---

## 17. Casos de uso centrales

Los casos de uso funcionales más relevantes del sistema son:

- Registrar aspirante
- Iniciar sesión
- Cargar CV
- Editar datos del perfil extraído
- Consultar estado de postulación
- Evaluar aspirante automáticamente
- Ver dashboard de aspirantes
- Configurar convocatoria

Estos casos de uso deben guiar la construcción del backlog, la arquitectura y las fases de implementación.

---

## 18. Historias de usuario prioritarias

Entre las historias de usuario más importantes se encuentran:

- Como aspirante, quiero registrarme para poder postularme.
- Como aspirante, quiero subir mi hoja de vida para que la IA extraiga mis datos automáticamente.
- Como aspirante, quiero editar los datos extraídos para corregir errores.
- Como aspirante, quiero consultar el estado de mi postulación.
- Como administrador, quiero ver un dashboard con todos los aspirantes.
- Como administrador, quiero configurar reglas y puntajes de la convocatoria.
- Como sistema, quiero evaluar automáticamente cada aspirante.

Estas historias deben traducirse en módulos concretos y en prioridades técnicas reales.

---

## 19. Módulos funcionales del sistema

## 19.1 Módulo de autenticación
Responsabilidades:
- login,
- registro si aplica,
- sesión,
- control de acceso,
- autorización por rol,
- logout.

## 19.2 Módulo de convocatorias
Responsabilidades:
- crear,
- consultar,
- activar,
- cerrar,
- listar convocatorias.

## 19.3 Módulo de hoja de vida
Responsabilidades:
- carga de CV,
- validación de archivo,
- procesamiento IA,
- normalización de datos,
- edición del formulario estructurado,
- persistencia de ítems.

## 19.4 Módulo de soportes
Responsabilidades:
- adjuntar soportes,
- almacenar archivos,
- asociarlos a ítems,
- visualizarlos.

## 19.5 Módulo de postulaciones
Responsabilidades:
- crear postulación,
- guardar borrador,
- enviar postulación,
- consultar detalle,
- consultar estado.

## 19.6 Módulo de reglas de evaluación
Responsabilidades:
- crear reglas,
- listar reglas,
- modificar configuración,
- asociar reglas a convocatoria.

## 19.7 Módulo de resultados
Responsabilidades:
- calcular puntaje,
- mostrar resumen,
- mostrar ranking,
- mostrar trazabilidad del resultado.

## 19.8 Módulo administrativo
Responsabilidades:
- ver aspirantes,
- filtrar por estado,
- consultar ranking,
- revisar soportes,
- gestionar proceso.

---

## 20. Arquitectura objetivo del frontend

```txt
frontend/
├── src/
│   ├── app/
│   │   ├── providers/
│   │   ├── router/
│   │   └── store/
│   ├── shared/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── services/
│   │   ├── types/
│   │   └── utils/
│   ├── features/
│   │   ├── auth/
│   │   ├── convocatorias/
│   │   ├── postulaciones/
│   │   ├── hoja-vida/
│   │   ├── resultados/
│   │   └── admin/
│   ├── pages/
│   ├── layouts/
│   ├── styles/
│   └── main.tsx
```

### Criterios del frontend
- Arquitectura por features.
- Formularios con Formik.
- Validación con Yup.
- Estado remoto con TanStack Query.
- Estado global mínimo con Zustand.
- UI basada en Tailwind.
- Comunicación HTTP centralizada con Axios.
- Componentes reutilizables pequeños y claros.

---

## 21. Arquitectura objetivo del backend

```txt
backend/
├── app/
│   ├── api/
│   │   ├── deps/
│   │   ├── routes/
│   │   └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── exceptions.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── migrations/
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── integrations/
│   │   └── gemini/
│   ├── utils/
│   └── main.py
├── tests/
└── alembic.ini
```

### Criterios del backend
- Rutas delgadas.
- Servicios para lógica de negocio.
- Repositorios para acceso a datos.
- Schemas de entrada y salida con Pydantic.
- Integraciones externas desacopladas.
- Seguridad centralizada.
- Configuración centralizada.
- Preparación para pruebas y evolución modular.

---

## 22. API base del sistema

La API debe seguir una convención REST clara y versionada.

### Prefijo base
`/api/v1`

### Endpoints base esperados
#### Auth
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

#### Convocatorias
- `GET /api/v1/convocatorias`
- `GET /api/v1/convocatorias/{id}`
- `POST /api/v1/convocatorias`

#### Postulaciones
- `POST /api/v1/postulaciones`
- `GET /api/v1/postulaciones/mine`
- `GET /api/v1/postulaciones/{id}`
- `PATCH /api/v1/postulaciones/{id}/submit`

#### Hoja de vida
- `POST /api/v1/hoja-vida/upload`
- `PUT /api/v1/hoja-vida/postulaciones/{id}`
- `POST /api/v1/hoja-vida/postulaciones/{id}/soportes`

#### Resultados
- `GET /api/v1/resultados/mis-resultados`
- `GET /api/v1/resultados/ranking`
- `GET /api/v1/resultados/postulaciones/{id}`

---

## 23. Estrategia de integración con IA

La integración con IA debe diseñarse de forma desacoplada.

### Flujo esperado
1. El frontend envía un archivo.
2. El backend valida formato y tamaño.
3. El backend almacena el archivo.
4. El backend invoca la integración IA.
5. La IA devuelve información estructurada.
6. El backend normaliza la respuesta a un esquema interno.
7. El frontend recibe datos listos para editar.

### Reglas de diseño
- No acoplar el sistema a un único proveedor.
- Mantener una interfaz interna estable.
- Permitir mock de respuestas.
- Facilitar pruebas e intercambio futuro de proveedor.

---

## 24. Estrategia del motor de reglas

El cálculo del puntaje debe estar aislado en un servicio de negocio especializado.

### Responsabilidades del motor
- obtener reglas de la convocatoria,
- evaluar ítems de hoja de vida,
- calcular puntaje por regla,
- aplicar límites o máximos acumulables,
- sumar puntaje total,
- devolver trazabilidad del cálculo.

Esto debe evitar lógica dispersa en endpoints o componentes.

---

## 25. Fases del proyecto

### Fase 1
Análisis, diseño, documentación y definición de bases.

### Fase 2
Base técnica de frontend y backend.

### Fase 3
Primer flujo funcional real, comenzando por autenticación y acceso.

### Fase 4
Carga de CV, extracción IA y edición de hoja de vida.

### Fase 5
Resultados, dashboard administrativo, integración y ajustes.

Estas fases pueden adaptarse, pero deben mantener una progresión lógica.

---

## 26. Primera prioridad de construcción

El proyecto debe comenzar por sentar correctamente la base técnica y luego cerrar el primer flujo funcional end-to-end.

### Orden recomendado
1. Base del backend  
2. Base del frontend  
3. Login completo  
4. Sesión y control de acceso  
5. Carga de CV  
6. Formato de hoja de vida  
7. Guardado y envío de postulación  
8. Resultados  
9. Dashboard administrativo  
10. Pruebas y documentación  

---

## 27. Criterios de calidad del proyecto

Todo desarrollo debe seguir estos criterios:

- claridad de arquitectura,
- modularidad,
- bajo acoplamiento,
- reutilización,
- validación robusta,
- manejo correcto de errores,
- consistencia visual y técnica,
- documentación continua,
- pruebas mínimas en flujos críticos.

### Casos críticos que requieren mayor cuidado
- autenticación,
- control de acceso,
- carga de archivos,
- persistencia de hoja de vida,
- evaluación automática,
- consulta de resultados.

---

## 28. Riesgos técnicos y de proyecto

- Construir rápido sin base técnica suficiente.
- Mezclar lógica de negocio con presentación.
- Duplicar lógica en frontend o backend.
- Definir contratos API ambiguos.
- Acoplar demasiado la IA.
- No alinear modelo de datos con implementación.
- No respetar el stack acordado.
- Crear lógica manual donde una librería ya resuelve el problema.

### Mitigación
- Usar este documento como fuente base.
- Apoyarse en los skills definidos.
- Revisar arquitectura antes de cada módulo.
- Mantener consistencia entre documentación, datos y código.

---

## 29. Relación con los skills del proyecto

El proyecto cuenta con skills de frontend y backend pensados para ser usados con ChatGPT durante el desarrollo.

### Skill de frontend
Debe reforzar:
- uso disciplinado del ecosistema React definido,
- arquitectura por features,
- formularios robustos,
- integración limpia con backend,
- priorización de librerías sobre lógica manual.

### Skill de backend
Debe reforzar:
- arquitectura limpia en FastAPI,
- separación de rutas, servicios y repositorios,
- validación y seguridad consistentes,
- diseño preparado para IA y reglas.

Estos skills no reemplazan el criterio de arquitectura; lo operacionalizan.

---

## 30. Convenciones generales de desarrollo

### Frontend
- Componentes en PascalCase.
- Hooks con prefijo `use`.
- Schemas de validación por feature.
- Queries y mutations con claves consistentes.
- No usar estado global para datos que correspondan a Query.

### Backend
- Endpoints REST consistentes.
- Schemas de entrada y salida separados.
- Servicios sin dependencia directa innecesaria de FastAPI.
- Repositorios enfocados en persistencia.
- Errores homogéneos y previsibles.

### Proyecto
- Documentar decisiones relevantes.
- Mantener carpetas organizadas.
- Evitar archivos gigantes.
- Una responsabilidad principal por módulo o servicio.

---

## 31. Definition of Done general

Una funcionalidad o módulo se considera terminado cuando:

- cumple su objetivo funcional,
- respeta la arquitectura definida,
- usa correctamente las librerías priorizadas,
- valida entrada y salida,
- maneja errores y estados,
- no introduce duplicación innecesaria,
- está documentado,
- fue probado en su flujo principal.

---

## 32. Qué debe pasar siempre antes de construir algo nuevo

Antes de implementar cualquier nuevo módulo, pantalla, endpoint o integración, se debe verificar:

1. cuál es su objetivo dentro del sistema,
2. qué entidad o módulo del dominio afecta,
3. cuál será el contrato API,
4. qué parte corresponde a frontend y cuál a backend,
5. qué librerías existentes lo resuelven,
6. cómo se integra con la arquitectura actual,
7. qué criterios de calidad debe cumplir.

---

## 33. Rol de este documento en el proyecto

Este archivo debe ser considerado:

- la base conceptual del proyecto,
- la fuente principal de alineación,
- el punto de partida para diseño técnico,
- la referencia madre para decisiones de arquitectura,
- el contexto común para frontend, backend, documentación y uso de IA.

Cuando exista duda entre múltiples caminos técnicos, debe priorizarse el que más respete este contexto base.

---

## 34. Conclusión

El Sistema Inteligente de Evaluación de Aspirantes Docentes no debe desarrollarse como una suma de pantallas o endpoints aislados, sino como una plataforma coherente, modular y preparada para crecer. La clave del proyecto está en construir desde bases sólidas: entender el problema, respetar el dominio, aprovechar bien el stack, separar responsabilidades y mantener una visión clara del producto.

Este documento establece esa base. Todo lo que se haga en adelante debe alinearse con este contexto integral.
