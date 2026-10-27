import base64
import requests
from pathlib import Path

IMAGE = Path("camera/g1_frame.jpg")
URL = "http://127.0.0.1:8000/v1/chat/completions"

image_data = base64.b64encode(IMAGE.read_bytes()).decode("utf-8")

response = requests.post(
    URL,
    json={
        "model": "Qwen/Qwen3-VL-4B-Instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Describe exactly what is visible in this "
                            "camera image. Identify people, objects, "
                            "furniture and surroundings. "
                            "Do not guess what is outside the image."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/jpeg;base64," + image_data
                        }
                    }
                ]
            }
        ],
        "max_tokens": 200,
        "temperature": 0
    },
    timeout=120
)

response.raise_for_status()

print("\n=== G1 CAMERA SCENE DESCRIPTION ===")
print(response.json()["choices"][0]["message"]["content"])
