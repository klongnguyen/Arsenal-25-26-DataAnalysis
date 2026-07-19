import json
import time
from scrapling.fetchers import StealthyFetcher

def parse_table(page, table_id, team_name):
    table = page.css(f'table#{table_id}')
    if not table:
        print(f"Không tìm thấy {table_id} cho đội {team_name}")
        return []
    
    rows = table[0].css('tbody tr')
    data = []
    
    for row in rows:
        player = row.css('th[data-stat="player"] a::text').get() or row.css('th[data-stat="player"]::text').get()
        if not player or player.strip().lower() in ('squad total', 'opponent total'):
            continue
        player = player.strip()
        
        row_data = {
            "team": team_name,
            "player": player
        }
        
        tds = row.css('td[data-stat]')
        for td in tds:
            stat_name = td.attrib.get('data-stat')
            # Xử lý đặc biệt cho quốc tịch vì có thể có span/icon
            if stat_name == "nationality":
                nat_text = td.xpath('.//text()').getall()
                val = ""
                if nat_text:
                    combined_nat = " ".join(nat_text).strip()
                    if combined_nat:
                        val = combined_nat.split()[-1]
            else:
                val = td.xpath('.//text()').get()
                if val:
                    val = val.strip()
                    # Lọc tuổi (vd: 27-142 -> 27)
                    if stat_name == "age" and '-' in val:
                        val = val.split('-')[0]
                        
                    # Ép kiểu dữ liệu
                    try:
                        if '.' in val:
                            val = float(val.replace(',', ''))
                        else:
                            val = int(val.replace(',', ''))
                    except:
                        pass
                else:
                    val = 0 # Mặc định là 0 nếu trống
            
            row_data[stat_name] = val
        data.append(row_data)
        
    return data

def scrape_advanced_stats():
    teams = [
        {"name": "Arsenal", "url": "https://fbref.com/en/squads/18bb7c10/Arsenal-Stats"},
        {"name": "Manchester City", "url": "https://fbref.com/en/squads/b8fd03ef/Manchester-City-Stats"},
        {"name": "Manchester Utd", "url": "https://fbref.com/en/squads/19538871/Manchester-United-Stats"}
    ]
    
    all_shooting = []
    all_playing_time = []
    all_misc = []
    
    for team in teams:
        print(f"Đang tải trang web của đội {team['name']}...")
        page = StealthyFetcher(headless=True).fetch(team['url'], solve_cloudflare=True)
        
        # 1. Shooting
        shooting_data = parse_table(page, 'stats_shooting_9', team['name'])
        all_shooting.extend(shooting_data)
        
        # 2. Playing Time
        playing_time_data = parse_table(page, 'stats_playing_time_9', team['name'])
        all_playing_time.extend(playing_time_data)
        
        # 3. Miscellaneous Stats
        misc_data = parse_table(page, 'stats_misc_9', team['name'])
        all_misc.extend(misc_data)
        
        print(f"Đã trích xuất xong 3 bảng dữ liệu cho {team['name']}")
        time.sleep(2) # Nghỉ một chút để tránh bị block

    # Lưu dữ liệu
    with open('data/top3_squads_shooting.json', 'w', encoding='utf-8') as f:
        json.dump(all_shooting, f, ensure_ascii=False, indent=4)
        print(f"Đã lưu top3_squads_shooting.json ({len(all_shooting)} bản ghi)")
        
    with open('data/top3_squads_playing_time.json', 'w', encoding='utf-8') as f:
        json.dump(all_playing_time, f, ensure_ascii=False, indent=4)
        print(f"Đã lưu top3_squads_playing_time.json ({len(all_playing_time)} bản ghi)")

    with open('data/top3_squads_misc.json', 'w', encoding='utf-8') as f:
        json.dump(all_misc, f, ensure_ascii=False, indent=4)
        print(f"Đã lưu top3_squads_misc.json ({len(all_misc)} bản ghi)")

if __name__ == "__main__":
    scrape_advanced_stats()
