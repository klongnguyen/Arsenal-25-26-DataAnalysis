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

def scrape_keepers():
    teams = [
        {"name": "Arsenal", "url": "https://fbref.com/en/squads/18bb7c10/Arsenal-Stats"},
        {"name": "Manchester City", "url": "https://fbref.com/en/squads/b8fd03ef/Manchester-City-Stats"},
        {"name": "Manchester Utd", "url": "https://fbref.com/en/squads/19538871/Manchester-United-Stats"},
        {"name": "Brentford", "url": "https://fbref.com/en/squads/cd051869/Brentford-Stats"},
        {"name": "Aston Villa", "url": "https://fbref.com/en/squads/8602292d/Aston-Villa-Stats"},
        {"name": "West Ham", "url": "https://fbref.com/en/squads/7c21e445/West-Ham-United-Stats"}
    ]
    
    all_keepers_data = []
    
    for team in teams:
        print(f"Đang tải trang web của đội {team['name']}...")
        page = StealthyFetcher(headless=True).fetch(team['url'], solve_cloudflare=True)
        
        # Bảng stats_keeper_9
        table = page.css('table#stats_keeper_9')
        if not table:
            print(f"Không tìm thấy bảng Goalkeeping cho đội {team['name']}")
            continue
            
        rows = table[0].css('tbody tr')
        added_keepers = 0
        
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
                age_text = age_text.split('-')[0]
                age = to_int(age_text)
            
            # Stats (skipping gk_games / MP / Matches)
            starts = row.css('td[data-stat="gk_games_starts"]::text').get()
            minutes = row.css('td[data-stat="gk_minutes"]::text').get()
            minutes_90s = row.css('td[data-stat="minutes_90s"]::text').get()
            
            ga = row.css('td[data-stat="gk_goals_against"]::text').get()
            ga90 = row.css('td[data-stat="gk_goals_against_per90"]::text').get()
            sota = row.css('td[data-stat="gk_shots_on_target_against"]::text').get()
            saves = row.css('td[data-stat="gk_saves"]::text').get()
            save_pct = row.css('td[data-stat="gk_save_pct"]::text').get()
            
            wins = row.css('td[data-stat="gk_wins"]::text').get()
            ties = row.css('td[data-stat="gk_ties"]::text').get()
            losses = row.css('td[data-stat="gk_losses"]::text').get()
            
            clean_sheets = row.css('td[data-stat="gk_clean_sheets"]::text').get()
            clean_sheets_pct = row.css('td[data-stat="gk_clean_sheets_pct"]::text').get()
            
            pens_att = row.css('td[data-stat="gk_pens_att"]::text').get()
            pens_allowed = row.css('td[data-stat="gk_pens_allowed"]::text').get()
            pens_saved = row.css('td[data-stat="gk_pens_saved"]::text').get()
            pens_missed = row.css('td[data-stat="gk_pens_missed"]::text').get()
            pens_save_pct = row.css('td[data-stat="gk_pens_save_pct"]::text').get()
            
            all_keepers_data.append({
                "team": team['name'],
                "player": player,
                "nationality": nationality,
                "position": position.strip() if position else "",
                "age": age,
                "starts": to_int(starts),
                "min": to_int(minutes),
                "90s": to_float(minutes_90s),
                "ga": to_int(ga),
                "ga90": to_float(ga90),
                "sota": to_int(sota),
                "saves": to_int(saves),
                "save_pct": to_float(save_pct),
                "wins": to_int(wins),
                "ties": to_int(ties),
                "losses": to_int(losses),
                "clean_sheets": to_int(clean_sheets),
                "clean_sheets_pct": to_float(clean_sheets_pct),
                "pens_att": to_int(pens_att),
                "pens_allowed": to_int(pens_allowed),
                "pens_saved": to_int(pens_saved),
                "pens_missed": to_int(pens_missed),
                "pens_save_pct": to_float(pens_save_pct)
            })
            added_keepers += 1
            
        print(f"Đã lấy xong {added_keepers} thủ môn của {team['name']}.")
        
        if team != teams[-1]:
            time.sleep(3)

    return all_keepers_data

if __name__ == "__main__":
    data = scrape_keepers()
    
    with open('data/top3_squads_keepers.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"\nĐã lưu toàn bộ dữ liệu ({len(data)} bản ghi) vào data/top3_squads_keepers.json")
