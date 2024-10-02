import concurrent.futures as cf
import io
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Literal
from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI
from promptic import llm
from pydantic import BaseModel, ValidationError
from pypdf import PdfReader
from tenacity import retry, retry_if_exception_type
from fishaudio.use import text_to_speech as fish_tts
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import traceback
import re
import time

os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# 加载 .env 文件
load_dotenv()

# 获取 API 密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FISH_AUDIO_API_KEY = os.getenv("FISH_AUDIO_API_KEY")

if not FISH_AUDIO_API_KEY:
    logger.warning("Fish Audio API key 未在环境变量中设置")

# 定义 Fish Audio 模型
FISH_AUDIO_MODELS = {
    "zhou": "d8cb9a2a89844babbeeda24c974a0af2",
    "dong": "22436dbbbfe94e0bb4e137725d16c8c2",
    "xing": "07ea9673918042debb4080f4efdc2da3",
    "yang": "afb76b7abffd48c49bed68cc01054fab"
}

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_fish_audio(text: str, model_id: str) -> bytes:
    if not FISH_AUDIO_API_KEY:
        raise ValueError("Fish Audio API key 未设置")
    return fish_tts(text, model_id, api_key=FISH_AUDIO_API_KEY)

def read_readme():
    readme_path = Path("README.md")
    if readme_path.exists():
        with open(readme_path, "r") as file:
            content = file.read()
            content = re.sub(r'--.*?--', '', content, flags=re.DOTALL)
            return content
    else:
        return "README.md not found. Please check the repository for more information."

INSTRUCTION_TEMPLATES = {
"podcast (Chinese)": {
"intro": """你的任务是将提供的输入文本转变为一个深度、引人入胜、信息丰富的播客对话，风格类似NPR，但更加深入和具体。输入文本可能来自各种来源，可能是未经整理的或非结构化的。
你的目标是提取关键点，识别定义和可能在播客中深入讨论的有趣事实。要善于使用具体例子和类比来解释抽象或复杂的概念，使其易于理解。
为广泛的听众仔细定义所有使用的术语，并提供深入的解释和背景信息。
""",
"text_instructions": "首先，仔细阅读输入文本，识别主要话题、关键点和任何有趣的事实或轶事。思考如何以一种深入且引人入胜的方式呈现这些信息，适合高质量的呈现。特别注意可能需要更详细解释或具体例子的复杂概念。",
"scratch_pad": """集思广益，想出一些讨论你在输入文本中识别到的主要话题和关键点的创新方式。考虑使用丰富的类比、具体的实际例子、引人入胜的故事或假设场景，让内容对听众更具相关性和吸引力。
对于每个关键概念，至少构思2-3个具体的例子或类比，以帮助听众更好地理解。这些例子应该涵盖不同的角度，以照顾到不同背景的听众。
虽然你的播客应面向普通大众，但不要害怕深入探讨复杂的主题。相反，要善于用简单的语言和生动的例子来解释复杂的概念。考虑如何将抽象的想法与日常生活联系起来。
利用你的想象力填补输入文本中的任何空白，或提出一些值得深入探讨的发人深省的问题。目标是创造一个既有深度又引人入胜的对话，因此在方法上要富有创意和洞察力。
明确地定义所有使用的术语，并花时间解释其背景和重要性。考虑这些概念如何与更广泛的主题或当前事件联系起来。
在这里写下你的头脑风暴想法和播客对话的详细大纲。务必记录你想在结尾重复的关键见解和收获，以及你打算用来解释这些见解的具体例子。
确保让它既有深度又令人兴奋，能够激发听众的思考和讨论。
""",
"prelude": """现在你已经进行了深入的头脑风暴并创建了一个详细大纲，是时候编写实际的播客对话了。目标是创造一个既有深度又自然流畅的对话。结合你头脑风暴中的最佳想法和例子，确保以简单易懂yet深入的方式解释复杂的主题。
""",
"dialog": """在这里写下一个非常长、深入且引人入胜的播客对话，基于你在头脑风暴会议中提出的关键点、创意和具体例子。使用自然的对话语气，并包含必要的上下文、解释和例子，使复杂的内容易于普通听众理解。
不要为主持人和嘉宾使用虚构的名字，而是让听众体验一个深入且沉浸式的经历。不要包括像[主持人]或[嘉宾]这样的占位符。设计你的输出以供大声朗读——它将被直接转换为音频。
使对话尽可能长且详细，同时保持在主题上并维持引人入胜的流畅性。对于每个关键概念，至少使用2-3个具体的例子或类比来解释。这些例子应该是多样化的，以适应不同背景的听众。
不要害怕深入探讨复杂的主题。相反，要善于用简单的语言和生动的例子来解释复杂的概念。考虑如何将抽象的想法与日常生活联系起来，使用听众熟悉的情景来阐述深奥的概念。
在讨论过程中，主持人和嘉宾应该提出思考性的问题，并探讨这些概念更广泛的影响和应用。鼓励听众思考这些想法如何与他们的生活或更大的社会问题相关联。
充分利用你的输出能力，创造尽可能长的播客节目，同时以深入且有趣的方式传达输入文本中的关键信息。
在对话的最后，主持人和嘉宾应自然总结他们讨论的主要见解和收获。这应从对话中自然流出，以随意、对话的方式重复关键点。避免显得像是显而易见的总结——目标是在结束前最后一次加强核心思想，同时提供一些具体的行动建议或进一步思考的方向。
播客应约有30,000字，以确保有足够的篇幅深入探讨主题。
""",
},
}

