import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

st.title("Extractor de presupuestos PDF a Excel")

pdf_file = st.file_uploader("Subí tu presupuesto PDF", type="pdf")

if pdf_file is not None:
    st.success("PDF cargado correctamente.")

    rows = []
    current_desc = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')
            for line in lines:
                line = line.strip()

                # Filtrar líneas que no necesitamos (datos cliente y líneas intermedias)
                if line.startswith("Cliente:") or line.startswith("Nombre:") or line.startswith("Cond. de Pago:") or line.startswith("Vendedor:") or line.startswith("Teléfono:") or line.startswith("Usuario:") or line.startswith("Zona Entrega:") or line.startswith("Observaciones:") or line == "":
                    continue

                # Detectar descripciones (solo líneas con "LAM." y en mayúsculas)
                if "LAM." in line:
                    current_desc = line
                    continue  # la guardamos pero no la procesamos como ítem

                # Detectar líneas de ítems (empiezan con número y tienen suficientes datos)
                parts = line.split()
                if len(parts) >= 10 and parts[0].isdigit():
                    row = [current_desc] + parts
                    rows.append(row)

    # Definir columnas
    columns = ["Descripción", "Pos", "Cant", "Medidas1", "Medidas2", "Perim.C", "Sup", "Junta", "Peso", "Precio", "P.Unit.", "Subtotal"]

    # Crear DataFrame
    df = pd.DataFrame(rows, columns=columns)

    # Mostrar tabla en Streamlit
    st.write("Tabla de ítems extraída:", df)

    # Botón para descargar Excel
    @st.cache_data
    def convert_df(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        processed_data = output.getvalue()
        return processed_data

    excel = convert_df(df)
    st.download_button(
        label="Descargar tabla en Excel",
        data=excel,
        file_name='presupuesto_extraido.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )