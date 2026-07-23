import asyncio
import aiohttp
import json
import os
import sys
from understat import Understat

sys.stdout.reconfigure(encoding='utf-8')

async def scrape_all():
    seasons = range(2014, 2025)
    
    all_teams_xg = []
    all_matches_xg = []
    
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        
        for year in seasons:
            season_str = f"{year}-{year+1}"
            print(f"Lấy dữ liệu xG mùa {season_str} từ Understat...")
            try:
                teams = await understat.get_teams("epl", year)
                
                for team_data in teams:
                    team_name = team_data['title']
                    history = team_data['history']
                    
                    total_xg = sum([h['xG'] for h in history])
                    total_xga = sum([h['xGA'] for h in history])
                    
                    all_teams_xg.append({
                        "season": season_str,
                        "understat_team": team_name,
                        "xg": round(total_xg, 2),
                        "xga": round(total_xga, 2),
                        "xg_diff": round(total_xg - total_xga, 2)
                    })
                    
                    for h in history:
                        all_matches_xg.append({
                            "season": season_str,
                            "understat_team": team_name,
                            "date": h['date'].split(' ')[0],
                            "xg_for": round(h['xG'], 2),
                            "xg_against": round(h['xGA'], 2)
                        })
            except Exception as e:
                print(f"Lỗi khi cào dữ liệu mùa {season_str}: {e}")
                
    return all_teams_xg, all_matches_xg

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    teams_xg, matches_xg = asyncio.run(scrape_all())
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    teams_path = os.path.join(data_dir, 'understat_teams_xg.json')
    matches_path = os.path.join(data_dir, 'understat_matches_xg.json')
    
    with open(teams_path, 'w', encoding='utf-8') as f:
        json.dump(teams_xg, f, ensure_ascii=False, indent=4)
        
    with open(matches_path, 'w', encoding='utf-8') as f:
        json.dump(matches_xg, f, ensure_ascii=False, indent=4)
        
    print(f"Đã lưu {len(teams_xg)} đội bóng và {len(matches_xg)} trận đấu vào thư mục data.")
