import requests
import json
import os

class DeepLTranslate:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "Hello World!"
                }),
                "target_language": ("STRING", {
                    "multiline": False,
                    "default": "EN"
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "translate"

    CATEGORY = "Fenghu"

    def translate(self, text, target_language):
        script_dir = os.path.dirname(__file__)
        #config_path = '/Users/chenglei/ComfyUI/custom_nodes/ComfyUI_fenghu/config.json'
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        # 打印路径进行调试
        print(f"Script directory: {script_dir}")
        print(f"Config path: {config_path}")

        with open(config_path, 'r') as f:
            config = json.load(f)
        auth_key = config['auth_key']
        
        url = "https://api-free.deepl.com/v2/translate"
        params = {
            "auth_key": auth_key,
            "text": text,
            "target_lang": target_language
        }
        response = requests.post(url, data=params)
        result = response.json()
        translated_text = result["translations"][0]["text"]
        return (translated_text,)

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "fenghu_Translate Node": DeepLTranslate
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "fenghu_Translate": "fenghu_Translate Node"
}