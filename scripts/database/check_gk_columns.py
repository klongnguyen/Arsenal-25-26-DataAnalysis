import pyodbc
conn = pyodbc.connect(r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=LAPTOP-8I1OVUBF\SQLEXPRESS;DATABASE=FootballAnalysis;Trusted_Connection=yes;')
c = conn.cursor()
c.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'goalkeepers'")
print(c.fetchall())
