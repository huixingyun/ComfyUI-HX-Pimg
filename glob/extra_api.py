from server import PromptServer
import execution
import logging
import time
import uuid

from aiohttp import web

@PromptServer.instance.routes.post("/pimg/prompt_check")
async def prompt_check(request):
    self = PromptServer.instance
    logging.info(f"[pimg] got prompt at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    start_time = time.time()
    json_data =  await request.json()
    json_data = self.trigger_on_prompt(json_data)

    if "number" in json_data:
        number = float(json_data['number'])
    else:
        number = self.number
        if "front" in json_data:
            if json_data['front']:
                number = -number

        self.number += 1

    if "prompt" in json_data:
        prompt = json_data["prompt"]
        prompt_id = str(json_data.get("prompt_id", uuid.uuid4()))
        valid = await execution.validate_prompt(prompt_id, prompt)
        if valid[0]:
            response = {"prompt_id": prompt_id, "number": number, "node_errors": valid[3]}
            elapsed_time = time.time() - start_time
            logging.info(f"[pimg] prompt_check request completed in {elapsed_time:.3f} seconds")
            return web.json_response(response)
        else:
            elapsed_time = time.time() - start_time
            logging.warning(f"[pimg] invalid prompt: {valid[1]}, request took {elapsed_time:.3f} seconds")
            return web.json_response({"error": valid[1], "node_errors": valid[3]}, status=400)
    else:
        elapsed_time = time.time() - start_time
        logging.warning(f"[pimg] no prompt, request took {elapsed_time:.3f} seconds")
        error = {
            "type": "no_prompt",
            "message": "No prompt provided",
            "details": "No prompt provided",
            "extra_info": {}
        }
        return web.json_response({"error": error, "node_errors": {}}, status=400)
