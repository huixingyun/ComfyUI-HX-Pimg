from PIL import Image
from PIL.PngImagePlugin import PngInfo
import json
from io import BytesIO
import numpy as np
import struct
import comfy.utils
import time
from comfy.cli_args import args
from server import PromptServer, BinaryEventTypes


class SaveImageWithPromptsWebsocket:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
            },
            "optional": {
                "enable_metadata": ("BOOLEAN", {"default": False}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"

    OUTPUT_NODE = True

    CATEGORY = "HX-Pimg/Image"
    DESCRIPTION = "Save images with prompts via websocket."

    def save_images(
        self, images, enable_metadata=False, prompt=None, extra_pnginfo=None
    ):
        total = images.shape[0]
        pbar = comfy.utils.ProgressBar(total)
        for image in images:
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            metadata = None
            if enable_metadata and not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        if isinstance(extra_pnginfo[x], str):
                            metadata.add_text(x, extra_pnginfo[x])
                        else:
                            metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            image_type = "PNG"
            type_num = 2
            bytesIO = BytesIO()
            header = struct.pack(">I", type_num)
            bytesIO.write(header)
            img.save(
                bytesIO,
                format=image_type,
                pnginfo=metadata,
                quality=95,
                compress_level=1,
            )
            preview_bytes = bytesIO.getvalue()

            pbar.update(1)
            server = PromptServer.instance
            if server.client_id is not None:
                server.send_sync(
                    BinaryEventTypes.PREVIEW_IMAGE, preview_bytes, server.client_id
                )

        return {}

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        return time.time()
