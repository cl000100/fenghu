import requests
import json
import os

class DeepLTranslate:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "Hello World!"
                }),
                "target_language": (["EN", "ZH", "AUTO"], {
                    "default": "AUTO"
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("Translated Text", "Original Text")
    FUNCTION = "translate"
    CATEGORY = "Fenghu"

    def translate(self, text, target_language):
        script_dir = os.path.dirname(__file__)
        config_path = os.path.join(script_dir, 'config.json')
        
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
            "target_lang": target_language if target_language != "AUTO" else ""
        }
        
        # # 如果目标语言是 AUTO，需要检测源语言
        if target_language == "AUTO":
            # 判断是否包含中文字符的函数
            def contains_chinese(text):
                for char in text:
                    if '\u4e00' <= char <= '\u9fff':
                        return True
                return False

            # 判断是否包含英文字符的函数
            def contains_english(text):
                for char in text:
                    if char.isalpha():
                        return True
                return False

            # 检测源语言
            if contains_chinese(text):
                source_lang = "ZH"
            elif contains_english(text):
                source_lang = "EN"
            else:
                # 如果既没有中文字符也没有英文字符，则默认为中文
                source_lang = "ZH"

            # 根据源语言决定目标语言
            if source_lang == "ZH":
                params["target_lang"] = "EN"
            else:
                params["target_lang"] = "ZH"        

        response = requests.post(url, data=params)
        result = response.json()
        translated_text = result["translations"][0]["text"]
        return (translated_text, text)


# 将节点类映射到框架中
NODE_CLASS_MAPPINGS = {
    "DeepLTranslateNode": DeepLTranslate
}

# 提供友好名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "DeepLTranslateNode": "DeepL Translate Node"
}