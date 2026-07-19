import json
import pyodbc
from scrapling.fetchers import StealthyFetcher

def get_connection():
    server = r'LAPTOP-8I1OVUBF\SQLEXPRESS'
    database = 'FootballAnalysis'
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    return pyodbc.connect(conn_str, autocommit=True)

def add_image_columns():
    conn = get_connection()
    cursor = conn.cursor()
    print("Thêm cột hình ảnh vào CSDL...")
    
    try:
        cursor.execute("ALTER TABLE teams ADD logo_url NVARCHAR(MAX)")
    except Exception as e:
        print("Cột logo_url có thể đã tồn tại.")
        
    try:
        cursor.execute("ALTER TABLE players ADD image_url NVARCHAR(MAX)")
    except Exception as e:
        print("Cột image_url có thể đã tồn tại.")
        
    cursor.close()
    conn.close()

def scrape_team_logos():
    conn = get_connection()
    cursor = conn.cursor()
    
    teams = [
        {"name": "Arsenal", "url": "https://fbref.com/en/squads/18bb7c10/Arsenal-Stats"},
        {"name": "Manchester City", "url": "https://fbref.com/en/squads/b8fd03ef/Manchester-City-Stats"},
        {"name": "Manchester Utd", "url": "https://fbref.com/en/squads/19538871/Manchester-United-Stats"}
    ]
    
    print("Đang cào Logo các đội bóng...")
    for team in teams:
        page = StealthyFetcher(headless=True).fetch(team['url'], solve_cloudflare=True)
        logo_img = page.css('img.teamlogo')
        if logo_img:
            logo_url = logo_img[0].attrib.get('src')
            if logo_url:
                cursor.execute("UPDATE teams SET logo_url = ? WHERE team_name = ?", (logo_url, team['name']))
                print(f"Đã cập nhật Logo cho {team['name']}: {logo_url}")
                
    cursor.close()
    conn.close()

def update_manutd_players():
    conn = get_connection()
    cursor = conn.cursor()
    
    print("Đang tải danh sách ảnh cầu thủ Man Utd từ file json...")
    with open('data/manutd_players_images.json', 'r', encoding='utf-8') as f:
        players_img = json.load(f)
        
    cursor.execute("SELECT player_id, player_name FROM players WHERE team_id = (SELECT team_id FROM teams WHERE team_name = 'Manchester Utd')")
    db_players = cursor.fetchall()
    
    matched_count = 0
    for db_p in db_players:
        db_id = db_p[0]
        db_name = db_p[1]
        
        # Thử tìm ảnh khớp tên
        matched_url = None
        for p_img in players_img:
            img_name = p_img['name'].replace(' - Square', '').replace('IMAGE - ', '').strip()
            
            # Simple matching logic
            if db_name.lower() in img_name.lower() or img_name.lower() in db_name.lower():
                matched_url = p_img['image_url']
                break
                
        if matched_url:
            cursor.execute("UPDATE players SET image_url = ? WHERE player_id = ?", (matched_url, db_id))
            matched_count += 1
            print(f"Đã cập nhật ảnh cho {db_name}")
            
    print(f"Đã cập nhật thành công ảnh cho {matched_count}/{len(db_players)} cầu thủ Man Utd.")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    add_image_columns()
    scrape_team_logos()
    update_manutd_players()
