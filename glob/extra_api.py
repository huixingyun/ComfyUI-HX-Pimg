from server import PromptServer
import execution
import logging
import time
import uuid
import functools

from aiohttp import web


def log_execution_time(func):
    """装饰器：记录函数执行时间"""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logging.info(f"[pimg] {func.__name__} request started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logging.info(
                f"[pimg] {func.__name__} request completed in {elapsed_time:.3f} seconds"
            )
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logging.error(
                f"[pimg] {func.__name__} request failed after {elapsed_time:.3f} seconds: {str(e)}"
            )
            raise

    return wrapper


@PromptServer.instance.routes.post("/pimg/prompt_check")
@log_execution_time
async def prompt_check(request):
    self = PromptServer.instance
    json_data = await request.json()
    json_data = self.trigger_on_prompt(json_data)

    if "number" in json_data:
        number = float(json_data["number"])
    else:
        number = self.number
        if "front" in json_data:
            if json_data["front"]:
                number = -number

        self.number += 1

    if "prompt" in json_data:
        prompt = json_data["prompt"]
        prompt_id = str(json_data.get("prompt_id", uuid.uuid4()))
        valid = await execution.validate_prompt(prompt_id, prompt)
        if valid[0]:
            response = {
                "prompt_id": prompt_id,
                "number": number,
                "node_errors": valid[3],
            }
            return web.json_response(response)
        else:
            logging.warning(f"[pimg] invalid prompt: {valid[1]}")
            return web.json_response(
                {"error": valid[1], "node_errors": valid[3]}, status=400
            )
    else:
        logging.warning(f"[pimg] no prompt")
        error = {
            "type": "no_prompt",
            "message": "No prompt provided",
            "details": "No prompt provided",
            "extra_info": {},
        }
        return web.json_response({"error": error, "node_errors": {}}, status=400)
