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
)
from pathlib import Path
import os
import shutil
import webbrowser
from modules import script_callbacks, scripts

download_url = ""
preview_select_model_id = ""
cur_select_detail_model_path = ""
pre_model_ids = []


def download_models_pre_fn(name, tag, types, nsfw, sort, page_num, per_page_num):
    global pre_model_ids
    if name == None or name == "":
        name = None
    if tag == None or tag == "":
        tag = None
    if types == None or types == "":
        types = "Checkpoint"
    res, pre_model_ids = download_models_pre(
        name, tag, types, nsfw, sort, int(page_num), int(per_page_num)
    )
    return res


def download_detail_fn(types):
    global download_url, cur_select_detail_model_path
    res, download_url, cur_select_detail_model_path = download_detail(
        preview_select_model_id, types
    )
    return res


def view_selected_detail(evt: gr.SelectData, types):
    # print(f"You selected {evt.value} at {evt.index} from {evt.target}")
    # print(evt.index)
    global preview_select_model_id
    preview_select_model_id = pre_model_ids[int(evt.index)]
    return None


def view_selected_prompts(evt: gr.SelectData):
    # print(evt.index)
    # print(evt.value)
    # mage_path=cur_select_detail_model_path+f"\\{evt.value}.jpg"
    print(cur_select_detail_model_path + f"\\{evt.value}.jpg")
    return load_image_prompts(cur_select_detail_model_path + f"\\{evt.value}.jpg")


ROOT_DIR = Path().absolute()
real_path_lora = os.path.join(ROOT_DIR, "models\\Lora\\")
real_path_model = os.path.join(ROOT_DIR, "models\\Stable-diffusion\\")


def download_save_model_fn(types):
    model_name = cur_select_detail_model_path.split("\\")[-1]
    if types == "LORA":
        shutil.copytree(cur_select_detail_model_path, real_path_lora + model_name)
    if types == "Checkpoint":
        shutil.copytree(cur_select_detail_model_path, real_path_model + model_name)
    webbrowser.open(download_url)


def tag_search_fn(query, page_num, per_page_num):
    res = tags_get(query, page_num, per_page_num)
    return res


def get_all_download_model(type):
    if type == "LORA":
        typedir = real_path_lora
    if type == "Checkpoint":
        typedir = real_path_model
    # print(typedir)
    dirs = dirs = os.listdir(typedir)
    dirs = [d for d in dirs if os.path.isdir(os.path.join(typedir, d))]
    dirs.sort(key=lambda x: os.path.getctime(os.path.join(typedir, x)))
    res = []
    if dirs == None:
        return None
    for dir in dirs:
        if os.path.exists(os.path.join(typedir, dir, "0.jpg")):
            res.append((os.path.join(typedir, dir, "0.jpg"), dir))
    return res


def load_all_image_localcache_fn(types):
    dir = os.path.join(
        current_ext_dir,
        types,
    )
    return load_all_image_local(dir, True)


def select_local_detail_fn(evt: gr.SelectData, type):
    global cur_select_detail_model_path
    if type == "LORA":
        cur_select_detail_model_path = os.path.join(real_path_lora, evt.value)
    if type == "Checkpoint":
        cur_select_detail_model_path = os.path.join(real_path_model, evt.value)
    with open(cur_select_detail_model_path + "\\info.txt", "r") as f:
        info = f.readlines()
    for line in info:
        if "base model:" in line:
            base_model = line.split("l:")[-1]
        if "name:" in line:
            name = line.split("e:")[-1]

    return load_all_image_local(cur_select_detail_model_path), name, base_model


def clear_cache_preview():
    # delete the lora and checkpoint floder
    shutil.rmtree(current_ext_dir + "\\LORA")
    shutil.rmtree(current_ext_dir + "\\Checkpoint")


