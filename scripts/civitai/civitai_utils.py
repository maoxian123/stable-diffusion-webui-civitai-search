import requests
import os
import time
import concurrent.futures
import json
import random
import requests

agents = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36 Edg/79.0.309.71",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
]
refers = [
    "https://www.google.com/",
    "https://www.yahoo.com/",
]


def gen_random_headers():
    headers = {
        #"Host": "civitai.com",
        # "If-None-Match": 'W/"wa4wt4hdb0uagx"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
        "Referer": "https://www.example.com/",
    }
    headers["User-Agent"] = random.choice(agents)
    headers["Referer"] = random.choice(refers)
    return headers


def my_request_get(url, params=None) -> requests.Response | None:
    req_count = 0
    while True:
        try:
            req_count += 1
            response = requests.get(
                url, params=params, headers=gen_random_headers(), timeout=5
            )
            break
        except requests.exceptions.RequestException as e:
            if req_count >= 5:
                print("req>5 check your network")
                return None
            time.sleep(1)
            continue
    return response


def download_images(download_url, save_name):
    response = my_request_get(download_url)
    if response is None:
        return None

    if response.status_code == 200:
        # Save the image to a file
        with open(save_name, "wb") as f:
            f.write(response.content)
    return None


def process_meta(meta):
    # Size: 540x768, Seed: 2972238300, Model: NeverEndingDream_2.2_BakedVae_fp16, Steps: 30, Sampler: DPM++ SDE Karras, CFG scale: 7, Clip skip: 2, Model hash: ecefb796ff, Hires steps: 40, Hires upscale: 1.8, Hires upscaler: Lanczos, Denoising strength: 0.3
    res = ""
    res += meta["prompt"] + "\n"
    res += "Negative prompt: " + meta["negativePrompt"] + "\n"
    for key, value in meta.items():
        if (
            key == "prompt"
            or key == "negativePrompt"
            or key == "resources"
            or key == "Model hash"
        ):
            continue
        if key == "seed":
            key = "Seed"
        if key == "model":
            key = "Model"
        if key == "steps":
            key = "Steps"
        if key == "sampler":
            key = "Sampler"
        if key == "cfgScale":
            key = "CFG scale"
        res += key + ": " + str(value) + ", "
    return res


def download_images_and_prompts(save_dir, save_name, image: dict, resources=False):
    if image["url"] is None:
        return
    download_url = image["url"]
    response = my_request_get(download_url)
    if response is None:
        return
    # Save the model image to a file
    with open((save_dir + "\\{}.jpg").format(save_name), "wb") as f:
        f.write(response.content)
    if image["meta"] is not None:
        with open((save_dir + "\\{}.txt").format(save_name), "w") as f:
            f.write(process_meta(image["meta"]))
    if resources and image["postId"] is not None:
        with open((save_dir + "\\{}_resources.txt").format(save_name), "w") as f:
            f.write(f"postId: {image['postId']}\n")
            if image["meta"]["resources"] is not None:
                for item in image["meta"]["resources"]:
                    f.write(f"name: {item['name']} type: {item['type']}\n")


def load_all_image_local(dir, cache=False):
    files = os.listdir(dir)
    # only image
    files = [
        f for f in files if os.path.isfile(os.path.join(dir, f)) and f.endswith(".jpg")
    ]
    files.sort(key=lambda x: os.path.getctime(os.path.join(dir, x)))
    images = []
    if cache:
        for file in files:
            images.append((os.path.join(dir, file), file.split(".jpg")[0]))
    else:
        for file in files:
            images.append((os.path.join(dir, file), file.split(".jpg")[0]))
    return images


def load_image_prompts(imagepath):
    txt_path = imagepath.split(".jpg")[0] + ".txt"
    if not os.path.exists(txt_path):
        return None

    with open(txt_path, "r") as f:
        # read all
        lines = f.readlines()
    res = ""
    for line in lines:
        line.replace("\n", "\r\n")
        res += line
    return res


def load_image_resources(imagepath) -> str | None:
    txt_path = imagepath.split(".jpg")[0] + "_resources.txt"
    if not os.path.exists(txt_path):
        return None

    with open(txt_path, "r") as f:
        # read all
        lines = f.readlines()
    res = ""
    for line in lines:
        line.replace("\n", "\r\n")
        res += line
    return res


def format_name(name):
    if "/" in name:
        name = name.replace("/", "-")
    if "\\" in name:
        name = name.replace("\\", "-")
    if " " in name:
        name = name.replace(" ", "-")
    if "|" in name:
        name = name.replace("|", "-")
    if "'" in name:
        name = name.replace("'", "-")
    if '"' in name:
        name = name.replace('"', "-")
    if "*" in name:
        name = name.replace("*", "-")
    if "?" in name:
        name = name.replace("?", "-")
    if name[len(name) - 1] == "-":
        name = name[: len(name) - 1]
    return name
