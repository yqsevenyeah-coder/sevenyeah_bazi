# -*- coding: utf-8 -*-
"""
DeepSeek 大模型调用：根据用户八字上下文生成回答
"""
import os
from typing import List, Optional
import httpx

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"


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
        f"命理总述：{summary}\n"
        f"事业概况：{career}\n"
        f"姻缘概况：{love}\n"
    )


SYSTEM_PROMPT_TEMPLATE = """你是一位顶尖的八字命理师、国学大师，精通四柱八字、大运流年、五行喜用与人生运势解读。你说话专业、温和、有条理，善于结合命盘给出具体建议，同时提醒咨询者理性看待、以现实为准。

回答时请务必结合下面「当前咨询者的命理信息」来个性化解读，不要泛泛而谈。若问题与命理无关，可简短回应并引导回运势、事业、姻缘、流年等话题。

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
        for h in history:
            if h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_message})

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
                    "max_tokens": 2048,
                    "temperature": 0.7,
                },
            )
            r.raise_for_status()
            data = r.json()
            choice = (data.get("choices") or [None])[0]
            if not choice:
                return "模型未返回有效内容，请重试。"
            return (choice.get("message") or {}).get("content") or "模型返回为空，请重试。"
        except httpx.HTTPStatusError as e:
            return f"接口请求异常（{e.response.status_code}）：请检查 API Key 或稍后重试。"
        except Exception as e:
            return f"请求失败：{str(e)}"
