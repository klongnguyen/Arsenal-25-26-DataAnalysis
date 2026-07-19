from scrapling.fetchers import StealthyFetcher
import json

def scrape_manutd_players():
    url = "https://www.manutd.com/en/teams/mens-team"
    print("Đang tải trang web Man Utd...")
    page = StealthyFetcher(headless=True).fetch(url, solve_cloudflare=True)
    
    # Mở file để debug
    with open('debug/manutd_debug.html', 'w', encoding='utf-8') as f:
        f.write(page.text)
        
    players = []
    
    # Tìm các div chứa thẻ profileCard
    # Theo ảnh người dùng gửi:
    # <div class="profileCard_profileCard_...">
    # Có thẻ img với alt là tên hoặc thẻ a/div chứa tên
    
    cards = page.css('div[data-component="ProfileCard"]')
    print(f"Tìm thấy {len(cards)} thẻ cầu thủ.")
    
    for card in cards:
        # Tên thường nằm trong thẻ chứa details
        # Hoặc thẻ a
        # Mình sẽ dùng XPath để lấy tất cả text
        name_elements = card.css('div[class*="profileCard_playerDetails"] *::text').getall()
        # Hoặc lấy thuộc tính alt của ảnh
        img_element = card.css('img')
        img_url = ""
        name = ""
        
        if img_element:
            img_url = img_element[0].attrib.get('src') or img_element[0].attrib.get('srcset', '').split(' ')[0]
            name = img_element[0].attrib.get('alt', '')
            
        # Làm sạch tên
        if name:
            name = name.strip()
            # Bỏ chữ 'IMAGE - ' nếu có
            if name.startswith('IMAGE - '):
                name = name.replace('IMAGE - ', '')
                
        if name and img_url:
            players.append({
                'name': name,
                'image_url': img_url
            })
            
    with open('data/manutd_players_images.json', 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=4)
        
    print(f"Lấy thành công {len(players)} ảnh cầu thủ.")

if __name__ == "__main__":
    scrape_manutd_players()
