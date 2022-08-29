import json
import shutil

import requests as req

def main():
    api_url = 'https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US'
    api = req.get(api_url)
    json_data = json.loads(api.text)
    images = json_data['images']
    for item in images:
        pic_url = r'https://www.bing.com{0}'.format(item['url'])
        start_date = item['startdate']
        open(r'./json/{0}.json'.format(start_date), 'wb').write(api.content)
        pic = req.get(pic_url, stream=True)
        if (pic.status_code == 200):
            open(f'./images/{start_date}.png', 'wb').write(pic.content)
            shutil.copyfile(f'./images/{start_date}.png',
                            f'./images/latest.png')
            #with open(f'./images/{start_date}.png', 'rb+') as f:
            #    uploadImage(f'{start_date}.png', f.read())
            print(f'Create {start_date} Image Success!')
        else:
            print(f'Create {start_date} Image Failed!')
    return


if __name__ == "__main__":
    main()
