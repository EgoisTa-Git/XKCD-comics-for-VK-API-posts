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


def post_comic(url, group_id, token, version, image):
    upload_server_payload = {
        'access_token': token,
        'v': version,
        'group_id': group_id,
    }
    upload_server_response = requests.get(
        f'{url}photos.getWallUploadServer',
        params=upload_server_payload,
    )
    upload_server_response.raise_for_status()
    response = upload_server_response.json()['response']
    album_id, upload_url, user_id = response.values()
    image_data = {
        'photo': image,
    }
    upload_post = requests.post(upload_url, files=image_data)
    upload_post.raise_for_status()
    server, photo, hash_ = upload_post.json().values()
    save_payload = {
        'access_token': token,
        'v': version,
        'server': server,
        'photo': photo,
        'hash': hash_,
    }
    save_response = requests.get(
        f'{url}photos.saveWallPhoto',
        params=save_payload,
    )
    save_response.raise_for_status()
    pprint(save_response.json())
    # вызовите метод photos.saveWallPhoto с параметрами server, photo, hash
    # wall.post в параметре attachments "photo" + {owner_id} + "_" + {photo_id}
    pass


if __name__ == '__main__':
    load_dotenv()
    vk_token = os.getenv('VK_ACCESS_TOKEN')
    vk_api_url = 'https://api.vk.com/method/'
    vk_group = os.getenv('VK_GROUP_ID')
    xkcd_number = 353
    xkcd_url = f'https://xkcd.com/{xkcd_number}/info.0.json'

    comic = get_comic(xkcd_url)
    comic_image_url = comic['img']
    comic_comment = comic['alt']
    with open(f'comic_{xkcd_number}.png', 'wb') as file:
        file.write(get_image(comic_image_url))

    with open(f'comic_{xkcd_number}.png', 'rb') as comic_image:
        post_comic(vk_api_url, vk_group, vk_token, VK_API_VERSION, comic_image)
