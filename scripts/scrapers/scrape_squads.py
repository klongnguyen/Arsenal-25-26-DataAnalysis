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

def to_float(val):
    if not val:
        return 0.0
    try:
        return float(val.replace(',', ''))
    except:
        return 0.0

def scrape_squad_standard_stats():
    teams = [
        {"name": "Arsenal", "url": "https://fbref.com/en/squads/18bb7c10/Arsenal-Stats"},
        {"name": "Manchester City", "url": "https://fbref.com/en/squads/b8fd03ef/Manchester-City-Stats"},
        {"name": "Manchester Utd", "url": "https://fbref.com/en/squads/19538871/Manchester-United-Stats"}
    ]
    
    all_players_data = []
    
    for team in teams:
        print(f"Đang tải trang web của đội {team['name']}...")
        page = StealthyFetcher(headless=True).fetch(team['url'], solve_cloudflare=True)
        
        # Bảng stats_standard_9
        table = page.css('table#stats_standard_9')
        if not table:
            print(f"Không tìm thấy bảng standard stats cho đội {team['name']}")
            continue
            
        rows = table[0].css('tbody tr')
        added_players = 0
        
        for row in rows:
            # Player name
            player = row.css('th[data-stat="player"] a::text').get() or row.css('th[data-stat="player"]::text').get()
            
            # Skip empty rows or totals
            if not player or player.strip().lower() in ('squad total', 'opponent total'):
                continue
                
            player = player.strip()
            
            # Nationality
            nat_text = row.css('td[data-stat="nationality"]').xpath('.//text()').getall()
                
            nationality = ""
            if nat_text:
                combined_nat = " ".join(nat_text).strip()
                if combined_nat:
                    nationality = combined_nat.split()[-1]
                
            position = row.css('td[data-stat="position"]::text').get()
            age_text = row.css('td[data-stat="age"]::text').get()
            age = 0
            if age_text:
                age_text = age_text.split('-')[0] # Sometimes age is like '27-142' meaning years-days
                age = to_int(age_text)
            
            # Stats
            games_starts = row.css('td[data-stat="games_starts"]::text').get()
            minutes = row.css('td[data-stat="minutes"]::text').get()
            minutes_90s = row.css('td[data-stat="minutes_90s"]::text').get()
            goals = row.css('td[data-stat="goals"]::text').get()
            assists = row.css('td[data-stat="assists"]::text').get()
            goals_assists = row.css('td[data-stat="goals_assists"]::text').get()
            goals_pens = row.css('td[data-stat="goals_pens"]::text').get()
            pens_made = row.css('td[data-stat="pens_made"]::text').get()
            pens_att = row.css('td[data-stat="pens_att"]::text').get()
            cards_yellow = row.css('td[data-stat="cards_yellow"]::text').get()
            cards_red = row.css('td[data-stat="cards_red"]::text').get()
            
            all_players_data.append({
                "team": team['name'],
                "player": player,
                "nationality": nationality,
                "position": position.strip() if position else "",
                "age": age,
                "starts": to_int(games_starts),
                "min": to_int(minutes),
                "90s": to_float(minutes_90s),
                "gls": to_int(goals),
                "ast": to_int(assists),
                "g_plus_a": to_int(goals_assists),
                "g_minus_pk": to_int(goals_pens),
                "pk": to_int(pens_made),
                "pkatt": to_int(pens_att),
                "crd_y": to_int(cards_yellow),
                "crd_r": to_int(cards_red)
            })
            added_players += 1
            
        print(f"Đã lấy xong {added_players} cầu thủ của {team['name']}.")
        
        # Nghỉ một chút giữa các trang để tránh bị block (chỉ chờ nếu chưa phải đội cuối cùng)
        if team != teams[-1]:
            time.sleep(3)

    return all_players_data

if __name__ == "__main__":
    data = scrape_squad_standard_stats()
    
    with open('data/top3_squads_standard_stats.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"\nĐã lưu toàn bộ dữ liệu ({len(data)} bản ghi) vào data/top3_squads_standard_stats.json")
