import requests
import os
import time
import concurrent.futures


def download_images(download_url, types, save_dir, save_name):
    while True:
        try:
            response = requests.get(download_url)
            break
        except requests.exceptions.RequestException as e:
            time.sleep(1)
            continue

    if response.status_code == 200:
        # Save the image to a file
        with open("{}/{}.jpg".format(save_dir, save_name), "wb") as f:
            f.write(response.content)
            print("type:{} Downloaded image {}".format(types, save_name))
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


def download_tag_images(save_dir, save_name, image: dict):
    download_url = image["url"]
    while True:
        try:
            response = requests.get(download_url)
            break
        except requests.exceptions.RequestException as e:
            time.sleep(1)
            continue
    # Save the model image to a file
    with open((save_dir + "\\{}.jpg").format(save_name), "wb") as f:
        f.write(response.content)
    if image["meta"] is not None:
        with open((save_dir + "\\{}.txt").format(save_name), "w") as f:
            f.write(process_meta(image["meta"]))


def load_all_image_local(dir,cache=False):
    files = os.listdir(dir)
    #only image
    files = [f for f in files if os.path.isfile(os.path.join(dir, f)) and f.endswith(".jpg")]
    files.sort(key=lambda x: os.path.getctime(os.path.join(dir, x)))
    images = []
    if cache:
        for file in files:
            images.append((os.path.join(dir, file), file.split(".jpg")[0]))
    else:
        for file in files:
            images.append((os.path.join(dir, file), os.path.join(dir, file)))
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
        res += line
    return res


def get_all_downloaded_dirs(typedir):
    dirs = os.listdir(typedir)
    
    dirs = [d for d in dirs if os.path.isdir(os.path.join(typedir, d))]
    dirs.sort(key=lambda x: os.path.getctime(os.path.join(typedir, x)))
    #add typedir
    dirs = [os.path.join(typedir, d) for d in dirs]
    return dirs
    