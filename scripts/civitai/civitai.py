import requests
import os
import time
import concurrent.futures
from .civitai_utils import (
    download_images,
    download_images_and_prompts,
    format_name,
    my_request_get,
)

current_ext_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
search_img_save_dir = os.path.join(current_ext_dir, "search_img")


def download_models_pre(name, tag, types, nsfw, sort, page_num, per_page_num):
    allcount = 0
    download_urls = []
    save_names = []
    res = []
    model_ids = []
    url = "https://civitai.com/api/v1/models"
    futures = []
    # porn nsfw sex sexy nude naked
    query_params = {
        "limit": per_page_num,
        "page": page_num,
        "tag": "cute",
        "query": "name",
        "types": "Checkpoint",
        "sort": sort,  # Newest Most Downloaded Highest Rated
        "period": "AllTime",
        "nsfw": "true",
    }
    if name:
        query_params["query"] = name
    else:
        del query_params["query"]
    if tag:
        query_params["tag"] = tag
    else:
        del query_params["tag"]

    if types:
        query_params["types"] = types
    else:
        del query_params["types"]

    if nsfw == "all":
        del query_params["nsfw"]
    elif nsfw == "nsfw=true":
        query_params["nsfw"] = "true"
    elif nsfw == "nsfw=false":
        query_params["nsfw"] = "false"

    print(query_params)

    dir_name = os.path.join(current_ext_dir, types)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    response = my_request_get(url, params=query_params)
    if response == None:
        return [(None, "get img error,please retry")]

    if response.status_code == 200:
        models = response.json()
        # Do something with the models
        print("this page num:{}".format(len(models["items"])))
        if len(models["items"]) == 0:
            return res
        for item in models["items"]:
            try:
                if nsfw == "nsfw=true":
                    if item["nsfw"] == False:
                        continue
                    else:
                        allcount += 1
                elif nsfw == "nsfw=false":
                    if item["nsfw"] == True:
                        continue
                    else:
                        allcount += 1
                else:
                    allcount += 1
                item["name"] = format_name(item["name"])
                image_save_name = "{}/{}.jpg".format(
                    dir_name, item["name"] + "-" + str(item["id"])
                )
                if os.path.exists(image_save_name):
                    # already downloaded
                    res.append((image_save_name, item["name"]))
                    model_ids.append(item["id"])
                    continue
                try:
                    download_url = item["modelVersions"][0]["images"][0]["url"]
                    if download_url:
                        download_urls.append(download_url)
                        save_names.append(image_save_name)
                        model_ids.append(item["id"])
                        res.append((image_save_name, item["name"]))
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
            future = executor.submit(download_images, url, save_names[i])
            futures.append(future)
    concurrent.futures.wait(futures)
    return res, model_ids


def download_detail(modelid, types):
    save_dir = ""
    res_model_download_url = ""
    save_model_path = ""
    save_dir = os.path.join(current_ext_dir, types)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    print(save_dir)
    res = []
    url = "https://civitai.com/api/v1/models/" + str(modelid)

    response = my_request_get(url)
    if response == None:
        return [(None, "get img error,please retry")]

    if response.status_code == 200:
        model = response.json()
        model["name"] = format_name(model["name"])
        res_model_download_url = model["modelVersions"][0]["downloadUrl"]
        save_model_path = os.path.join(save_dir, model["name"])

        if not os.path.exists(save_model_path):
            os.makedirs(save_model_path)
        # Save the model_tag to a file
        with open((save_model_path + "\\info.txt"), "w") as f:
            f.write("model_id:" + str(model["id"]) + "\n")
            f.write(
                "lastest model_ver_id:"
                + str(model["modelVersions"][0]["modelId"])
                + "\n"
            )
            f.write("base model:" + model["modelVersions"][0]["baseModel"] + "\n")
            f.write("name:" + model["name"] + "\n")
            f.write("tags:")
            for tag in model["tags"]:
                f.write(tag + ",")
        count = 0
        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for image in model["modelVersions"][0]["images"]:
                res.append(
                    (
                        (save_model_path + "\\{}.jpg").format(count),
                        str(count),
                    )
                )
                future = executor.submit(
                    download_images_and_prompts, save_model_path, count, image
                )
                count += 1
                futures.append(future)
        concurrent.futures.wait(futures)

    return res, res_model_download_url, save_model_path


def tags_get(query, page, per_page_count):
    url = "https://civitai.com/api/v1/tags"
    res = ""
    if query is None or query == "":
        params = {"limit": per_page_count, "page": page}
    else:
        params = {"limit": per_page_count, "page": page, "query": query}

    response = my_request_get(url, params=params)
    if response == None:
        return res
    if response.status_code == 200:
        tags = response.json()["items"]
        for tag in tags:
            res += tag["name"] + "\n"
    return res


def search_img(nsfw, sort, page_num, per_page_num):
    if not os.path.exists(search_img_save_dir):
        os.makedirs(search_img_save_dir)
    url = "https://civitai.com/api/v1/images"
    res = []
    query_params = {
        "limit": per_page_num,
        "page": page_num,
        "sort": sort,  # Most Reactions, Most Comments, Newest
        "period": "AllTime",
        "nsfw": "true",
    }
    # choices=["all", "nsfw=true", "nsfw=false", "Soft", "Mature", "X"],
    if nsfw == "nsfw=all":
        del query_params["nsfw"]
    elif nsfw == "nsfw=false":
        query_params["nsfw"] = "None"
    elif nsfw == "nsfw=true":
        query_params["nsfw"] = "true"
    elif nsfw == "Soft":
        query_params["nsfw"] = "Soft"
    elif nsfw == "Mature":
        query_params["nsfw"] = "Mature"
    elif nsfw == "X":
        query_params["nsfw"] = "X"
        
    print(query_params)

    response = my_request_get(url, params=query_params)
    if response == None:
        return [(None, "get img error,please retry")]
    if response.status_code == 200:
        items = response.json()["items"]
        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for item in items:
                try:
                    image_save_name = "{}/{}.jpg".format(
                        search_img_save_dir, str(item["id"])
                    )
                    if os.path.exists(image_save_name):
                        # already downloaded
                        res.append((image_save_name, item["id"]))
                        continue
                    res.append((image_save_name, item["id"]))
                    future = executor.submit(
                        download_images_and_prompts,
                        search_img_save_dir,
                        item["id"],
                        item,
                        True,
                    )
                    futures.append(future)
                except KeyError:
                    print("Error: item does not have the expected property")
                    continue
        concurrent.futures.wait(futures)
    return res
