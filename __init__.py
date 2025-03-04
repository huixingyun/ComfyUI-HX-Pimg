from .websocket_image_save_prompt import SaveImageWithPromptsWebsocket

from .glob import extra_api

NODE_CLASS_MAPPINGS = {
    "SaveImageWithPromptsWebsocket": SaveImageWithPromptsWebsocket,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageWithPromptsWebsocket": "Save Image Websocket",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
