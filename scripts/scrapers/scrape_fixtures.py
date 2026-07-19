import json
import time
from scrapling.fetchers import StealthyFetcher

def to_int(val):
    if not val:
        return 0
    try:
        return int(val.replace(',', ''))
    except:
        return 0

def get_text(row, data_stat):
    # Trích xuất văn bản từ thẻ td hoặc th dựa vào data-stat
    # Thử lấy toàn bộ text bên trong (kể cả trong thẻ <a>)
    texts = row.css(f'[data-stat="{data_stat}"]').xpath('.//text()').getall()
    if texts:
        return " ".join(texts).strip()
    return ""

def scrape_fixtures():
    teams = [
        {"name": "Arsenal", "url": "https://fbref.com/en/squads/18bb7c10/Arsenal-Stats"},
        {"name": "Manchester City", "url": "https://fbref.com/en/squads/b8fd03ef/Manchester-City-Stats"},
        {"name": "Manchester Utd", "url": "https://fbref.com/en/squads/19538871/Manchester-United-Stats"}
    ]
    
    all_fixtures_data = []
    
    for team in teams:
        print(f"Đang tải trang web của đội {team['name']}...")
        page = StealthyFetcher(headless=True).fetch(team['url'], solve_cloudflare=True)
        
        # Bảng matchlogs_for
        table = page.css('table#matchlogs_for')
        if not table:
            print(f"Không tìm thấy bảng Scores & Fixtures cho đội {team['name']}")
            continue
            
        rows = table[0].css('tbody tr')
        added_matches = 0
        
        for row in rows:
            # Bỏ qua các hàng trống hoặc các hàng class spacer
            if 'spacer' in row.attrib.get('class', '') or 'thead' in row.attrib.get('class', ''):
                continue
                
            date = get_text(row, 'date')
            if not date:
                continue # Nếu không có ngày thi đấu thì bỏ qua
                
            comp = get_text(row, 'comp')
            match_round = get_text(row, 'round')
            dayofweek = get_text(row, 'dayofweek')
            venue = get_text(row, 'venue')
            result = get_text(row, 'result')
            goals_for = get_text(row, 'goals_for')
            goals_against = get_text(row, 'goals_against')
            opponent = get_text(row, 'opponent')
            possession = get_text(row, 'possession')
            attendance = get_text(row, 'attendance')
            captain = get_text(row, 'captain')
            formation = get_text(row, 'formation')
            opp_formation = get_text(row, 'opp_formation')
            
            all_fixtures_data.append({
                "team": team['name'],
                "date": date,
                "comp": comp,
                "round": match_round,
                "dayofweek": dayofweek,
                "venue": venue,
                "result": result,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "opponent": opponent,
                "possession": to_int(possession),
                "attendance": to_int(attendance),
                "captain": captain,
                "formation": formation,
                "opp_formation": opp_formation
            })
            added_matches += 1
            
        print(f"Đã lấy xong {added_matches} trận đấu của {team['name']}.")
        
        if team != teams[-1]:
            time.sleep(3)

    return all_fixtures_data

if __name__ == "__main__":
    data = scrape_fixtures()
    
    with open('data/top3_squads_fixtures.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"\nĐã lưu toàn bộ dữ liệu ({len(data)} bản ghi) vào data/top3_squads_fixtures.json")
