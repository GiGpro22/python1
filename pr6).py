import aiohttp
import asyncio

API_KEY = 'hVpQjCxNMgh6cmu3gADPzQ==RfqC4TpYUyRmfRcF'

async def get_city_data(session, name):
    """Получаем данные о городе"""
    api_url = f'https://api.api-ninjas.com/v1/city?name={name}'
    try:
        async with session.get(api_url, headers={'X-Api-Key': API_KEY}) as response:
            if response.status == 200:
                data = await response.json()
                return data[0] if data else None
            print(f"Ошибка города {name}: HTTP {response.status}")
            return None
    except Exception as e:
        print(f"Ошибка запроса города {name}: {str(e)}")
        return None

async def get_country_data(session, country_code):
    """Получаем данные о стране"""
    api_url = f'https://api.api-ninjas.com/v1/country?name={country_code}'
    try:
        async with session.get(api_url, headers={'X-Api-Key': API_KEY}) as response:
            if response.status == 200:
                data = await response.json()
                return data[0] if data else None
            return None
    except Exception:
        return None

async def process_city(city_name):
    """Обработка данных для одного города"""
    async with aiohttp.ClientSession() as session:
        try:
            # 1. Получаем данные города
            city_data = await get_city_data(session, city_name)
            if not city_data:
                print(f"Город {city_name} не найден")
                return

            country_code = city_data.get('country')
            if not country_code:
                print(f"У города {city_name} нет кода страны")
                return

            # 2. Получаем данные страны
            country_data = await get_country_data(session, country_code)

            # 3. Выводим результат
            print(f"\nГород: {city_name}")
            print(f"Координаты: {city_data.get('latitude')}, {city_data.get('longitude')}")
            print(f"Население города: {city_data.get('population', 'N/A'):,}")

            if country_data:
                print(f"\nСтрана: {country_data.get('name', 'N/A')} ({country_code})")
                print(f"Столица: {country_data.get('capital', 'N/A')}")
                print(f"ВВП на душу: ${country_data.get('gdp_per_capita', 'N/A'):,}")

        except Exception as e:
            print(f"Критическая ошибка обработки города {city_name}: {str(e)}")

async def main():
    """Основная функция"""
    cities = ["Berlin", "Paris", "Tokyo", "London", "New York", "Moscow"]
    await asyncio.gather(*[process_city(city) for city in cities])

if __name__ == '__main__':
    asyncio.run(main())