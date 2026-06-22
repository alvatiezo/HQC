import pandas as pd
from io import BytesIO
import xlsxwriter

def generar_reporte_compilado(archivo):
    output = BytesIO()
    # Usamos xlsxwriter para personalizar el diseño
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    workbook = writer.book

    # Definir formatos de diseño (UX/UI)
    header_format = workbook.add_format({'bold': True, 'bg_color': '#1F4E79', 'font_color': 'white', 'border': 1})
    money_format = workbook.add_format({'num_format': '$#,##0.00'})
    num_format = workbook.add_format({'num_format': '#,##0.00'})

    # Lista de pestañas a procesar
    sheets = ["OT", "Bonus", "Double Pay"]
    
    for sheet in sheets:
        try:
            df = pd.read_excel(archivo, sheet_name=sheet)
            df.to_excel(writer, index=False, sheet_name=sheet)
            worksheet = writer.sheets[sheet]
            
            # Aplicar formato a encabezados
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 18)
        except:
            continue

    summary_ws = workbook.add_worksheet('Executive Summary')
    summary_ws.write(0, 0, "MASTER SUMMARY REPORT", header_format)
            
    writer.close()
    return output.getvalue()
