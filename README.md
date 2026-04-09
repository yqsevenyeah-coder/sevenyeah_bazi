# AI 算命问答小助手

一款基于八字的 **问答式** AI 算命小助手：在**设置**中填写出生年月日、时辰与性别后，在聊天框向小助手提问，由 **DeepSeek 大模型**结合您的命盘个性化回答。

## 功能

- **问答界面**：聊天式对话，用户提问、DeepSeek 结合命理上下文回答。
- **设置（必填）**：在聊天页右上角「设置」中填写出生年、月、日、时辰（选填）、性别；**未填写不能发起提问**。
- **命盘驱动**：根据设置中的出生信息自动排盘（四柱、大运、流年、喜用神等），并将命理总述、事业与姻缘概况注入大模型上下文，回答均依据用户命盘生成。

## 运行方式

### 1. 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置 DeepSeek API Key（必配）

问答依赖 DeepSeek 接口，请先获取 [DeepSeek API Key](https://platform.deepseek.com/)，并设置环境变量：

```bash
export DEEPSEEK_API_KEY="你的API Key"
```

或在项目根目录创建 `.env` 文件（若你使用 python-dotenv 可后续扩展读取），启动前在终端中执行上述 `export` 即可。

### 3. 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. 使用

- 浏览器打开：**http://localhost:8000**
- 点击右上角 **「设置」**，填写出生年、月、日、时辰（选填）、性别，点击 **「保存」**。
- 保存后即可在下方输入框提问，小助手将结合您的命盘回答。

API 文档：http://localhost:8000/docs

## 项目结构

```
ai_suanming/
├── app/
│   ├── __init__.py
│   ├── main.py      # FastAPI：/api/paipan、/api/chat
│   ├── bazi.py      # 八字排盘、大运流年、喜用神
│   ├── interpret.py # 事业、姻缘解读文案
│   └── llm.py       # DeepSeek 调用与命理上下文拼接
├── static/
│   └── index.html   # 前端：聊天界面 + 设置弹窗
├── requirements.txt
└── README.md
```

## 技术说明

- **排盘**：使用 [lunar_python](https://github.com/6tail/lunar-python) 做公历转农历、四柱与大运计算。
- **喜用神**：按八字五行统计判断身强身弱，据此取喜用神与忌神。
- **问答**：后端根据出生信息排盘并生成命理总述、事业与姻缘概况，拼成「用户命盘上下文」作为 system prompt，调用 DeepSeek 对话接口，返回结合命盘的回复。

## 免责声明

本工具仅供娱乐与文化学习，不构成任何人生决策依据。请理性看待命理，以现实生活为准。
