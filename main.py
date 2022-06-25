import os
from random import randint

import requests
from dotenv import load_dotenv

VK_API_VERSION = 5.131


def get_comic(number):
    url = f'https://xkcd.com/{number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_image_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def post_comic(url, group_id, token, version, image, message):
    upload_server_params = {
        'access_token': token,
        'v': version,
        'group_id': group_id,
    }
    upload_server_response = requests.get(
        f'{url}photos.getWallUploadServer',
        params=upload_server_params,
    )
    upload_server_response.raise_for_status()
    response = upload_server_response.json()['response']
    upload_url = response['upload_url']
    image_payload = {
        'photo': image,
    }
    upload_image_response = requests.post(upload_url, files=image_payload)
    upload_image_response.raise_for_status()
    server = upload_image_response.json()['server']
    photo = upload_image_response.json()['photo']
    hash_ = upload_image_response.json()['hash']
    save_params = {
        'access_token': token,
        'v': version,
        'server': server,
        'photo': photo,
        'hash': hash_,
        'group_id': group_id,
    }
    save_response = requests.get(
        f'{url}photos.saveWallPhoto',
        params=save_params,
    )
    save_response.raise_for_status()
    response = save_response.json()['response'][0]
    owner_id = response['owner_id']
    photo_id = response['id']
    photo = f'photo{owner_id}_{photo_id}'
    post_params = {
        'access_token': token,
        'v': version,
        'owner_id': -group_id,
        'from_group': 1,
        'attachments': photo,
        'message': message,
        'close_comments': 1,
    }
    response = requests.get(
        f'{url}wall.post',
        params=post_params,
    )
    response.raise_for_status()


if __name__ == '__main__':
    load_dotenv()
    vk_token = os.getenv('VK_ACCESS_TOKEN')
    vk_api_url = 'https://api.vk.com/method/'
    vk_group = int(os.getenv('VK_GROUP_ID'))
    latest_xkcd = requests.get('https://xkcd.com/info.0.json').json()['num']
    xkcd_number = randint(1, latest_xkcd)
    comic = get_comic(xkcd_number)
    comic_image_url = comic['img']
    comic_comment = comic['alt']
    with open(f'comic_{xkcd_number}.png', 'wb') as file:
        file.write(get_image_from_url(comic_image_url))
    with open(f'comic_{xkcd_number}.png', 'rb') as comic_image:
        post_comic(
            vk_api_url,
            vk_group,
            vk_token,
            VK_API_VERSION,
            comic_image,
            comic_comment
        )
        os.remove(comic_image.name)
