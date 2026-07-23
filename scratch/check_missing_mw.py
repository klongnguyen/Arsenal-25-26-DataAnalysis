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

def check_missing_mw():
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    
    query = """
    SELECT match_round, match_date, xg_for, xg_against
    FROM fixtures f
    JOIN teams t ON f.team_id = t.team_id
    WHERE t.team_name = 'Arsenal' AND f.comp = 'Premier League' AND match_round IN ('Matchweek 5', 'Matchweek 26', 'Matchweek 31', 'Matchweek 27')
    ORDER BY f.match_date
    """
    
    cursor.execute(query)
    for row in cursor.fetchall():
        print(f"{row[0]} | {row[1]} | xG: {row[2]} | xGA: {row[3]}")
        
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check_missing_mw()
