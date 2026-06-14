import streamlit as st
from script_load import load_data
import pandas as pd
from io import BytesIO
import plotly.express as px

st.set_page_config(
    page_title="Panel de control de fidelización",
    layout="wide"
)

st.title("📊 Panel de control de fidelización")

clientes, productos, negocios, calendario, ventas = load_data()

# =====================
# UNIR TABLAS
# =====================

df = ventas.merge(
    clientes,
    on="ClienteID",
    how="left"
)

df = df.merge(
    productos,
    on="ProductoID",
    how="left"
)

df = df.merge(
    negocios,
    on="NegocioID",
    how="left",
    suffixes=("_Cliente", "_Negocio")
)

st.success("Datos cargados correctamente")

# =====================
# FILTROS
# =====================

st.sidebar.header("🔎 Filtros")

# =====================
# FILTRO FECHAS
# =====================

fecha_inicio = st.sidebar.date_input(
    "Fecha inicio oferta",
    df["Fecha"].min()
)

fecha_fin = st.sidebar.date_input(
    "Fecha fin oferta",
    df["Fecha"].max()
)

segmento = st.sidebar.multiselect(
    "Segmento",
    options=df["Segmento"].unique(),
    default=df["Segmento"].unique()
)

categoria = st.sidebar.multiselect(
    "Categoría",
    options=df["Categoria"].unique(),
    default=df["Categoria"].unique()
)

ciudad = st.sidebar.multiselect(
    "Ciudad Cliente",
    options=df["Ciudad_Cliente"].unique(),
    default=df["Ciudad_Cliente"].unique()
)

productos_oferta = st.sidebar.multiselect(
    "Productos Oferta",
    options=df["NombreProducto"].unique(),
    default=df["NombreProducto"].unique()
)

monto_minimo = st.sidebar.number_input(
    "Monto mínimo (compra de la oferta)",
    value=55000,
    step=5000
)

monto_historico = st.sidebar.number_input(
    "Monto mínimo histórico",
    value=30000,
    step=5000
)
# =====================
# PERIODO COMPARATIVO
# =====================

st.sidebar.markdown("---")
st.sidebar.subheader("📅 Periodo Comparativo")

fecha_comp_inicio = st.sidebar.date_input(
    "Inicio comparativo",
    value=df["Fecha"].min(),
    key="comp_inicio"
)

fecha_comp_fin = st.sidebar.date_input(
    "Fin comparativo",
    value=df["Fecha"].max(),
    key="comp_fin"
)

# Aplicar filtros

df_filtrado = df[
    (df["Segmento"].isin(segmento)) &
    (df["Categoria"].isin(categoria)) &
    (df["Ciudad_Cliente"].isin(ciudad)) &
    (df["NombreProducto"].isin(productos_oferta)) &
    (df["Fecha"] >= pd.to_datetime(fecha_inicio)) &
    (df["Fecha"] <= pd.to_datetime(fecha_fin))
]

# =====================
# KPIs
# =====================

clientes_unicos = df_filtrado["ClienteID"].nunique()

transacciones = df_filtrado["VentaID"].nunique()

venta_total = df_filtrado["ValorVenta"].sum()

ticket_promedio = round(
    df_filtrado["ValorVenta"].mean(),
    0
)


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "👥 Clientes",
    clientes_unicos
)

col2.metric(
    "🧾 Transacciones",
    transacciones
)

col3.metric(
    "💰 Venta Total",
    f"${venta_total:,.0f}"
)

col4.metric(
    "📦 Ticket Promedio",
    f"${ticket_promedio:,.0f}"
)

st.subheader("Vista integrada de datos")

st.dataframe(df_filtrado)

st.subheader("🌎 Clientes por Ciudad")

clientes_ciudad = (
    df_filtrado.groupby("Ciudad_Cliente")
    .agg(
        Clientes=("ClienteID", "nunique")
    )
    .reset_index()
)

fig_ciudad = px.pie(
    clientes_ciudad,
    names="Ciudad_Cliente",
    values="Clientes",
    title="Distribución de Clientes"
)

fig_ciudad.update_traces(
    textinfo="label+percent"
)

fig_ciudad.update_layout(
    legend_title="Ciudad"
)

st.plotly_chart(
    fig_ciudad,
    use_container_width=True
)

# =====================
# CLIENTES POR DIA
# =====================

st.subheader("📅 Clientes por Día")

clientes_dia = (
    df_filtrado.groupby("Fecha")
    .agg(
        Clientes=("ClienteID", "nunique"),
        Transacciones=("VentaID", "nunique"),
        Venta=("ValorVenta", "sum")
    )
    .reset_index()
)

fig_ventas = px.line(
    clientes_dia,
    x="Fecha",
    y="Venta",
    text="Venta",
    markers=True,
    title="Tendencia de Ventas por Día"
)

fig_ventas.update_traces(
    texttemplate='$%{y:,.0f}',
    textposition='top center'
)

