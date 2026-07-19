import pyodbc

def get_connection():
    server = r'LAPTOP-8I1OVUBF\SQLEXPRESS'
    database = 'FootballAnalysis'
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    return pyodbc.connect(conn_str, autocommit=True)

# Dữ liệu từ người dùng
user_input = """
https://assets.arsenal.com/prod/images/medium_square/b22b5eee4eb2-1-david-raya.png
https://assets.arsenal.com/prod/images/medium_square/efd02a29e98d-13-kepa-arrizabalaga.png
https://assets.arsenal.com/prod/images/medium_square/c88bc8a5f6a1-9x16-im-no-background.png
https://assets.arsenal.com/prod/images/medium_square/acb476e282e8-2-william-saliba.png
https://assets.arsenal.com/prod/images/medium_square/4571a2d817f5-35-tommy-setford.png
https://assets.arsenal.com/prod/images/medium_square/7ca5a09b28a6-3-cristhian-mosquera.png
https://assets.arsenal.com/prod/images/medium_square/c83cc5eae5b9-4-ben-white.png
https://assets.arsenal.com/prod/images/medium_square/f0078dc16527-5-piero-hincapie.png
https://assets.arsenal.com/prod/images/medium_square/bce152cb2522-6-gabriel-magalhaes.png
https://assets.arsenal.com/prod/images/medium_square/3016059da8aa-12-jurrien-timber.png
https://assets.arsenal.com/prod/images/medium_square/7e33fd9a4107-33-riccardo-calafiori.png
https://assets.arsenal.com/prod/images/medium_square/1e9b0547f835-49-myles-lewis-skelly.png
https://assets.arsenal.com/prod/images/medium_square/2e86615cc272-8-martin-odegaard.png
https://assets.arsenal.com/prod/images/medium_square/f00b2940dc17-10-eze.png
https://assets.arsenal.com/prod/images/medium_square/37a6aab2a31f-16-christian-norgaard.png
https://assets.arsenal.com/prod/images/medium_square/aa4948097821-fabio-vieira-profile.png
https://assets.arsenal.com/prod/images/medium_square/0dcc2bebe505-22-ethan-nwaneri.png
https://assets.arsenal.com/prod/images/medium_square/7a4cb0eddeec-23-mikel-merino.png
https://assets.arsenal.com/prod/images/medium_square/89a2025f4c16-36-martin-zubimendi.png
https://assets.arsenal.com/prod/images/medium_square/425d06dffbbc-41-declan-rice.png
https://assets.arsenal.com/prod/images/medium_square/8477ef76d028-7-bukayo-saka.png
https://assets.arsenal.com/prod/images/medium_square/53d91cc81f2e-9-gabriel-jesus.png
https://assets.arsenal.com/prod/images/medium_square/7eea33c0f65f-11-gabriel-martinelli.png
https://assets.arsenal.com/prod/images/medium_square/c35e10005c3b-14-viktor-gyokeres.png
https://assets.arsenal.com/prod/images/medium_square/85956f966d90-20-noni-madueke.png
https://assets.arsenal.com/prod/images/medium_square/012e4fe902f1-reiss-nelson.png
https://assets.arsenal.com/prod/images/medium_square/4bb4301201cd-29-kai-havertz.png

Benjamin sesko:
https://dynamic-crop-cdn.scoreplay.io/472/4896326/media_102559907_102167031.jpg?fmt=webp&f=center&w=600&h=818

Leny Yoro: https://dynamic-crop-cdn.scoreplay.io/472/4896325/media_102559869_102166993_compressed.jpg?fmt=webp&f=center&w=600&h=818

Lisandro Martínez:https://dynamic-crop-cdn.scoreplay.io/472/4896325/media_102559864_102166988.jpg?fmt=webp&f=center&w=600&h=818

Patrick Dorgu: https://dynamic-crop-cdn.scoreplay.io/472/4896325/media_102559867_102166991.jpg?fmt=webp&f=center&w=600&h=818

Altay Bayındır:https://dynamic-crop-cdn.scoreplay.io/472/4896327/media_102559947_102167070.jpg?fmt=webp&f=center&w=600&h=818

Rayan Aït-Nouri: https://www.mancity.com/meta/media/axsdvp2v/rayan-ait-nouri-elec-bl.png?width=282&quality=100

Joško Gvardiol: https://www.mancity.com/meta/media/5mifkhls/josko-gvardiol-elec-bl.png?width=282&quality=100

Ruben Dias: https://www.mancity.com/meta/media/v2xnzosw/ruben-dias-elec-bl.png?width=282&quality=100

Bernardo Silva:
https://resources.premierleague.com/premierleague25/photos/players/110x140/165809.png

John Stone: https://resources.premierleague.com/premierleague25/photos/players/110x140/97299.png
"""

import re

def parse_input(text):
    player_images = []
    lines = text.strip().split('\n')
    
    current_name = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if 'http' in line and ':' not in line.split('http')[0]:
            # Chỉ có URL (ví dụ link arsenal)
            url = line
            # Trích xuất tên từ URL của arsenal: 
            # ví dụ: b22b5eee4eb2-1-david-raya.png -> david raya
            match = re.search(r'-(\d+-)?([a-z-]+)\.png', url)
            name = None
            if match:
                name_part = match.group(2)
                # Loại trừ những tên ko hợp lệ
                if 'im-no-background' not in name_part and 'profile' not in name_part:
                    name = name_part.replace('-', ' ')
                elif 'profile' in name_part:
                    name = name_part.replace('-profile', '').replace('-', ' ')
            
            if name:
                player_images.append({'name': name, 'url': url})
        elif ':' in line:
            # Dạng Tên: URL
            parts = line.split(':', 1)
            name = parts[0].strip()
            url = parts[1].strip()
            
            # fix url bị thiếu do split
            if url.startswith('//'):
                url = 'https:' + url
                
            if name and url:
                if name.lower() == 'john stone':
                    name = 'John Stones' # fix typo
                player_images.append({'name': name, 'url': url})
                
    return player_images

def update_images_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    players_data = parse_input(user_input)
    print(f"Đã phân tích được {len(players_data)} ảnh cầu thủ từ text của bạn.")
    
    cursor.execute("SELECT player_id, player_name FROM players")
    db_players = cursor.fetchall()
    
    matched_count = 0
    for p_data in players_data:
        p_name_lower = p_data['name'].lower()
        url = p_data['url']
        
        # Tìm cầu thủ trong DB khớp tên
        matched = False
        for db_p in db_players:
            db_id = db_p[0]
            db_name = db_p[1].lower()
            
            # Khớp chuỗi đơn giản
            if p_name_lower in db_name or db_name in p_name_lower:
                cursor.execute("UPDATE players SET image_url = ? WHERE player_id = ?", (url, db_id))
                print(f"Đã cập nhật ảnh cho {db_p[1]} (Khớp với: {p_data['name']})")
                matched = True
                matched_count += 1
                break
                
        if not matched:
            print(f"Không tìm thấy cầu thủ: {p_data['name']} trong DB để cập nhật.")
            
    print(f"\\nHoàn tất! Đã cập nhật thành công {matched_count} cầu thủ.")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    update_images_db()
