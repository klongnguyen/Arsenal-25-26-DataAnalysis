import pyodbc
conn = pyodbc.connect(r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=LAPTOP-8I1OVUBF\SQLEXPRESS;DATABASE=FootballAnalysis;Trusted_Connection=yes;')
c = conn.cursor()
c.execute("SELECT player_name, position, image_url FROM players WHERE team_id = (SELECT team_id FROM teams WHERE team_name = 'Manchester Utd')")
res = c.fetchall()
print(f'Total MU players in DB: {len(res)}')
for row in res:
    print(row)
