# -*- coding: utf-8 -*-
"""
根据排盘结果生成佩戴、工作与城市等建议文案
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
    """工作及城市建议"""
    xiyong_str = _wuxing_desc(xiyong)
    day_wx_name = {"木": "木", "火": "火", "土": "土", "金": "金", "水": "水"}.get(
        day_master_wuxing, day_master_wuxing
    )
    work_tips = {
        "木": "工作方向可偏教育、文化、设计、内容、园林、生长拓展类行业；城市宜选绿化好、节奏相对舒展、重视创意与文化氛围的地方。",
        "火": "工作方向可偏互联网、传媒、品牌、餐饮、演艺、能源、电子类行业；城市宜选经济活跃、曝光度高、信息流动快的一二线城市。",
        "土": "工作方向可偏地产、建筑、咨询、行政、供应链、仓储与稳定经营类岗位；城市宜选省会、交通枢纽或生活稳定、产业扎实的城市。",
        "金": "工作方向可偏金融、法律、管理、机械、审计、精密技术类岗位；城市宜选制度成熟、产业规范、制造业或金融业较强的城市。",
        "水": "工作方向可偏贸易、物流、旅游、咨询、跨境、流动性强的行业；城市宜选临江临海、交通便利、开放度高、资源流动快的城市。",
    }
    city_by_xiyong = {
        "木": "东方、东南方的城市通常更合拍，可多关注绿化多、文化感强的新一线或省会城市。",
        "火": "南方城市更容易带动气场，适合考虑发展机会多、市场活跃、消费与传播产业发达的地方。",
        "土": "中部、内陆、平台型城市更稳，适合长期沉淀、积累资源与人脉。",
        "金": "西方、西北方或产业成熟的城市更利发挥执行力与专业能力。",
        "水": "北方、沿海、港口或国际化程度高的城市更利资源流动与机会拓展。",
    }
    work_tip = work_tips.get(day_master_wuxing, "宜结合命局喜用择业，以补足五行之气。")
    city_tip = "；".join(city_by_xiyong[x] for x in xiyong if x in city_by_xiyong) or "城市选择上，可优先考虑与你喜用五行相呼应、资源流动性更强的地方。"
    return (
        f"命主日主为{day_wx_name}，当前喜用神为{xiyong_str}。"
        f"现阶段行{current_dayun_ganzhi or '未起运'}大运、流年{current_liunian}，工作选择宜顺势贴近喜用五行。"
        f"{work_tip} {city_tip}"
    )


def interpret_love(
    day_master_wuxing: str,
    xiyong: List[str],
    current_dayun_ganzhi: str,
    current_liunian: str,
    gender: str,
) -> str:
    """佩戴建议（五行水晶）"""
    xiyong_str = _wuxing_desc(xiyong)
    crystal_map = {
        "木": "绿幽灵、东陵玉、孔雀石",
        "火": "草莓晶、红玛瑙、石榴石",
        "土": "黄水晶、虎眼石、茶晶",
        "金": "白水晶、月光石、白玛瑙",
        "水": "海蓝宝、黑曜石、青金石",
    }
    crystal_list = [crystal_map[x] for x in xiyong if x in crystal_map]
    crystal_text = "；".join(crystal_list) if crystal_list else "白水晶、黑曜石等相对中性的水晶"
    return (
        f"你的喜用神为{xiyong_str}，当前行{current_dayun_ganzhi or '未起运'}大运、流年{current_liunian}。"
        f"日常佩戴可优先考虑对应五行的水晶：{crystal_text}。"
        "佩戴上以长期、稳定、不过量堆叠为宜，主饰建议集中在 1 到 2 种主五行，避免同时混戴过多相冲属性。"
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
