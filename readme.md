榴莲猫播客生成器

榴莲猫播客生成器是一个基于 AI 的工具，可以将 PDF 文档转换为播客形式的音频内容。

该项目使用 React 构建前端界面，Flask 作为后端服务，并集成了 OpenAI 和 Fish Audio 的 API 来生成对话和语音。

# 功能特点

- 上传 PDF 文件并转换为播客对话
- 支持 OpenAI 和 Fish Audio 两种音频生成方式
- 可自定义说话者声音
- 生成文本记录和音频文件
- 支持音频预览和下载

# 技术栈

- 前端: React, Tailwind CSS
- 后端: Flask, Python
- API: OpenAI, Fish Audio

# 安装和运行

## 前端

1. 进入 `client` 目录
2. 安装依赖: `npm install`
3. 运行开发服务器: `npm start`

## 后端

1. 进入 `backend` 目录
2. 创建虚拟环境: `python -m venv venv`
3. 激活虚拟环境:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. 安装依赖: `pip install -r requirements.txt`
5. 设置环境变量:
   - 创建 `.env` 文件并添加以下内容:
     ```
     OPENAI_API_KEY=your_openai_api_key
     FISH_AUDIO_API_KEY=your_fish_audio_api_key
     ```
6. 运行 Flask 服务器: `python app.py`

# 使用说明

1. 打开浏览器访问 `http://localhost:3000`
2. 上传 PDF 文件
3. 选择文本生成模型和音频生成选项
4. 点击"转换 PDF"按钮
5. 等待转换完成
6. 查看生成的文本记录和音频文件
7. 可以预览或下载生成的音频

# 文件结构

- `client/`: 前端 React 应用
  - `src/App.js`: 主要的 React 组件
  - `src/index.css`: 全局样式文件
- `backend/`: 后端 Flask 应用
  - `app.py`: 主要的 Flask 应用文件
  - `fishaudio/`: Fish Audio API 相关功能

# 注意事项

- 确保已正确设置 OpenAI 和 Fish Audio 的 API 密钥
- 转换大文件可能需要较长时间，请耐心等待
- 使用 Fish Audio API 需要额外的配置和权限