fig_ventas.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Ventas ($ COP)"
)

st.plotly_chart(
    fig_ventas,
    use_container_width=True
)

# =====================
# CLIENTES QUE CUMPLEN OFERTA
# =====================

st.subheader("👥 Clientes que cumplen la oferta")

clientes_oferta = df_filtrado[
    df_filtrado["ValorVenta"] >= monto_minimo
][["ClienteID", "Nombre", "VentaID", "ValorVenta"]]

clientes_oferta = clientes_oferta.drop_duplicates()

st.metric(
    "Clientes que cumplen monto mínimo",
    clientes_oferta["ClienteID"].nunique()
)

st.dataframe(
    clientes_oferta.style.format({
        "ValorVenta": "${:,.0f}"
    }),
    use_container_width=True
)


# =====================
# VENTA COMPARATIVA
# =====================

df_comparativo = df[
    (df["Segmento"].isin(segmento)) &
    (df["Categoria"].isin(categoria)) &
    (df["Ciudad_Cliente"].isin(ciudad)) &
    (df["NombreProducto"].isin(productos_oferta)) &
    (df["Fecha"] >= pd.to_datetime(fecha_comp_inicio)) &
    (df["Fecha"] <= pd.to_datetime(fecha_comp_fin))
]

venta_comparativa = df_comparativo["ValorVenta"].sum()

# Calcular variación %

if venta_comparativa > 0:
    variacion = (
        (venta_total - venta_comparativa)
        / venta_comparativa
    ) * 100
else:
    variacion = 0
    
st.subheader("📊 Comparativo de Ventas")

col_comp1, col_comp2, col_comp3 = st.columns(3)

col_comp1.metric(
    "💰 Venta Oferta",
    f"${venta_total:,.0f}"
)

col_comp2.metric(
    "📅 Venta Comparativa",
    f"${venta_comparativa:,.0f}"
)

col_comp3.metric(
    "📈 Variación %",
    f"{variacion:.2f}%"
)

# =====================
# CLIENTES CON HISTORICO
# =====================

st.subheader("🔄 Clientes con compra previa")

clientes_historico = df_comparativo.groupby(
    ["ClienteID", "Nombre"]
)["ValorVenta"].sum().reset_index()

clientes_historico = clientes_historico[
    clientes_historico["ValorVenta"] >= monto_historico
]

clientes_finales = clientes_oferta.merge(
    clientes_historico[["ClienteID"]],
    on="ClienteID",
    how="inner"
)

st.metric(
    "Clientes con compra previa",
    clientes_finales["ClienteID"].nunique()
)

st.dataframe(
    clientes_finales.style.format({
        "ValorVenta": "${:,.0f}"
    })
)

# =====================
# PARETO 80/20
# =====================

st.subheader("📈 Pareto de Productos (80% de la venta)")

pareto = (
    df_filtrado.groupby("NombreProducto")["ValorVenta"]
    .sum()
    .reset_index()
)

pareto = pareto.sort_values(
    by="ValorVenta",
    ascending=False
)

pareto["Porcentaje"] = (
    pareto["ValorVenta"]
    / pareto["ValorVenta"].sum()
) * 100

pareto["Acumulado"] = pareto["Porcentaje"].cumsum()

pareto_80 = pareto[
    pareto["Acumulado"] <= 80
]

st.dataframe(
    pareto_80.style.format({
        "ValorVenta": "${:,.0f}",
        "Porcentaje": "{:,.2f}%",
        "Acumulado": "{:,.2f}%"
    })
)

fig_pareto = px.bar(
    pareto_80,
    x="NombreProducto",
    y="ValorVenta",
    text="ValorVenta",
    title="Productos que generan el 80% de las ventas"
)

fig_pareto.update_traces(
    texttemplate='$%{y:,.0f}',
    textposition='outside'
)

fig_pareto.update_layout(
    title="Productos que generan el 80% de las ventas",
    yaxis_title="Ventas ($ COP)",
    xaxis_title="Producto",
    height=500
)

st.plotly_chart(
    fig_pareto,
    use_container_width=True
)

# =====================
# EXPORTAR EXCEL
# =====================

st.subheader("📥 Exportar Resultados")

def convertir_excel(df_exportar):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df_exportar.to_excel(
            writer,
            index=False,
            sheet_name="Datos"
        )

    return output.getvalue()


# Datos filtrados

archivo_principal = convertir_excel(df_filtrado)

st.download_button(
    label="📊 Descargar Datos Filtrados",
    data=archivo_principal,
    file_name="datos_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Clientes oferta

archivo_clientes = convertir_excel(clientes_oferta)

st.download_button(
    label="👥 Descargar Oferta Clientes",
    data=archivo_clientes,
    file_name="clientes_oferta.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Pareto

archivo_pareto = convertir_excel(pareto_80)

st.download_button(
    label="📈 Descargar Pareto",
    data=archivo_pareto,
    file_name="pareto_productos.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)