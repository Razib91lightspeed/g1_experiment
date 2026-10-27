import base64
import json
import sys
from pathlib import Path

import requests

SPARK_URL = "http://127.0.0.1:8000/v1/chat/completions"
MODEL = "Qwen/Qwen3-VL-4B-Instruct"

def analyze_image(image_path):
    image = Path(image_path)
    if not image.is_file():
        raise FileNotFoundError(image)

    encoded = base64.b64encode(image.read_bytes()).decode()

    response = requests.post(
        SPARK_URL,
        json={
            "model": MODEL,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Is a person visible in this image? "
                            "Answer with JSON only: "
                            '{"person_visible": true} or '
                            '{"person_visible": false}.'
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded}"
                        }
                    }
                ]
            }],
            "temperature": 0,
            "max_tokens": 100
        },
        timeout=120
    )
    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]
    print("VLM response:", content)

    # Display only. No robot action is executed.
    return content


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m spark_client.vlm_client image.jpg")

    analyze_image(sys.argv[1])
