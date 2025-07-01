import requests

headers = {
    "User-Agent": "Mozilla/5.0"  # 可加上请求头防止被拒
}

def download_video(url, filename):
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def download_pic(url, filedir):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filedir, "wb") as f:
            f.write(response.content)