STANDARD_TEXT_MODELS = [
    "gpt-4o-mini",
     "gpt-4o",
    "o1-preview",
    "o1-mini",

]

STANDARD_AUDIO_MODELS = [
    "tts-1",
    "tts-1-hd",
]

STANDARD_VOICES = [
    "alloy",
    "echo",
    "fable",
    "onyx",
    "nova",
    "shimmer",
]

class DialogueItem(BaseModel):
    text: str
    speaker: Literal["speaker-1", "speaker-2"]

class Dialogue(BaseModel):
    scratchpad: str
    dialogue: List[DialogueItem]

def get_mp3(text: str, voice: str, audio_model: str, api_key: str = None) -> bytes:
    client = OpenAI(
        api_key=api_key or os.getenv("OPENAI_API_KEY"),
    )

    with client.audio.speech.with_streaming_response.create(
        model=audio_model,
        voice=voice,
        input=text,
    ) as response:
        with io.BytesIO() as file:
            for chunk in response.iter_bytes():
                file.write(chunk)
            return file.getvalue()

from functools import wraps

def conditional_llm(model, api_base=None, api_key=None):
    def decorator(func):
        if api_base:
            return llm(model=model, api_base=api_base)(func)
        else:
            return llm(model=model, api_key=api_key)(func)
    return decorator

