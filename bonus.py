import streamlit as st
import pandas as pd
import plotly.express as px

def mostrar_dashboard_bonus(archivo_subido):
    st.header("🏆 Dashboard de Bonos Aprobados")
    
    try:
        # 1. Leer específicamente la hoja "Bonus" del Excel
        df_bonus = pd.read_excel(archivo_subido, sheet_name="Bonus")
        
        # 2. Limpieza y Filtro de la columna "Status"
        if "Status" in df_bonus.columns:
            # Aseguramos que no haya errores si hay celdas vacías y estandarizamos texto
            df_bonus["Status"] = df_bonus["Status"].astype(str).str.strip().str.lower()
            
            # FILTRAR: Solo mantener los que dicen "yes" (ignorando "no" o vacíos)
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
        
        # Gráfico 1: Sumatoria por Cuenta dividida por Fecha
        with col1:
            st.subheader("Pagos por Cuenta y Fecha")
            # Agrupamos por Account y Date, sumando el Amount
            df_acc_date = df_filtrado.groupby(["Account", "Date"], as_index=False)["Amount"].sum()
            
            fig_acc_date = px.bar(
                df_acc_date, 
                x="Date", 
                y="Amount", 
                color="Account", 
                barmode="group",
                title="Monto Total por Fecha (Agrupado por Cuenta)",
                text_auto='.2s'
            )
            st.plotly_chart(fig_acc_date, use_container_width=True)
            
        # Gráfico 2: Sumatoria por Tipo de Bono
        with col2:
            st.subheader("Distribución por Tipo de Bono")
            # Agrupamos por Bonus, sumando el Amount
            df_bonus_type = df_filtrado.groupby("Bonus", as_index=False)["Amount"].sum()
            
            fig_bonus = px.pie(
                df_bonus_type, 
                names="Bonus", 
                values="Amount", 
                title="Participación de cada Bono en el Total",
                hole=0.4
            )
            st.plotly_chart(fig_bonus, use_container_width=True)
            
        st.divider()
        
        # 5. Tabla de datos procesados (Opcional, para revisar la info calculada)
        st.subheader("Desglose Final de Cuentas")
        # Mostramos una tabla pivote limpia para que se vea exactamente cuánto se le paga a cada cuenta por fecha
        tabla_resumen = pd.pivot_table(
            df_filtrado, 
            values='Amount', 
            index=['Account', 'Date'], 
            columns=['Bonus'], 
            aggfunc='sum', 
            fill_value=0
        )
        st.dataframe(tabla_resumen, use_container_width=True)
        
    except ValueError:
        st.error("⚠️ El archivo subido no contiene una pestaña llamada 'Bonus'. Verifica tu Excel.")
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al procesar la información: {e}")
