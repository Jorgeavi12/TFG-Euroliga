# TFG-Euroliga


Este repositorio contiene el ecosistema completo de scripts y flujos de datos desarrollado para el Trabajo Fin de Grado (TFG) en Ingeniería Informática por la **Universitat Politècnica de València (UPV) - ETSINF**. 

El objetivo del proyecto es la construcción de una arquitectura de datos integrada (Pipeline ETL) que automatiza la ingesta, transformación y modelado semántico de los datos históricos de la Euroliga para su posterior explotación analítica en un cuadro de mando interactivo en Power BI.

---

## Estructura del Repositorio y Componentes

El núcleo de desarrollo se divide en tres fases lógicas distribuidas en módulos de scripts en Python:

### 1. Módulo de Extracción (Web Scraping)
Encargado de la ingesta automatizada en bruto desde los portales oficiales de datos.
* `estadisticas_partidos.py`: Extracción automatizada de los eventos y datos generales de los partidos por temporada empleando automatización de navegador.
    * *Librerías:* `selenium` (Webdriver, Options), `beautifulsoup4`, `json`, `pandas`, `time`, `warnings`, `datetime`.
* `estadisticas_jugadores.py`: Extracción del rendimiento estadístico de los jugadores vinculados a las URLs de los partidos previamente capturados.
    * *Librerías:* `pandas`, `requests`, `os`, `time`, `random`, `re`.

### 2. Módulo de Transformación (Procesamiento y Analítica Avanzada)
Fase dedicada a la limpieza profunda, cálculo de métricas avanzadas de baloncesto (Four Factors, ritmos, eficiencias) y consolidación temporal.
* `analisis_avanzado_jugadores.py` y `analisis_avanzado_equipos.py`
* `promedios_jugadores.py` y `promedios_equipos.py` (Cálculo segmentado por temporada).
* `promedios_jugadores_todas.py` y `promedios_equipos_todas.py` (Unificación de series históricas).
* `historico_jugadores.py` y `historico_equipos.py`
* *Librerías:* `pandas`, `glob`, `os`, `re`.

### 3. Módulo de Carga (Modelado Dimensional)
Scripts encargados de estructurar y normalizar los datos bajo el paradigma del modelo en estrella (tablas de dimensiones y hechos) listos para la capa de presentación.
* `dimFactequipos.py` y `FactHistoricoequipos.py`
* `dimfactjugadores.py` y `factHistorico_jugadores.py`
* *Librerías:* `pandas`, `os`.

---

## Flujo de Ejecución e Instrucciones de Uso

> **IMPORTANTE:** Para garantizar la integridad referencial y evitar errores de ejecución, **se debe completar el flujo completo de los EQUIPOS en primer lugar**, y posteriormente el flujo de los JUGADORES. Diversos scripts del módulo de jugadores realizan cruces de datos mapeando los archivos de los equipos.

Para generar correctamente los archivos CSV finales destinados a alimentar el modelo semántico, se han de ejecutar los scripts estrictamente en el siguiente orden secuencial:

### Fase I: Ingesta en Bruto
1.  **Ejecutar `estadisticas_partidos.py`**: Debe correrse año a año para las temporadas deseadas (en nuestro caso de la 2010 a la actual, se desconoce si funciona para más antiguas)
2.  **Ejecutar `estadisticas_jugadores.py`**: Requiere obligatoriamente que el script anterior haya finalizado, ya que consume dinámicamente las URLs de los partidos 

### Fase II: Enriquecimiento de Datos
3.  **Ejecutar `analisis_avanzado_equipos.py` y `analisis_avanzado_jugadores.py`**: Incorpora algoritmos para inyectar estadísticas avanzadas a los registros de cada encuentro.
4.  **Ejecutar `promedios_equipos.py` y `promedios_jugadores.py`**: Consolida las estadísticas medias de rendimiento divididas de forma independiente en archivos anuales.

### Fase III: Unificación e Integración Cruzada
5.  **Ejecutar `promedios_equipos_todas.py`**: Unifica el histórico completo de promedios de los clubes.
6.  **Completar la Carga de Equipos (`dimFactequipos.py`)**: Es imperativo generar las dimensiones de los equipos en este punto para evitar fallos de desalineación de nombres.
7.  **Ejecutar `promedios_jugadores_todas.py`**: Cruza los promedios globales de jugadores apoyándose en la tabla de dimensiones ya procesada de los equipos.
8.  **Ejecutar `historico_equipos.py` e `historico_jugadores.py`**: Unifica en un archivo los totales de cada equipo/jugador.

### Fase IV: Generación del Modelo en Estrella
9.  **Ejecutar scripts de Carga Restantes (`dimfactjugadores.py`, `FactHistoricoequipos.py`, `factHistorico_jugadores.py`)**: Divide la información de forma definitiva en entidades normativas de hechos y dimensiones óptimas para la carga de datos en Power BI.

---

## Notas de Configuración y Enriquecimiento Manual

* **Variables de Enriquecimiento Geográfico:** Los campos de datos relativos a `pais`, `ciudad` y la URL del `logo` institucional de los clubes no forman parte de las propiedades nativas extraídas por Web Scraping. Estas métricas visuales y descriptivas fueron añadidas e integradas de manera manual para potenciar el análisis de las interfaces. Cualquier réplica del flujo que desee contar con dichas columnas deberá hacerlo de forma manual.
* **Políticas de Rate Limiting:** Los scripts de extracción incorporan lógicas de tiempo aleatorias (`time.sleep`) y gestión de cabeceras de red para respetar las políticas de concurrencia y restricciones de tráfico de las plataformas origen.

---
Universidad Politécnica de Valencia | Escuela Técnica Superior de Ingeniería Informática (ETSINF)
