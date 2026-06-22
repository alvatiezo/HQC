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
        # 7. PREPARACIÓN DE DATOS
