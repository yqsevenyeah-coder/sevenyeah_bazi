# -*- coding: utf-8 -*-
"""
DeepSeek 大模型调用：根据用户八字上下文生成回答
"""
import os
from typing import List, Optional
import httpx

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"
MAX_HISTORY_MESSAGES = 6
MAX_HISTORY_CHARS = 600
MAX_USER_MESSAGE_CHARS = 800


def _clip_text(text: str, max_chars: int) -> str:
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def build_user_context(paipan_result: dict, summary: str, career: str, love: str) -> str:
    """根据排盘与解读结果拼出给大模型的用户命理上下文"""
    s = paipan_result.get("sizhu", {})
    sizhu = f"四柱：年{s.get('year','')} 月{s.get('month','')} 日{s.get('day','')} 时{s.get('time','')}"
    return (
        "【当前咨询者的命盘信息，请据此个性化回答】\n"
        f"{sizhu}；纳音：{', '.join(s.get('nayin') or [])}。\n"
        f"日主：{paipan_result.get('day_master','')}（{paipan_result.get('day_master_wuxing','')}）。\n"
        f"喜用神：{', '.join(paipan_result.get('xiyong') or [])}；忌神：{', '.join(paipan_result.get('jishen') or [])}。\n"
        f"当前年龄 {paipan_result.get('current_age')} 岁，大运 {paipan_result.get('current_dayun', {}).get('ganzhi') or '未起运'}，"
        f"流年 {paipan_result.get('current_liunian')}。\n"
        f"命理总述：{_clip_text(summary, 160)}\n"
        f"工作及城市建议：{_clip_text(career, 180)}\n"
        f"佩戴建议：{_clip_text(love, 160)}\n"
    )


SYSTEM_PROMPT_TEMPLATE = """你是一位有耐心、会循循善诱的命理老师。回答要结合命盘，语气温和、自然、清楚，像在和学生一对一交流。

回答规则：
1. 先回答用户最关心的问题，再解释原因。
2. 默认不要太长，控制在 220 字以内；除非用户明确要求详细展开。
3. 不要写成营销文案或产品提示语，也不要故作神秘。
4. 可以像老师一样适度安抚、提醒，但不要空泛说教。
5. 给建议时尽量具体、能落地，优先回答用户这次提问本身。
6. 若不确定，明确说“偏向”或“更适合”，不要说得过满。

%s"""


async def chat_with_deepseek(
    user_message: str,
    user_context: str,
    history: Optional[List[dict]] = None,
    api_key: Optional[str] = None,
) -> str:
    """
    调用 DeepSeek 对话接口。
    history: 可选，格式 [{"role":"user","content":"..."},{"role":"assistant","content":"..."}, ...]
    返回助手回复文本。
    """
    key = (api_key or os.environ.get("DEEPSEEK_API_KEY") or "").strip()
    if not key:
        return "未配置 DeepSeek API Key。请在服务端设置环境变量 DEEPSEEK_API_KEY 后重试。"

    system_content = SYSTEM_PROMPT_TEMPLATE % user_context
    messages = [{"role": "system", "content": system_content}]
    if history:
        for h in history[-MAX_HISTORY_MESSAGES:]:
            if h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({
                    "role": h["role"],
                    "content": _clip_text(h["content"], MAX_HISTORY_CHARS),
                })
    messages.append({"role": "user", "content": _clip_text(user_message, MAX_USER_MESSAGE_CHARS)})

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            r = await client.post(
                DEEPSEEK_API_URL,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MODEL,
                    "messages": messages,
                    "max_tokens": 420,
                    "temperature": 0.55,
                },
            )
            r.raise_for_status()
            data = r.json()
            choice = (data.get("choices") or [None])[0]
            if not choice:
                return "模型未返回有效内容，请重试。"
            return (choice.get("message") or {}).get("content") or "模型返回为空，请重试。"
        except httpx.HTTPStatusError as e:
            detail = ""
            try:
                payload = e.response.json()
                detail = payload.get("error", {}).get("message") or payload.get("detail") or ""
            except Exception:
                detail = e.response.text[:160]
            return f"接口请求异常（{e.response.status_code}）：{detail or '请检查 API Key、额度或稍后重试。'}"
        except Exception as e:
            return f"请求失败：{str(e)}"
