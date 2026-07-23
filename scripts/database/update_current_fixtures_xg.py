import asyncio
import aiohttp
import sys
import pyodbc
from understat import Understat

sys.stdout.reconfigure(encoding='utf-8')

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

def alter_table_if_needed(cursor):
    # Kiểm tra xem cột xg_for và xg_against đã tồn tại chưa
    cursor.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'fixtures' AND COLUMN_NAME IN ('xg_for', 'xg_against')
    """)
    existing_cols = [row[0] for row in cursor.fetchall()]
    
    if 'xg_for' not in existing_cols:
        print("Đang thêm cột xg_for vào bảng fixtures...")
        cursor.execute("ALTER TABLE fixtures ADD xg_for FLOAT;")
    if 'xg_against' not in existing_cols:
        print("Đang thêm cột xg_against vào bảng fixtures...")
        cursor.execute("ALTER TABLE fixtures ADD xg_against FLOAT;")

async def scrape_and_update():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Thêm cột nếu chưa có
    alter_table_if_needed(cursor)
    
    # 2. Lấy danh sách đội bóng trong database để lấy team_id
    cursor.execute("SELECT team_name, team_id FROM teams")
    team_map = {row[0]: row[1] for row in cursor.fetchall()}
    
    # 3. Cào dữ liệu xG Premier League 2025-2026 từ Understat
    print("Đang tải dữ liệu trận đấu mùa giải 2025/26 từ Understat...")
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        try:
            teams_data = await understat.get_teams("epl", 2025)
        except Exception as e:
            print(f"Lỗi khi cào dữ liệu từ Understat: {e}")
            cursor.close()
            conn.close()
            return
            
    print("Đang cập nhật dữ liệu xG/xGA cho từng trận đấu...")
    updated_count = 0
    
    for team in teams_data:
        understat_team_name = team['title']
        fbref_team_name = get_fbref_name(understat_team_name)
        team_id = team_map.get(fbref_team_name)
        
        if not team_id:
            print(f"Bỏ qua đội bóng không có trong database: {fbref_team_name} (Understat name: {understat_team_name})")
            continue
            
        history = team['history']
        for match in history:
            match_date = match['date'].split(' ')[0] # Lấy YYYY-MM-DD
            xg_for = round(match['xG'], 2)
            xg_against = round(match['xGA'], 2)
            
            # Cập nhật vào bảng fixtures
            cursor.execute("""
                UPDATE fixtures
                SET xg_for = ?, xg_against = ?
                WHERE team_id = ? AND match_date = ? AND comp = N'Premier League'
            """, (xg_for, xg_against, team_id, match_date))
            
            if cursor.rowcount > 0:
                updated_count += 1
                
    print(f"Cập nhật hoàn tất! Đã cập nhật thành công xG/xGA cho {updated_count} trận đấu mùa giải hiện tại.")
    cursor.close()
    conn.close()

if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(scrape_and_update())
