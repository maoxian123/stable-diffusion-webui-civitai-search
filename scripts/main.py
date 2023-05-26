import gradio as gr
import requests
from scripts.civitai.civitai import (
    download_models_pre,
    download_detail,
    tags_get,
    current_ext_dir,
)
from scripts.civitai.civitai_utils import (
    load_all_image_local,
    load_image_prompts,
    get_all_downloaded_dirs,
)
from pathlib import Path
import os
import shutil
import webbrowser
from modules import script_callbacks, scripts


def download_models_pre_fn(tag, types, nsfw, sort, page_num, per_page_num):
    if tag == None or tag == "":
        tag = None
    if types == None or types == "":
        types = "Checkpoint"
    if nsfw == None or nsfw == "":
        nsfw = None
    return download_models_pre(tag, types, nsfw, sort, int(page_num), int(per_page_num))


download_url = ""
detail_save_path = ""


def download_detail_fn(model_id, types):
    if ".jpg" in model_id:
        model_id = model_id.split(".jpg")[0]
    global download_url, detail_save_path
    res, detail_save_path, download_url = download_detail(model_id, types)
    return res


def view_selected_detail(evt: gr.SelectData, types):
    print(types)
    print(f"You selected {evt.value} at {evt.index} from {evt.target}")
    return evt.value, types


def view_selected_prompts(evt: gr.SelectData):
    print(evt.index)
    print(evt.value)
    return load_image_prompts(evt.value)


ROOT_DIR = Path().absolute()
real_path_lora = os.path.join(ROOT_DIR, "models\\Lora\\")
real_path_model = os.path.join(ROOT_DIR, "models\\Stable-diffusion\\")


def download_save_model_fn(types):
    model_name = detail_save_path.split("\\")[-1]
    if types == "LORA":
        shutil.copytree(detail_save_path, real_path_lora + model_name)
    if types == "Checkpoint":
        shutil.copytree(detail_save_path, real_path_model + model_name)
    webbrowser.open(download_url)


def tag_search_fn(query, page_num, per_page_num):
    res = tags_get(query, page_num, per_page_num)
    return res


def get_all_download_model(type):
    if type == "LORA":
        typedir = real_path_lora
    if type == "Checkpoint":
        typedir = real_path_model
    print(typedir)
    dirs = get_all_downloaded_dirs(typedir)
    res = []
    if dirs == None:
        return None
    for dir in dirs:
        if os.path.exists(dir + "\\1.jpg"):
            res.append((dir + "\\1.jpg", dir))
    return res


def load_all_image_localcache_fn(types):
    dir = os.path.join(
        current_ext_dir,
        types,
    )
    return load_all_image_local(dir, True)


def select_local_detail_fn(evt: gr.SelectData):
    return load_all_image_local(evt.value)


def on_ui_tabs():
    with gr.Blocks() as grapp:
        with gr.Tab("model、lora 预览图下载"):
            input_text = gr.inputs.Textbox(label="Enter a search tag")
            with gr.Row():
                type_dropdown = gr.inputs.Dropdown(
                    label="类型选择", choices=["Checkpoint", "LORA"], default="Checkpoint"
                )
                sort_dropdown = gr.inputs.Dropdown(
                    label="排序选择",
                    choices=["Newest", "Most Downloaded", "Highest Rated"],
                    default="Most Downloaded",
                )
            nsfw_checkbox = gr.inputs.Checkbox(label="是否包含NSFW")

            with gr.Row():
                page_num = gr.inputs.Number(label="页数", default=1)
                per_page_num = gr.inputs.Number(label="每页数量", default=20)
            button = gr.Button(value="搜索")
            button3 = gr.Button(value="加载已缓存的")
            gallery = gr.Gallery(
                label="images", show_label=True, elem_id="gallery1"
            ).style(columns=[5], object_fit="contain", height="auto")

        with gr.Tab("查看详细信息"):
            input_text2 = gr.inputs.Textbox(label="Enter a model id")
            dropdown2 = gr.inputs.Dropdown(
                label="类型选择", choices=["Checkpoint", "LORA"], default="Checkpoint"
            )
            image_prompts = gr.inputs.Textbox(label="image prompts")
            gallery2 = gr.Gallery(
                label="images", show_label=True, elem_id="gallery2"
            ).style(columns=[5], object_fit="contain", height="auto")
            button2 = gr.Button(value="预览")
            button4 = gr.Button(value="下载")

        with gr.Tab("tags搜索") as tab3:
            tag_input = gr.inputs.Textbox(label="Enter a search tag or null for all")
            with gr.Row():
                tag_page_num = gr.inputs.Number(label="页数", default=1)
                tag_per_page_num = gr.inputs.Number(label="每页数量", default=20)
            tag_search_button = gr.Button(value="搜索")
            res_text = gr.outputs.Textbox(label="搜索结果")

        with gr.Tab("查看已经下载的model和lora"):
            local_type_dropdown = gr.inputs.Dropdown(
                label="类型选择", choices=["Checkpoint", "LORA"], default="Checkpoint"
            )
            local_image_prompts = gr.inputs.Textbox(label="image prompts")
            button_load_local = gr.Button(value="加载")
            gallery3 = gr.Gallery(
                label="images", show_label=True, elem_id="gallery3"
            ).style(columns=[5], object_fit="contain", height="auto")
            gallery4 = gr.Gallery(
                label="images", show_label=True, elem_id="gallery4"
            ).style(columns=[5], object_fit="contain", height="auto")

        button.click(
            fn=download_models_pre_fn,
            inputs=[
                input_text,
                type_dropdown,
                nsfw_checkbox,
                sort_dropdown,
                page_num,
                per_page_num,
            ],
            outputs=gallery,
        )
        button2.click(
            fn=download_detail_fn,
            inputs=[input_text2, dropdown2],
            outputs=[gallery2],
        )
        button3.click(
            fn=load_all_image_localcache_fn, inputs=[type_dropdown], outputs=gallery
        )
        gallery.select(
            fn=view_selected_detail,
            inputs=type_dropdown,
            outputs=[input_text2, dropdown2],
        )
        button4.click(download_save_model_fn, inputs=[dropdown2])
        tag_search_button.click(
            fn=tag_search_fn,
            inputs=[tag_input, tag_page_num, tag_per_page_num],
            outputs=res_text,
        )
        gallery2.select(fn=view_selected_prompts, outputs=[image_prompts])
        button_load_local.click(
            fn=get_all_download_model, inputs=[local_type_dropdown], outputs=gallery3
        )
        gallery3.select(fn=select_local_detail_fn, outputs=gallery4)
        gallery4.select(fn=view_selected_prompts, outputs=[local_image_prompts])

        return [(grapp, "Civitai Search", "civitai search")]


script_callbacks.on_ui_tabs(on_ui_tabs)
