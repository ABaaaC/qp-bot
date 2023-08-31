import requests
from bs4 import BeautifulSoup

def extract_schedule(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Identify the HTML elements containing schedule information
        schedule_elements = soup.find_all('div', class_='schedule-block')
        
        schedule = []
        for element in schedule_elements:
            date_element = element.find('div', class_='block-date-with-language-game')
            title_element, package_number_element = element.find_all('div', class_='h2-game-card')
            description_element = element.find('div', class_='techtext')
            place_element = element.find('div', class_='schedule-block-info-bar')
            price_element = element.find('div', class_='new-price')

            info_element = element.find_all('div', class_='schedule-info')
            time_element = info_element[2]
            address_element = info_element[1].find('div', class_='techtext-halfwhite')

            # Extract the game package number from the title
            title_text = title_element.get_text(strip=True) if title_element else None
            package_number_text = package_number_element.get_text(strip=True) if title_element else None
            if package_number_text and '#' in package_number_text:
                package_number = package_number_text.split('#')[-1].strip()

            game_info = {
                'date': date_element.get_text(strip=True) if date_element else None,
                'title': title_text if title_text != 'Квиз, плиз!' else 'Классика',
                'description': description_element.get_text(strip=True) if description_element else None,
                'place': place_element.contents[0].strip() if place_element else None,
                'package_number': package_number,
                'price': price_element.get_text(strip=True)[:4] if price_element else None,
                'time': time_element.get_text(strip=True).split()[-1] if time_element else None,
                'address': address_element.contents[0].strip() if address_element else None,
            }
            schedule.append(game_info)
        
        return schedule
    else:
        print(f"Failed to fetch content from {url}. Status code: {response.status_code}")
        return []

if __name__ == "__main__":
    target_url = "https://moscow.quizplease.ru/schedule"
    extracted_schedule = extract_schedule(target_url)
    
    if extracted_schedule:
        for game in extracted_schedule:
            print(f"Date: {game['date']}, Title: {game['title']}, Time: {game['time']}, Place: {game['place']}")
    else:
        print("No schedule information extracted.")
