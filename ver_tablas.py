import pandas as pd

archivos = [
    "Calendario.csv",
    "Clientes.csv",
    "Negocios.csv",
    "Productos.csv",
    "Ventas.csv"
]

for archivo in archivos:

    print("\n" + "="*50)
    print("ARCHIVO:", archivo)
    print("="*50)

    df = pd.read_csv(archivo)

    print("\nCOLUMNAS:")
    print(df.columns.tolist())

    print("\nPRIMERAS FILAS:")
    print(df.head())