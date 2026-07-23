import pyodbc

def get_connection():
    server = r'LAPTOP-8I1OVUBF\SQLEXPRESS'
    database = 'FootballAnalysis'
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    try:
        return pyodbc.connect(conn_str, autocommit=True)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def check_arsenal_dates():
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    
    query = """
    SELECT match_round, match_date
    FROM fixtures f
    JOIN teams t ON f.team_id = t.team_id
    WHERE t.team_name = 'Arsenal' AND f.comp = 'Premier League'
    ORDER BY f.match_date
    """
    
    cursor.execute(query)
    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]}")
        
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check_arsenal_dates()
