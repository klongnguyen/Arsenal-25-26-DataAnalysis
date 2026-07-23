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

def check_arsenal_mw17():
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    
    query = """
    SELECT match_round, match_date, team_name, opponent, xg_for, xg_against, f.goals_for, f.goals_against
    FROM fixtures f
    JOIN teams t ON f.team_id = t.team_id
    WHERE t.team_name = 'Arsenal' AND f.comp = 'Premier League' AND f.match_round IN ('Matchweek 17', 'Matchweek 18', 'Matchweek 19')
    ORDER BY f.match_date
    """
    
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    print("\t".join(columns))
    for row in cursor.fetchall():
        print("\t".join(str(val) for val in row))
        
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check_arsenal_mw17()
