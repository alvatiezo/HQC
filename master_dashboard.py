import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_master_dashboard(archivo):
    st.header("📈 Executive Master Dashboard")
    
    # 1. CARGA Y PROCESAMIENTO DE DATOS
    try:
        # Cargar hojas
        df_bonus = pd.read_excel(archivo, sheet_name="Bonus")
        df_ot = pd.read_excel(archivo, sheet_name="OT")
        df_dp = pd.read_excel(archivo, sheet_name="Double Pay")
        
        # Limpieza OT
        df_ot["Var"] = df_ot["Var"].astype(str).str.replace(',', '.').astype(float)
        df_ot["Total OT"] = df_ot["Hours"] * df_ot["Rate"] * df_ot["Var"]
        
        # Limpieza DP
        df_dp["Total DP"] = df_dp["Hours"] * df_dp["Rate"]
        
        # Filtrar Bonos activos
        df_bonus_active = df_bonus[df_bonus["Status"].astype(str).str.lower() == "yes"]

        # 2. CÁLCULOS MAESTROS
        # Totales
        tot_bonus = df_bonus_active["Amount"].sum()
        tot_ot_pay = df_ot["Total OT"].sum()
        tot_ot_hours = df_ot["Hours"].sum()
        tot_dp_pay = df_dp["Total DP"].sum()
        tot_dp_hours = df_dp["Hours"].sum()

        # Agrupaciones
        bonus_by_acc = df_bonus_active.groupby("Account")["Amount"].sum().reset_index()
        bonus_by_type = df_bonus_active.groupby("Bonus")["Amount"].sum().reset_index()
        ot_by_var = df_ot.groupby("Var")["Total OT"].sum().reset_index()
        dp_by_acc = df_dp.groupby("Account").agg({"Total DP": "sum", "Hours": "sum"}).reset_index()

        # 3. RENDERIZADO DE KPIs (UI)
        st.subheader("Financial Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Bonus Paid", f"${tot_bonus:,.2f}")
        col2.metric("Total OT Paid", f"${tot_ot_pay:,.2f}")
        col3.metric("Total Double Pay", f"${tot_dp_pay:,.2f}")
        
        col4, col5 = st.columns(2)
        col4.metric("Total OT Hours", f"{tot_ot_hours:,.2f} hrs")
        col5.metric("Total DP Hours", f"{tot_dp_hours:,.2f} hrs")

        st.divider()

        # 4. GRÁFICOS INTERACTIVOS
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Bonus by Account**")
            st.plotly_chart(px.pie(bonus_by_acc, names="Account", values="Amount"), use_container_width=True)
        with c2:
            st.write("**OT Pay by Var**")
            st.plotly_chart(px.bar(ot_by_var, x="Var", y="Total OT", color="Var"), use_container_width=True)

        # 5. DESCARGA DE EXCEL (Compilado)
        st.divider()
        st.subheader("📥 Download Master Report")
        
        def generar_excel_maestro():
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Resumen Ejecutivo
                summary = pd.DataFrame({
                    "Metric": ["Total Bonus", "Total OT Paid", "Total OT Hours", "Total DP Paid", "Total DP Hours"],
                    "Value": [tot_bonus, tot_ot_pay, tot_ot_hours, tot_dp_pay, tot_dp_hours]
                })
                summary.to_excel(writer, index=False, sheet_name='Executive Summary')
                
                # Desgloses
                bonus_by_acc.to_excel(writer, index=False, sheet_name='Bonus by Account')
                bonus_by_type.to_excel(writer, index=False, sheet_name='Bonus by Type')
                ot_by_var.to_excel(writer, index=False, sheet_name='OT by Var')
                dp_by_acc.to_excel(writer, index=False, sheet_name='DP by Account')
            return output.getvalue()

        st.download_button(
            label="Download Master Executive Report (Excel)",
            data=generar_excel_maestro(),
            file_name="Master_Executive_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