def generate_audio(
    pdf_files: list,
    text_model: str = "gpt-4o-mini",
    audio_model: str = "tts-1",
    speaker_1_voice: str = "alloy",
    speaker_2_voice: str = "echo",
    fish_speaker_1: str = "xing",
    fish_speaker_2: str = "dong",
    api_base: str = None,
    debug: bool = False,
    use_fish_audio: bool = False,
) -> tuple:
    logger.info("开始生成音频")
    start_time = time.time()

    # 从环境变量获取 API 密钥
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OpenAI API key is not set in environment variables")

    combined_text = ""
    logger.info("开始读取PDF文件")
    for file in pdf_files:
        with Path(file).open("rb") as f:
            reader = PdfReader(f)
            text = "\n\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            combined_text += text + "\n\n"
    logger.info(f"PDF文件读取完成，共{len(combined_text)}个字符")

    template = INSTRUCTION_TEMPLATES["podcast (Chinese)"]

    @retry(retry=retry_if_exception_type(ValidationError))
    @conditional_llm(model=text_model, api_base=api_base, api_key=openai_api_key)
    def generate_dialogue(text: str, intro_instructions: str, text_instructions: str, scratch_pad_instructions: str, 
                          prelude_dialog: str, podcast_dialog_instructions: str) -> Dialogue:
        """
        {intro_instructions}
        
        Here is the original input text:
        
        <input_text>
        {text}
        </input_text>

        {text_instructions}
        
        <scratchpad>
        {scratch_pad_instructions}
        </scratchpad>
        
        {prelude_dialog}
        
        <podcast_dialogue>
        {podcast_dialog_instructions}
        </podcast_dialogue>
        """

    logger.info(f"开始生成对话，使用模型：{text_model}")
    dialogue_start_time = time.time()
    llm_output = generate_dialogue(
        combined_text,
        intro_instructions=template["intro"],
        text_instructions=template["text_instructions"],
        scratch_pad_instructions=template["scratch_pad"],
        prelude_dialog=template["prelude"],
        podcast_dialog_instructions=template["dialog"]
    )
    logger.info(f"对话生成完成，耗时：{time.time() - dialogue_start_time:.2f}秒")

    audio = b""
    transcript = ""
    characters = 0

    logger.info("开始生成音频")
    audio_start_time = time.time()
    with cf.ThreadPoolExecutor() as executor:
        futures = []
        for line in llm_output.dialogue:
            transcript_line = f"{line.speaker}: {line.text}"
            if use_fish_audio:
                voice = FISH_AUDIO_MODELS[fish_speaker_1] if line.speaker == "speaker-1" else FISH_AUDIO_MODELS[fish_speaker_2]
                future = executor.submit(get_fish_audio, line.text, voice)
            else:
                voice = speaker_1_voice if line.speaker == "speaker-1" else speaker_2_voice
                future = executor.submit(get_mp3, line.text, voice, audio_model, openai_api_key)
            futures.append((future, transcript_line))
            characters += len(line.text)

        for i, (future, transcript_line) in enumerate(futures):
            logger.info(f"开始处理音频段 {i+1}/{len(futures)}, 文本长度: {len(line.text)}")
            try:
                audio_chunk = future.result()
                logger.info(f"音频段 {i+1} 处理成功")
            except Exception as e:
                logger.error(f"处理音频段 {i+1} 时出错: {str(e)}")
                raise
            audio += audio_chunk
            transcript += transcript_line + "\n\n"

    logger.info(f"音频生成完成，耗时：{time.time() - audio_start_time:.2f}秒")
    logger.info(f"生成了{characters}个字符的音频")

    temporary_directory = "./tmp/"
    os.makedirs(temporary_directory, exist_ok=True)

    temporary_file = NamedTemporaryFile(
        dir=temporary_directory,
        delete=False,
        suffix=".mp3",
    )
    temporary_file.write(audio)
    temporary_file.close()

    logger.info(f"音频文件已保存：{temporary_file.name}")
    logger.info(f"总耗时：{time.time() - start_time:.2f}秒")

    return temporary_file.name, transcript, combined_text

@app.route('/api/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件部分'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        text_model = request.form.get('text_model', 'o1-preview-2024-09-12')
        audio_model = request.form.get('audio_model', 'tts-1')
        speaker_1_voice = request.form.get('speaker_1_voice', 'alloy')
        speaker_2_voice = request.form.get('speaker_2_voice', 'echo')
        use_fish_audio = request.form.get('use_fish_audio', 'false').lower() == 'true'
        fish_speaker_1 = request.form.get('fish_speaker_1', 'zhou')
        fish_speaker_2 = request.form.get('fish_speaker_2', 'dong')

        try:
            audio_file, transcript, _ = generate_audio(
                [file_path],
                text_model=text_model,
                audio_model=audio_model,
                speaker_1_voice=speaker_1_voice,
                speaker_2_voice=speaker_2_voice,
                fish_speaker_1=fish_speaker_1,
                fish_speaker_2=fish_speaker_2,
                use_fish_audio=use_fish_audio
            )
            return jsonify({'success': True, 'transcript': transcript, 'audio_file': audio_file})
        except Exception as e:
            logger.error(f"转换过程中出错：{str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/download', methods=['GET'])
def download():
    audio_file = request.args.get('file')
    if not audio_file:
        return jsonify({'error': '没有指定文件'}), 400
    return send_file(audio_file, as_attachment=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)