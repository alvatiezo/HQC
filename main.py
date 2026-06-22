import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Importamos los módulos secundarios
import bonus 
import ot
import doublepay
import report_generator
import master_dashboard

# Configuración principal de la página
st.set_page_config(page_title="Dashboard Analítico", layout="wide")

# ==========================================
# 1. BARRA LATERAL - MENÚ DE NAVEGACIÓN
# ==========================================
st.sidebar.title("Navegación")
# Asegúrate de que esta lista tenga todos los nombres que usas en los elif
menu_opcion = st.sidebar.radio(
    "Select Module:",
    [
        "Dashboard Principal", 
        "Master Dashboard", 
        "Dashboard de Bonos", 
        "Dashboard de Horas Extra (OT)", 
        "Dashboard de Double Pay", 
        "Generate Master Report"
    ]
)

# ==========================================
# 2. ENCABEZADO Y SUBIDA DE ARCHIVO
# ==========================================
st.title("📊 Panel de Control y Reportes Automáticos")
st.write("Sube tu base de datos para visualizar las métricas y descargar informes personalizados.")

# Único uploader para todas las pantallas
archivo_subido = st.file_uploader("📥 Arrastra o sube tu archivo Excel (.xlsx)", type=["xlsx"])

if archivo_subido is not None:
    
    # --- RUTA 1: DASHBOARD PRINCIPAL ---
    if menu_opcion == "Dashboard Principal":
        try:
            df = pd.read_excel(archivo_subido)
            st.sidebar.header("Filtros Interactivos")
            
            if "Región" in df.columns:
                regiones_seleccionadas = st.sidebar.multiselect(
                    "Filtrar por Región:", options=df["Región"].unique(), default=df["Región"].unique()
                )
                df = df[df["Región"].isin(regiones_seleccionadas)]
                
            if "Vendedor" in df.columns:
                vendedores_seleccionados = st.sidebar.multiselect(
                    "Filtrar por Vendedor:", options=df["Vendedor"].unique(), default=df["Vendedor"].unique()
                )
                df = df[df["Vendedor"].isin(vendedores_seleccionados)]

            st.subheader("Resumen de Rendimiento")
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Total de Registros", len(df))
            with col2: 
                if "Venta Total" in df.columns: st.metric("Ingresos Totales", f"${df['Venta Total'].sum():,.2f}")
            with col3: 
                if "Cantidad" in df.columns: st.metric("Unidades Procesadas", f"{df['Cantidad'].sum()}")

            st.divider()

            col_graf1, col_graf2 = st.columns(2)
            with col_graf1:
                if "Región" in df.columns and "Venta Total" in df.columns:
                    df_region = df.groupby("Región", as_index=False)["Venta Total"].sum()
                    st.plotly_chart(px.bar(df_region, x="Región", y="Venta Total", title="Ventas por Región", color="Región"), use_container_width=True)
            with col_graf2:
                if "Vendedor" in df.columns and "Venta Total" in df.columns:
                    df_vendedor = df.groupby("Vendedor", as_index=False)["Venta Total"].sum()
                    st.plotly_chart(px.pie(df_vendedor, names="Vendedor", values="Venta Total", title="Participación Vendedor"), use_container_width=True)

            st.divider()
            st.subheader("Base de Datos (Filtrada)")
            st.dataframe(df, use_container_width=True)

            st.subheader("📥 Exportar Informe")
            def convertir_df_a_excel(dataframe):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    dataframe.to_excel(writer, index=False, sheet_name='Reporte Filtrado')
                return output.getvalue()
                
            st.download_button(
                label="Descargar Excel Filtrado", data=convertir_df_a_excel(df),
                file_name="Reporte_Dashboard.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Error en dashboard principal. {e}")
            
    # --- RUTA 2: DASHBOARD DE BONOS ---
    elif menu_opcion == "Dashboard de Bonos":
        bonus.mostrar_dashboard_bonus(archivo_subido)
        
    # --- RUTA 3: DASHBOARD DE HORAS EXTRA (OT) ---
    elif menu_opcion == "Dashboard de Horas Extra (OT)":
        ot.mostrar_dashboard_ot(archivo_subido)
    # --- RUTA 4: Double Pay ---
    elif menu_opcion == "Dashboard de Double Pay":
        doublepay.mostrar_dashboard_doublepay(archivo_subido)
    # ... (dentro de los bloques IF/ELIF)
    elif menu_opcion == "Generate Master Report":
        st.subheader("📊 Generate Master Excel Report")
        if st.button("Compile All Data & Download"):
            with st.spinner("Compiling report..."):
                master_data = report_generator.generar_reporte_compilado(archivo_subido)
                st.download_button(
                    label="Download Compiled Report",
                    data=master_data,
                    file_name="Master_Report_Consolidated.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.success("Report ready for download!")
    elif menu_opcion == "Master Dashboard":
        # Asegúrate de tener archivo_subido capturado del st.file_uploader
        if archivo_subido is not None:
            master_dashboard.mostrar_master_dashboard(archivo_subido)
        else:
            st.warning("Por favor, sube un archivo Excel primero.")
else:
    st.info("👆 Por favor, sube un archivo Excel en el recuadro superior para comenzar.")
