import json
import time
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from scrapling.fetchers import StealthyFetcher

def to_int(val):
    if not val:
        return 0
    try:
        return int(val.replace(',', ''))
    except:
        return 0

def get_text(row, data_stat):
    texts = row.css(f'[data-stat="{data_stat}"]').xpath('.//text()').getall()
    if texts:
        return " ".join(texts).strip()
    return ""

def scrape_historical_fixtures():
    # Danh sách 10 nhà vô địch gần nhất (2014/15 - 2023/24)
    champions = [
        {"season": "2014-2015", "team": "Chelsea", "url": "https://fbref.com/en/squads/cff3d9bb/2014-2015/Chelsea-Stats"},
        {"season": "2015-2016", "team": "Leicester City", "url": "https://fbref.com/en/squads/a2d435b3/2015-2016/Leicester-City-Stats"},
        {"season": "2016-2017", "team": "Chelsea", "url": "https://fbref.com/en/squads/cff3d9bb/2016-2017/Chelsea-Stats"},
        {"season": "2017-2018", "team": "Manchester City", "url": "https://fbref.com/en/squads/b8fd03ef/2017-2018/Manchester-City-Stats"},
        {"season": "2018-2019", "team": "Manchester City", "url": "https://fbref.com/en/squads/b8fd03ef/2018-2019/Manchester-City-Stats"},
        {"season": "2019-2020", "team": "Liverpool", "url": "https://fbref.com/en/squads/822bd0ba/2019-2020/Liverpool-Stats"},
        {"season": "2020-2021", "team": "Manchester City", "url": "https://fbref.com/en/squads/b8fd03ef/2020-2021/Manchester-City-Stats"},
        {"season": "2021-2022", "team": "Manchester City", "url": "https://fbref.com/en/squads/b8fd03ef/2021-2022/Manchester-City-Stats"},
        {"season": "2022-2023", "team": "Manchester City", "url": "https://fbref.com/en/squads/b8fd03ef/2022-2023/Manchester-City-Stats"},
        {"season": "2023-2024", "team": "Manchester City", "url": "https://fbref.com/en/squads/b8fd03ef/2023-2024/Manchester-City-Stats"}
    ]
    
    all_fixtures_data = []
    
    for champ in champions:
        print(f"Đang tải trang web của đội vô địch {champ['team']} (mùa {champ['season']})...")
        try:
            page = StealthyFetcher(headless=True).fetch(champ['url'], solve_cloudflare=True)
            
            table = page.css('table#matchlogs_for')
            if not table:
                print(f"Không tìm thấy bảng Scores & Fixtures cho {champ['team']} mùa {champ['season']}")
                continue
                
            rows = table[0].css('tbody tr')
            added_matches = 0
            
            for row in rows:
                if 'spacer' in row.attrib.get('class', '') or 'thead' in row.attrib.get('class', ''):
                    continue
                    
                date = get_text(row, 'date')
                if not date:
                    continue
                    
                comp = get_text(row, 'comp')
                # Chỉ lấy các trận ở Premier League
                if comp != "Premier League":
                    continue
                    
                match_round = get_text(row, 'round')
                dayofweek = get_text(row, 'dayofweek')
                venue = get_text(row, 'venue')
                result = get_text(row, 'result')
                goals_for = get_text(row, 'goals_for')
                goals_against = get_text(row, 'goals_against')
                opponent = get_text(row, 'opponent')
                possession = get_text(row, 'possession')
                
                # Advanced stats
                xg_for = get_text(row, 'xg_for')
                xg_against = get_text(row, 'xg_against')
                
                all_fixtures_data.append({
                    "season": champ['season'],
                    "team": champ['team'],
                    "date": date,
                    "comp": comp,
                    "round": match_round,
                    "venue": venue,
                    "result": result,
                    "goals_for": goals_for,
                    "goals_against": goals_against,
                    "opponent": opponent,
                    "possession": to_int(possession),
                    "xg_for": float(xg_for) if xg_for else 0.0,
                    "xg_against": float(xg_against) if xg_against else 0.0
                })
                added_matches += 1
                
            print(f"Đã lấy xong {added_matches} trận đấu của {champ['team']} mùa {champ['season']}.")
            
            if champ != champions[-1]:
                time.sleep(3)
                
        except Exception as e:
            print(f"Lỗi khi cào dữ liệu lịch thi đấu {champ['team']} mùa {champ['season']}: {str(e)}")
            
    return all_fixtures_data

if __name__ == "__main__":
    # Đảm bảo lưu đúng thư mục data (đi lùi 2 cấp nếu chạy script từ scripts/scrapers)
    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    data = scrape_historical_fixtures()
    
    output_path = os.path.join(data_dir, 'historical_champions_fixtures.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"\nĐã lưu toàn bộ dữ liệu ({len(data)} bản ghi) vào {output_path}")
