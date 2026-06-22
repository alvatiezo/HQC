import streamlit as st
import pandas as pd

def mostrar_master_dashboard(archivo):
    st.header("📈 Executive Master Dashboard")
    
    # 1. Procesar Bonos
    df_bonus = pd.read_excel(archivo, sheet_name="Bonus")
    df_bonus = df_bonus[df_bonus["Status"].astype(str).str.lower() == "yes"]
    total_bonus = df_bonus["Amount"].sum()
    
    # 2. Procesar OT
    df_ot = pd.read_excel(archivo, sheet_name="OT")
    df_ot["Var"] = df_ot["Var"].astype(str).str.replace(',', '.').astype(float)
    df_ot["Total OT"] = df_ot["Hours"] * df_ot["Rate"] * df_ot["Var"]
    total_ot_pay = df_ot["Total OT"].sum()
    total_ot_hours = df_ot["Hours"].sum()
    
    # 3. Procesar Double Pay
    df_dp = pd.read_excel(archivo, sheet_name="Double Pay")
    df_dp["Total DP"] = df_dp["Hours"] * df_dp["Rate"]
    total_dp_pay = df_dp["Total DP"].sum()
    total_dp_hours = df_dp["Hours"].sum()

    # --- RENDERIZADO DE KPIs ---
    st.subheader("Financial Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Bonus Paid", f"${total_bonus:,.2f}")
    c2.metric("Total OT Paid", f"${total_ot_pay:,.2f}")
    c3.metric("Total Double Pay", f"${total_dp_pay:,.2f}")
    
    c4, c5 = st.columns(2)
    c4.metric("Total OT Hours", f"{total_ot_hours:,.2f} hrs")
    c5.metric("Total DP Hours", f"{total_dp_hours:,.2f} hrs")

    # --- RENDERIZADO DE DETALLES ---
    st.divider()
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("**Bonus by Account**")
        st.dataframe(df_bonus.groupby("Account")["Amount"].sum(), use_container_width=True)
        st.write("**OT by Multiplier (Var)**")
        st.dataframe(df_ot.groupby("Var")["Total OT"].sum(), use_container_width=True)
        
    with col_b:
        st.write("**Double Pay by Account**")
        st.dataframe(df_dp.groupby("Account")["Total DP"].sum(), use_container_width=True)
        st.write("**Bonus by Type**")
        st.dataframe(df_bonus.groupby("Bonus")["Amount"].sum(), use_container_width=True)
