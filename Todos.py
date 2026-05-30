# -*- coding: utf-8 -*-
import pandas as pd
import os

# --- RUTAS ---
ruta_carpeta = r'C:\Users\Jorge\Desktop\TFG\Datos\jugadores\Promedios_jugadores'
ruta_archivo = os.path.join(ruta_carpeta, 'Fact_Jugadores_Temporadas.csv')

def generar_fase_todas_jugadores():
    print(f"📖 Leyendo estadísticas de jugadores desde: {ruta_archivo}")
    if not os.path.exists(ruta_archivo):
        print("❌ Error: No se encuentra el archivo Fact_Jugadores_Temporadas.csv.")
        return

    try:
        # Cargamos el archivo respetando tus separadores
        df = pd.read_csv(ruta_archivo, sep=';', encoding='utf-8-sig', decimal=',', dtype=str)
        df.columns = [c.strip() for c in df.columns]
        
        # Función auxiliar para convertir columnas a números flotantes de forma segura
        def n(col, fila_df):
            val = fila_df.get(col, 0)
            try: return float(str(val).replace(',', '.'))
            except: return 0.0

        print("⚙️ Calculando agregados globales ('TODAS') por jugador, temporada y equipo...")
        
        lista_todas = []
        
        # Agrupamos por Temporada, Jugador y Equipo (por si un jugador fue traspasado a mitad de año)
        agrupacion_columnas = ['ID Temporada', 'ID Jugador', 'ID_Equipo']
        
        for (temporada, id_jugador, id_equipo), sub_df in df.groupby(agrupacion_columnas):
            
            # Inicializamos acumuladores de volúmenes absolutos
            pj_total = 0.0
            pts_abs = 0.0; asist_abs = 0.0; ro_abs = 0.0; rd_abs = 0.0; reb_abs = 0.0
            robos_abs = 0.0; perd_abs = 0.0; tapones_abs = 0.0; tapones_rec_abs = 0.0
            faltas_c_abs = 0.0; faltas_r_abs = 0.0; val_abs = 0.0; mas_menos_abs = 0.0
            minutos_abs = 0.0
            
            # Tiros totales para porcentajes exactos
            t2a_abs = 0.0; t2i_abs = 0.0
            t3a_abs = 0.0; t3i_abs = 0.0
            t1a_abs = 0.0; t1i_abs = 0.0
            
            # Ponderados simples para ratios ya avanzados de fase
            oreb_pct_pond = 0.0; dreb_pct_pond = 0.0
            
            # Datos fijos de texto (Nombre largo de Equipo y Nombre de Jugador)
            equipo_nombre = str(sub_df.iloc[0].get('Equipo', '')).strip()
            nombre_jugador = str(sub_df.iloc[0].get('Nombre', '')).strip()

            # 1. Pasamos promedios a volúmenes absolutos multiplicando por los partidos jugados en esa fase
            for _, fila in sub_df.iterrows():
                pj = n('Partidos_Jugados', fila)
                if pj == 0: continue
                
                pj_total += pj
                pts_abs += n('Puntos', fila) * pj
                asist_abs += n('Asistencias', fila) * pj
                ro_abs += n('Reb_Off', fila) * pj
                rd_abs += n('Reb_Def', fila) * pj
                reb_abs += n('Rebotes', fila) * pj
                robos_abs += n('Robos', fila) * pj
                perd_abs += n('Perdidas', fila) * pj
                tapones_abs += n('Tapones', fila) * pj
                tapones_rec_abs += n('Tapones_Recibidos', fila) * pj
                faltas_c_abs += n('Faltas_Cometidas', fila) * pj
                faltas_r_abs += n('Faltas_Recibidas', fila) * pj
                val_abs += n('Valoracion_PIR', fila) * pj
                mas_menos_abs += n('Mas_Menos', fila) * pj
                minutos_abs += n('Minutos_Dec', fila) * pj
                
                t2a_abs += n('T2a', fila) * pj
                t2i_abs += n('T2i', fila) * pj
                t3a_abs += n('T3a', fila) * pj
                t3i_abs += n('T3i', fila) * pj
                t1a_abs += n('T1a', fila) * pj
                
                if 'T1i' in fila:
                    t1i_abs += n('T1i', fila) * pj

                # Avanzados ponderados por partidos
                oreb_pct_pond += n('OREB%', fila) * pj
                dreb_pct_pond += n('DREB%', fila) * pj

            if pj_total == 0: continue

            # 2. Re-calculamos promedios por partido y eficiencias avanzadas blindadas contra ceros
            t2_pct = round((t2a_abs / replace_zero(t2i_abs)) * 100, 2)
            t3_pct = round((t3a_abs / replace_zero(t3i_abs)) * 100, 2)
            t1_pct = round((t1a_abs / replace_zero(t1i_abs)) * 100, 2)
            
            tca_abs = t2a_abs + t3a_abs
            tci_abs = t2i_abs + t3i_abs
            
            efg_pct = round(((tca_abs + 0.5 * t3a_abs) / replace_zero(tci_abs)) * 100, 2)
            ts_pct = round((pts_abs / replace_zero(2 * (tci_abs + 0.44 * t1i_abs))) * 100, 2)
            
            ast_to_ratio = round(asist_abs / replace_zero(perd_abs), 2)
            ppm_final = round(pts_abs / replace_zero(minutos_abs), 2)
            
            # Intentos de tiro (Ratios de volumen de tiro)
            p2ar_final = round(t2i_abs / replace_zero(tci_abs), 3)
            p3ar_final = round(t3i_abs / replace_zero(tci_abs), 3)
            p1ar_final = round(t1i_abs / replace_zero(tci_abs), 3)
            
            # Protección por si el jugador tiene 0 puntos anotados
            pct_pts_t2 = round((t2a_abs * 2 / replace_zero(pts_abs)) * 100, 2)
            pct_pts_t3 = round((t3a_abs * 3 / replace_zero(pts_abs)) * 100, 2)
            pct_pts_t1 = round((t1a_abs / replace_zero(pts_abs)) * 100, 2)
            
            # Fórmula oficial de Game Score adaptada a volúmenes y dividida por partidos
            gs_sum = (pts_abs + 0.4 * tca_abs - 0.7 * tci_abs - 0.4 * (t1i_abs - t1a_abs) + 
                      0.7 * ro_abs + 0.3 * rd_abs + robos_abs + 0.7 * asist_abs + 
                      0.7 * tapones_abs - 0.4 * faltas_c_abs - perd_abs)
            game_score_final = round(gs_sum / pj_total, 2)

            # CORRECCIÓN: Guardamos los valores directamente como tipos numéricos puros (sin str)
            fila_todas = {
                'ID Temporada': temporada,
                'Nombre': nombre_jugador if 'Nombre' in df.columns else '',
                'ID Jugador': id_jugador,
                'Equipo': equipo_nombre,
                'ID_Equipo': id_equipo,
                'Fase': 'TODAS',
                'Partidos_Jugados': int(pj_total),
                'Puntos': round(pts_abs / pj_total, 2),
                'Asistencias': round(asist_abs / pj_total, 2),
                'Reb_Off': round(ro_abs / pj_total, 2),
                'Reb_Def': round(rd_abs / pj_total, 2),
                'Rebotes': round(reb_abs / pj_total, 2),
                'OREB%': round(oreb_pct_pond / pj_total, 2),
                'DREB%': round(dreb_pct_pond / pj_total, 2),
                'T2a': round(t2a_abs / pj_total, 2),
                'T2i': round(t2i_abs / pj_total, 2),
                'T2%': t2_pct,
                'T3a': round(t3a_abs / pj_total, 2),
                'T3i': round(t3i_abs / pj_total, 2),
                'T3%': t3_pct,
                'T1a': round(t1a_abs / pj_total, 2),
                'T1i': round(t1i_abs / pj_total, 2),
                'T1%': t1_pct,
                '%_Pts_T2': pct_pts_t2,
                '%_Pts_T3': pct_pts_t3,
                '%_Pts_T1': pct_pts_t1,
                'Robos': round(robos_abs / pj_total, 2),
                'Perdidas': round(perd_abs / pj_total, 2),
                'Tapones': round(tapones_abs / pj_total, 2),
                'Tapones_Recibidos': round(tapones_rec_abs / pj_total, 2),
                'Faltas_Cometidas': round(faltas_c_abs / pj_total, 2),
                'Faltas_Recibidas': round(faltas_r_abs / pj_total, 2),
                'Valoracion_PIR': round(val_abs / pj_total, 2),
                'Mas_Menos': round(mas_menos_abs / pj_total, 2),
                'eFG%': efg_pct,
                'TS%': ts_pct,
                '2PAr': p2ar_final,
                '3PAr': p3ar_final,
                '1PAr': p1ar_final,
                'AST_TO_Ratio': ast_to_ratio,
                'PPM': ppm_final,
                'Game_Score': game_score_final,
                'Minutos_Dec': round(minutos_abs / pj_total, 2)
            }
            lista_todas.append(fila_todas)
            
        # 3. Convertimos las nuevas filas calculadas a un DataFrame
        df_todas = pd.DataFrame(lista_todas)
        
        print("🔗 Unificando y formateando tipos numéricos de forma homogénea...")
        # Pasamos los datos originales a numéricos para que no haya colisión de tipos (Texto vs Float)
        cols_excluidas = ['ID Temporada', 'Nombre', 'ID Jugador', 'Equipo', 'ID_Equipo', 'Fase']
        for col in df.columns:
            if col not in cols_excluidas:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)
                df_todas[col] = pd.to_numeric(df_todas[col], errors='coerce').fillna(0.0)
                
                # Mantenemos limpia la estética de la columna de partidos jugados
                if col == 'Partidos_Jugados':
                    df[col] = df[col].astype(int)
                    df_todas[col] = df_todas[col].astype(int)

        # Combinamos el DataFrame original con las nuevas filas globales calculadas
        df_final = pd.concat([df, df_todas], ignore_index=True)
        
        # Nos aseguramos de mantener el mismo orden exacto de columnas que el archivo original
        df_final = df_final[df.columns]
        
        # Ordenamos las filas para que queden agrupadas de forma perfecta para análisis
        df_final = df_final.sort_values(by=['ID Temporada', 'ID_Equipo', 'ID Jugador', 'Fase'])
        
        # Guardamos machacando el archivo original traduciendo de forma estricta los puntos a comas
        df_final.to_csv(ruta_archivo, index=False, sep=';', encoding='utf-8-sig', decimal=',')
        
        print(f"\n✅ ¡Completado con éxito!")
        print(f"📊 Se han calculado e insertado {len(df_todas)} filas nuevas con Fase = 'TODAS'")
        print(f"🔤 Formato de comas (,) inyectado correctamente en todos los decimales.")
        print(f"💾 El archivo Fact_Jugadores_Temporadas.csv ha sido sobrescrito en: {ruta_archivo}")

    except Exception as e:
        print(f"❌ Error al procesar el cálculo de fases en jugadores: {e}")

def replace_zero(val):
    return val if val != 0 else 1.0

if __name__ == "__main__":
    generar_fase_todas_jugadores()