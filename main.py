
#使用样例:python .\main.py --id 34198

import json
import time
from datetime import datetime
from pathlib import Path
import logging
import requests
from tqdm import tqdm
import pandas
import requests
import os
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl import load_workbook
from auth import do_auth
from utils import env_in_github_workflow
from argparse import ArgumentParser

API_SERVER = "https://api.bgm.tv"
LOAD_WAIT_MS = 500
ACCESS_TOKEN = ""
IN_GITHUB_WORKFLOW = env_in_github_workflow()



def get_json_with_bearer_token(url):
    time.sleep(LOAD_WAIT_MS/1000)
    logging.debug(f"load url: {url}")
    headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN, 'accept': 'application/json', 'User-Agent': 'bangumi-takeout-python/v1'}
    response = requests.get(url, headers=headers)
    return response.json()


def load_user_collections(user_id):
    endpoint = f"{API_SERVER}/v0/persons/{user_id}/characters"
    collections = get_json_with_bearer_token(endpoint)
    logging.info(f"loaded {len(collections)} collections")
    with open("collections.json","w",encoding="u8") as f:
        json.dump(collections, f, ensure_ascii=False, indent=4)
    return collections

def load_user():
    # global USERNAME_OR_UID

    logging.info("loading user info")
    endpoint = f"{API_SERVER}/v0/persons/{id}"
    # import pdb;pdb.set_trace()
    user_data = get_json_with_bearer_token(endpoint)
    # USERNAME_OR_UID = user_data["username"]
    # print("user_data['username'] =", user_data['username'])
    
    return user_data

def trigger_auth():
    global ACCESS_TOKEN
    if IN_GITHUB_WORKFLOW:
        logging.info("in Github workflow, reading from secrets")
        ACCESS_TOKEN = os.environ['BANGUMI_ACCESS_TOKEN']
        return

    
    if Path("./no_gui").exists():
        logging.info("no gui, skipping oauth")
    else:
        do_auth()

    if not Path("./.bgm_token").exists():
        raise Exception("no access token (auth failed?)")

    with open("./.bgm_token", "r", encoding="u8") as f:
        tokens = json.load(f)
        ACCESS_TOKEN = tokens["access_token"]
        logging.info("access token loaded")

    if not ACCESS_TOKEN:
        logging.error("ACCESS_TOKEN is empty!")
        raise Exception("need access token (auth failed?)")
    
def characters_info(collections):
    subject_name = []
    subject_id = []
    staff = []
    name = []
    link = []
    for chara in collections:
        subject_name.append(f'{chara["subject_name"]}')
        subject_id.append(f'{chara["subject_id"]}')
        staff.append(f'{chara["staff"]}')
        name.append(f'{chara["name"]}')
        link.append(f'https://bangumi.tv/subject/{chara["subject_id"]}')
    return subject_id, subject_name, staff, name, link




def get_update_time(subject_id_list):
    kaifa = []
    update_time = {}
    
    # 使用tqdm包装subject_id_list来创建一个进度条
    for n, subject_id in enumerate(tqdm(subject_id_list, desc="Processing subjects")):
        subject_url = f"{API_SERVER}/v0/subjects/{subject_id}"
        try:
            subject_info = get_json_with_bearer_token(subject_url)
            update_time[n] = subject_info.get("date", "未知")
            subject_plat = subject_info.get("platform", "未知")
            if subject_plat == "游戏":
                developer_info = next((item["value"] for item in subject_info.get("infobox", []) if item["key"] == "开发"), "信息缺失")
                kaifa.append(developer_info)
            else:
                kaifa.append(subject_plat)
        except Exception as e:
            print(f"处理{subject_url}时发生错误：{e}")
            update_time[n] = "错误"
            kaifa.append("错误")
    
    return update_time, kaifa


def get_time_json(update_time_list):
    with open("updata_time.json","w",encoding="u8") as f:
        json.dump(update_time_list, f, ensure_ascii=False, indent=4)


def image_download(user_id, chara_number):

    # 读取JSON文件中的数据。
    with open('collections.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open("updata_time.json", "r", encoding="utf-8") as t:
        data_time = json.load(t)

    # 初始化image（图片链接）列表和time（更新时间）列表。
    image = []  # 图片链接列表。
    time = list(data_time.values())  # 更新时间列表。
    directory = f"{user_id}_images"  # 图片存储目录。
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 初始化进度条。
    pbar = tqdm(total=chara_number, desc="Downloading images")

    for n in range(min(chara_number, len(data))):
        chara = data[n]  # 获取角色数据。
        image_url = chara["images"]["small"]  # 获取小图链接。
        image.append(image_url)  # 将图片链接添加到列表中。

        if image_url:  # 如果图片链接存在。
            try:
                response = requests.get(image_url, stream=True)  # 请求图片。
                file_path = os.path.join(directory, f"{n}.jpg")  # 设置图片的存储路径。
                with open(file_path, "wb") as file:  # 打开文件用于写入。
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)  # 写入文件。
            except Exception as e:
                print(f"处理 {image_url} 时发生错误：{e}")  # 错误处理。

        pbar.update(1)  

    pbar.close()  
    
    return image 

def data_to_xlsx(user_id, name, subject_name, kaifa, staff, time, image, link):
    
    df = pandas.DataFrame()
    df["肖像"]=[]
    df["角色名"] = name
    df["作品名"] = subject_name
    df["开发"] = kaifa
    df["主配角"] = staff
    df["登场时间"] = time
    # 新建一个Excel文件
    df.to_excel(f"Cv_id_{user_id}.xlsx", index=False)

    # 载入Excel文件，并添加图片和超链接
    wb = load_workbook(f'Cv_id_{user_id}.xlsx')
    ws = wb['Sheet1']

    # 设定列宽度
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 60
    ws.column_dimensions["D"].width = 20
    ws.column_dimensions["E"].width = 10
    ws.column_dimensions["F"].width = 15

    for n in range(len(name)):
        N = n + 2  # Excel中行号从1开始，标题行为第一行，因此数据行从2开始
        # 插入图片
        if image[n]:
            img_path = f"{user_id}_images/{n}.jpg"
            img = Image(img_path)
            img.width, img.height = img.width * 0.75, img.height * 0.75  # 缩放图片大小
            ws.row_dimensions[N].height = img.height * 0.75
            ws.add_image(img, f"A{N}")

        # 添加超链接
        ws[f"C{N}"].hyperlink = link[n]
        ws[f"C{N}"].style = "Hyperlink"

    # 保存Excel文件
    wb.save(f"Cv_id_{user_id}.xlsx")



def main():
    parser = ArgumentParser(description='bangumi cv character list')
    parser.add_argument('--id', type=int, required=True)
    args = parser.parse_args()
    user_id = args.id  
    trigger_auth()  

    collections = load_user_collections(user_id)  
    subject_id, subject_name, staff, name, link = characters_info(collections)

    update_time_list, kaifa = get_update_time(subject_id) 
    print('get_time_json') 
    get_time_json(update_time_list)
    print('image dl')
    image = image_download(user_id, len(subject_id))
    print(f'save to Cv_id_{user_id}.xlsx')
    data_to_xlsx(user_id, name, subject_name, kaifa, staff, update_time_list, image, link)
    print('done')

if __name__ == '__main__':
    main()