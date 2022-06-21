import os
from pprint import pprint

import requests
from dotenv import load_dotenv

VK_API_VERSION = 5.131


def get_comic(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_image(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def get_vk_groups(url, token, version):
    url = f'{url}groups.get'
    payload = {
        'access_token': token,
        'v': version,
        'extended': 1,
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()


if __name__ == '__main__':
    load_dotenv()
    vk_token = os.getenv('VK_ACCESS_TOKEN')
    vk_api_url = 'https://api.vk.com/method/'
    xkcd_number = 353
    xkcd_url = f'https://xkcd.com/{xkcd_number}/info.0.json'

    comic = get_comic(xkcd_url)
    comic_image_url = comic['img']
    comic_comment = comic['alt']
    with open(f'comic_{xkcd_number}.png', 'wb') as file:
        file.write(get_image(comic_image_url))

    pprint(get_vk_groups(vk_api_url, vk_token, VK_API_VERSION))
