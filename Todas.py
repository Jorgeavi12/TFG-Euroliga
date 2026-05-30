# -*- coding: utf-8 -*-
import pandas as pd
import os

# --- RUTAS ---
ruta_carpeta = r'C:\Users\Jorge\Desktop\TFG\Datos\equipos\Promedios_equipos'
ruta_archivo = os.path.join(ruta_carpeta, 'Fact_Estadisticas_Equipos.csv')

def generar_fase_todas_y_rebotes_equipos():
    print(f"📖 Leyendo estadísticas de equipos desde: {ruta_archivo}")
    if not os.path.exists(ruta_archivo):
        print("❌ Error: No se encuentra el archivo Fact_Estadisticas_Equipos.csv.")
        return

    try:
        # Cargamos el archivo respetando tus separadores
        df = pd.read_csv(ruta_archivo, sep=';', encoding='utf-8-sig', decimal=',', dtype=str)
        df.columns = [c.strip() for c in df.columns]
        
        # Función auxiliar interna para convertir columnas a números flotantes de forma segura
        def n(col, fila_df):
            val = fila_df.get(col, 0)
            try: return float(str(val).replace(',', '.'))
            except: return 0.0

        print("⚙️ Calculando agregados globales ('TODAS') por equipo y temporada...")
        
        lista_todas = []
        
        # Agrupamos los datos reales por Temporada e ID_Equipo para construir las filas 'TODAS'
        for (temporada, id_equipo), sub_df in df.groupby(['Temporada', 'ID_Equipo']):
            
            # Inicializamos acumuladores para volúmenes absolutos
            partidos_totales = 0.0
            w_totales = 0.0
            l_totales = 0.0
            
            # Totales absolutos para promedios por partido
            pts_abs = 0.0; asist_abs = 0.0; perd_abs = 0.0; robos_abs = 0.0; tapones_abs = 0.0
            ro_abs = 0.0; rd_abs = 0.0; val_abs = 0.0; pts_perm_abs = 0.0
            
            # Totales absolutos de tiros y estadísticas de volumen (Equipo_FGA, etc.)
            t2a_abs = 0.0; t2i_abs = 0.0; t3a_abs = 0.0; t3i_abs = 0.0; t1a_abs = 0.0; t1i_abs = 0.0
            fga_abs = 0.0; fta_abs = 0.0; tov_abs = 0.0
            
            # Ritmo y ratings ponderados
            pace_ponderado = 0.0; ortg_ponderado = 0.0; drtg_ponderado = 0.0
            
            # Entrenador: nos quedamos con el último registrado en la temporada por si cambió
            entrenador_final = str(sub_df.iloc[-1].get('Entrenador', '')).strip()

            # 1. Pasamos los promedios a volúmenes absolutos multiplicando por los partidos de cada fase
            for _, fila in sub_df.iterrows():
                pj = n('Partidos', fila)
                if pj == 0: continue
                
                partidos_totales += pj
                w_totales += n('W', fila)
                l_totales += n('L', fila)
                
                pts_abs += n('PPG', fila) * pj
                asist_abs += n('Asist_PG', fila) * pj
                perd_abs += n('Perd_PG', fila) * pj
                robos_abs += n('Robos_PG', fila) * pj
                tapones_abs += n('Tapones_PG', fila) * pj
                ro_abs += n('Reb_Off_PG', fila) * pj
                rd_abs += n('Reb_Def_PG', fila) * pj
                val_abs += n('Val_PG', fila) * pj
                pts_perm_abs += n('Pts_Permitidos_PG', fila) * pj
                
                t2a_abs += n('T2a_PG', fila) * pj
                t2i_abs += n('T2i_PG', fila) * pj
                t3a_abs += n('T3a_PG', fila) * pj
                t3i_abs += n('T3i_PG', fila) * pj
                t1a_abs += n('T1a_PG', fila) * pj
                t1i_abs += n('T1i_PG', fila) * pj
                
                fga_abs += n('Equipo_FGA', fila) * pj
                fta_abs += n('Equipo_FTA', fila) * pj
                tov_abs += n('Equipo_TOV', fila) * pj
                
                pace_ponderado += n('Pace_Medio', fila) * pj
                ortg_ponderado += n('ORTG', fila) * pj
                drtg_ponderado += n('DRTG', fila) * pj

            if partidos_totales == 0: continue

            # 2. Re-calculamos promedios y fórmulas avanzadas sobre el total anual de partidos
            pct_wins = round((w_totales / partidos_totales) * 100, 2)
            
            t2_pct = round((t2a_abs / replace_zero(t2i_abs)) * 100, 2)
            t3_pct = round((t3a_abs / replace_zero(t3i_abs)) * 100, 2)
            t1_pct = round((t1a_abs / replace_zero(t1i_abs)) * 100, 2)
            
            tca_abs = t2a_abs + t3a_abs
            tci_abs = t2i_abs + t3i_abs
            
            efg_pct = round(((tca_abs + 0.5 * t3a_abs) / replace_zero(tci_abs)) * 100, 2)
            ts_pct = round((pts_abs / replace_zero(2 * (tci_abs + 0.44 * t1i_abs))) * 100, 2)
            
            ast_to_ratio = round(asist_abs / replace_zero(perd_abs), 2)
            
            # Reparto de puntos
            pct_pts_triple = round((t3a_abs * 3 / replace_zero(pts_abs)) * 100, 2)
            pct_pts_dos = round((t2a_abs * 2 / replace_zero(pts_abs)) * 100, 2)
            pct_pts_tl = round((t1a_abs / replace_zero(pts_abs)) * 100, 2)
            
            # Avanzados de Ritmo y Ratings
            pace_medio = round(pace_ponderado / partidos_totales, 2)
            ortg_final = round(ortg_ponderado / partidos_totales, 2)
            drtg_final = round(drtg_ponderado / partidos_totales, 2)
            netrtg_final = round(ortg_final - drtg_final, 2)
            
            three_par_final = round(t3i_abs / replace_zero(tci_abs), 3)
            ftr_final = round(t1i_abs / replace_zero(tci_abs), 3)

            # Promedios finales por partido para la fila TODAS
            reb_off_pg_todas = round(ro_abs / partidos_totales, 2)
            reb_def_pg_todas = round(rd_abs / partidos_totales, 2)
            rebotes_pg_todas = round(reb_off_pg_todas + reb_def_pg_todas, 2)

            # CORRECCIÓN: Guardamos los valores numéricos directamente (sin meter str)
            fila_todas = {
                'Temporada': temporada,
                'ID_Equipo': id_equipo,
                'Fase': 'TODAS',
                'Entrenador': entrenador_final,
                'Partidos': int(partidos_totales),
                'W': int(w_totales),
                'L': int(l_totales),
                '%_Wins': pct_wins,
                'PPG': round(pts_abs / partidos_totales, 2),
                'Asist_PG': round(asist_abs / partidos_totales, 2),
                'Perd_PG': round(perd_abs / partidos_totales, 2),
                'Robos_PG': round(robos_abs / partidos_totales, 2),
                'Tapones_PG': round(tapones_abs / partidos_totales, 2),
                'AST/TO_Ratio': ast_to_ratio,
                'AST%': round((asist_abs / replace_zero(tca_abs)) * 100, 2),
                'Reb_Off_PG': reb_off_pg_todas,
                'Reb_Def_PG': reb_def_pg_todas,
                'Rebotes': rebotes_pg_todas, 
                'REB%_Total': round(((ro_abs + rd_abs) / replace_zero(ro_abs + rd_abs + 1)) * 100, 2), 
                'Val_PG': round(val_abs / partidos_totales, 2),
                'T2a_PG': round(t2a_abs / partidos_totales, 2),
                'T2i_PG': round(t2i_abs / partidos_totales, 2),
                '%T2': t2_pct,
                'T3a_PG': round(t3a_abs / partidos_totales, 2),
                'T3i_PG': round(t3i_abs / partidos_totales, 2),
                '%T3': t3_pct,
                'T1a_PG': round(t1a_abs / partidos_totales, 2),
                'T1i_PG': round(t1i_abs / partidos_totales, 2),
                '%T1': t1_pct,
                '%_Pts_Triple': pct_pts_triple,
                '%_Pts_Dos': pct_pts_dos,
                '%_Pts_TL': pct_pts_tl,
                'Pace_Medio': pace_medio,
                'ORTG': ortg_final,
                'DRTG': drtg_final,
                'NetRTG': netrtg_final,
                'eFG%': efg_pct,
                'TS%': ts_pct,
                '3PAr': three_par_final, 
                'FTr': ftr_final,
                'ORB%': round(sum(n('ORB%', f) * n('Partidos', f) for _, f in sub_df.iterrows()) / partidos_totales, 2),
                'DRB%': round(sum(n('DRB%', f) * n('Partidos', f) for _, f in sub_df.iterrows()) / partidos_totales, 2),
                'Pts_Permitidos_PG': round(pts_perm_abs / partidos_totales, 2),
                'eFG%_Ol': round(sum(n('eFG%_Ol', f) * n('Partidos', f) for _, f in sub_df.iterrows()) / partidos_totales, 2),
                'TOV%_Ol': round(sum(n('TOV%_Ol', f) * n('Partidos', f) for _, f in sub_df.iterrows()) / partidos_totales, 2),
                'OREB%_Ol': round(sum(n('OREB%_Ol', f) * n('Partidos', f) for _, f in sub_df.iterrows()) / partidos_totales, 2),
                'FT/FGA_Ol': round(sum(n('FT/FGA_Ol', f) * n('Partidos', f) for _, f in sub_df.iterrows()) / partidos_totales, 3),
                'eFG_opp%_Ol': round(sum(n('eFG_opp%_Ol', f) * n('Partidos', f) for _, f in sub_df.iterrows()) / partidos_totales, 2),
                'TOV_opp%_Ol': round(sum(n('TOV_opp%_Ol', f) * n('Partidos', f) for _, f in sub_df.iterrows()) / partidos_totales, 2),
                'DREB%_Ol': round(sum(n('DREB%_Ol', f) * n('Partidos', f) for _, f in sub_df.iterrows()) / partidos_totales, 2),
                'FT/FGA_opp_Ol': round(sum(n('FT/FGA_opp_Ol', f) * n('Partidos', f) for _, f in sub_df.iterrows()) / partidos_totales, 3),
                'Equipo_FGA': round(fga_abs / partidos_totales, 2),
                'Equipo_FTA': round(fta_abs / partidos_totales, 2),
                'Equipo_TOV': round(tov_abs / partidos_totales, 2)
            }
            lista_todas.append(fila_todas)
            
        # 3. Convertimos las filas 'TODAS' en Dataframe
        df_todas = pd.DataFrame(lista_todas)
        
        print("🏀 Calculando la columna 'Rebotes' para las fases originales...")
        # Convertimos columnas de entrada a numérico para poder sumarlas en las filas originales
        reb_off_orig = pd.to_numeric(df['Reb_Off_PG'].str.replace(',', '.'), errors='coerce').fillna(0)
        reb_def_orig = pd.to_numeric(df['Reb_Def_PG'].str.replace(',', '.'), errors='coerce').fillna(0)
        
        # Asignamos la suma a la columna 'Rebotes' en el dataframe original
        df['Rebotes'] = (reb_off_orig + reb_def_orig).round(2)
        
        print("🔗 Unificando y formateando tipos numéricos de forma homogénea...")
        # Pasamos datos originales a numéricos para evitar que se mezclen textos y números
        cols_excluidas = ['Temporada', 'ID_Equipo', 'Fase', 'Entrenador']
        for col in df.columns:
            if col not in cols_excluidas:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)
                df_todas[col] = pd.to_numeric(df_todas[col], errors='coerce').fillna(0.0)
                
                # Columnas enteras por mantener el formato estético limpio
                if col in ['Partidos', 'W', 'L']:
                    df[col] = df[col].astype(int)
                    df_todas[col] = df_todas[col].astype(int)

        # Juntamos los dos bloques de datos de forma limpia
        df_final = pd.concat([df, df_todas], ignore_index=True)
        
        # --- RE-ORDENAMIENTO DE COLUMNAS ESTÉTICO ---
        columnas = list(df_final.columns)
        if 'Rebotes' in columnas:
            columnas.remove('Rebotes')
            pos_reb_def = columnas.index('Reb_Def_PG')
            columnas.insert(pos_reb_def + 1, 'Rebotes')
        df_final = df_final[columnas]
        
        # Ordenamos filas por Temporada, ID_Equipo y Fase
        df_final = df_final.sort_values(by=['Temporada', 'ID_Equipo', 'Fase'])
        
        # Guardamos machacando el archivo original traduciendo todos los decimales a coma
        df_final.to_csv(ruta_archivo, index=False, sep=';', encoding='utf-8-sig', decimal=',')
        
        print(f"\n✅ ¡Proceso completado con éxito!")
        print(f"📊 Fila 'TODAS' calculada uniformemente para cada equipo y año ({len(df_todas)} filas nuevas).")
        print(f"🏀 Formato de comas (,) aplicado estrictamente en todos los decimales.")
        print(f"💾 Archivo sobrescrito en: {ruta_archivo}")

    except Exception as e:
        print(f"❌ Error al procesar el archivo de equipos: {e}")

def replace_zero(val):
    return val if val != 0 else 1.0

if __name__ == "__main__":
    generar_fase_todas_y_rebotes_equipos()