import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_dashboard_bonus(archivo_subido):
    st.header("🏆 Dashboard de Bonos Aprobados")
    
    try:
        # 1. Leer específicamente la hoja "Bonus" del Excel
        df_bonus = pd.read_excel(archivo_subido, sheet_name="Bonus")
        
        # 2. Limpieza y Filtro de la columna "Status"
        if "Status" in df_bonus.columns:
            df_bonus["Status"] = df_bonus["Status"].astype(str).str.strip().str.lower()
            df_filtrado = df_bonus[df_bonus["Status"] == "yes"].copy()
        else:
            st.error("No se encontró la columna 'Status' en la hoja 'Bonus'.")
            return

        if df_filtrado.empty:
            st.warning("No hay datos con Status 'Yes' para mostrar.")
            return

        # 3. KPIs Generales
        total_monto = df_filtrado["Amount"].sum()
        st.metric("Total a Pagar (Bonos Aprobados)", f"${total_monto:,.2f}")
        
        st.divider()
        
        # 4. Gráficos y Divisiones
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Pagos por Cuenta y Fecha")
            df_acc_date = df_filtrado.groupby(["Account", "Date"], as_index=False)["Amount"].sum()
            fig_acc_date = px.bar(
                df_acc_date, x="Date", y="Amount", color="Account", barmode="group",
                title="Monto Total por Fecha (Agrupado por Cuenta)", text_auto='.2s'
            )
            st.plotly_chart(fig_acc_date, use_container_width=True)
            
        with col2:
            st.subheader("Distribución por Tipo de Bono")
            df_bonus_type = df_filtrado.groupby("Bonus", as_index=False)["Amount"].sum()
            fig_bonus = px.pie(
                df_bonus_type, names="Bonus", values="Amount", 
                title="Participación de cada Bono en el Total", hole=0.4
            )
            st.plotly_chart(fig_bonus, use_container_width=True)
            
        st.divider()
        
        # ==========================================
        # 5. PREPARACIÓN DE DATOS PARA DESCARGA
        # ==========================================
        st.subheader("📥 Exportar Resultados")
        st.write("Descarga un archivo Excel con los totales netos consolidados por cuenta y el desglose de los bonos.")
        
        # Tabla 1: Total general por cuenta
        df_total_cuenta = df_filtrado.groupby("Account", as_index=False)["Amount"].sum()
        df_total_cuenta.rename(columns={"Amount": "Total a Pagar ($)"}, inplace=True)
        
        # Tabla 2: Desglose de cuenta por bono (Pivot Table)
        df_cuenta_bono = pd.pivot_table(
            df_filtrado, 
            values='Amount', 
            index='Account', 
            columns='Bonus', 
            aggfunc='sum', 
            fill_value=0
        ).reset_index()

        # Mostrar una vista previa en la pantalla
        st.dataframe(df_total_cuenta, use_container_width=True)

        # Función para compilar ambas tablas en un solo archivo Excel
        def generar_excel_resultados(df_totales, df_bonos):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Guardar en diferentes hojas
                df_totales.to_excel(writer, index=False, sheet_name='Total por Cuenta')
                df_bonos.to_excel(writer, index=False, sheet_name='Desglose por Bono')
                
                # Formato visual básico para el archivo descargado
                for sheet_name in ['Total por Cuenta', 'Desglose por Bono']:
                    worksheet = writer.sheets[sheet_name]
                    worksheet.set_column(0, 0, 20) # Ancho columna Account
                    worksheet.set_column(1, 10, 15) # Ancho columnas de montos
                    
            return output.getvalue()
            
        excel_resultados = generar_excel_resultados(df_total_cuenta, df_cuenta_bono)
        
        # Botón de descarga
        st.download_button(
            label="Descargar Resultados (Excel)",
            data=excel_resultados,
            file_name="Resultados_Consolidados_Bonos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except ValueError:
        st.error("⚠️ El archivo subido no contiene una pestaña llamada 'Bonus'. Verifica tu Excel.")
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al procesar la información: {e}")
