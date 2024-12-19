import pyodbc

try:
    conn = pyodbc.connect(
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\\Python\\_Proyectos\\Personal-Finance-Management\\_db\\ddbbPFM.accdb;'
    )
    print("Connection successful!")
    conn.close()
except pyodbc.Error as e:
    print("Error:", e)
    # Enseñar los drivers instalados, si no esta algo como (Microsoft Access Driver (*.mdb, *.accdb)), descargar el driver: https://www.microsoft.com/en-us/download/details.aspx?id=54920
    print(pyodbc.drivers())
