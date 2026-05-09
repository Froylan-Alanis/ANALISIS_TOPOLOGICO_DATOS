# Sistema de Análisis Topológico de Datos (TDA) sobre ITER 2020

## Descripción General

Este proyecto consiste en el desarrollo de un sistema web interactivo para el análisis de datos poblacionales del archivo ITER 2020 del INEGI utilizando técnicas de Análisis Topológico de Datos (TDA).

El sistema permite visualizar, explorar y analizar información geográfica y poblacional mediante herramientas estadísticas, métricas y representaciones topológicas.

La aplicación fue desarrollada utilizando Flask, SQLite, Bootstrap y Plotly.

---

# Objetivo del Proyecto

Aplicar conceptos de:

- Análisis Topológico de Datos (TDA)
- Espacios métricos
- Distancias
- Representación multidimensional
- Detección de anomalías

sobre información real del Censo de Población y Vivienda 2020.

---

# Tecnologías Utilizadas

## Backend

- Python 3
- Flask
- SQLite3

## Frontend

- HTML5
- CSS3
- Bootstrap 5
- Bootstrap Icons
- JavaScript

## Visualización

- Plotly.js
- DataTables

---

# Base de Datos

El sistema utiliza una base de datos SQLite llamada:

BD_PROJECT_ULISES.db

La tabla principal utilizada es:

ITER_NALCSV20

---

# Variables Utilizadas

| Variable | Descripción |
|---|---|
| NOM_ENT | Nombre de la entidad |
| NOM_MUN | Nombre del municipio |
| NOM_LOC | Nombre de la localidad |
| POBTOT | Población total |
| POB0_14 | Población de 0 a 14 años |
| POB15_64 | Población de 15 a 64 años |
| POB65_MAS | Población de 65 años y más |
| LATITUD | Coordenada geográfica |
| LONGITUD | Coordenada geográfica |

---

# Funcionalidades del Sistema

## Página principal

Dashboard principal del sistema con acceso a todas las vistas analíticas.

---

## Consulta de localidades

Visualización tabular interactiva utilizando DataTables:

- búsqueda
- paginación
- ordenamiento
- estadísticas rápidas

---

# Análisis Topológico de Datos (TDA)

## 1. Nube de puntos geográfica

Representación espacial de localidades mediante coordenadas geográficas.

### Conceptos aplicados

- Nubes de puntos
- Espacios métricos
- Distribución espacial
- Agrupamientos geográficos

---

## 2. Espacio multidimensional

Representación vectorial de variables poblacionales.

### Conceptos aplicados

- Vectores multidimensionales
- Norma euclidiana
- Similitud poblacional
- Espacios métricos

---

## 3. Distancias Manhattan

Cálculo de similitud entre localidades mediante distancia Manhattan.

### Conceptos aplicados

- Métrica Manhattan
- Similitud topológica
- Cercanía geométrica
- Espacios multidimensionales

---

## 4. Componentes conectados

Agrupamiento de localidades por entidad federativa.

### Conceptos aplicados

- Componentes conectados
- Agrupamientos topológicos
- Densidad poblacional
- Relaciones espaciales

---

## 5. Outliers poblacionales

Detección de localidades atípicas mediante análisis estadístico.

### Conceptos aplicados

- Detección de anomalías
- Outliers topológicos
- Desviación estándar
- Distribución poblacional

---

# Arquitectura del Sistema

Usuario
   │
   ▼
Frontend (HTML + Bootstrap + Plotly)
   │
   ▼
Flask (Python)
   │
   ▼
SQLite
   │
   ▼
ITER 2020

---

# Estructura del Proyecto

PROYECTO_TDA/
│
├── inicio.py
├── BD_PROJECT_ULISES.db
│
├── templates/
│   ├── index.html
│   ├── tabla_simple.html
│   ├── tda_nube_puntos.html
│   ├── tda_vector.html
│   ├── tda_distancias.html
│   ├── tda_componentes.html
│   └── tda_outliers.html
│
├── Files/
│   └── reporte.csv
│
└── README.md

---

# Instalación

## 1. Clonar o descargar el proyecto

```bash
git clone proyecto_tda.git
```

---

## 2. Instalar dependencias

```bash
pip install flask
```

---

## 3. Ejecutar el sistema

```bash
python inicio.py
```

---

## 4. Abrir en navegador

http://127.0.0.1:5000

---

# Características del Sistema

- Dashboard interactivo
- Visualización avanzada
- APIs REST
- Consultas SQL analíticas
- Gráficas dinámicas
- Heatmaps
- Scatter plots
- DataTables
- Diseño responsive
- Manejo de errores

---

# Fuente de Datos

Instituto Nacional de Estadística y Geografía (INEGI)

ITER 2020 — Censo de Población y Vivienda 2020

---

# Conclusión

El sistema desarrollado permite aplicar técnicas de Análisis Topológico de Datos sobre información poblacional real utilizando herramientas modernas de análisis, visualización y procesamiento de datos.

El proyecto integra conceptos matemáticos, estadísticos y computacionales mediante una arquitectura web interactiva y visualmente profesional.
