import requests


def get_comic(url):
    response = requests.get(url)
    return response.json()['img']


def get_image(url):
    response = requests.get(url)
    return response.content


if __name__ == '__main__':
    xkcd_number = 353
    xkcd_url = f'https://xkcd.com/{xkcd_number}/info.0.json'
    comic_image_url = get_comic(xkcd_url)
    with open(f'comic_{xkcd_number}.png', 'wb') as file:
        file.write(get_image(comic_image_url))
