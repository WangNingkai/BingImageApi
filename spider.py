import json
import random
import shutil

import requests as req

secret = r''

USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; "
    "SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; "
    "SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; "
    "Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; "
    "Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; "
    ".NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; "
    "Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; "
    ".NET CLR 3.5.30729; .NET CLR 3.0.30729; "
    ".NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; "
    "Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; "
    "InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) "
    "AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) "
    "Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ "
    "(KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; "
    "rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) "
    "Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) "
    "Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) "
    "Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 "
    "(KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) "
    "AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) "
    "Presto/2.9.168 Version/11.52"
]


def parseUrl(url):
    tenant = url.split('/')[2]
    mail = url.split('/')[6]
    return tenant, mail


def getCookies(url):
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    response = req.get(url, headers=headers)
    cookies = response.cookies.get_dict()
    # print('提取 FedAuth:' + cookies['FedAuth'])
    return cookies


def getAccessToken(url):
    tenant, mail = parseUrl(url)
    cookies = getCookies(url)
    url = "https://" + tenant + "/personal/" + mail + \
        "/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream?@a1='/personal/" + mail + \
        "/Documents'&RootFolder=/personal/" + mail + \
        "/Documents/&TryNewExperienceSingle=TRUE"

    headers = {
        'Accept': 'application/json;odata=verbose',
        'Content-Type': 'application/json;odata=verbose',
        'User-Agent': random.choice(USER_AGENTS)
    }

    payload = {
        "parameters": {
            "__metadata": {
                "type": "SP.RenderListDataParameters"
            },
            "RenderOptions": 136967,
            "AllowMultipleValueFilterForTaxonomyFields": True,
            "AddRequiredFields": True
        }
    }

    response = req.post(url,
                        cookies=cookies,
                        headers=headers,
                        data=json.dumps(payload))

    payload = json.loads(response.text)
    token = payload['ListSchema']['.driveAccessToken'][13:]
    api_url = payload['ListSchema']['.driveUrl'] + '/'
    shared_folder = payload['ListData']['Row'][0]['FileRef'].split('/')[-1]
    # print('提取 目录名:' + shared_folder)
    # print('提取 AccessToken:' + token)
    # print('提取 api_url:' + api_url)
    return token, api_url, shared_folder


def uploadImage(name, file):
    """ 
    OneDrive 上传
    """
    token, api_url, shared_folder = getAccessToken(secret)

    uploadpath = f'Images/Bing/{name}'
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    url = f'{api_url}items/root:/{shared_folder}/{uploadpath}:/content'
    response = req.put(url, headers=headers, data=file)
    file_id = json.loads(response.text)['id']
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    url = api_url + 'items/' + file_id + '/content'
    response = req.get(url, headers=headers, allow_redirects=False)
    download_link = response.headers['Location']
    print(f'文件上传成功，下载地址：\n{download_link}')


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
            with open(f'./images/{start_date}.png', 'rb+') as f:
                uploadImage(f'{start_date}.png', f.read())
            print(f'Create {start_date} Image Success!')
        else:
            print(f'Create {start_date} Image Failed!')
    return


if __name__ == "__main__":
    main()
