import json
import pyodbc
import sys
import unicodedata

def normalize_name(name):
    if not name: return ""
    name = name.replace('ı', 'i').replace('ş', 's').replace('ğ', 'g').replace('ö', 'o').replace('ü', 'u').replace('ç', 'c')
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    return name.lower().strip()

def get_connection(db_name=None):
    server = r'LAPTOP-8I1OVUBF\SQLEXPRESS'
    database = db_name if db_name else 'master'
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    try:
        conn = pyodbc.connect(conn_str, autocommit=True)
        return conn
    except Exception as e:
        # Fallback to older driver if ODBC Driver 17 is not available
        try:
            conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
            conn = pyodbc.connect(conn_str, autocommit=True)
            return conn
        except Exception as e2:
            print(f"Lỗi kết nối CSDL: {e2}")
            sys.exit(1)

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Kiểm tra xem Database đã tồn tại chưa
    cursor.execute("SELECT name FROM master.dbo.sysdatabases WHERE name = N'FootballAnalysis'")
    exists = cursor.fetchone()
    
    if not exists:
        print("Đang tạo Database FootballAnalysis...")
        cursor.execute("CREATE DATABASE FootballAnalysis")
    else:
        print("Database FootballAnalysis đã tồn tại.")
    
    cursor.close()
    conn.close()

