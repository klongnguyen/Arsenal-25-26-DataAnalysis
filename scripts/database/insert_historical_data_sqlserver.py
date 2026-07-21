import json
import pyodbc
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

def get_connection():
    server = r'LAPTOP-8I1OVUBF\SQLEXPRESS'
    database = 'FootballAnalysis'
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

def setup_historical_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tạo bảng historical_standings
    cursor.execute("""
    IF OBJECT_ID('historical_standings', 'U') IS NOT NULL 
        DROP TABLE historical_standings;
    """)
    cursor.execute("""
    CREATE TABLE historical_standings (
        id INT IDENTITY(1,1) PRIMARY KEY,
        season NVARCHAR(20),
        rank INT,
        team NVARCHAR(100),
        matches INT,
        wins INT,
        draws INT,
        losses INT,
        goals_for INT,
        goals_against INT,
        goal_diff INT,
        points INT,
        xg FLOAT,
        xga FLOAT,
        xg_diff FLOAT
    )
    """)
    
    # Tạo bảng historical_fixtures
    cursor.execute("""
    IF OBJECT_ID('historical_fixtures', 'U') IS NOT NULL 
        DROP TABLE historical_fixtures;
    """)
    cursor.execute("""
    CREATE TABLE historical_fixtures (
        id INT IDENTITY(1,1) PRIMARY KEY,
        season NVARCHAR(20),
        team NVARCHAR(100),
        match_date DATE,
        comp NVARCHAR(100),
        match_round NVARCHAR(100),
        venue NVARCHAR(50),
        result NVARCHAR(10),
        goals_for NVARCHAR(50),
        goals_against NVARCHAR(50),
        opponent NVARCHAR(100),
        possession INT,
        xg_for FLOAT,
        xg_against FLOAT
    )
    """)
    
    print("Đã tạo bảng historical_standings và historical_fixtures.")
    cursor.close()
    conn.close()

def insert_historical_data():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Lấy đường dẫn đúng tới thư mục data
    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    
    standings_file = os.path.join(data_dir, 'historical_standings.json')
    fixtures_file = os.path.join(data_dir, 'historical_champions_fixtures.json')
    
    if not os.path.exists(standings_file) or not os.path.exists(fixtures_file):
        print("Lỗi: Không tìm thấy file dữ liệu JSON trong thư mục data.")
        return
        
    print("Đang chèn dữ liệu historical_standings...")
    with open(standings_file, 'r', encoding='utf-8') as f:
        standings_data = json.load(f)
        
    for s in standings_data:
        cursor.execute("""
            INSERT INTO historical_standings (season, rank, team, matches, wins, draws, losses, goals_for, goals_against, goal_diff, points, xg, xga, xg_diff)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            s['season'], s['rank'], s['team'], s['matches'], s['wins'], s['draws'], s['losses'],
            s['goals_for'], s['goals_against'], s['goal_diff'], s['points'],
            s.get('xg', 0.0), s.get('xga', 0.0), s.get('xg_diff', 0.0)
        ))
        
    print(f"Đã chèn {len(standings_data)} bản ghi vào historical_standings.")
    
    print("Đang chèn dữ liệu historical_fixtures...")
    with open(fixtures_file, 'r', encoding='utf-8') as f:
        fixtures_data = json.load(f)
        
    for fx in fixtures_data:
        match_date = fx['date'] if fx['date'] else None
        cursor.execute("""
            INSERT INTO historical_fixtures (season, team, match_date, comp, match_round, venue, result, goals_for, goals_against, opponent, possession, xg_for, xg_against)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fx['season'], fx['team'], match_date, fx['comp'], fx['round'], fx['venue'], fx['result'],
            str(fx['goals_for']), str(fx['goals_against']), fx['opponent'], fx.get('possession', 0),
            fx.get('xg_for', 0.0), fx.get('xg_against', 0.0)
        ))
        
    print(f"Đã chèn {len(fixtures_data)} bản ghi vào historical_fixtures.")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Hoàn tất chèn dữ liệu lịch sử vào SQL Server!")

if __name__ == "__main__":
    setup_historical_tables()
    insert_historical_data()
