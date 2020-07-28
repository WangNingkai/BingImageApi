import json
import sys

from requests import get


def fetchImage(idx=0):
    api_url = r'https://www.bing.com/HPImageArchive.aspx?format=js&idx={0}&n=1&mkt=en-US'.format(
        idx)
    api = get(api_url)
    json_data = json.loads(api.text)
    images = json_data['images']
    for item in images:
        pic_url = r'https://www.bing.com{0}'.format(item['url'])
        start_date = item['startdate']
        open(r'./json/{0}.json'.format(start_date), 'wb').write(api.content)
        pic = get(pic_url, stream=True)
        if (pic.status_code == 200):
            open(r'./images/{0}.png'.format(start_date),
                 'wb').write(pic.content)
            print(r'Create {0} Image Success!'.format(start_date))
        else:
            print(r'Create {0} Image Failed!'.format(start_date))
    return


if __name__ == "__main__":
    try:
        idx = sys.argv[1]
    except IndexError as e:
        idx = 0
    fetchImage(idx)
