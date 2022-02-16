import asyncio
import aiohttp
import requests 
import os
from bs4 import BeautifulSoup


def get_soup(comics_url):
    """Получаем объект супа из comics_url"""
    r = requests.get(comics_url)
    soup = BeautifulSoup(r.text, 'lxml')

    return soup

def get_comics_pages(comics_url):
    """Получаем ссылки на страницы сайта с номерами"""
    comics_pages = []
    soup = get_soup(comics_url)
    try:
        last_page_number = int(soup.find(title="Последняя").get('href').split('/')[-1])
        for i in range(1, last_page_number + 1):
            comics_pages.append(f'{comics_url}/page/{i}')
    except:
        comics_pages.append(comics_url)
        
    return comics_pages


def get_chapters(comics_pages):
    """Получаем ссылки на номера комиксов"""
    comics_chapters_list = []
    for page in comics_pages:
        soup = get_soup(page)
        links = soup.find_all('a')
        for link in links:
            comics = link.get('href')
            if 'online/' not in comics:
                continue
            else:
                comics_chapters_list.append(comics)

    return set(comics_chapters_list)

async def get_image_link(comics_url, session):
    """"Получаем ссылки на изображения страниц и скачиваем их"""
    soup = get_soup(comics_url)
    base_url = soup.find('img', id='b_image').get('src')[:-6]
    i = 1
    while True:
        img_link = base_url + f'{i:02d}.jpg'
        comics_path = comics_url.split('/')[-1]
        page_number = img_link.split('/')[-1]
        async with session.get(img_link) as response:
            if response.status == 200:
                data = await response.read()
                download_img(data, comics_path, page_number)
                i+=1
            else:
                print(f'Комикс скачан {comics_path}')
                break


def download_img(data, comics_path, page_number):
    """Скачиваем изображение страницы с комикса"""
    if not os.path.exists(f'{comics_path}'):
        os.mkdir(f'{comics_path}')
    with open(f'{comics_path}/{page_number}', 'wb') as file:
        print(f'Скачивание {comics_path}/{page_number}')
        file.write(data)

async def main():
    comics_url = input('Введите ссылку на серию комиксов:\n')
    comics_pages = get_comics_pages(comics_url)
    comics_chapters = get_chapters(comics_pages)
    tasks = []
    async with aiohttp.ClientSession() as session:
        for chapter in comics_chapters:
            task = asyncio.create_task(get_image_link(chapter, session))
            tasks.append(task)

        await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())

    # https://unicomics.ru/comics/series/superior-spider-man