import json
import time
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from scrapling.fetchers import StealthyFetcher

def scrape_historical_standings():
    seasons = [
        "2014-2015", "2015-2016", "2016-2017", "2017-2018", 
        "2018-2019", "2019-2020", "2020-2021", "2021-2022", 
        "2022-2023", "2023-2024", "2024-2025"
    ]
    
    all_seasons_data = []
    
    for season in seasons:
        url = f'https://fbref.com/en/comps/9/{season}/{season}-Premier-League-Stats'
        print(f"Đang tải trang web cho mùa giải {season}...")
        
        try:
            page = StealthyFetcher(headless=True).fetch(url, solve_cloudflare=True)
            
            # Lấy bảng xếp hạng tổng
            tables = page.css('table.stats_table')
            if not tables:
                print(f"Không tìm thấy bảng xếp hạng cho mùa {season}")
                continue
                
            standings_table = tables[0]
            rows = standings_table.css('tbody tr')
            
            season_teams = []
            
            for row in rows:
                team_name = row.css('[data-stat="team"] a::text').get()
                matches = row.css('td[data-stat="games"]::text').get()
                wins = row.css('td[data-stat="wins"]::text').get()
                draws = row.css('td[data-stat="ties"]::text').get()
                losses = row.css('td[data-stat="losses"]::text').get()
                goals_for = row.css('td[data-stat="goals_for"]::text').get()
                goals_against = row.css('td[data-stat="goals_against"]::text').get()
                goal_diff = row.css('td[data-stat="goal_diff"]::text').get()
                points = row.css('td[data-stat="points"]::text').get()
                
                # Advanced stats (có thể không có đối với các mùa trước 2017/2018)
                xg = row.css('td[data-stat="xg"]::text').get()
                xga = row.css('td[data-stat="xg_against"]::text').get()
                xg_diff = row.css('td[data-stat="xg_diff"]::text').get()
                
                if team_name:
                    season_teams.append({
                        'season': season,
                        'rank': len(season_teams) + 1,
                        'team': team_name,
                        'matches': int(matches) if matches else 0,
                        'wins': int(wins) if wins else 0,
                        'draws': int(draws) if draws else 0,
                        'losses': int(losses) if losses else 0,
                        'goals_for': int(goals_for) if goals_for else 0,
                        'goals_against': int(goals_against) if goals_against else 0,
                        'goal_diff': int(goal_diff) if goal_diff else 0,
                        'points': int(points) if points else 0,
                        'xg': float(xg) if xg else 0.0,
                        'xga': float(xga) if xga else 0.0,
                        'xg_diff': float(xg_diff) if xg_diff else 0.0
                    })
            
            all_seasons_data.extend(season_teams)
            print(f"Đã lấy thành công {len(season_teams)} đội của mùa {season}.")
            
            if season != seasons[-1]:
                time.sleep(3) # Tránh bị block
                
        except Exception as e:
            print(f"Lỗi khi cào dữ liệu mùa {season}: {str(e)}")
            
    return all_seasons_data

if __name__ == "__main__":
    # Đảm bảo lưu đúng thư mục data (đi lùi 2 cấp nếu chạy script từ scripts/scrapers)
    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    data = scrape_historical_standings()
    
    output_path = os.path.join(data_dir, 'historical_standings.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"\nĐã lưu toàn bộ dữ liệu ({len(data)} bản ghi) vào {output_path}")
