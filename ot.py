import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_dashboard_ot(archivo_subido):
    st.header("⏱️ Overtime (OT) Dashboard")
    
    try:
        # 1. Leer específicamente la hoja "OT" del Excel
        df_ot = pd.read_excel(archivo_subido, sheet_name="OT")
        
        # 2. Verificación de columnas necesarias
        cols_requeridas = ["Agent", "Hours", "Rate", "Var", "Date"]
        faltantes = [col for col in cols_requeridas if col not in df_ot.columns]
        if faltantes:
            st.error(f"The following columns are missing in the 'OT' sheet: {', '.join(faltantes)}")
            return
            
        # 3. Limpieza y conversión de datos matemáticos
        # Asegurarnos de que "Var" sea un número válido (cambiando "1,5" por "1.5")
        df_ot["Var"] = df_ot["Var"].astype(str).str.replace(',', '.').astype(float)
        
        # Asegurar que Hours y Rate sean numéricos
        df_ot["Hours"] = pd.to_numeric(df_ot["Hours"], errors='coerce').fillna(0)
        df_ot["Rate"] = pd.to_numeric(df_ot["Rate"], errors='coerce').fillna(0)
        
        # 4. LA FÓRMULA PRINCIPAL
        # Multiplicamos Hours * Rate * Var
        df_ot["Total Pay"] = df_ot["Hours"] * df_ot["Rate"] * df_ot["Var"]
        
        # 5. KPIs Generales
        total_pagado = df_ot["Total Pay"].sum()
        total_horas = df_ot["Hours"].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total OT Payments", f"${total_pagado:,.2f}")
        with col2:
            st.metric("Total Hours Paid", f"{total_horas:,.2f} hrs")
            
        st.divider()
        
        # 6. Gráficos Originales (Por Fecha y Agente)
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Total Paid by Date")
            df_date = df_ot.groupby("Date", as_index=False)["Total Pay"].sum()
            fig_date = px.bar(df_date, x="Date", y="Total Pay", title="Payment Distribution by Day", text_auto='.2s')
            st.plotly_chart(fig_date, use_container_width=True)
            
        with c2:
            st.subheader("Total Paid by Agent")
            df_agent = df_ot.groupby("Agent", as_index=False)["Total Pay"].sum().sort_values(by="Total Pay", ascending=False)
            fig_agent = px.bar(df_agent, x="Agent", y="Total Pay", color="Agent", title="Accumulated Payment by Agent")
            st.plotly_chart(fig_agent, use_container_width=True)
            
        st.divider()

        # ==========================================
        # NUEVO: ANÁLISIS POR MULTIPLICADOR (VAR)
        # ==========================================
        st.subheader("Analysis by Time Multiplier (Var)")
        c3, c4 = st.columns(2)
        
        # Agrupamos por 'Var' sumando las horas y el dinero
        df_var = df_ot.groupby("Var", as_index=False).agg({
            "Hours": "sum",
            "Total Pay": "sum"
        })
        
        with c3:
            # Para el gráfico, convertimos Var a texto agregándole una "x" (ej. "1.5x") para que se vea como categoría
            df_var_chart = df_var.copy()
            df_var_chart["Var_Text"] = df_var_chart["Var"].astype(str) + "x"
            
            fig_var = px.pie(
                df_var_chart, 
                names="Var_Text", 
                values="Total Pay", 
                title="Payment Proportion by Multiplier",
                hole=0.4
            )
            st.plotly_chart(fig_var, use_container_width=True)
            
        with c4:
            st.write("Numerical Breakdown:")
            # Renombramos columnas para que la tabla sea más legible en inglés
            df_var_display = df_var.rename(columns={"Hours": "Total Hours", "Total Pay": "Total Amount Paid ($)"})
            st.dataframe(df_var_display, use_container_width=True)

        st.divider()
        
        # ==========================================
        # 7. PREPARACIÓN DE DATOS PARA DESCARGA EXCEL
        # ==========================================
        st.subheader("📥 Export OT Results")
        st.write("Download the consolidated summaries ready for payment processing.")
        
        # DataFrames resumidos que irán en el Excel (columnas en inglés)
        df_excel_agent = df_ot.groupby("Agent", as_index=False).agg({"Hours": "sum", "Total Pay": "sum"}).rename(columns={"Hours": "Total Hours Worked"})
        df_excel_date = df_ot.groupby("Date", as_index=False).agg({"Hours": "sum", "Total Pay": "sum"}).rename(columns={"Hours": "Total Approved Hours"})
        df_excel_var = df_var.rename(columns={"Hours": "Total Hours", "Total Pay": "Total Amount Paid"})
        
        def generar_excel_ot(df_agentes, df_fechas, df_variables, df_crudo):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Guardar en diferentes pestañas con nombres en inglés
                df_agentes.to_excel(writer, index=False, sheet_name='Total by Agent')
                df_fechas.to_excel(writer, index=False, sheet_name='Total by Date')
                df_variables.to_excel(writer, index=False, sheet_name='Total by Var')
                df_crudo.to_excel(writer, index=False, sheet_name='Calculated Details')
                
                # Ajuste de ancho de columnas
                for sheet_name in ['Total by Agent', 'Total by Date', 'Total by Var', 'Calculated Details']:
                    worksheet = writer.sheets[sheet_name]
                    worksheet.set_column(0, 5, 20)
                    
            return output.getvalue()
            
        # Generar el archivo pasándole la nueva tabla de variables
        excel_resultados_ot = generar_excel_ot(df_excel_agent, df_excel_date, df_excel_var, df_ot)
        
        # Botón de descarga traducido
        st.download_button(
            label="Download OT Results (Excel)",
            data=excel_resultados_ot,
            file_name="OT_Results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except ValueError:
        st.error("⚠️ The uploaded file does not contain a sheet named 'OT'. Check your Excel file.")
    except Exception as e:
        st.error(f"An unexpected error occurred while processing the information: {e}")
