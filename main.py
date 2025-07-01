import requests
from client import get_user_profiles, cookies, headers
import re
from urllib.parse import urljoin
import json
import os
from get_pic import download_pic
from get_video import download_video


def extract_note_dict(html_text):
    """从html文件中提取对应note: {...} 的内容"""
    pattern = r'"note"\s*:\s*\{'
    match = re.search(pattern, html_text)
    if not match:
        print("❌ 未找到 '\"note\": {'")
        return None

    start = match.end() - 1
    text = html_text[start:]

    # 配对大括号
    count = 0
    end = None
    for i, c in enumerate(text):
        if c == '{':
            count += 1
        elif c == '}':
            count -= 1
            if count == 0:
                end = i + 1
                break

    if end is None:
        print("❌ 大括号不匹配")
        return None

    json_text = text[:end]

    # 清理非法控制字符（如 \x0e）
    json_text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', json_text)

    try:
        note_dict = json.loads(json_text)
        return note_dict
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}")
        print(json_text[max(0, e.pos - 50):e.pos + 50])
        return None


def get_blogs(html):
    """正则表达式匹配 class="cover mask ld" 的 <a> 标签里的 href"""
    pattern = r'<a[^>]*class="cover mask ld"[^>]*href="([^"]+)"'

    matches = re.findall(pattern, html)

    return matches


# 数目前已经存了多少篇笔记
total_count = sum(os.path.isdir(os.path.join("./notes/videos", name)) for name in os.listdir("./notes/videos")) + sum(os.path.isdir(os.path.join("./notes/texts", name)) for name in os.listdir("./notes/texts"))
video_count = sum(os.path.isdir(os.path.join("./notes/videos", name)) for name in os.listdir("./notes/videos"))

while total_count < 5000 or video_count < 50:
    print(f"目前总量：{total_count}, 视频总量：{video_count}")

    # 获取当前主页的所有用户信息
    profiles = get_user_profiles()

    # 对每个用户...
    for profile in profiles:
        url = urljoin("https://xiaohongshu.com", profile)
        response = requests.get(url, headers=headers, cookies=cookies)
        html = response.text

        blogs = get_blogs(html)

        # 的每一篇帖子
        for blog in blogs:
            blog_url = urljoin("https://xiaohongshu.com", blog)
            response = requests.get(blog_url, headers=headers, cookies=cookies)
            html = response.text

            notes_block = extract_note_dict(html)
            firstNoteId = notes_block["firstNoteId"]
            

            # 标题
            title = notes_block["noteDetailMap"][firstNoteId]["note"]["title"]

            # 正文
            text = notes_block["noteDetailMap"][firstNoteId]["note"]["desc"]

            # 图片链接
            image_urls = [image["infoList"][0]["url"] for image in notes_block["noteDetailMap"][firstNoteId]["note"]["imageList"]]

            # 视频链接(可能无)
            if "video" in notes_block["noteDetailMap"][firstNoteId]["note"].keys():
                filedir = f"./notes/videos/笔记{total_count+1}"
                os.mkdir(filedir)
                video_url = notes_block["noteDetailMap"][firstNoteId]["note"]["video"]["media"]["stream"]["h264"][0]["masterUrl"]
                download_video(video_url, filedir+"/video.mp4")
                video_count += 1

            # 如果只差视频了
            elif total_count >=5000: continue
            else:
                filedir = f"./notes/texts/笔记{total_count+1}"
                os.mkdir(filedir)
                for idx, image_url in enumerate(image_urls):
                    download_pic(image_url, filedir+f"/image{idx}.webp")

            info = {"title":title, "text":text}
            with open(f'{filedir}/info.json', 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=4)
            total_count += 1



