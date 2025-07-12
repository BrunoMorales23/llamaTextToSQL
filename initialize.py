import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv


def initialize():
    load_dotenv()

    csv_path = os.getenv("INPUTCSV")
    sqlite_path = os.getenv("SQLPATH")

    #df = pd.read_csv(csv_path, sep="\s+")}
    df = pd.read_excel("C:/Users/MarsuDIOS666/Desktop/TextToSQL/XLSX.xlsx")
    print(df)

    engine = create_engine(f"sqlite:///{sqlite_path}")
    df.to_sql("csv_table", con=engine, if_exists="replace", index=False)

    print("CSV cargado a la base de datos correctamente.")
    df = pd.read_sql("SELECT * FROM csv_table", con=engine)
    print(df)
    return
