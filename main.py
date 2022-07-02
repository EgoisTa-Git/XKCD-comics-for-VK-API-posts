import os
from pprint import pprint
from random import randint

import requests
from dotenv import load_dotenv

VK_API_VERSION = 5.131


class VkApiError(Exception):
    pass


def get_upload_url(url, group_id, token, version):
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
    exist_errors(upload_server_response.json())
    return upload_server_response.json()['response']['upload_url']


def upload_image(url, image):
    image_payload = {
        'photo': image,
    }
    upload_image_response = requests.post(url, files=image_payload)
    upload_image_response.raise_for_status()
    json_response = upload_image_response.json()
    exist_errors(json_response)
    server = json_response['server']
    photo = json_response['photo']
    hash_ = json_response['hash']
    return server, photo, hash_


def save_image_on_server(url, group_id, token, version, server, photo, hash_):
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
    exist_errors(save_response.json())
    response = save_response.json()['response'][0]
    owner_id = response['owner_id']
    photo_id = response['id']
    return owner_id, photo_id


def post_on_wall(url, group_id, token, version, owner_id, photo_id, message):
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
    exist_errors(response.json())
    return response.json()


def post_comic(url, group_id, token, version, image, message):
    upload_url = get_upload_url(url, group_id, token, version)
    server, photo, hash_ = upload_image(upload_url, image)
    owner_id, photo_id = save_image_on_server(
        url,
        group_id,
        token,
        version,
        server,
        photo,
        hash_
    )
    post_on_wall(
        url,
        group_id,
        token,
        version,
        owner_id,
        photo_id,
        message
    )


def exist_errors(json_response):
    if 'error' in json_response.keys():
        pprint(json_response['error'])
        raise VkApiError(json_response['error']['error_msg'])


if __name__ == '__main__':
    load_dotenv()
    vk_token = os.getenv('VK_ACCESS_TOKEN')
    vk_api_url = 'https://api.vk.com/method/'
    vk_group = int(os.getenv('VK_GROUP_ID'))
    latest_xkcd = requests.get('https://xkcd.com/info.0.json').json()['num']
    xkcd_number = randint(1, latest_xkcd)
    comic_url = f'https://xkcd.com/{xkcd_number}/info.0.json'
    comic_response = requests.get(comic_url)
    comic_response.raise_for_status()
    comic = comic_response.json()
    comic_image_url = comic['img']
    comic_comment = comic['alt']
    with open(f'comic_{xkcd_number}.png', 'wb') as file:
        image_response = requests.get(comic_image_url)
        image_response.raise_for_status()
        file.write(image_response.content)
    try:
        with open(f'comic_{xkcd_number}.png', 'rb') as comic_image:
            post_comic(
                vk_api_url,
                vk_group,
                vk_token,
                VK_API_VERSION,
                comic_image,
                comic_comment
            )
    finally:
        os.remove(comic_image.name)