def on_ui_tabs():
    with gr.Blocks() as grapp:
        with gr.Tab("model、lora 预览", elem_id="civitai_preview"):
            name_input_text = gr.inputs.Textbox(label="根据name搜索")
            tag_input_text = gr.inputs.Textbox(label="根据tag搜索")
            with gr.Row():
                type_dropdown = gr.inputs.Dropdown(
                    label="类型选择", choices=["Checkpoint", "LORA"], default="Checkpoint"
                )
                sort_dropdown = gr.inputs.Dropdown(
                    label="排序选择",
                    choices=["Newest", "Most Downloaded", "Highest Rated"],
                    default="Most Downloaded",
                )
                nsfw_dropdown = gr.inputs.Dropdown(
                    label="nsfw选择",
                    choices=["all", "nsfw=true", "nsfw=false"],
                    default="all",
                )

            with gr.Row():
                page_num = gr.inputs.Number(label="页数", default=1)
                per_page_num = gr.inputs.Number(label="每页数量", default=20)
            search_btn = gr.Button(value="搜索")
            with gr.Row():
                load_cache_btn = gr.Button(value="加载已缓存的")
                clear_cache_btn = gr.Button(value="清理缓存")

            gallery = gr.Gallery(label="预览", show_label=True, elem_id="gallery1").style(
                columns=[5], object_fit="contain", height="auto"
            )
            with gr.Row():
                preview_btn = gr.Button(value="查看选中的")
                download_select_btn = gr.Button(value="下载选中的")
            with gr.Row(elem_id="detail_prompts"):
                image_prompts = gr.inputs.Textbox(label="image prompts")
            detail_send_t2i = gr.Button(value="发送到文生图")
            detail_gallery = gr.Gallery(
                label="具体信息", show_label=True, elem_id="detail_gallery"
            ).style(columns=[5], object_fit="contain", height="auto")
        clear_cache_btn.click(clear_cache_preview)
        search_btn.click(
            fn=download_models_pre_fn,
            inputs=[
                name_input_text,
                tag_input_text,
                type_dropdown,
                nsfw_dropdown,
                sort_dropdown,
                page_num,
                per_page_num,
            ],
            outputs=gallery,
        )
        load_cache_btn.click(
            fn=load_all_image_localcache_fn, inputs=[type_dropdown], outputs=gallery
        )
        gallery.select(
            fn=view_selected_detail,
        )
        preview_btn.click(
            fn=download_detail_fn,
            inputs=[type_dropdown],
            outputs=[detail_gallery],
        )
        download_select_btn.click(download_save_model_fn, inputs=[type_dropdown])
        detail_gallery.select(fn=view_selected_prompts, outputs=[image_prompts])

        with gr.Tab("tags搜索") as tab3:
            tag_input = gr.inputs.Textbox(label="Enter a search tag or null for all")
            with gr.Row():
                tag_page_num = gr.inputs.Number(label="页数", default=1)
                tag_per_page_num = gr.inputs.Number(label="每页数量", default=20)
            tag_search_button = gr.Button(value="搜索")
            res_text = gr.outputs.Textbox(label="搜索结果")

        with gr.Tab("查看已经下载的model和lora"):
            with gr.Row():
                local_type_dropdown = gr.inputs.Dropdown(
                    label="类型选择", choices=["Checkpoint", "LORA"], default="Checkpoint"
                )
                button_load_local = gr.Button(value="加载")
            with gr.Row():
                select_model_name = gr.inputs.Textbox(label="选中的模型名")
                select_model_base_model = gr.inputs.Textbox(label="模型底模")
            local_send_t2i = gr.Button(value="发送到文生图")
            gallery3 = gr.Gallery(
                label="模型列表", show_label=True, elem_id="gallery3"
            ).style(columns=[5], object_fit="contain", height="auto")
            with gr.Row(elem_id="local_prompts"):
                local_image_prompts = gr.inputs.Textbox(label="image prompts")
            gallery4 = gr.Gallery(
                label="对应的具体信息", show_label=True, elem_id="gallery4"
            ).style(columns=[5], object_fit="contain", height="auto")

        tag_search_button.click(
            fn=tag_search_fn,
            inputs=[tag_input, tag_page_num, tag_per_page_num],
            outputs=res_text,
        )

        button_load_local.click(
            fn=get_all_download_model, inputs=[local_type_dropdown], outputs=gallery3
        )
        gallery3.select(
            fn=select_local_detail_fn,
            inputs=local_type_dropdown,
            outputs=[gallery4, select_model_name, select_model_base_model],
        )
        gallery4.select(fn=view_selected_prompts, outputs=[local_image_prompts])

        detail_send_t2i.click(fn=None, _js=f"detail_text_send_t2i")
        local_send_t2i.click(fn=None, _js=f"local_text_send_t2i")

        detail_send_t2i.click(fn=None, _js=f"switch_to_txt2img")
        local_send_t2i.click(fn=None, _js=f"switch_to_txt2img")

        return [(grapp, "Civitai Search", "civitai search")]


script_callbacks.on_ui_tabs(on_ui_tabs)
