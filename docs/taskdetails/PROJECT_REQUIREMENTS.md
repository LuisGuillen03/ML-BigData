# Proyecto Final - Analítica Predictiva en Entornos de Datos Masivos

**Asignatura:** Aprendizaje Máquina para G.D.  
**Universidad Panamericana**  
**Profesor:** Omar Velázquez López

---

## Objetivo

Diseñar, implementar y documentar una solución de analítica en la nube que trate con datos masivos (≥ 32 millones de registros), integrando componentes de almacenamiento, procesamiento distribuido o incremental, modelado predictivo y despliegue o análisis explicativo.

---

## Ruta Seleccionada: A - Procesamiento Distribuido con PySpark en Dataproc

Esta ruta se centra en la implementación de técnicas de cómputo distribuido para procesar datos masivos utilizando clusters de Dataproc y la API de PySpark.

---

## Actividades Obligatorias

### 1. Selección y exportación del dataset hacia GCS

- **Requisito:** Dataset con ≥ 32 millones de registros
- **Fuente:** BigQuery o fuente de datos seleccionada
- **Tareas:**
  - Exportación desde BigQuery
  - Verificación de estructura, consistencia y tamaños
  - Almacenamiento en Cloud Storage (GCS)

### 2. Procesamiento distribuido en Dataproc

- **Tareas:**
  - Creación del cluster
  - Lectura del dataset desde GCS mediante PySpark
  - Aplicación de limpieza, filtrado, transformación y muestreo

### 3. Modelado predictivo en PySpark

- **Implementación de modelo supervisado:**
  - Logistic Regression
  - Linear Regression
  - One-vs-Rest (según naturaleza del dataset)
- **Métricas:**
  - Accuracy
  - Recall
  - F1
  - R²

### 4. Evaluación comparativa entre dos configuraciones de cluster

**Requisitos críticos:**
- Incluir métricas de tiempo y observaciones del Job UI
- Interpretar cómo afecta el tamaño del cluster a la ejecución
- Comentar sobre latencia, paralelismo y escalabilidad

### 5. Documentación y análisis

- Interpretación de resultados
- Justificación del muestreo
- Evaluación del desempeño del modelo

---

## Evidencias Requeridas

### Capturas de pantalla:
- ✅ Bucket en GCS
- ✅ Cluster y jobs en Dataproc
- ✅ Job UI con métricas de tiempo

### Código:
- ✅ Script del programa principal de PySpark

### Análisis:
- ✅ Tabla comparativa de tiempos y métricas de evaluación
- ✅ Conclusiones

---

## Formato de Entrega

**Archivo:** `Proyecto_Final_NombreApellido.pdf`

**Debe incluir:**
1. Dataset utilizado
   - Fuente, tamaño y justificación
2. Descripción de la arquitectura implementada (diagrama)
3. Desarrollo de la ruta elegida
4. Métricas, gráficas, tablas
5. Análisis crítico: Ventajas y limitaciones del enfoque elegido

---

## Rúbrica de Evaluación

| Criterio | Descripción | Puntos |
|----------|-------------|--------|
| **Implementación del pipeline de datos** | Ejecución completa y reproducible del flujo técnico (ingesta, preparación, procesamiento y ejecución del pipeline PySpark) | 40 |
| **Modelado predictivo y análisis del desempeño** | Correcta implementación del modelo, métricas reportadas, visualizaciones y análisis crítico de resultados o estabilidad | 35 |
| **Exposición del trabajo** | Claridad y conclusiones bien fundamentadas durante la presentación | 25 |
| **Total** | | **100** |

---

## Referencias

- Google LLC (s. f.). Google Cloud Console. https://console.cloud.google.com/
- Google Cloud. (2024). Crea un clúster de Dataproc con la consola de Google Cloud. https://cloud.google.com/dataproc/docs/quickstarts/create-cluster-console?hl=es-419
- Velázquez O. (2025). Material de trabajo de la asignatura [Notebooks]. Google Colab. https://drive.google.com/drive/folders/1jE3cqnPqAXtPCpcZDjMivKE6ipb2v7Wy?usp=sharing
