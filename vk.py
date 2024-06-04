import requests
import json
import os
from tqdm import tqdm

# Данные
VK_USER_ID = ""
VK_TOKEN = ""
YANDEX_DISK_TOKEN = ""
PHOTOS_COUNT = 5
YANDEX_DISK_FOLDER = "vk_photos"

def get_vk_photos(user_id, token, count=PHOTOS_COUNT):
    url = "https://api.vk.com/method/photos.get"
    params = {
        "owner_id": user_id,
        "album_id": "profile",
        "rev": 1,
        "extended": 1,
        "photo_sizes": 1,
        "count": count,
        "access_token": token,
        "v": "5.131"
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "response" in data and "items" in data["response"]:
        return data["response"]["items"]
    else:
        print("Ошибка при получении фотографий с профиля VK:", data)
        return []


def upload_to_yandex_disk(file_url, file_name, token):
    headers = {
        "Authorization": f"OAuth {token}"
    }
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    params = {
        "path": f"{YANDEX_DISK_FOLDER}/{file_name}",
        "url": file_url
    }
    response = requests.post(upload_url, headers=headers, params=params)
    return response.status_code == 202


def create_yandex_disk_folder(token, folder_name):
    headers = {
        "Authorization": f"OAuth {token}"
    }
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    params = {
        "path": folder_name
    }
    requests.put(url, headers=headers, params=params)

def main():
  
    create_yandex_disk_folder(YANDEX_DISK_TOKEN, YANDEX_DISK_FOLDER)

    photos = get_vk_photos(VK_USER_ID, VK_TOKEN)
    result = []

    for photo in tqdm(photos, desc="Uploading photos"):
        max_size_photo = max(photo["sizes"], key=lambda size: size["width"] * size["height"])
        file_url = max_size_photo["url"]
        file_name = f"{photo['likes']['count']}.jpg"
        size_type = max_size_photo["type"]

        if upload_to_yandex_disk(file_url, file_name, YANDEX_DISK_TOKEN):
            result.append({"file_name": file_name, "size": size_type})

    with open("photos_info.json", "w") as f:
        json.dump(result, f, indent=4)

    print("Фотографии успешно загружены и информация сохранена в photos_info.json")

if __name__ == "__main__":
    main()
