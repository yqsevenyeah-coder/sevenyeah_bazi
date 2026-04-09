# -*- coding: utf-8 -*-
"""
八字排盘：四柱、大运、流年、五行喜用
"""
from datetime import datetime
from typing import List, Optional, Tuple
from lunar_python import Solar, Lunar


# 天干地支对应的五行
TIAN_GAN_WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土",
    "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}
DI_ZHI_WUXING = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水",
}
# 地支藏干（本气）
DI_ZHI_CANG_GAN = {
    "子": "癸", "丑": "己", "寅": "甲", "卯": "乙", "辰": "戊", "巳": "丙",
    "午": "丁", "未": "己", "申": "庚", "酉": "辛", "戌": "戊", "亥": "壬",
}


def _count_wuxing(ganzhi_list: List[str]) -> dict:
    """统计干支列表中的五行数量（天干+地支本气）"""
    wuxing = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for gz in ganzhi_list:
        if len(gz) != 2:
            continue
        g, z = gz[0], gz[1]
        wuxing[TIAN_GAN_WUXING.get(g, "")] = wuxing.get(TIAN_GAN_WUXING.get(g, ""), 0) + 1
        wuxing[DI_ZHI_WUXING.get(z, "")] = wuxing.get(DI_ZHI_WUXING.get(z, ""), 0) + 1
    return wuxing


def _day_master_strong(wuxing: dict, day_gan_wx: str) -> bool:
    """简单身强身弱：日主五行在八字中数量 >= 3 视为偏强"""
    return wuxing.get(day_gan_wx, 0) >= 3


def get_xiyong(ganzhi_list: List[str], day_gan: str) -> Tuple[List[str], List[str]]:
    """
    根据日主与八字五行分布，简单取喜用神与忌神。
    日主五行：日干对应的五行。
    身强：喜克、泄、耗（官杀、食伤、财）；身弱：喜生、扶（印、比劫）。
    返回 (喜用神列表, 忌神列表)，元素为五行名。
    """
    wuxing = _count_wuxing(ganzhi_list)
    day_gan_wx = TIAN_GAN_WUXING.get(day_gan, "")
    strong = _day_master_strong(wuxing, day_gan_wx)

    # 五行生克：木生火，火生土，土生金，金生水，水生木；克：木克土，土克水，水克火，火克金，金克木
    sheng = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    ke = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    inv_sheng = {v: k for k, v in sheng.items()}  # 生我者为印

    if strong:
        # 身强喜克(官杀)、泄(食伤)、耗(财)
        xi_yong = [ke[day_gan_wx], sheng[day_gan_wx], ke[sheng[day_gan_wx]]]
        ji = [day_gan_wx, inv_sheng.get(day_gan_wx, "")]  # 比劫、印
    else:
        # 身弱喜生(印)、扶(比劫)
        xi_yong = [inv_sheng.get(day_gan_wx, ""), day_gan_wx]
        ji = [ke[day_gan_wx], sheng[day_gan_wx]]  # 官杀、食伤
    xi_yong = list(dict.fromkeys(x for x in xi_yong if x))
    ji = list(dict.fromkeys(x for x in ji if x))
    return (xi_yong, ji)


def paipan(
    birth_year: int,
    birth_month: int,
    birth_day: int,
    gender: str,
    birth_hour: Optional[int] = None,
    birth_minute: Optional[int] = None,
) -> dict:
    """
    排盘入口。
    gender: 'male' | 'female'
    若无时辰，默认午时 12:00（便于无时辰用户也能看四柱与大致运势）。
    """
    if birth_hour is None:
        birth_hour, birth_minute = 12, 0
    if birth_minute is None:
        birth_minute = 0

    solar = Solar.fromYmdHms(birth_year, birth_month, birth_day, birth_hour, birth_minute, 0)
    lunar = solar.getLunar()
    ec = lunar.getEightChar()

    # 四柱（lunar_python 的 getYear/getMonth 等返回干支字符串）
    year_gz = ec.getYear()
    month_gz = ec.getMonth()
    day_gz = ec.getDay()
    time_gz = ec.getTime()

    # 十神（日干视角）
    ss_gan = lunar.getBaZiShiShenGan()
    ss_zhi = lunar.getBaZiShiShenZhi()
    wuxing_cols = lunar.getBaZiWuXing()
    nayin = lunar.getBaZiNaYin()

    # 大运
    yun_gender = 1 if gender.lower() in ("male", "男", "m") else 0
    yun = ec.getYun(yun_gender)
    dayun_list = yun.getDaYun()

    # 当前年龄（周岁）
    today = datetime.now()
    birth = datetime(birth_year, birth_month, birth_day)
    age = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1

    # 当前所在大运
    current_dayun = None
    current_dayun_index = -1
    for i, dy in enumerate(dayun_list):
        start_age = dy.getStartAge()
        end_age = dy.getEndAge()
        if start_age is not None and end_age is not None and start_age <= age <= end_age:
            current_dayun = dy
            current_dayun_index = i
            break
    if current_dayun is None and dayun_list:
        if age < dayun_list[0].getStartAge():
            current_dayun = dayun_list[0]
            current_dayun_index = 0
        else:
            current_dayun = dayun_list[-1]
            current_dayun_index = len(dayun_list) - 1

    current_dayun_ganzhi = current_dayun.getGanZhi() if current_dayun else ""
    current_dayun_range = ""
    if current_dayun:
        current_dayun_range = f"{current_dayun.getStartAge()}-{current_dayun.getEndAge()}岁"

    # 当前流年：用今年公历转干支
    current_year = today.year
    solar_year = Solar.fromYmdHms(current_year, 6, 15, 12, 0, 0)
    lunar_year = solar_year.getLunar()
    liunian_ganzhi = lunar_year.getYearInGanZhi()

    # 喜用神（四柱干支列表 + 日干，日干为日柱干支的第一个字）
    ganzhi_list = [year_gz, month_gz, day_gz, time_gz]
    day_gan = day_gz[0] if len(day_gz) >= 1 else ""
    xi_yong, ji_shen = get_xiyong(ganzhi_list, day_gan)

    # 大运列表（前 10 步）
    dayun_items = []
    for i, dy in enumerate(dayun_list[:10]):
        gz = dy.getGanZhi()
        if not gz:
            continue
        start_a = dy.getStartAge()
        end_a = dy.getEndAge()
        dayun_items.append({
            "ganzhi": gz,
            "startAge": start_a,
            "endAge": end_a,
            "current": (current_dayun_index == i),
        })

    return {
        "sizhu": {
            "year": year_gz,
            "month": month_gz,
            "day": day_gz,
            "time": time_gz,
            "wuxing": wuxing_cols,
            "shishen_gan": ss_gan,
            "shishen_zhi": ss_zhi,
            "nayin": nayin,
        },
        "day_master": day_gan,
        "day_master_wuxing": TIAN_GAN_WUXING.get(day_gan, ""),
        "xiyong": xi_yong,
        "jishen": ji_shen,
        "dayun": dayun_items,
        "current_dayun": {
            "ganzhi": current_dayun_ganzhi,
            "ageRange": current_dayun_range,
        },
        "current_liunian": liunian_ganzhi,
        "current_age": age,
        "lunar_birth": lunar.toString(),
    }
