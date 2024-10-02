import requests
import json

def text_to_speech(text, model_id, api_key):
    url = "https://api.fish.audio/v1/tts"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "text": text,
        "reference_id": model_id
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")

# 移除了之前的示例使用代码