import requests
import re

def get_user_profiles():
    
    response = requests.get('https://www.xiaohongshu.com/explore', cookies=cookies, headers=headers)

    html = response.text

    # 先匹配所有 <div class="author-wrapper"> ... </div> 块
    author_divs = re.findall(r'<div class="author-wrapper"[^>]*>(.*?)</div>', html, re.S)

    hrefs = []
    for div in author_divs:
        # 在每个 author-wrapper 里匹配 <a href="...">
        match = re.search(r'<a[^>]+href="([^"]+)"', div)
        if match:
            hrefs.append(match.group(1))

    return hrefs
