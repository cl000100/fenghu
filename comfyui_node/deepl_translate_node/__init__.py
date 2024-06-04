from .fenghu_deepl_translate_node import DeepLTranslate
NODE_CLASS_MAPPINGS = {"fenghu_Translate Node": DeepLTranslate}
NODE_DISPLAY_NAME_MAPPINGS = {"fenghu_Translate": "fenghu_Translate Node"}
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']