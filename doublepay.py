import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_dashboard_doublepay(archivo_subido):
    st.header("💵 Double Pay Dashboard")
    
    try:
        # 1. Leer específicamente la hoja "Double Pay" del Excel
        df_dp = pd.read_excel(archivo_subido, sheet_name="Double Pay")
        
        # 2. Verificación de columnas necesarias según tu estructura
        cols_requeridas = ["Date", "Account", "Agent", "Hours", "Rate"]
        faltantes = [col for col in cols_requeridas if col not in df_dp.columns]
        if faltantes:
            st.error(f"The following columns are missing in the 'Double Pay' sheet: {', '.join(faltantes)}")
            return
            
        # 3. Limpieza y conversión de datos matemáticos
        # Aseguramos que Hours y Rate sean numéricos
        df_dp["Hours"] = pd.to_numeric(df_dp["Hours"], errors='coerce').fillna(0)
        df_dp["Rate"] = pd.to_numeric(df_dp["Rate"], errors='coerce').fillna(0)
        
        # 4. LA FÓRMULA PRINCIPAL
        # Multiplicamos Hours * Rate
        df_dp["Total Pay"] = df_dp["Hours"] * df_dp["Rate"]
        
        # 5. KPIs Generales
        total_pagado = df_dp["Total Pay"].sum()
        total_horas = df_dp["Hours"].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Grand Total to Pay", f"${total_pagado:,.2f}")
        with col2:
            st.metric("Total Hours Paid", f"{total_horas:,.2f} hrs")
            
        st.divider()
        
        # 6. Gráficos y Desglose
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Total to Pay by Account")
            # Agrupar por Account sumando el Total Pay
            df_account = df_dp.groupby("Account", as_index=False)["Total Pay"].sum().sort_values(by="Total Pay", ascending=False)
            
            fig_account = px.bar(
                df_account, 
                x="Account", 
                y="Total Pay", 
                color="Account",
                title="Payment Distribution by Account", 
                text_auto='.2s'
            )
            st.plotly_chart(fig_account, use_container_width=True)
            
        with c2:
            st.subheader("Total Hours and Amount by Agent")
            # Agrupar por Agente sumando Horas y Total a Pagar
            df_agent_summary = df_dp.groupby("Agent", as_index=False).agg({
                "Hours": "sum",
                "Total Pay": "sum"
            }).sort_values(by="Total Pay", ascending=False)
            
            # Renombramos columnas para mostrarlas limpias en la pantalla
            df_agent_display = df_agent_summary.rename(columns={
                "Hours": "Total Hours",
                "Total Pay": "Total Amount ($)"
            })
            
            # Mostramos la tabla directamente (hide_index quita los números de fila)
            st.dataframe(df_agent_display, use_container_width=True, hide_index=True)
            
        st.divider()
        
        # ==========================================
        # 7. PREPARACIÓN DE DATOS PARA DESCARGA EXCEL
        # ==========================================
        st.subheader("📥 Export Double Pay Results")
        st.write("Download the consolidated summaries.")
        
        # DataFrames para las pestañas del Excel
        # NUEVO: Ahora agrupa por Account sumando tanto Hours como Total Pay
        df_excel_account = df_dp.groupby("Account", as_index=False).agg({
            "Hours": "sum",
            "Total Pay": "sum"
        }).rename(columns={"Hours": "Total Hours", "Total Pay": "Total Amount Paid"})
        
        df_excel_agent = df_dp.groupby("Agent", as_index=False).agg({
            "Hours": "sum", 
            "Total Pay": "sum"
        }).rename(columns={"Hours": "Total Hours", "Total Pay": "Total Amount Paid"})
        
        def generar_excel_dp(df_acc, df_ag, df_raw):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Guardar en diferentes pestañas en inglés
                df_acc.to_excel(writer, index=False, sheet_name='Total by Account')
                df_ag.to_excel(writer, index=False, sheet_name='Total by Agent')
                df_raw.to_excel(writer, index=False, sheet_name='Calculated Details')
                
                # Ajuste de ancho de columnas
                for sheet in ['Total by Account', 'Total by Agent', 'Calculated Details']:
                    worksheet = writer.sheets[sheet]
                    worksheet.set_column(0, 5, 20)
                    
            return output.getvalue()
            
        # Generar el archivo final
        excel_dp = generar_excel_dp(df_excel_account, df_excel_agent, df_dp)
        
        # Botón de descarga
        st.download_button(
            label="Download Double Pay Results (Excel)",
            data=excel_dp,
            file_name="Double_Pay_Results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except ValueError:
        st.error("⚠️ The uploaded file does not contain a sheet named 'Double Pay'. Check your Excel file.")
    except Exception as e:
        st.error(f"An unexpected error occurred while processing the information: {e}")
