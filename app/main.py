# -*- coding: utf-8 -*-
"""
命询 - FastAPI 入口
"""
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

# 从项目根目录加载 .env（可选：把 DEEPSEEK_API_KEY 写在 .env 里，不要提交）
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.bazi import paipan
from app.interpret import interpret_career, interpret_love, interpret_summary
from app.llm import build_user_context, chat_with_deepseek

# 静态文件目录（项目根下的 static）
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app = FastAPI(
    title="命询",
    description="八字排盘，五行喜用，事业姻缘解读",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PaipanRequest(BaseModel):
    birth_date: str = Field(..., description="出生日期，格式 YYYY-MM-DD")
    gender: str = Field(..., description="性别：male/female 或 男/女")
    birth_time: Optional[str] = Field(None, description="出生时辰，如 10:30，不填默认午时")


class ChatMessage(BaseModel):
    role: str = Field(..., description="user 或 assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    birth_date: str = Field(..., description="出生日期 YYYY-MM-DD")
    gender: str = Field(..., description="性别：male/female 或 男/女")
    birth_time: Optional[str] = Field(None, description="出生时辰，如 10:30")
    message: str = Field(..., description="用户提问")
    history: Optional[List[ChatMessage]] = Field(None, description="历史对话，用于上下文")
    api_key: Optional[str] = Field(None, description="可选：前端传入的 DeepSeek API Key")


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def _send_index():
    from fastapi.responses import FileResponse
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file.resolve()))
    return {"message": "未找到 index.html，请从项目根目录启动", "docs": "/docs"}


@app.get("/")
def root():
    return _send_index()


@app.get("/index.html")
def index_html():
    return _send_index()


@app.get("/health")
def health():
    return {"status": "ok"}


def _parse_birth(birth_date: str, birth_time: Optional[str]):
    """解析出生日期和时辰，返回 (year, month, day, hour, minute)。"""
    try:
        parts = birth_date.strip().split("-")
        if len(parts) != 3:
            raise HTTPException(status_code=400, detail="出生日期格式应为 YYYY-MM-DD")
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    except (ValueError, IndexError):
        raise HTTPException(status_code=400, detail="出生日期格式应为 YYYY-MM-DD，且为有效数字")

    birth_hour, birth_minute = None, None
    if birth_time and birth_time.strip():
        try:
            t = birth_time.strip().replace("：", ":")
            if ":" in t:
                h, m = t.split(":", 1)
                birth_hour, birth_minute = int(h.strip()), int(m.strip())
            else:
                birth_hour = int(t.strip())
                birth_minute = 0
            if not (0 <= birth_hour <= 23 and 0 <= birth_minute <= 59):
                raise ValueError("invalid time")
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="出生时辰格式请用 时:分，如 14:30")
    return year, month, day, birth_hour, birth_minute


def _run_paipan_and_interpret(birth_date: str, gender: str, birth_time: Optional[str]):
    """排盘并附加解读，返回 result 字典。"""
    year, month, day, birth_hour, birth_minute = _parse_birth(birth_date, birth_time)
    try:
        result = paipan(
            birth_year=year,
            birth_month=month,
            birth_day=day,
            gender=gender,
            birth_hour=birth_hour,
            birth_minute=birth_minute,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"排盘计算异常：{str(e)}")
    result["summary"] = interpret_summary(
        day_master=result["day_master"],
        day_master_wuxing=result["day_master_wuxing"],
        xiyong=result["xiyong"],
        jishen=result["jishen"],
        current_dayun_ganzhi=result["current_dayun"]["ganzhi"],
        current_liunian=result["current_liunian"],
        current_age=result["current_age"],
    )
    result["career"] = interpret_career(
        day_master_wuxing=result["day_master_wuxing"],
        xiyong=result["xiyong"],
        current_dayun_ganzhi=result["current_dayun"]["ganzhi"],
        current_liunian=result["current_liunian"],
    )
    result["love"] = interpret_love(
        day_master_wuxing=result["day_master_wuxing"],
        xiyong=result["xiyong"],
        current_dayun_ganzhi=result["current_dayun"]["ganzhi"],
        current_liunian=result["current_liunian"],
        gender=gender,
    )
    return result


@app.post("/api/paipan")
def api_paipan(req: PaipanRequest):
    """排盘并返回四柱、大运、流年、喜用神及事业姻缘解读"""
    return _run_paipan_and_interpret(req.birth_date, req.gender, req.birth_time)


@app.post("/api/chat")
async def api_chat(req: ChatRequest):
    """问答：根据用户出生信息生成命理上下文，由 DeepSeek 结合上下文回答用户提问。"""
    if not (req.birth_date and req.birth_date.strip() and req.gender and req.gender.strip()):
        raise HTTPException(status_code=400, detail="请先在设置中填写出生年月日与性别")
    if not (req.message and req.message.strip()):
        raise HTTPException(status_code=400, detail="请输入提问内容")

    result = _run_paipan_and_interpret(req.birth_date, req.gender, req.birth_time)
    user_context = build_user_context(
        result,
        result["summary"],
        result["career"],
        result["love"],
    )
    history = None
    if req.history:
        history = [{"role": m.role, "content": m.content} for m in req.history]
    reply = await chat_with_deepseek(
        user_message=req.message.strip(),
        user_context=user_context,
        history=history,
        api_key=req.api_key,
    )
    return {"reply": reply}
