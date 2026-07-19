from scrapling.fetchers import StealthyFetcher
import json
import time

def scrape_premier_league():
    url = 'https://fbref.com/en/comps/9/Premier-League-Stats'
    
    print("Đang tải trang web...")
    # Sử dụng StealthyFetcher để giả lập trình duyệt thực, vượt qua Cloudflare
    page = StealthyFetcher(headless=True).fetch(url, solve_cloudflare=True)

    # Lấy bảng xếp hạng tổng (thường là bảng stats_table đầu tiên trên trang)
    # FBref có thể có nhiều bảng, ta lấy bảng đầu tiên [0]
    standings_table = page.css('table.stats_table')[0]
    
    # Trích xuất tất cả các hàng (tr) trong phần thân bảng (tbody)
    rows = standings_table.css('tbody tr')

    teams_data = []

    for row in rows:
        # Dùng ::text để lấy phần chữ bên trong thẻ HTML
        team_name = row.css('[data-stat="team"] a::text').get()
        matches = row.css('td[data-stat="games"]::text').get()
        wins = row.css('td[data-stat="wins"]::text').get()
        draws = row.css('td[data-stat="ties"]::text').get()
        losses = row.css('td[data-stat="losses"]::text').get()
        goals_for = row.css('td[data-stat="goals_for"]::text').get()
        goals_against = row.css('td[data-stat="goals_against"]::text').get()
        goal_diff = row.css('td[data-stat="goal_diff"]::text').get()
        points = row.css('td[data-stat="points"]::text').get()
        points_avg = row.css('td[data-stat="points_avg"]::text').get()
        attendance_per_g = row.css('td[data-stat="attendance_per_g"]::text').get()
        top_team_scorers = row.css('td[data-stat="top_team_scorers"] a::text').get()

        # Lọc bỏ các hàng trống (nếu có)
        if team_name:
            teams_data.append({
                'rank': len(teams_data) + 1,
                'team': team_name,
                'matches': int(matches) if matches else 0,
                'wins': int(wins) if wins else 0,
                'draws': int(draws) if draws else 0,
                'losses': int(losses) if losses else 0,
                'goals_for': int(goals_for) if goals_for else 0,
                'goals_against': int(goals_against) if goals_against else 0,
                'goal_diff': int(goal_diff) if goal_diff else 0,
                'points': int(points) if points else 0,
                'points_avg': float(points_avg) if points_avg else 0.0,
                'attendance_per_g': attendance_per_g.replace(',', '') if attendance_per_g else "0",
                'top_team_scorers': top_team_scorers if top_team_scorers else ""
            })

    return teams_data

if __name__ == "__main__":
    data = scrape_premier_league()
    
    # In ra màn hình xem thử 5 đội dẫn đầu
    for team in data[:5]:
        print(f"{team['rank']}. {team['team']} - {team['points']} pts")

    # Lưu dữ liệu vào file JSON để xử lý tiếp (ví dụ: đưa vào database)
    with open('data/premier_league_standings.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print("\nĐã lưu toàn bộ dữ liệu vào data/premier_league_standings.json")
