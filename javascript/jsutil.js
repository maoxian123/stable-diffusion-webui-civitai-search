function switch_to_civitai_tab(num) {
    gradioApp().getElementById('tab_civitai search').querySelectorAll('button')[num].click();
}
function switch_to_civitai_search() {
    switch_to_civitai_tab(0);

    return args_to_array(arguments);
}

function switch_to_civitai_detail() {
    switch_to_civitai_tab(1);

    return args_to_array(arguments);
}
function switch_to_civitai_tags() {
    switch_to_civitai_tab(2);

    return args_to_array(arguments);
}

function switch_to_civitai_local_view() {
    switch_to_civitai_tab(3);

    return args_to_array(arguments);
}

function detail_text_send_t2i() {
    gradioApp().getElementById('txt2img_prompt').querySelectorAll('textarea')[0].value = gradioApp().getElementById('detail_prompts').querySelectorAll('textarea')[0].value;
    return args_to_array(arguments);
}

function local_text_send_t2i() {
    gradioApp().getElementById('txt2img_prompt').querySelectorAll('textarea')[0].value = gradioApp().getElementById('local_prompts').querySelectorAll('textarea')[0].value;
    return args_to_array(arguments);
}

function send_test() {
    gradioApp().getElementById('txt2img_prompt').querySelectorAll('textarea')[0].value = '123';
    return args_to_array(arguments);
}