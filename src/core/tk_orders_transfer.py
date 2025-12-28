import pandas as pd
import datetime
import io
from src.core.db_manager import get_sku_map_dict

# ========== 美国州名缩写表 ==========
US_STATE_MAP = {
    # English
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
    "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
    "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",

    # 中文
    "阿拉巴马": "AL",
    "阿拉巴马州": "AL", "阿拉斯加": "AK", "亚利桑那": "AZ", "阿肯色": "AR",
    "加利福尼亚": "CA", "加州": "CA",
    "科罗拉多": "CO",
    "康涅狄格": "CT",
    "特拉华": "DE",
    "佛罗里达": "FL", "佛州": "FL",
    "乔治亚": "GA",
    "夏威夷": "HI",
    "爱达荷": "ID",
    "伊利诺伊": "IL",
    "印第安纳": "IN",
    "艾奥瓦": "IA",
    "堪萨斯": "KS",
    "肯塔基": "KY",
    "路易斯安那": "LA",
    "缅因": "ME",
    "马里兰": "MD",
    "马萨诸塞": "MA",
    "密歇根": "MI",
    "明尼苏达": "MN",
    "密西西比": "MS",
    "密苏里": "MO",
    "蒙大拿": "MT",
    "内布拉斯加": "NE",
    "内华达": "NV",
    "新罕布什尔": "NH",
    "新泽西": "NJ",
    "新墨西哥": "NM",
    "纽约": "NY",
    "北卡罗来纳": "NC",
    "北达科他": "ND",
    "俄亥俄": "OH",
    "俄克拉何马": "OK",
    "俄勒冈": "OR",
    "宾夕法尼亚": "PA",
    "罗德岛": "RI",
    "南卡罗来纳": "SC",
    "南达科他": "SD",
    "田纳西": "TN",
    "得克萨斯": "TX", "德州": "TX",
    "犹他": "UT",
    "佛蒙特": "VT",
    "弗吉尼亚": "VA",
    "华盛顿": "WA", "华州": "WA",
    "西弗吉尼亚": "WV",
    "威斯康星": "WI",
    "怀俄明": "WY"
}

def convert_state(s):
    if pd.isna(s):
        return ""
    s = str(s).strip()
    if s.upper() in US_STATE_MAP.values():
        return s.upper()
    return US_STATE_MAP.get(s, s)

def parse_sku_map(text: str) -> dict:
    """
    解析用户输入的 SKU 映射文本 (Key: Value)
    """
    mapping = {}
    if not text:
        return mapping
        
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or ':' not in line:
            continue
        
        # 允许 : 或 ：
        if ':' in line:
            parts = line.split(':', 1)
        else:
            parts = line.split('：', 1)
            
        if len(parts) == 2:
            key = parts[0].strip().strip('"').strip("'")
            value = parts[1].strip().strip('"').strip("'")
            mapping[key] = value
            
    return mapping

def process_csv(input_file) -> pd.DataFrame:
    """
    核心转换逻辑
    """
    # 1. 获取 SKU 映射 (从数据库)
    sku_name_map = get_sku_map_dict()
    
    # 2. 读取 CSV
    try:
        df_raw = pd.read_csv(input_file, encoding="utf-8", engine="python")
    except Exception as e:
        raise Exception(f"CSV 读取失败: {e}")
        
    # 3. 构建输出结构
    out = pd.DataFrame(index=df_raw.index)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    out["填写日期"] = today
    out["订单平台"] = "TK"
    out["产品名称"] = df_raw["SKU ID"].apply(lambda sku: sku_name_map.get(str(sku), ""))
    out["产品图片"] = ""
    out["销售平台单号"] = df_raw["Order ID"]
    out["收件人姓名"] = df_raw["Recipient"]
    out["国家/地区"] = df_raw["Country"]
    out["州or省"] = df_raw["State"].apply(convert_state)
    out["城市"] = df_raw["City"]
    out["邮编"] = df_raw["Zipcode"]
    out["地址一"] = df_raw["Address Line 1"]
    out["地址二"] = df_raw["Address Line 2"]
    out["联系电话"] = df_raw["Phone #"]

    out["邮箱"] = ""
    out["备注"] = ""

    out["SKU编码"] = df_raw["SKU ID"]
    out["数量"] = df_raw["Quantity"]

    # 批量添加空字段
    empty_fields = [
        "单价", "SHIPMENTID", "REFERENCEID", "特殊说明",
        "特殊分货要求", "操作指令要求", "特别备注", "签名服务",
        "发货分区", "店铺号"
    ]
    for f in empty_fields:
        out[f] = ""

    out["客户出快递面单"] = df_raw["Tracking ID"]
    out["物流状态"] = df_raw["Delivery Option Type"]

    out["邮件记录"] = ""
    
    return out
