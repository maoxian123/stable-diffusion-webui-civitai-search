import requests
import os
import time
import concurrent.futures
from .civitai_utils import download_images, download_tag_images
from pathlib import Path

def download_models_pre(tag, types, nsfw, sort, page_num, per_page_num):
    allcount = 0
    download_urls = []
    save_names = []
    res = []
    url = "https://civitai.com/api/v1/models"
    futures = []
    # porn nsfw sex sexy nude naked
    query_params = {
        "limit": per_page_num,
        "page": page_num,
        "tag": "cute",
        "types": "Checkpoint",
        "sort": sort,  # Newest Most Downloaded Highest Rated
        "period": "AllTime",
        "nsfw": "true",
    }
    if tag:
        query_params["tag"] = tag
    else:
        del query_params["tag"]

    if types:
        query_params["types"] = types
    else:
        del query_params["types"]

    # 如果nsfw为true 则只要nsfw=true的图片，否则直接去掉nsfw参数，下载所有类型图片
    if nsfw == True:
        query_params["nsfw"] = "true"
    else:
        del query_params["nsfw"]

    print(query_params)

    dir_name=os.path.join(Path().absolute(),f"extensions\\stable-diffusion-webui-extension-civitai-search\\{types}")
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    print(dir_name)

    while True:
        try:
            response = requests.get(url, params=query_params)
            break
        except requests.exceptions.RequestException as e:
            time.sleep(1)
            continue

    if response.status_code == 200:
        models = response.json()
        # Do something with the models
        print("this page num:{}".format(len(models["items"])))
        if len(models["items"]) == 0:
            return res
        for item in models["items"]:
            try:
                if nsfw == True:
                    if item["nsfw"] == False:
                        print("nsfw is false")
                        continue
                    else:
                        allcount += 1
                elif nsfw == False:
                    allcount += 1
                res.append(("{}/{}.jpg".format(dir_name, item["id"]), f'{item["id"]}'))
                if os.path.exists("{}/{}.jpg".format(dir_name, item["id"])):
                    # print("Image {} already exists".format(item['id']))
                    continue
                try:
                    download_url=item["modelVersions"][0]["images"][0]["url"]
                    if download_url:
                        download_urls.append(download_url)
                        save_names.append(item["id"])
                except IndexError:
                    print("Error: item does not have the expected property")
                    continue
            except KeyError:
                print("Error: item does not have the expected property")
                continue
    else:
        print("Error: ", response.status_code)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for i, url in enumerate(download_urls):
            future = executor.submit(
                download_images, url, types, dir_name, save_names[i]
            )
            futures.append(future)
    concurrent.futures.wait(futures)
    return res


def download_detail(modelid, types):
    save_dir = ""
    res_save_path = ""
    res_download_url = ""
    if types == "Checkpoint":
        save_dir = "Detail_Stable-diffusion"
    if types == "LORA":
        save_dir = "Detail_Lora"
    save_dir=os.path.join(Path().absolute(),f"extensions\\stable-diffusion-webui-extension-civitai-search\\{save_dir}")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    print(save_dir)
    res = []
    url = "https://civitai.com/api/v1/models/" + str(modelid)
    while True:
        try:
            response = requests.get(url)
            break
        except requests.exceptions.RequestException as e:
            time.sleep(1)
            continue
    if response.status_code == 200:
        model = response.json()
        if "/" in model["name"]:
            model["name"] = model["name"].replace("/", "-")
        if "\\" in model["name"]:
            model["name"] = model["name"].replace("\\", "-")
        if " " in model["name"]:
            model["name"] = model["name"].replace(" ", "-")
        if "|" in model["name"]:
            model["name"] = model["name"].replace("|", "-")

        res_download_url = model["modelVersions"][0]["downloadUrl"]

        if not os.path.exists((save_dir + "\\{}").format(model["name"])):
            os.makedirs((save_dir + "\\{}").format(model["name"]))
        res_save_path = (save_dir + "\\{}").format(model["name"])
        # Save the model_tag to a file
        with open(
            (save_dir + "\\{}\\{}.txt").format(model["name"], model["name"]), "w"
        ) as f:
            f.write("id:" + str(model["id"]) + "\n")
            f.write("name:" + model["name"] + "\n")
            for tag in model["tags"]:
                f.write(tag + ",")
            print("write model {} tag".format(model["name"]))
        count = 0
        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            for image in model["modelVersions"][0]["images"]:
                count += 1
                res.append(
                    (
                        (save_dir + "\\{}\\{}.jpg").format(model["name"], count),
                        (save_dir + "\\{}\\{}.jpg").format(model["name"], count),
                    )
                )
                future = executor.submit(
                    download_tag_images, res_save_path, count, image
                )
                futures.append(future)
        concurrent.futures.wait(futures)

    return res, res_save_path, res_download_url


def tags_get(query, page, per_page_count):
    url = "https://civitai.com/api/v1/tags"
    res = ""
    if query is None or query == "":
        params = {"limit": per_page_count, "page": page}
    else:
        params = {"limit": per_page_count, "page": page, "query": query}
    while True:
        try:
            response = requests.get(url, params=params)
            break
        except requests.exceptions.RequestException as e:
            time.sleep(1)
            continue
    if response.status_code == 200:
        tags = response.json()["items"]
        for tag in tags:
            res += tag["name"] + "\n"
    return res


# # main
# if __name__ == "__main__":
#     res = download_models_pre(None, "LORA", None, "Newest", 4, 50)
#     print(res)
