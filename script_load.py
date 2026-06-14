import pandas as pd

def load_data():

    clientes = pd.read_csv("Clientes.csv")
    productos = pd.read_csv("Productos.csv")
    negocios = pd.read_csv("Negocios.csv")
    calendario = pd.read_csv("Calendario.csv")
    ventas = pd.read_csv("Ventas.csv")

    ventas["Fecha"] = pd.to_datetime(ventas["Fecha"])
    calendario["Fecha"] = pd.to_datetime(calendario["Fecha"])

    return clientes, productos, negocios, calendario, ventas