import requests
from client import get_user_profiles, cookies, headers
from urllib.parse import urljoin
import json
import os
from utils import download_pic, download_video, extract_note_dict, get_blogs
import time


# 若无notes文件夹，则创建
os.makedirs("./notes/texts", exist_ok=True)
os.makedirs("./notes/videos", exist_ok=True)

# 数目前已经存了多少篇笔记
total_count = sum(os.path.isdir(os.path.join("./notes/videos", name)) for name in os.listdir("./notes/videos")) + sum(os.path.isdir(os.path.join("./notes/texts", name)) for name in os.listdir("./notes/texts"))
video_count = sum(os.path.isdir(os.path.join("./notes/videos", name)) for name in os.listdir("./notes/videos"))

while total_count < 5000 or video_count < 50:
    print(f"目前总量：{total_count}, 视频总量：{video_count}")

    # # 获取当前主页的所有用户信息
    # profiles = get_user_profiles()

    # # 对每个用户...
    # for profile in profiles:
    #     url = urljoin("https://xiaohongshu.com", profile)
    #     response = requests.get(url, headers=headers, cookies=cookies)
    #     html = response.text

    response = requests.get('https://www.xiaohongshu.com/explore', cookies=cookies, headers=headers)
    html = response.text
    blogs = get_blogs(html)

    # 对主页的每一篇帖子
    for blog in blogs:
        blog_url = urljoin("https://xiaohongshu.com", blog)
        response = requests.get(blog_url, headers=headers, cookies=cookies)
        html = response.text
        notes_block = extract_note_dict(html)
        
        try:
            firstNoteId = notes_block["firstNoteId"]
            # 标题
            title = notes_block["noteDetailMap"][firstNoteId]["note"]["title"]

            # 正文
            text = notes_block["noteDetailMap"][firstNoteId]["note"]["desc"]
        except Exception as e:
            continue

        # 图片链接
        image_urls = [image["infoList"][0]["url"] for image in notes_block["noteDetailMap"][firstNoteId]["note"]["imageList"]]

        # 视频链接(可能无)
        if "video" in notes_block["noteDetailMap"][firstNoteId]["note"].keys() and video_count<50:
            filedir = f"./notes/videos/笔记{total_count+1}"
            os.mkdir(filedir)
            video_url = notes_block["noteDetailMap"][firstNoteId]["note"]["video"]["media"]["stream"]["h264"][0]["masterUrl"]
            download_video(video_url, filedir+"/video.mp4")
            video_count += 1

        else:
            filedir = f"./notes/texts/笔记{total_count+1}"
            os.mkdir(filedir)
            for idx, image_url in enumerate(image_urls):
                download_pic(image_url, filedir+f"/image{idx}.webp")

        info = {"title":title, "text":text}
        with open(f'{filedir}/info.json', 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=4)
        total_count += 1
        time.sleep(5)



