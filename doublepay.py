import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_dashboard_doublepay(archivo_subido):
    st.header("💵 Double Pay Dashboard")
    
    try:
        # 1. Cargar hoja específica
        df_dp = pd.read_excel(archivo_subido, sheet_name="Double Pay")
        
        # 2. Validación de columnas
        cols_requeridas = ["Account", "Agent", "Hours", "Rate"]
        if not all(col in df_dp.columns for col in cols_requeridas):
            st.error(f"Missing columns. Please ensure your 'Double Pay' sheet has: {', '.join(cols_requeridas)}")
            return
            
        # 3. Limpieza y Cálculos
        df_dp["Hours"] = pd.to_numeric(df_dp["Hours"], errors='coerce').fillna(0)
        df_dp["Rate"] = pd.to_numeric(df_dp["Rate"], errors='coerce').fillna(0)
        df_dp["Total Pay"] = df_dp["Hours"] * df_dp["Rate"]
        
        # 4. KPIs
        total_pagado = df_dp["Total Pay"].sum()
        total_horas = df_dp["Hours"].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("Total General to Pay", f"${total_pagado:,.2f}")
        c2.metric("Total Hours Paid", f"{total_horas:,.2f} hrs")
        
        st.divider()
        
        # 5. Visualización
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("Total Pay by Account")
            df_acc = df_dp.groupby("Account", as_index=False)["Total Pay"].sum()
            fig_acc = px.bar(df_acc, x="Account", y="Total Pay", color="Account", title="Payment by Account")
            st.plotly_chart(fig_acc, use_container_width=True)
            
        with col_b:
            st.subheader("Details by Agent")
            df_agent = df_dp.groupby("Agent", as_index=False).agg({"Hours": "sum", "Total Pay": "sum"})
            df_agent = df_agent.rename(columns={"Hours": "Total Hours", "Total Pay": "Total Amount ($)"})
            st.dataframe(df_agent, use_container_width=True, hide_index=True)
            
        # 6. Descarga
        st.divider()
        st.subheader("📥 Export Double Pay Results")
        
        def generar_excel():
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_acc.to_excel(writer, index=False, sheet_name='Total by Account')
                df_agent.to_excel(writer, index=False, sheet_name='Total by Agent')
                df_dp.to_excel(writer, index=False, sheet_name='Raw Data')
            return output.getvalue()
            
        st.download_button(
            label="Download Double Pay Results (Excel)",
            data=generar_excel(),
            file_name="Double_Pay_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"Error processing 'Double Pay' sheet: {e}")
