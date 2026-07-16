"""生成 100 条多样化用户资料，输出为 user_data.json

用法: uv run python test/generate_users.py
"""
import json
import random
from datetime import date, timedelta

random.seed(42)

# ────────────── 数据池 ──────────────

SURNAMES = ["赵", "钱", "孙", "李", "周", "吴", "郑", "王", "冯", "陈", "褚", "卫", "蒋", "沈", "韩", "杨", "朱", "秦", "尤", "许", "何", "吕", "张", "孔", "曹", "严", "华", "金", "魏", "陶", "姜", "戚", "谢", "邹", "喻", "柏", "水", "窦", "章", "云", "苏", "潘", "葛", "奚", "范", "彭", "郎", "鲁", "韦", "昌", "马", "苗", "凤", "花", "方", "俞", "任", "袁", "柳", "丰", "鲍", "史", "唐", "费", "廉", "岑", "薛", "雷", "贺", "倪", "汤", "滕", "殷", "罗", "毕", "郝", "邬", "安", "常", "乐", "于", "时", "傅", "皮", "卞", "齐", "康", "伍", "余", "元", "卜", "顾", "孟", "平", "黄", "和", "穆", "萧", "尹", "姚", "邵", "湛", "汪", "祁", "毛", "禹", "狄", "米", "贝", "明", "臧", "计", "伏", "成", "戴", "谈", "宋", "茅", "庞", "熊", "纪", "舒", "屈", "项", "祝", "董", "梁", "杜", "阮", "蓝", "闵", "席", "季", "麻", "强", "贾", "路", "娄", "危", "江", "童", "颜", "郭", "梅", "盛", "林", "刁", "钟", "徐", "邱", "骆", "高", "夏", "蔡", "田", "樊", "胡", "凌", "霍", "虞", "万", "支", "柯", "昝", "管", "卢", "莫"]

GIVEN_NAMES_M = ["伟", "强", "磊", "军", "勇", "杰", "涛", "明", "超", "华", "林", "鹏", "飞", "志", "浩", "峰", "毅", "宇", "轩", "文", "辉", "斌", "龙", "刚", "健", "恒", "睿", "博", "逸", "宇轩", "子涵", "浩然", "俊杰", "志远", "天佑", "子豪"]
GIVEN_NAMES_F = ["芳", "敏", "静", "丽", "婷", "娟", "霞", "娜", "燕", "玲", "慧", "莉", "雪", "红", "蕾", "丹", "萍", "蓉", "鑫", "彤", "欣怡", "诗涵", "梦瑶", "梓萱", "雨桐", "雪莹", "婉清", "若兰", "思琪", "晓萌"]

PROVINCE_CITY = [
    ("北京", "北京"), ("上海", "上海"), ("广东", "广州"), ("广东", "深圳"),
    ("广东", "珠海"), ("浙江", "杭州"), ("浙江", "宁波"), ("江苏", "南京"),
    ("江苏", "苏州"), ("四川", "成都"), ("湖北", "武汉"), ("湖南", "长沙"),
    ("陕西", "西安"), ("山东", "济南"), ("山东", "青岛"), ("福建", "厦门"),
    ("福建", "福州"), ("河南", "郑州"), ("重庆", "重庆"), ("天津", "天津"),
    ("安徽", "合肥"), ("辽宁", "大连"), ("辽宁", "沈阳"),
]

SCHOOLS = [
    ("北京大学", "本科"), ("清华大学", "硕士"), ("复旦大学", "博士"),
    ("上海交通大学", "硕士"), ("浙江大学", "本科"), ("南京大学", "本科"),
    ("武汉大学", "硕士"), ("中山大学", "本科"), ("华中科技大学", "硕士"),
    ("同济大学", "本科"), ("中国人民大学", "硕士"), ("厦门大学", "本科"),
    ("四川大学", "本科"), ("中国传媒大学", "本科"), ("中央美术学院", "本科"),
    ("西安交通大学", "硕士"), ("哈尔滨工业大学", "本科"), ("东南大学", "硕士"),
    ("华东师范大学", "硕士"), ("华东政法大学", "本科"),
    ("重庆大学", "本科"), ("北京理工大学", "本科"),
    ("华南理工大学", "本科"), ("电子科技大学", "硕士"),
    ("本地高中", "高中"), ("本地职业技术学院", "大专"),
]

