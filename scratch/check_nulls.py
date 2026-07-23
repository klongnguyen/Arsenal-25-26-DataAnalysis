import pyodbc
import sys
sys.stdout.reconfigure(encoding='utf-8')

def get_connection():
    server = r'LAPTOP-8I1OVUBF\SQLEXPRESS'
    database = 'FootballAnalysis'
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    try:
        return pyodbc.connect(conn_str, autocommit=True)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def check_nulls():
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    
    queries = {
        "fixtures (Current Season) - Tong so NULL": "SELECT COUNT(*) FROM fixtures WHERE xg_for IS NULL OR xg_against IS NULL",
        "fixtures - NULL theo giai dau": "SELECT comp, COUNT(*) FROM fixtures WHERE xg_for IS NULL OR xg_against IS NULL GROUP BY comp",
        "historical_fixtures - Tong so NULL": "SELECT COUNT(*) FROM historical_fixtures WHERE xg_for IS NULL OR xg_against IS NULL",
        "historical_standings - Tong so NULL": "SELECT COUNT(*) FROM historical_standings WHERE xg IS NULL OR xga IS NULL"
    }
    
    for desc, query in queries.items():
        cursor.execute(query)
        print(f"--- {desc} ---")
        for row in cursor.fetchall():
            print(row)
        print()
        
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check_nulls()
