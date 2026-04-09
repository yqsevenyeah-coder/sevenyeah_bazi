# -*- coding: utf-8 -*-
"""
根据排盘结果生成事业、姻缘等解读文案（规则+模板，大师口吻）
"""
from typing import List


def _wuxing_desc(wuxing_list: List[str]) -> str:
    """五行描述"""
    names = {"木": "木", "火": "火", "土": "土", "金": "金", "水": "水"}
    return "、".join(names.get(x, x) for x in wuxing_list)


def interpret_career(
    day_master_wuxing: str,
    xiyong: List[str],
    current_dayun_ganzhi: str,
    current_liunian: str,
) -> str:
    """事业运势解读"""
    xiyong_str = _wuxing_desc(xiyong)
    day_wx_name = {"木": "木", "火": "火", "土": "土", "金": "金", "水": "水"}.get(day_master_wuxing, day_master_wuxing)
    career_tips = {
        "木": "宜从事文化、教育、林业、设计、出版、木类行业，或与生长、拓展相关的工作。",
        "火": "宜从事能源、互联网、传媒、餐饮、演艺、照明、电子等属火行业。",
        "土": "宜从事房地产、建筑、农业、咨询、仓储、中介等稳重、收纳类工作。",
        "金": "宜从事金融、法律、机械、金属、军警、管理、精密技术等。",
        "水": "宜从事贸易、物流、旅游、水产、咨询、玄学、流动性强的行业。",
    }
    tip = career_tips.get(day_master_wuxing, "宜结合命局喜用择业，以补足五行之气。")
    return (
        f"命主日主为{day_wx_name}，当前喜用神为{xiyong_str}。"
        f"大运{current_dayun_ganzhi or '未起运'}、流年{current_liunian}，"
        f"事业上宜顺势而为，多接触喜用五行所代表的领域与方位。{tip} "
        "今年宜稳中求进，贵人缘尚可，可多结交对你有助益之人。"
    )


def interpret_love(
    day_master_wuxing: str,
    xiyong: List[str],
    current_dayun_ganzhi: str,
    current_liunian: str,
    gender: str,
) -> str:
    """姻缘运势解读"""
    xiyong_str = _wuxing_desc(xiyong)
    is_male = gender and str(gender).lower() in ("male", "男", "m")
    role = "男命" if is_male else "女命"
    return (
        f"{role}日主为{day_master_wuxing}，喜用{xiyong_str}。"
        f"当前大运{current_dayun_ganzhi or '未起运'}、流年{current_liunian}，"
        "姻缘方面宜在喜用神旺的流年流月多把握机缘，单身者可多参加社交、相亲或通过长辈介绍。"
        "已有伴侣者今年宜多沟通、少争执，可择吉日订婚或成婚。"
        "婚恋对象若命局中喜用五行较旺，则更利长久和谐。"
    )


def interpret_summary(
    day_master: str,
    day_master_wuxing: str,
    xiyong: List[str],
    jishen: List[str],
    current_dayun_ganzhi: str,
    current_liunian: str,
    current_age: int,
) -> str:
    """五行喜用与当前运势总述"""
    xiyong_str = _wuxing_desc(xiyong)
    ji_str = _wuxing_desc(jishen)
    return (
        f"命主日干为{day_master}，属{day_master_wuxing}。"
        f"命局喜用神为：{xiyong_str}；忌神为：{ji_str}。"
        f"当前{current_age}岁，正行大运{current_dayun_ganzhi or '未起运'}，流年{current_liunian}。"
        "行事宜多趋喜用、避忌神，如穿衣配色、方位、行业、结交之人皆可略作参考，以助运势。"
    )