OCCUPATIONS = [
    ("软件工程师", "互联网"), ("产品经理", "互联网"), ("UI设计师", "互联网"),
    ("数据分析师", "互联网"), ("算法工程师", "人工智能"), ("前端开发", "互联网"),
    ("后端开发", "互联网"), ("测试工程师", "互联网"), ("运维工程师", "互联网"),
    ("中学教师", "教育"), ("小学教师", "教育"), ("大学讲师", "教育"),
    ("外科医生", "医疗"), ("护士", "医疗"), ("药剂师", "医疗"),
    ("律师", "法律"), ("法务", "法律"),
    ("建筑设计师", "建筑"), ("结构工程师", "建筑"),
    ("会计师", "金融"), ("投资经理", "金融"), ("银行职员", "金融"),
    ("公务员", "政府"), ("事业单位职员", "政府"),
    ("自由职业者", "自媒体"), ("摄影师", "艺术"), ("插画师", "艺术"),
    ("健身教练", "体育"), ("瑜伽老师", "体育"),
    ("销售经理", "零售"), ("市场策划", "广告"),
    ("餐饮老板", "餐饮"), ("厨师", "餐饮"),
    ("HR经理", "人力资源"), ("行政主管", "行政"),
    ("物流经理", "物流"), ("采购经理", "贸易"),
    ("翻译", "文化"), ("编辑", "出版"), ("记者", "媒体"),
]

SELF_INTROS_M = [
    "性格稳重，不烟不酒，工作稳定，喜欢健身和看电影，希望能遇到合拍的女生",
    "阳光开朗爱笑，喜欢户外运动，周末常去爬山或骑行，希望对方性格温柔",
    "比较宅的技术男，但为了另一半愿意改变，平时喜欢打游戏和研究新技术",
    "热爱生活，厨艺不错，周末喜欢做一桌菜招待朋友，找有缘人共度余生",
    "事业心强但尊重家庭，希望找一个能互相支持、共同成长的伴侣",
    "文艺青年一枚，喜欢读书、摄影、旅行，希望对方也有自己的爱好和追求",
    "踏实稳重型，不善于表达但行动力强，希望能遇到一个懂我的人",
]
SELF_INTROS_F = [
    "温柔体贴，喜欢烘焙和养花，生活规律，想找一个顾家有责任心的男士",
    "独立自信，工作努力但也懂得享受生活，希望对方成熟稳重",
    "性格活泼开朗，喜欢旅行和尝试新鲜事物，找能一起看世界的你",
    "文艺小清新，平时喜欢画画、看书、做手工，慢热但长情",
    "善良孝顺，家庭观念强，会做饭会持家，希望能组建一个温暖的小家",
    "知性优雅，喜欢古典音乐和戏剧，希望能遇见灵魂伴侣",
    "热爱运动，羽毛球、瑜伽都会一点，希望对方也喜欢运动",
]

INTEREST_POOLS = [
    ["篮球", "跑步", "游泳"],
    ["登山", "骑行", "露营"],
    ["瑜伽", "健身", "普拉提"],
    ["画画", "摄影", "书法"],
    ["看电影", "听音乐", "追剧"],
    ["烹饪", "烘焙", "美食探店"],
    ["读书", "写作", "看展"],
    ["旅行", "自驾", "徒步"],
    ["象棋", "围棋", "桌游"],
    ["唱歌", "弹吉他", "舞蹈"],
    ["养宠物", "园艺", "手工"],
    ["羽毛球", "乒乓球", "台球"],
]

MARRIAGE_WEIGHTS = [("未婚", 85), ("离异", 13), ("丧偶", 2)]
INCOME_WEIGHTS = [("10万以下", 10), ("10-20万", 30), ("20-50万", 35), ("50-100万", 20), ("100万以上", 5)]


