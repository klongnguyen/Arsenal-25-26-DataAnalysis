import pyodbc
import json
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

def get_connection(db_name=None):
    server = r'LAPTOP-8I1OVUBF\SQLEXPRESS'
    database = db_name if db_name else 'master'
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    try:
        conn = pyodbc.connect(conn_str, autocommit=True)
        return conn
    except Exception as e:
        try:
            conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
            conn = pyodbc.connect(conn_str, autocommit=True)
            return conn
        except Exception as e2:
            print(f"Lỗi kết nối CSDL: {e2}")
            sys.exit(1)

TEAM_MAPPING = {
    "Manchester United": "Manchester Utd",
    "Wolverhampton Wanderers": "Wolves",
    "Newcastle United": "Newcastle",
    "Nottingham Forest": "Nottingham",
    "West Bromwich Albion": "West Brom",
    "Queens Park Rangers": "QPR",
    "Leeds": "Leeds United",
    "Stoke": "Stoke City",
    "Norwich": "Norwich City",
    "Hull": "Hull City",
    "Luton": "Luton Town",
    "Cardiff": "Cardiff City",
    "Swansea": "Swansea City",
    "Ipswich": "Ipswich Town",
    "Leicester": "Leicester City"
}

def get_fbref_name(understat_name):
    return TEAM_MAPPING.get(understat_name, understat_name)

def update_xg_data():
    conn = get_connection('FootballAnalysis')
    cursor = conn.cursor()
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    
    # 1. Update historical_standings
    print("Đang cập nhật xG cho historical_standings...")
    with open(os.path.join(data_dir, 'understat_teams_xg.json'), 'r', encoding='utf-8') as f:
        teams_xg = json.load(f)
        
    for t in teams_xg:
        fbref_team = get_fbref_name(t['understat_team'])
        season = t['season']
        
        cursor.execute("""
            UPDATE hs 
            SET hs.xg = ?, hs.xga = ?, hs.xg_diff = ?
            FROM historical_standings hs
            JOIN teams t ON hs.team_id = t.team_id
            WHERE t.team_name = ? AND hs.season = ?
        """, (t['xg'], t['xga'], t['xg_diff'], fbref_team, season))
        
    print("Đã cập nhật bảng historical_standings!")
    
    # 2. Update historical_fixtures
    print("Đang cập nhật xG cho historical_fixtures...")
    with open(os.path.join(data_dir, 'understat_matches_xg.json'), 'r', encoding='utf-8') as f:
        matches_xg = json.load(f)
        
    for m in matches_xg:
        fbref_team = get_fbref_name(m['understat_team'])
        season = m['season']
        match_date = m['date']
        
        cursor.execute("""
            UPDATE hf
            SET hf.xg_for = ?, hf.xg_against = ?
            FROM historical_fixtures hf
            JOIN teams t ON hf.team_id = t.team_id
            WHERE t.team_name = ? AND hf.season = ? AND hf.match_date = ?
        """, (m['xg_for'], m['xg_against'], fbref_team, season, match_date))
        
    print("Đã cập nhật bảng historical_fixtures!")
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    update_xg_data()
