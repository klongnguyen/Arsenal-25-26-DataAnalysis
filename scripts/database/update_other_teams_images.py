import pyodbc
from scrapling.fetchers import StealthyFetcher
import time

def get_connection():
    server = r'LAPTOP-8I1OVUBF\SQLEXPRESS'
    database = 'FootballAnalysis'
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    return pyodbc.connect(conn_str, autocommit=True)

def update_team_players(team_name, url, fetch_logic):
    conn = get_connection()
    cursor = conn.cursor()
    
    print(f"\nĐang tải trang web {team_name}...")
    try:
        page = StealthyFetcher(headless=True).fetch(url, solve_cloudflare=True)
    except Exception as e:
        print(f"Lỗi tải trang: {e}")
        return

    players_img = fetch_logic(page)
    print(f"Lấy được {len(players_img)} ảnh từ trang chủ {team_name}.")
    
    cursor.execute("SELECT player_id, player_name FROM players WHERE team_id = (SELECT team_id FROM teams WHERE team_name = ?)", (team_name,))
    db_players = cursor.fetchall()
    
    matched_count = 0
    for db_p in db_players:
        db_id = db_p[0]
        db_name = db_p[1]
        
        matched_url = None
        for p_img in players_img:
            img_name = p_img['name'].strip()
            
            # Xử lý các tên có ký tự đặc biệt hoặc tên ngắn
            # VD: "Ruben Dias" vs "Rúben Dias", "David Raya" vs "David Raya"
            # Loại bỏ dấu phẩy, chuyển chữ thường để dễ match
            name1 = db_name.lower().replace('-', ' ')
            name2 = img_name.lower().replace('-', ' ')
            
            if name1 in name2 or name2 in name1:
                matched_url = p_img['url']
                break
                
        if matched_url:
            # Fix cho Mancity url tương đối
            if matched_url.startswith('/'):
                matched_url = 'https://www.mancity.com' + matched_url
                
            cursor.execute("UPDATE players SET image_url = ? WHERE player_id = ?", (matched_url, db_id))
            matched_count += 1
            print(f"Đã cập nhật ảnh cho {db_name}")
            
    print(f"Đã cập nhật thành công ảnh cho {matched_count}/{len(db_players)} cầu thủ {team_name}.")
    
    cursor.close()
    conn.close()

def parse_arsenal(page):
    players = []
    imgs = page.css('img[data-testid="player-card-image"]')
    for img in imgs:
        name = img.attrib.get('alt', '')
        url = img.attrib.get('src', '')
        if name and url:
            players.append({'name': name, 'url': url})
    return players

def parse_mancity(page):
    players = []
    # Man city dùng article > img
    articles = page.css('article')
    for art in articles:
        name = art.attrib.get('aria-label', '')
        imgs = art.css('img')
        if name and imgs:
            # Ưu tiên lấy src, nếu không có lấy từ srcset
            url = imgs[0].attrib.get('src')
            if not url:
                srcset = imgs[0].attrib.get('srcset', '')
                if srcset:
                    url = srcset.split(' ')[0]
            if url:
                players.append({'name': name, 'url': url})
    return players

if __name__ == "__main__":
    # Cập nhật Arsenal
    update_team_players("Arsenal", "https://www.arsenal.com/fixtures/men/players", parse_arsenal)
    
    time.sleep(3)
    
    # Cập nhật Man City
    update_team_players("Manchester City", "https://www.mancity.com/players/mens", parse_mancity)
