import requests
import json
import os   

API_TOKEN = os.getenv("FISH_API_TOKEN")
API_URL = "https://api.fish.audio"

def create_model(title, voice_file_path, text):
    url = f"{API_URL}/model"
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    data = {
        "visibility": "unlist",  # 改为 unlist 以避免需要封面图片
        "type": "tts",
        "title": title,
        "train_mode": "fast"
    }
    

    files = {
        "voices": open(voice_file_path, "rb"),
        "texts": (None, text)
    }
    
    response = requests.post(url, headers=headers, data=data, files=files)
    
    if response.status_code == 201:
        return response.json()["_id"]
    else:
        print(f"错误: {response.status_code}")
        print(response.text)
        return None

# 使用示例
model_id = create_model("zhou", "D:\\pdf-to-podcast\\model-wav\\yang.wav", 
                        "我觉得对于我来说的未来就是比如说你更有想要去做的事情了并且这些事情你有努力的方向和目标了你也知道该怎么去做了以及对于自己你说接系也好或者是待人处事也好或者人与人的关系也好你会有更深刻的不能说是更深刻吧我觉得是有一些更新的理解人与人的关系也好你会有更深刻的不能说是更深刻吧我觉得是有一些更新的理解")
print(f"创建的模型ID: {model_id}")