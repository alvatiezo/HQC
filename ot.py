import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_dashboard_ot(archivo_subido):
    st.header("⏱️ Dashboard de Horas Extra (OT)")
    
    try:
        # 1. Leer específicamente la hoja "OT" del Excel
        df_ot = pd.read_excel(archivo_subido, sheet_name="OT")
        
        # 2. Verificación de columnas necesarias
        cols_requeridas = ["Agent", "Hours", "Rate", "Var", "Date"]
        faltantes = [col for col in cols_requeridas if col not in df_ot.columns]
        if faltantes:
            st.error(f"Faltan las siguientes columnas en la hoja 'OT': {', '.join(faltantes)}")
            return
            
        # 3. Limpieza y conversión de datos matemáticos
        # Asegurarnos de que "Var" sea un número válido (cambiando "1,5" por "1.5")
        df_ot["Var"] = df_ot["Var"].astype(str).str.replace(',', '.').astype(float)
        
        # Asegurar que Hours y Rate sean numéricos
        df_ot["Hours"] = pd.to_numeric(df_ot["Hours"], errors='coerce').fillna(0)
        df_ot["Rate"] = pd.to_numeric(df_ot["Rate"], errors='coerce').fillna(0)
        
        # 4. LA FÓRMULA PRINCIPAL
        # Multiplicamos Hours * Rate * Var
        df_ot["Total a Pagar"] = df_ot["Hours"] * df_ot["Rate"] * df_ot["Var"]
        
        # 5. KPIs Generales
        total_pagado = df_ot["Total a Pagar"].sum()
        total_horas = df_ot["Hours"].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total General de Pagos (OT)", f"${total_pagado:,.2f}")
        with col2:
            st.metric("Cantidad de Horas Pagadas", f"{total_horas:,.2f} hrs")
            
        st.divider()
        
        # 6. Gráficos Originales (Por Fecha y Agente)
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Total Pagado por Fecha")
            df_date = df_ot.groupby("Date", as_index=False)["Total a Pagar"].sum()
            fig_date = px.bar(df_date, x="Date", y="Total a Pagar", title="Distribución de Pagos por Día", text_auto='.2s')
            st.plotly_chart(fig_date, use_container_width=True)
            
        with c2:
            st.subheader("Total Pagado por Agente")
            df_agent = df_ot.groupby("Agent", as_index=False)["Total a Pagar"].sum().sort_values(by="Total a Pagar", ascending=False)
            fig_agent = px.bar(df_agent, x="Agent", y="Total a Pagar", color="Agent", title="Pago Acumulado por Agente")
            st.plotly_chart(fig_agent, use_container_width=True)
            
        st.divider()

        # ==========================================
        # NUEVO: ANÁLISIS POR MULTIPLICADOR (VAR)
        # ==========================================
        st.subheader("Análisis por Multiplicador de Tiempo (Var)")
        c3, c4 = st.columns(2)
        
        # Agrupamos por 'Var' sumando las horas y el dinero
        df_var = df_ot.groupby("Var", as_index=False).agg({
            "Hours": "sum",
            "Total a Pagar": "sum"
        })
        
        with c3:
            # Para el gráfico, convertimos Var a texto agregándole una "x" (ej. "1.5x") para que se vea como categoría
            df_var_chart = df_var.copy()
            df_var_chart["Var_Text"] = df_var_chart["Var"].astype(str) + "x"
            
            fig_var = px.pie(
                df_var_chart, 
                names="Var_Text", 
                values="Total a Pagar", 
                title="Proporción del Pago por Multiplicador",
                hole=0.4
            )
            st.plotly_chart(fig_var, use_container_width=True)
            
        with c4:
            st.write("Desglose Numérico:")
            # Renombramos columnas para que la tabla sea más legible
            df_var_display = df_var.rename(columns={"Hours": "Total Horas", "Total a Pagar": "Monto Total Pagado ($)"})
            st.dataframe(df_var_display, use_container_width=True)

        st.divider()
        
        # ==========================================
        # 7. PREPARACIÓN DE DATOS PARA DESCARGA EXCEL
        # ==========================================
        st.subheader("📥 Exportar Resultados de Horas Extra")
        st.write("Descarga los resúmenes consolidados listos para procesar los pagos.")
        
        # DataFrames resumidos que irán en el Excel
        df_excel_agent = df_ot.groupby("Agent", as_index=False).agg({"Hours": "sum", "Total a Pagar": "sum"}).rename(columns={"Hours": "Total Horas Trabajadas"})
        df_excel_date = df_ot.groupby("Date", as_index=False).agg({"Hours": "sum", "Total a Pagar": "sum"}).rename(columns={"Hours": "Total Horas Aprobadas"})
        df_excel_var = df_var.rename(columns={"Hours": "Total Horas", "Total a Pagar": "Monto Total Pagado"})
        
        def generar_excel_ot(df_agentes, df_fechas, df_variables, df_crudo):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Guardar en diferentes pestañas (Ahora son 4)
                df_agentes.to_excel(writer, index=False, sheet_name='Total por Agente')
                df_fechas.to_excel(writer, index=False, sheet_name='Total por Fecha')
                df_variables.to_excel(writer, index=False, sheet_name='Total por Var')
                df_crudo.to_excel(writer, index=False, sheet_name='Detalle Calculado')
                
                # Ajuste de ancho de columnas
                for sheet_name in ['Total por Agente', 'Total por Fecha', 'Total por Var', 'Detalle Calculado']:
                    worksheet = writer.sheets[sheet_name]
                    worksheet.set_column(0, 5, 20)
                    
            return output.getvalue()
            
        # Generar el archivo pasándole la nueva tabla de variables
        excel_resultados_ot = generar_excel_ot(df_excel_agent, df_excel_date, df_excel_var, df_ot)
        
        # Botón de descarga
        st.download_button(
            label="Descargar Resultados OT (Excel)",
            data=excel_resultados_ot,
            file_name="Resultados_Horas_Extra.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except ValueError:
        st.error("⚠️ El archivo subido no contiene una pestaña llamada 'OT'. Verifica tu Excel.")
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al procesar la información: {e}")
