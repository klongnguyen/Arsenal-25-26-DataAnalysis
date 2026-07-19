import pyodbc

def get_connection():
    server = r'LAPTOP-8I1OVUBF\SQLEXPRESS'
    database = 'FootballAnalysis'
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    return pyodbc.connect(conn_str, autocommit=True)

def update_transparent_logos():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Link logo SVG từ Wikipedia (trong suốt 100% và sắc nét)
    logos = {
        "Arsenal": "https://upload.wikimedia.org/wikipedia/en/5/53/Arsenal_FC.svg",
        "Manchester City": "https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg",
        "Manchester Utd": "https://upload.wikimedia.org/wikipedia/en/7/7a/Manchester_United_FC_crest.svg",
        "Brentford": "https://upload.wikimedia.org/wikipedia/en/2/2a/Brentford_FC_crest.svg",
        "Aston Villa": "https://upload.wikimedia.org/wikipedia/en/9/9a/Aston_Villa_FC_new_crest.svg",
        "West Ham": "https://upload.wikimedia.org/wikipedia/en/c/c2/West_Ham_United_FC_logo.svg"
    }
    
    for team, url in logos.items():
        cursor.execute("UPDATE teams SET logo_url = ? WHERE team_name = ?", (url, team))
        print(f"Đã cập nhật logo trong suốt cho {team}")
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    update_transparent_logos()
