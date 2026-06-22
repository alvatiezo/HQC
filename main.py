import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Importamos el módulo secundario que maneja la hoja de bonos
import bonus 

# Configuración principal de la página
st.set_page_config(page_title="Dashboard HQC", layout="wide")

# ==========================================
# 1. BARRA LATERAL - MENÚ DE NAVEGACIÓN
# ==========================================
st.sidebar.title("Navegación")
menu_opcion = st.sidebar.radio(
    "Selecciona el módulo a visualizar:",
    ["Dashboard Principal", "Dashboard de Bonos"]
)

# ==========================================
# 2. ENCABEZADO Y SUBIDA DE ARCHIVO
# ==========================================
st.title("📊 Panel de Control y Reportes Automáticos")
st.write("Sube tu base de datos para visualizar las métricas y descargar informes personalizados.")

# El archivo subido se guarda en esta variable y sirve para cualquier pantalla que elijamos
archivo_subido = st.file_uploader("📥 Arrastra o sube tu archivo Excel (.xlsx)", type=["xlsx"])

if archivo_subido is not None:
    
    # ==========================================
    # RUTA 1: DASHBOARD PRINCIPAL
    # ==========================================
    if menu_opcion == "Dashboard Principal":
        try:
            # Leer la primera hoja del Excel por defecto para las ventas/datos generales
            df = pd.read_excel(archivo_subido)
            
            st.sidebar.header("Filtros Interactivos")
            
            # Filtros dinámicos en la barra lateral
            if "Región" in df.columns:
                regiones_seleccionadas = st.sidebar.multiselect(
                    "Filtrar por Región:", 
                    options=df["Región"].unique(), 
                    default=df["Región"].unique()
                )
                df = df[df["Región"].isin(regiones_seleccionadas)]
                
            if "Vendedor" in df.columns:
                vendedores_seleccionados = st.sidebar.multiselect(
                    "Filtrar por Vendedor:", 
                    options=df["Vendedor"].unique(), 
                    default=df["Vendedor"].unique()
                )
                df = df[df["Vendedor"].isin(vendedores_seleccionados)]

            # Sección de KPIs
            st.subheader("Resumen de Rendimiento")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Registros (Filas)", len(df))
                
            with col2:
                if "Venta Total" in df.columns:
                    total_ventas = df['Venta Total'].sum()
                    st.metric("Ingresos Totales", f"${total_ventas:,.2f}")
                    
            with col3:
                 if "Cantidad" in df.columns:
                    total_cantidad = df['Cantidad'].sum()
                    st.metric("Unidades Procesadas", f"{total_cantidad}")

            st.divider()

            # Gráficos Interactivos
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                if "Región" in df.columns and "Venta Total" in df.columns:
                    df_region = df.groupby("Región", as_index=False)["Venta Total"].sum()
                    fig_region = px.bar(df_region, x="Región", y="Venta Total", title="Ventas Acumuladas por Región", color="Región")
                    st.plotly_chart(fig_region, use_container_width=True)
                    
            with col_graf2:
                if "Vendedor" in df.columns and "Venta Total" in df.columns:
                    df_vendedor = df.groupby("Vendedor", as_index=False)["Venta Total"].sum()
                    fig_vendedor = px.pie(df_vendedor, names="Vendedor", values="Venta Total", title="Participación por Vendedor")
                    st.plotly_chart(fig_vendedor, use_container_width=True)

            st.divider()

            # Tabla de datos filtrados
            st.subheader("Base de Datos (Filtrada)")
            st.dataframe(df, use_container_width=True)

            # Botón de Descarga
            st.subheader("📥 Exportar Informe")
            st.write("Descarga los datos que estás viendo en pantalla como un nuevo archivo Excel.")
            
            def convertir_df_a_excel(dataframe):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    dataframe.to_excel(writer, index=False, sheet_name='Reporte Filtrado')
                    worksheet = writer.sheets['Reporte Filtrado']
                    # Autoajustar el ancho de las columnas
                    for i, col in enumerate(dataframe.columns):
                        ancho_columna = max(dataframe[col].astype(str).map(len).max(), len(col)) + 2
                        worksheet.set_column(i, i, ancho_columna)
                processed_data = output.getvalue()
                return processed_data
                
            excel_generado = convertir_df_a_excel(df)
            
            st.download_button(
                label="Descargar Excel Filtrado",
                data=excel_generado,
                file_name="Reporte_Dashboard.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Hubo un error al procesar el archivo principal. Asegúrate de que sea un Excel válido y contenga las columnas esperadas. Error: {e}")
            
    # ==========================================
    # RUTA 2: DASHBOARD DE BONOS
    # ==========================================
    elif menu_opcion == "Dashboard de Bonos":
        # Llamamos directamente a la función que escribimos en bonus.py
        # y le pasamos el archivo que el usuario ya subió
        bonus.mostrar_dashboard_bonus(archivo_subido)

else:
    st.info("👆 Por favor, sube un archivo Excel en el recuadro superior para comenzar.")