def setup_tables():
    conn = get_connection('FootballAnalysis')
    cursor = conn.cursor()
    
    # Xóa bảng cũ nếu tồn tại (theo thứ tự khóa ngoại)
    tables = ['historical_fixtures', 'historical_standings', 'fixtures', 'goalkeepers', 'player_misc', 'player_playing_time', 'player_shooting', 'players', 'teams']
    for table in tables:
        cursor.execute(f"""
        IF OBJECT_ID('{table}', 'U') IS NOT NULL 
        DROP TABLE {table};
        """)
        
    print("Đang tạo các bảng...")
    
    # 1. Bảng teams
    cursor.execute("""
    CREATE TABLE teams (
        team_id INT IDENTITY(1,1) PRIMARY KEY,
        team_name NVARCHAR(100) UNIQUE,
        rank INT,
        matches INT,
        wins INT,
        draws INT,
        losses INT,
        goals_for INT,
        goals_against INT,
        goal_diff INT,
        points INT,
        points_avg FLOAT,
        attendance_per_g INT,
        top_team_scorer NVARCHAR(100)
    )
    """)
    
    # 2. Bảng players
    cursor.execute("""
    CREATE TABLE players (
        player_id INT IDENTITY(1,1) PRIMARY KEY,
        team_id INT FOREIGN KEY REFERENCES teams(team_id),
        player_name NVARCHAR(100),
        nationality NVARCHAR(10),
        position NVARCHAR(50),
        age INT,
        starts INT,
        min INT,
        [90s] FLOAT,
        gls INT,
        ast INT,
        g_plus_a INT,
        g_minus_pk INT,
        pk INT,
        pkatt INT,
        crd_y INT,
        crd_r INT
    )
    """)
    
    # 3. Bảng goalkeepers
    cursor.execute("""
    CREATE TABLE goalkeepers (
        keeper_id INT IDENTITY(1,1) PRIMARY KEY,
        player_id INT FOREIGN KEY REFERENCES players(player_id),
        team_id INT FOREIGN KEY REFERENCES teams(team_id),
        ga INT,
        ga90 FLOAT,
        sota INT,
        saves INT,
        save_pct FLOAT,
        wins INT,
        ties INT,
        losses INT,
        clean_sheets INT,
        clean_sheets_pct FLOAT,
        pens_att INT,
        pens_allowed INT,
        pens_saved INT,
        pens_missed INT,
        pens_save_pct FLOAT
    )
    """)
    
    # 4. Bảng fixtures
    cursor.execute("""
    CREATE TABLE fixtures (
        match_id INT IDENTITY(1,1) PRIMARY KEY,
        team_id INT FOREIGN KEY REFERENCES teams(team_id),
        match_date DATE,
        comp NVARCHAR(100),
        match_round NVARCHAR(100),
        dayofweek NVARCHAR(10),
        venue NVARCHAR(50),
        result NVARCHAR(10),
        goals_for NVARCHAR(50),
        goals_against NVARCHAR(50),
        opponent NVARCHAR(100),
        possession INT,
        attendance INT,
        captain NVARCHAR(100),
        formation NVARCHAR(50),
        opp_formation NVARCHAR(50),
        xg_for FLOAT,
        xg_against FLOAT
    )
    """)
    
    # 5. Bảng player_shooting
    cursor.execute("""
    CREATE TABLE player_shooting (
        shooting_id INT IDENTITY(1,1) PRIMARY KEY,
        player_id INT FOREIGN KEY REFERENCES players(player_id),
        team_id INT FOREIGN KEY REFERENCES teams(team_id),
        gls INT,
        sh INT,
        sot INT,
        sot_pct FLOAT,
        sh_per90 FLOAT,
        sot_per90 FLOAT,
        g_per_sh FLOAT,
        g_per_sot FLOAT,
        dist FLOAT,
        fk INT,
        pk INT,
        pkatt INT,
        xg FLOAT,
        npxg FLOAT,
        npxg_per_sh FLOAT,
        xg_net FLOAT,
        npxg_net FLOAT
    )
    """)
    
    # 6. Bảng player_playing_time
    cursor.execute("""
    CREATE TABLE player_playing_time (
        pt_id INT IDENTITY(1,1) PRIMARY KEY,
        player_id INT FOREIGN KEY REFERENCES players(player_id),
        team_id INT FOREIGN KEY REFERENCES teams(team_id),
        matches_played INT,
        minutes INT,
        mn_per_mp INT,
        min_pct FLOAT,
        starts INT,
        mn_per_start INT,
        compl INT,
        subs INT,
        mn_per_sub INT,
        unsub INT,
        ppm FLOAT,
        on_goals_for INT,
        on_goals_against INT,
        plus_minus INT,
        plus_minus_per90 FLOAT,
        plus_minus_wowy FLOAT,
        xg_plus_minus FLOAT,
        xg_plus_minus_per90 FLOAT,
        xg_plus_minus_wowy FLOAT
    )
    """)
    
    # 7. Bảng player_misc
    cursor.execute("""
    CREATE TABLE player_misc (
        misc_id INT IDENTITY(1,1) PRIMARY KEY,
        player_id INT FOREIGN KEY REFERENCES players(player_id),
        team_id INT FOREIGN KEY REFERENCES teams(team_id),
        cards_yellow INT,
        cards_red INT,
        cards_yellow_red INT,
        fouls INT,
        fouled INT,
        offsides INT,
        crosses INT,
        interceptions INT,
        tackles_won INT,
        pens_won INT,
        pens_conceded INT,
        own_goals INT,
        ball_recoveries INT,
        aerials_won INT,
        aerials_lost INT,
        aerials_won_pct FLOAT
    )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Tạo bảng thành công.")

def insert_data():
    conn = get_connection('FootballAnalysis')
    cursor = conn.cursor()
    
    # 1. Insert Teams
    print("Đang chèn dữ liệu Teams...")
    with open('data/premier_league_standings.json', 'r', encoding='utf-8') as f:
        teams_data = json.load(f)
        
    for t in teams_data:
        cursor.execute("""
            INSERT INTO teams (team_name, rank, matches, wins, draws, losses, goals_for, goals_against, goal_diff, points, points_avg, attendance_per_g, top_team_scorer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            t['team'], t['rank'], t['matches'], t['wins'], t['draws'], t['losses'], 
            t['goals_for'], t['goals_against'], t['goal_diff'], t['points'], 
            t['points_avg'], int(t['attendance_per_g']) if t.get('attendance_per_g') else 0, 
            t.get('top_team_scorers', '')
        ))
    
    conn.commit()
    
    # Lấy map team_name -> team_id
    cursor.execute("SELECT team_name, team_id FROM teams")
    team_map = {row[0]: row[1] for row in cursor.fetchall()}
    
    # 2. Insert Players
    print("Đang chèn dữ liệu Players...")
    with open('data/top3_squads_standard_stats.json', 'r', encoding='utf-8') as f:
        players_data = json.load(f)
        
    for p in players_data:
        team_id = team_map.get(p['team'])
        if not team_id: continue
        cursor.execute("""
            INSERT INTO players (team_id, player_name, nationality, position, age, starts, min, [90s], gls, ast, g_plus_a, g_minus_pk, pk, pkatt, crd_y, crd_r)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            team_id, p['player'], p['nationality'], p['position'], p['age'],
            p['starts'], p['min'], p['90s'], p['gls'], p['ast'], p['g_plus_a'],
            p['g_minus_pk'], p['pk'], p['pkatt'], p['crd_y'], p['crd_r']
        ))
        
    conn.commit()
    
    # Lấy map (team_id, player_name) -> player_id
    cursor.execute("SELECT team_id, player_name, player_id FROM players")
    player_map = {(row[0], normalize_name(row[1])): row[2] for row in cursor.fetchall()}
    
    # 3. Insert Goalkeepers
    print("Đang chèn dữ liệu Goalkeepers...")
    with open('data/top3_squads_keepers.json', 'r', encoding='utf-8') as f:
        keepers_data = json.load(f)
        
    for gk in keepers_data:
        team_id = team_map.get(gk['team'])
        if not team_id: continue
        
        player_id = player_map.get((team_id, normalize_name(gk['player'])))
        if not player_id:
            continue
        
        cursor.execute("""
            INSERT INTO goalkeepers (player_id, team_id, ga, ga90, sota, saves, save_pct, wins, ties, losses, clean_sheets, clean_sheets_pct, pens_att, pens_allowed, pens_saved, pens_missed, pens_save_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player_id, team_id, gk['ga'], gk['ga90'], gk['sota'], gk['saves'], gk['save_pct'],
            gk['wins'], gk['ties'], gk['losses'], gk['clean_sheets'], gk['clean_sheets_pct'],
            gk['pens_att'], gk['pens_allowed'], gk['pens_saved'], gk['pens_missed'], gk['pens_save_pct']
        ))
        
    conn.commit()
    
    # 4. Insert Fixtures
    print("Đang chèn dữ liệu Fixtures...")
    with open('data/top3_squads_fixtures.json', 'r', encoding='utf-8') as f:
        fixtures_data = json.load(f)
        
    for fx in fixtures_data:
        team_id = team_map.get(fx['team'])
        if not team_id: continue
        
        # Xử lý chuỗi ngày rỗng
        match_date = fx['date'] if fx['date'] else None
        
        cursor.execute("""
            INSERT INTO fixtures (team_id, match_date, comp, match_round, dayofweek, venue, result, goals_for, goals_against, opponent, possession, attendance, captain, formation, opp_formation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            team_id, match_date, fx['comp'], fx['round'], fx['dayofweek'], fx['venue'], fx['result'],
            str(fx['goals_for']), str(fx['goals_against']), fx['opponent'], fx['possession'], fx['attendance'],
            fx['captain'], fx['formation'], fx['opp_formation']
        ))
        
    conn.commit()

    # 5. Insert Shooting
    print("Đang chèn dữ liệu Shooting...")
    with open('data/top3_squads_shooting.json', 'r', encoding='utf-8') as f:
        shooting_data = json.load(f)
    for sh in shooting_data:
        team_id = team_map.get(sh['team'])
        if not team_id: continue
        player_id = player_map.get((team_id, normalize_name(sh['player'])))
        if not player_id: continue
        cursor.execute("""
            INSERT INTO player_shooting (player_id, team_id, gls, sh, sot, sot_pct, sh_per90, sot_per90, g_per_sh, g_per_sot, dist, fk, pk, pkatt, xg, npxg, npxg_per_sh, xg_net, npxg_net)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player_id, team_id, sh.get('goals', 0), sh.get('shots', 0), sh.get('shots_on_target', 0), sh.get('shots_on_target_pct', 0),
            sh.get('shots_per90', 0), sh.get('shots_on_target_per90', 0), sh.get('goals_per_shot', 0), sh.get('goals_per_shot_on_target', 0),
            sh.get('average_shot_distance', 0), sh.get('shots_free_kicks', 0), sh.get('pens_made', 0), sh.get('pens_att', 0),
            sh.get('xg', 0), sh.get('npxg', 0), sh.get('npxg_per_shot', 0), sh.get('xg_net', 0), sh.get('npxg_net', 0)
        ))
    conn.commit()

    # 6. Insert Playing Time
    print("Đang chèn dữ liệu Playing Time...")
    with open('data/top3_squads_playing_time.json', 'r', encoding='utf-8') as f:
        pt_data = json.load(f)
    for pt in pt_data:
        team_id = team_map.get(pt['team'])
        if not team_id: continue
        player_id = player_map.get((team_id, normalize_name(pt['player'])))
        if not player_id: continue
        cursor.execute("""
            INSERT INTO player_playing_time (player_id, team_id, matches_played, minutes, mn_per_mp, min_pct, starts, mn_per_start, compl, subs, mn_per_sub, unsub, ppm, on_goals_for, on_goals_against, plus_minus, plus_minus_per90, plus_minus_wowy, xg_plus_minus, xg_plus_minus_per90, xg_plus_minus_wowy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player_id, team_id, pt.get('games', 0), pt.get('minutes', 0), pt.get('minutes_per_game', 0), pt.get('minutes_pct', 0),
            pt.get('games_starts', 0), pt.get('minutes_per_start', 0), pt.get('games_complete', 0), pt.get('games_subs', 0),
            pt.get('minutes_per_sub', 0), pt.get('unused_subs', 0), pt.get('points_per_game', 0), pt.get('on_goals_for', 0),
            pt.get('on_goals_against', 0), pt.get('plus_minus', 0), pt.get('plus_minus_per90', 0), pt.get('plus_minus_wowy', 0),
            pt.get('xg_plus_minus', 0), pt.get('xg_plus_minus_per90', 0), pt.get('xg_plus_minus_wowy', 0)
        ))
    conn.commit()

    # 7. Insert Misc
    print("Đang chèn dữ liệu Misc...")
    with open('data/top3_squads_misc.json', 'r', encoding='utf-8') as f:
        misc_data = json.load(f)
    for m in misc_data:
        team_id = team_map.get(m['team'])
        if not team_id: continue
        player_id = player_map.get((team_id, normalize_name(m['player'])))
        if not player_id: continue
        cursor.execute("""
            INSERT INTO player_misc (player_id, team_id, cards_yellow, cards_red, cards_yellow_red, fouls, fouled, offsides, crosses, interceptions, tackles_won, pens_won, pens_conceded, own_goals, ball_recoveries, aerials_won, aerials_lost, aerials_won_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player_id, team_id, m.get('cards_yellow', 0), m.get('cards_red', 0), m.get('cards_yellow_red', 0), m.get('fouls', 0),
            m.get('fouled', 0), m.get('offsides', 0), m.get('crosses', 0), m.get('interceptions', 0), m.get('tackles_won', 0),
            m.get('pens_won', 0), m.get('pens_conceded', 0), m.get('own_goals', 0), m.get('ball_recoveries', 0),
            m.get('aerials_won', 0), m.get('aerials_lost', 0), m.get('aerials_won_pct', 0)
        ))
    conn.commit()
    cursor.close()
    conn.close()
    print("Chèn dữ liệu hoàn tất!")

if __name__ == "__main__":
    setup_database()
    setup_tables()
    insert_data()
