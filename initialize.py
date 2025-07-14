import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv


def initialize():
    load_dotenv()

    xlsx_path = os.getenv("INPUTXLSX")
    sqlite_path = os.getenv("SQLPATH")

    #df = pd.read_csv(csv_path, sep="\s+")}
    df = pd.read_excel(xlsx_path)

    engine = create_engine(f"sqlite:///{sqlite_path}")
    df.to_sql("xlsx_table", con=engine, if_exists="replace", index=False)

    print("CSV cargado a la base de datos correctamente.")
    df = pd.read_sql("SELECT * FROM xlsx_table", con=engine)
    print(df)
    return