def pick_weighted(options):
    opts, weights = zip(*options)
    return random.choices(opts, weights=weights, k=1)[0]


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def gen_profile(i: int) -> dict:
    gender = "男" if random.random() < 0.52 else "女"
    surname = random.choice(SURNAMES)
    name_pool = GIVEN_NAMES_M if gender == "男" else GIVEN_NAMES_F
    given = random.choice(name_pool)
    nickname = f"{surname}{given}{random.randint(100, 999)}" if i % 5 == 0 else f"{surname}{given}"

    birth = random_date(date(1990, 1, 1), date(2002, 12, 31)).isoformat()
    if gender == "男":
        height = random.randint(168, 192)
        weight = random.randint(58, 95)
        body_pool = ["匀称", "运动型", "偏瘦", "丰满"]
        body_weights = [40, 30, 20, 10]
    else:
        height = random.randint(155, 175)
        weight = random.randint(42, 68)
        body_pool = ["偏瘦", "匀称", "运动型", "丰满"]
        body_weights = [40, 35, 15, 10]
    body_type = random.choices(body_pool, weights=body_weights, k=1)[0]

    province, city = random.choice(PROVINCE_CITY)

    school, edu = random.choice(SCHOOLS)
    if edu == "高中":
        school = "本地高中"
    elif edu == "大专":
        school = "本地职业技术学院"
    occupation, industry = random.choice(OCCUPATIONS)
    income = pick_weighted(INCOME_WEIGHTS)
    marriage = pick_weighted(MARRIAGE_WEIGHTS)
    has_children = marriage == "离异" and random.random() < 0.3
    want_children = random.choice([True, False])
    smoking = random.choice([True, False])
    drinking = random.choice([True, False])

    interests = random.choice(INTEREST_POOLS)[: random.randint(2, 3)]

    intro_pool = SELF_INTROS_M if gender == "男" else SELF_INTROS_F
    self_intro = random.choice(intro_pool) + "。"

    # 择偶偏好
    pref_gender = "女" if gender == "男" else "男"
    pref_edu = random.choice(["高中", "大专", "本科", "硕士", "博士"])
    pref_marriage = random.choice(["未婚", "离异"])
    pref = {
        "gender": pref_gender,
        "age_min": max(22, random.randint(22, 30)),
        "age_max": min(45, random.randint(32, 45)),
        "height_min": 168 if pref_gender == "男" else 155,
        "height_max": 185 if pref_gender == "男" else 170,
        "education": pref_edu,
        "province": province if random.random() < 0.5 else random.choice([p for p, _ in PROVINCE_CITY]),
        "city": city if random.random() < 0.5 else random.choice([c for _, c in PROVINCE_CITY]),
        "marriage_status": pref_marriage,
    }

    avatar_id = random.randint(1, 99)
    avatar_url = f"https://api.dicebear.com/7.x/avataaars/svg?seed={nickname}{avatar_id}"

    return {
        "nickname": nickname,
        "gender": gender,
        "birth_date": birth,
        "height": height,
        "weight": weight,
        "province": province,
        "city": city,
        "education": edu,
        "school": school,
        "occupation": occupation,
        "industry": industry,
        "income_range": income,
        "body_type": body_type,
        "marriage_status": marriage,
        "has_children": has_children,
        "want_children": want_children,
        "smoking": smoking,
        "drinking": drinking,
        "self_intro": self_intro,
        "interests": interests,
        "avatar_url": avatar_url,
        "preference": pref,
    }


if __name__ == "__main__":
    users = [gen_profile(i) for i in range(100)]

    out_path = "test/user_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

    # 统计概览
    males = sum(1 for u in users if u["gender"] == "男")
    females = sum(1 for u in users if u["gender"] == "女")
    cities = len(set(u["city"] for u in users))
    marriage_counts = {}
    for u in users:
        marriage_counts[u["marriage_status"]] = marriage_counts.get(u["marriage_status"], 0) + 1

    print(f"✓ 已生成 100 条用户数据 → {out_path}")
    print(f"  男: {males}  女: {females}")
    print(f"  覆盖城市: {cities} 个")
    print(f"  婚姻状态: {marriage_counts}")
