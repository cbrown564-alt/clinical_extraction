import json
import os
import argparse
import re
from sklearn.metrics import precision_recall_fscore_support, accuracy_score, classification_report
from utils.llm import ChatGPT
from z_step3_csv2json_and_get_freq import parse_label_bounds
llm = ChatGPT("gpt-4o-mini", None)

# --- 1. Purist mapping function ---
def map_seizure_category_purist(x):
    if x == 0:
        return "currently_no_seizure"
    elif x == 1000:
        return "seizure_freq_unknown"
    elif 0 < x <= 0.16:
        return "seizure_freq_1_per_yr"
    elif 0.16 < x <= 0.18:
        return "seizure_freq_1_per_6mon"
    elif 0.18 < x <= 0.99:
        return "seizure_freq_more1per6mon_less1mon"
    elif 0.99 < x <= 1.1:
        return "seizure_freq_1_per_mon"
    elif 1.1 < x <= 3.9:
        return "seizure_freq_more1mon_less1week"
    elif 3.9 < x <= 4.1:
        return "seizure_freq_1_per_week"
    elif 4.1 < x <= 29:
        return "seizure_freq_more1week_less1day"
    elif 29 < x <= 999:
        return "seizure_freq_1ormore_daily"
    else:
        return "seizure_freq_unknown"
        # return "invalid_value"

# 0.15 or 0.5
# --- 2. Pragmatic mapping function ---
def map_seizure_category_pragmatic(x):
    if x == 0:
        return "currently_no_seizure"
    elif x == 1000:
        return "seizure_freq_unknown"
    elif 0 < x <= 1.1:
        return "seizure_infrequent"
    elif 1.1 < x <= 999:
        return "seizure_frequent"
    else:
        return "seizure_freq_unknown"
        # return "invalid_value"

# --- 3. Batch mapping ---
def convert_to_categories(values, method="purist"):
    if method == "purist":
        return [map_seizure_category_purist(x) for x in values]
    elif method == "pragmatic":
        return [map_seizure_category_pragmatic(x) for x in values]
    else:
        raise ValueError("method must be 'purist' or 'pragmatic'")

# --- 4. Calculate metrics ---
def evaluate_predictions(y_true, y_pred, method="purist"):
    y_true_cat = convert_to_categories(y_true, method=method)
    y_pred_cat = convert_to_categories(y_pred, method=method)

    results = {}
    for avg in ["micro", "macro", "weighted"]:
        p, r, f1, _ = precision_recall_fscore_support(
            y_true_cat, y_pred_cat, average=avg, zero_division=0
        )
        acc = accuracy_score(y_true_cat, y_pred_cat)
        results[avg] = {
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f1, 4),
            "accuracy": round(acc, 4),
        }

    report = classification_report(y_true_cat, y_pred_cat, digits=4, zero_division=0)
    print(f"\n=== {method.upper()} METHOD Classification Report ===\n")
    print(report)
    
    return results, report


def normalize_period(raw: str) -> str:
    s = raw.strip().lower()
    s = re.sub(r'\s*(?:-|–)\s*', ' to ', s)  # 2-3 / 2–3 -> 2 to 3
    s = re.sub(r'\s+', ' ', s)
    for u in ['week', 'day', 'month', 'year']:
        s = re.sub(rf'\b{u}s\b', u, s)  # weeks -> week 等
    return s

def parse_range(token: str):
    """
    解析整数或范围，返回 (min, max)
    支持: '3', '2 to 5', '2-5', '2–5'
    """
    token = token.strip().lower()
    m = re.match(r'^(\d+)\s*(?:to|-|–)\s*(\d+)$', token)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return (min(a, b), max(a, b))
    m = re.match(r'^(\d+)$', token)
    if m:
        v = int(m.group(1))
        return (v, v)
    return None

def seizure_frequency(text: str) -> str:
    """
    示例：
    "2 to 5 cluster per month, 2 to 3 per cluster" -> "4 to 15 per month"
    """
    txt = text.strip().lower()

    # cluster 数量（支持单复数、范围）
    m_cluster = re.search(r'(\d+(?:\s*(?:to|-|–)\s*\d+)?)\s*clusters?\b', txt)
    if not m_cluster:
        return "Invalid input: no cluster info found."
    c_rng = parse_range(m_cluster.group(1))
    if not c_rng:
        return "Invalid input: malformed cluster range."
    cmin, cmax = c_rng

    # 周期（per ... 直到逗号或结尾）
    m_period = re.search(r'per\s+(.+?)(?:,|$)', txt)
    period_raw = m_period.group(1).strip() if m_period else "time"
    period = normalize_period(period_raw)

    # 每 cluster 次数（支持范围）
    m_pc = re.search(r'(\d+(?:\s*(?:to|-|–)\s*\d+)?)\s*per\s*cluster\b', txt)
    if not m_pc:
        return "Invalid input: no per-cluster info found."
    pc_rng = parse_range(m_pc.group(1))
    if not pc_rng:
        return "Invalid input: malformed per-cluster range."
    pcmin, pcmax = pc_rng

    # 区间乘法：最小×最小 到 最大×最大
    fmin = cmin * pcmin
    fmax = cmax * pcmax

    return f"{fmin} per {period}" if fmin == fmax else f"{fmin} to {fmax} per {period}"


def parse_label_to_yearly_count(label: str) -> float:
    label = label.replace(" per multiple week", " per 2 week").replace(" per multiple month", " per 2 month").replace(" per multiple year", " per 2 year").replace(" per multiple day", " per 2 day")
    if label.endswith("week") or label.endswith("weeks") or 'week,' in label or 'weeks,' in label:
        label = label.replace("multiple per ", "2 per ")
        label = label.replace("multiple cluster per ", "2 cluster per ")
    elif label.endswith("month") or label.endswith("months") or 'month,' in label or 'months,' in label:
        label = label.replace("multiple per ", "8 per ")
        label = label.replace("multiple cluster per ", "8 cluster per ")
    elif label.endswith("year") or label.endswith("years") or 'year,' in label or 'years,' in label:
        label = label.replace("multiple per ", "18 per ")
        label = label.replace("multiple cluster per ", "18 cluster per ")
    elif label.endswith("day") or label.endswith("days") or 'day,' in label or 'days,' in label:
        label = label.replace("multiple per ", "2 per ")
        label = label.replace("multiple cluster per ", "2 cluster per ")

    if 'cluster' in label:
        label = label.replace("multiple per cluster", "2 per cluster")
        if 'unknown' in label:
            return -1, -1, -1
        else:
            label = seizure_frequency(label)
    min_y, max_y = parse_label_bounds(label)
    return max_y, (max_y + min_y) / 2, min_y


# === predict label 修复器 ===
# 作用：把各种不合规表达修成规范允许的 6 种格式之一，避免 parse_label_bounds 报错。
# 用法：在 parse_label_to_yearly_count() 的最开始调用 repair_predict_label(label)

import re
from typing import Optional, Tuple

# —— 数字英文词、单位缩写/复数 的映射 ——
NUM_WORDS = {
    "zero": "0","one": "1","two": "2","three": "3","four": "4","five": "5",
    "six": "6","seven": "7","eight": "8","nine": "9","ten": "10",
    "eleven": "11","twelve": "12",
}
UNIT_SYNONYMS = {
    "d":"day","day":"day","days":"day",
    "wk":"week","wks":"week","w":"week","week":"week","weeks":"week",
    "mo":"month","mos":"month","mon":"month","mons":"month","month":"month","months":"month",
    "yr":"year","yrs":"year","yr.":"year","y":"year","year":"year","years":"year",
}

# —— 允许格式校验（最终关卡） ——
ALLOWED_PATTERNS = {
    'unknown': re.compile(r'^unknown$'),
    'no_ref': re.compile(r'^no seizure frequency reference$'),
    'seizure_free': re.compile(r'^seizure free for (?:multiple|\d+(?: to \d+)?) (?:month|year)$'),
    'per': re.compile(r'^(?:multiple|\d+(?: to \d+)?) per (?:(?:multiple|\d+(?: to \d+)?) )?(?:day|week|month|year)$'),
    'cluster': re.compile(r'^(?:multiple|\d+(?: to \d+)?) cluster per (?:(?:multiple|\d+(?: to \d+)?) )?(?:day|week|month|year), (?:multiple|\d+(?: to \d+)?) per cluster$'),
    'unknown_cluster': re.compile(r'^unknown, (?:multiple|\d+(?: to \d+)?) per cluster$'),
}
def is_allowed_format(s: str) -> bool:
    return any(pat.match(s) for pat in ALLOWED_PATTERNS.values())

# —— 一系列标准化子过程（顺序很重要） ——
def normalize_spaces(s: str) -> str:
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'\s*,\s*', ', ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def normalize_cluster_label(text: str) -> str:
    text = text.strip().lower()
    # 先去掉 cluster
    text = re.sub(r"\bcluster\b", "", text).strip()
    # 匹配模式: 数字或范围 + per + (数字或范围)? + 单位
    pattern = r"^(\d+(?:\s*to\s*\d+)?)\s*(?:per\s+)?(\d+(?:\s*to\s*\d+)?\s+)?(\w+)?$"
    match = re.match(pattern, text, re.IGNORECASE)
    if not match:
        return text  # 不符合规则就原样返回

    number1 = match.group(1)  # 前面的数字或范围
    number2 = match.group(2)  # per 后的数字或范围 (可能为空)
    unit = match.group(3)     # 单位 (week, month, year…)

    if number2 and unit:
        return f"{number1} per {number2.strip()} {unit}"
    elif unit:
        return f"{number1} per {unit}"
    else:
        return f"{number1} per month"  # 默认补 month


def words_to_nums(s: str) -> str:
    return re.sub(r'\b(' + '|'.join(NUM_WORDS.keys()) + r')\b',
                  lambda m: NUM_WORDS[m.group(0)], s)

def normalize_units(s: str) -> str:
    s = re.sub(r'\b(' + '|'.join(map(re.escape, sorted(UNIT_SYNONYMS.keys(), key=len, reverse=True))) + r')\b',
               lambda m: UNIT_SYNONYMS[m.group(0)], s)
    s = re.sub(r'\b(day|week|month|year)s\b', r'\1', s)  # 强制单数
    return s

def numeric_ranges_to_to(s: str) -> str:
    return re.sub(r'(\d+)\s*[-–—]\s*(\d+)', r'\1 to \2', s)

def slash_per_forms(s: str) -> str:
    # 3-5/mo, 2/wk, 4/month 等
    def repl(m):
        num = m.group('num')
        unit = UNIT_SYNONYMS.get(m.group('unit'), m.group('unit'))
        return f"{num} per {unit}"
    return re.sub(
        r'(?P<num>\d+(?:\s*to\s*\d+)?)\s*/\s*(?P<unit>d|day|wk|wks?|week|mo|mon|mos|mons?|month|yr|yrs?|y|year)s?\b',
        repl, s)

def x_times_forms(s: str) -> str:
    s = re.sub(r'(?<=\d)\s*[x×]\s*(?=per\b|/)', ' ', s)  # 3x per -> 3 per
    s = re.sub(r'\bx\s*(\d+)\s*/\s*(d|day|wk|wks?|week|mo|mon|mos?|month|yr|yrs?|y|year)s?\b',
               lambda m: f"{m.group(1)} per {UNIT_SYNONYMS.get(m.group(2),'')}", s)
    s = re.sub(r'(\d+(?:\s*to\s*\d+)?)\s*(?:x|times?)\s*(?=per\b|/|\b(?:daily|weekly|monthly|yearly|annually)\b)',
               r'\1 ', s)
    return s

def remove_times_word(s: str) -> str:
    # multiple times per week -> multiple per week
    return re.sub(r'\btimes?\b(?=\s+per\b)', '', s)

def once_twice_thrice(s: str) -> str:
    s = re.sub(r'\bonce\b', '1', s)
    s = re.sub(r'\btwice\b', '2', s)
    s = re.sub(r'\bthrice\b', '3', s)
    return s

def every_each_forms(s: str) -> str:
    # 先去掉 "数字 + every other ..." 前缀的数字
    s = re.sub(r'\b\d+\s+(?=every\s+other\s+(day|week|month|year)\b)', '', s)
    # every other week -> 1 per 2 week
    s = re.sub(r'\b(?:every|each)\s+other\s+(day|week|month|year)\b', r'1 per 2 \1', s)
    # every 2 weeks -> 1 per 2 week; each month -> 1 per month
    s = re.sub(r'\b(?:every|each)\s+(\d+)\s*(day|week|month|year)s?\b', r'1 per \1 \2', s)
    s = re.sub(r'\b(?:every|each)\s+(day|week|month|year)s?\b', r'1 per \1', s)
    # per each/every -> per
    s = re.sub(r'\bper\s+(?:each|every)\s+', 'per ', s)
    return s

def period_words(s: str) -> str:
    # weekly/monthly/daily/yearly/annually -> 1 per unit
    s = re.sub(r'(\d+(?:\s*to\s*\d+)?|\bmultiple\b)?\s*\bweekly\b',
               lambda m: (m.group(1) or '1') + ' per week', s)
    s = re.sub(r'(\d+(?:\s*to\s*\d+)?|\bmultiple\b)?\s*\bmonthly\b',
               lambda m: (m.group(1) or '1') + ' per month', s)
    s = re.sub(r'(\d+(?:\s*to\s*\d+)?|\bmultiple\b)?\s*\bdaily\b',
               lambda m: (m.group(1) or '1') + ' per day', s)
    s = re.sub(r'\b(?:annually|yearly)\b', '1 per year', s)
    s = re.sub(r'\bsemiweekly\b', '2 per week', s)
    s = re.sub(r'\bbiweekly\b', '1 per 2 week', s)
    s = re.sub(r'\bsemimonthly\b', '2 per month', s)
    s = re.sub(r'\bbimonthly\b', '1 per 2 month', s)
    return s

def inequality_to_multiple(s: str) -> str:
    # 文本形式
    s = re.sub(r'\b(?:at least|no less than|more than|over|greater than)\b\s*(\d+(?:\s*to\s*\d+)?)', 'multiple', s)
    s = re.sub(r'\b(?:at most|no more than|less than|under|up to)\b\s*(\d+(?:\s*to\s*\d+)?)', 'multiple', s)
    # 符号形式
    s = re.sub(r'[≥>]\s*\d+(?:\s*to\s*\d+)?', 'multiple', s)
    s = re.sub(r'[≤<]\s*\d+(?:\s*to\s*\d+)?', 'multiple', s)
    return s

def adverbs_and_noise(s: str) -> str:
    # 近似词
    s = re.sub(r'\b(?:approximately|approx\.?|about|around|nearly|~)\b', '', s)
    # few/several -> multiple；“a couple of” -> 2
    s = re.sub(r'\b(?:a few|few|several)\b', 'multiple', s)
    s = re.sub(r'\ba couple of\b', '2', s)
    # 删除多余名词，但保留 "seizure free" 短语
    s = re.sub(r'\bseizures?\b(?!\s*[- ]?free)', '', s)
    s = re.sub(r'\b(?:episodes?|events?|attacks?|spells?|szs?)\b', '', s)
    # 去掉冠词/介词等
    s = re.sub(r'\b(?:of|the|a|an)\b', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def cleanup_commas(s: str) -> str:
    s = re.sub(r'\s*,\s*', ', ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def drop_per_one(s: str) -> str:
    return re.sub(r'\bper\s+1\s+(day|week|month|year)\b', r'per \1', s)

def reorder_per_week_num(s: str) -> str:
    # "per week 2 to 3" -> "2 to 3 per week"，但若涉及 cluster 则不动
    if 'cluster' in s:
        return s
    return re.sub(r'\bper\s+(day|week|month|year)\s+(\d+(?:\s*to\s*\d+)?|multiple)\b', r'\2 per \1', s)

def compress_double_per_range(s: str) -> str:
    # "1 to 2 per month to 2 to 3 per month" -> "1 to 3 per month"（仅单位与分母一致时）
    pattern = re.compile(
        r'\b(?P<a>(?:multiple|\d+(?:\s*to\s*\d+)?))\s*per\s*(?P<dena>(?:\d+(?:\s*to\s*\d+)?\s+)?)?(?P<unita>day|week|month|year)\s*to\s*'
        r'(?P<b>(?:multiple|\d+(?:\s*to\s*\d+)?))\s*per\s*(?P<denb>(?:\d+(?:\s*to\s*\d+)?\s+)?)?(?P<unitb>day|week|month|year)\b'
    )
    def repl(m):
        unita, unitb = m.group('unita'), m.group('unitb')
        dena = (m.group('dena') or '').strip() or '1'
        denb = (m.group('denb') or '').strip() or '1'
        if unita != unitb or dena != denb:
            return m.group(0)  # 不能安全合并
        a, b = m.group('a'), m.group('b')
        if 'multiple' in (a, b):
            return f"multiple per {unita}"
        def bounds(x: str) -> Tuple[int,int]:
            if 'to' in x:
                lo, hi = re.split(r'\s*to\s*', x); return int(lo), int(hi)
            v = int(x); return v, v
        a_lo, a_hi = bounds(a); b_lo, b_hi = bounds(b)
        lo, hi = min(a_lo, b_lo), max(a_hi, b_hi)
        return f"{lo} per {unita}" if lo == hi else f"{lo} to {hi} per {unita}"
    prev = None
    while prev != s:
        prev = s
        s = pattern.sub(repl, s)
    return s

def canonicalize_seizure_free(s: str) -> str:
    # 把各种 seizure-free 写法统一
    if 'seizure free' in s or 'seizure-free' in s or 'sz free' in s or 'sz-free' in s:
        s = s.replace('seizure-free', 'seizure free').replace('sz free', 'seizure free').replace('sz-free', 'seizure free')
        m = re.search(r'seizure free(?:\s*for)?\s*(\d+(?:\s*to\s*\d+)?)\s*(month|year)s?\b', s)
        if m:
            return f"seizure free for {m.group(1)} {m.group(2)}"
        if re.search(r'seizure free since\b', s):
            return "seizure free for multiple year"
        return "seizure free for multiple year"
    return s

def normalize_unknown_no_ref(s: str) -> str:
    if re.search(r'\bno (?:seizure )?(?:frequency|freq)(?: reference| info(?:rmation)?| mentioned| noted)?\b', s):
        return 'no seizure frequency reference'
    if s.strip() == 'unknown' or re.fullmatch(r'unknown\s*[,;:]*\s*', s):
        return 'unknown'
    return s

def fix_cluster_block(s: str) -> str:
    s = s.strip()
    if 'cluster' not in s:
        return s
    # 统一为单数 cluster
    s = re.sub(r'\bclusters\b', 'cluster', s)
    # unknown per cluster 2 / unknown per cluster, 2 / unknown per cluster
    s = re.sub(r'\bunknown\s+per\s+cluster\s+(\d+(?:\s*to\s*\d+)?)\b', r'unknown, \1 per cluster', s)
    s = re.sub(r'\bunknown\s+per\s+cluster\s*,\s*(\d+(?:\s*to\s*\d+)?|multiple)\b', r'unknown, \1 per cluster', s)
    s = re.sub(r'\bunknown\s+per\s+cluster\b', 'unknown, multiple per cluster', s)
    # 合并 "Y per cluster to Z per cluster"
    s = re.sub(r'\b(\d+(?:\s*to\s*\d+)?)\s*per\s*cluster\s*to\s*(\d+(?:\s*to\s*\d+)?)\s*per\s*cluster\b', r'\1 to \2 per cluster', s)
    # 缺逗号时补逗号
    s = re.sub(r'\b(cluster per (?:\d+(?:\s*to\s*\d+)?\s*)?(?:day|week|month|year))\s+(?=(?:\d+(?:\s*to\s*\d+)?|multiple)\s*per\s*cluster\b)', r'\1, ', s)
    # 若 "per cluster" 在前，调换顺序
    s = re.sub(r'\b((?:\d+(?:\s*to\s*\d+)?|multiple)\s*per\s*cluster)\s*,\s*((?:\d+(?:\s*to\s*\d+)?|multiple)\s*)cluster\s*per\s*((?:\d+(?:\s*to\s*\d+)?\s*)?)(day|week|month|year)\b',
               r'\2cluster per \3\4, \1', s)
    # 若只有 cluster 计数，无 per cluster 段，无法可靠推断
    if 'cluster per' in s and 'per cluster' not in s and 'unknown' not in s:
        return 'unknown'
    return s


NUM = r"\d+(?:\s*to\s*\d+)?"
UNIT = r"(?:day|week|month|year)s?"  # 输入可带复数，输出统一为单数

def _singular_unit(u: str) -> str:
    u = u.lower().strip()
    # 只允许 day|week|month|year；去掉尾部 s
    if u.endswith('s'):
        u = u[:-1]
    return u

def _omit_one(v2):
    if v2 is None:
        return None
    v2 = re.sub(r"\s+", " ", v2.strip())
    return None if v2 == "1" else v2

def normalize_cluster_label2(text: str) -> str:
    s = text.strip()
    if not s:
        return s

    # 标准化：小写单位与关键词、合并空白、中文逗号转英文
    s = s.replace("，", ",")
    s = re.sub(r"\s+", " ", s).strip().lower()

    # ---------- 先匹配 “双子句” ----------
    # 形如：<v1> per [<v2>] <unit> , <v3> per cluster
    pat_dual = re.compile(
        rf"^(?P<v1>{NUM})\s*(?:cluster\s+)?per\s+(?:(?P<v2>{NUM})\s+)?(?P<unit>{UNIT})\s*,\s*(?P<v3>{NUM})\s+per\s+cluster$",
        re.IGNORECASE
    )
    m = pat_dual.match(s)
    if m:
        v1 = m.group("v1")
        v2 = _omit_one(m.group("v2"))
        unit = _singular_unit(m.group("unit"))
        v3 = m.group("v3")

        left = f"{v1} cluster per "
        left += f"{v2} {unit}" if v2 else unit
        right = f"{v3} per cluster"
        return f"{left}, {right}"

    # ---------- 处理包含噪声 cluster 的单子句 ----------
    # 1) 把 "<num> cluster per ..." 归一到 "<num> per ..."
    s1 = re.sub(rf"\b({NUM})\s+cluster\s+per\b", r"\1 per", s)
    # 2) 把 "per cluster per ..." 归一到 "per ..."
    s1 = re.sub(r"\bper\s+cluster\s+per\b", "per", s1)

    # ---------- 匹配 “单子句（有单位）”：<v1> per [<v2>] <unit> ----------
    pat_single = re.compile(
        rf"^(?P<v1>{NUM})\s*per\s+(?:(?P<v2>{NUM})\s+)?(?P<unit>{UNIT})$",
        re.IGNORECASE
    )
    m = pat_single.match(s1)
    if m:
        v1 = m.group("v1")
        v2 = _omit_one(m.group("v2"))
        unit = _singular_unit(m.group("unit"))
        return f"{v1} per {v2 + ' ' if v2 else ''}{unit}"

    # ---------- 匹配 “仅 cluster 子句”：<v1> per cluster ----------
    pat_cluster_only = re.compile(rf"^(?P<v1>{NUM})\s+per\s+cluster$", re.IGNORECASE)
    m = pat_cluster_only.match(s)
    if m:
        v1 = m.group("v1")
        return f"unknown, {v1} per cluster"

    # 其它情况：尽量再试一次把前置 cluster 清理后再匹配单子句
    m = pat_single.match(s)
    if m:
        v1 = m.group("v1")
        v2 = _omit_one(m.group("v2"))
        unit = _singular_unit(m.group("unit"))
        return f"{v1} per {v2 + ' ' if v2 else ''}{unit}"

    # 最后兜底：不改变
    return text




def clean_extras(text: str) -> str:
    """
    清理两类“多余尾巴”：
    A) <num> per <num> year <num> month   -> 删除末尾的 `<num> month`
    B) <...> per <unit> to <num> per <unit> -> 删除 `to <num> per <unit>` 尾巴
    仅在完全匹配错误模式时才改动，否则原样返回。
    """
    if not text or not text.strip():
        return text

    s = text.strip()
    # 统一空格 / 逗号
    s = s.replace("，", ",")
    s = re.sub(r"\s+", " ", s)

    # ---------- 规则 A ----------
    # 形如：开头任意、出现 "per <num> year" 后紧跟 "<num> month" 在行尾（或逗号前）
    # 我们只删除最后这个 "<num> month" 片段
    pat_a = re.compile(
        rf"^(?P<head>.*?\bper\s+{NUM}\s+year)\s+(?P<tail>{NUM}\s+month)\s*(?P<end>,?.*)$",
        re.IGNORECASE
    )
    m = pat_a.match(s)
    if m:
        head = m.group("head").rstrip()
        end = m.group("end") or ""
        # 删除尾部 "<num> month"；保留其后可能跟着的逗号/其它内容
        fixed = f"{head}{(' ' + end.strip()) if end.strip() else ''}".strip()
        return fixed

    # ---------- 规则 B ----------
    # 形如：<前半句> per [<num>] <unit> to <num> per [<num>] <unit> [行尾]
    # 仅当 "to <num> per ..." 明确出现时才删除
    pat_b = re.compile(
        rf"^(?P<left>.*?\bper\s+(?:{NUM}\s+)?{UNIT})\s+to\s+{NUM}\s+per\s+(?:{NUM}\s+)?{UNIT}\s*$",
        re.IGNORECASE
    )
    m = pat_b.match(s)
    if m:
        # 只保留左侧的完整子句
        return m.group("left").strip()

    # 不匹配就原样返回
    return text

def repair_predict_label(raw: Optional[str]) -> str:
    """
    把原始预测文本修成规范允许的 6 种格式之一。
    """
    if raw is None:
        return 'no seizure frequency reference'
    s = str(raw).strip().lower()
    if s == '':
        return 'no seizure frequency reference'

    s = s.replace(" per night", " per day").replace(" per morning", " per day").replace(" per afternoon", " per day").replace(" per evening", " per day")
    # 先统一“无引用/未知”表达
    s = normalize_unknown_no_ref(s)

    # 序贯规范化（顺序不能打乱）
    s = words_to_nums(s)
    s = numeric_ranges_to_to(s)
    s = once_twice_thrice(s)
    s = slash_per_forms(s)
    s = x_times_forms(s)
    s = remove_times_word(s)
    s = every_each_forms(s)
    s = period_words(s)
    s = inequality_to_multiple(s)
    s = adverbs_and_noise(s)
    s = normalize_units(s)
    s = re.sub(r'\s+', ' ', s).strip()
    s = reorder_per_week_num(s)
    s = canonicalize_seizure_free(s)
    s = normalize_units(s)
    s = fix_cluster_block(s)
    s = normalize_units(s)
    s = drop_per_one(s)
    s = cleanup_commas(s)
    s = compress_double_per_range(s)
    s = normalize_spaces(s)
    s = normalize_cluster_label(s)
    s = normalize_cluster_label2(s)
    s = clean_extras(s)

    # 非法分母 0 -> unknown
    if re.search(r'\bper\s+0\s+(day|week|month|year)\b', s):
        s = 'unknown'

    # 若仍不合规，尝试最后的兜底抽取；再不行就 unknown/no_ref
    if not is_allowed_format(s):
        if 'unknown' in s:
            m = re.search(r'(\d+(?:\s*to\s*\d+)?|multiple)\s*per\s*cluster', s)
            s = f"unknown, {m.group(1)} per cluster" if m else "unknown"
        elif 'cluster' in s:
            m = re.search(r'(?P<count>(?:\d+(?:\s*to\s*\d+)?|multiple))\s*clusters?\s*per\s*(?P<den>(?:\d+(?:\s*to\s*\d+)?\s*)?)(?P<unit>day|week|month|year)', s)
            m2 = re.search(r'(?P<pc>(?:\d+(?:\s*to\s*\d+)?|multiple))\s*per\s*cluster', s)
            if m and m2:
                den = (m.group('den') or '').strip()
                unit = m.group('unit')
                den_str = (den + ' ').strip() if den and den != '1' else ''
                s = f"{m.group('count')} cluster per {den_str}{unit}, {m2.group('pc')} per cluster"
            else:
                s = "unknown"
        else:
            m = re.search(r'(?P<num>(?:\d+(?:\s*to\s*\d+)?|multiple))\s*per\s*(?P<den>(?:\d+(?:\s*to\s*\d+)?\s*)?)(?P<unit>day|week|month|year)', s)
            if m:
                den = (m.group('den') or '').strip()
                unit = m.group('unit')
                den_str = (den + ' ').strip() if den and den != '1' else ''
                s = f"{m.group('num')} per {den_str}{unit}"
            else:
                s = 'no seizure frequency reference'

    # 最终清理
    s = drop_per_one(s)
    s = normalize_spaces(s)

    # 仍不合规时的最后兜底
    if not is_allowed_format(s):
        if s.startswith('seizure free'):
            if re.search(r'\b(month|year)\b', s) is None:
                s = 'seizure free for multiple year'
        else:
            if 'per ' in s and not re.search(r'\b(day|week|month|year)\b', s):
                s = re.sub(r'per\s+\S+\b', 'per month', s)
            if not is_allowed_format(s):
                s = 'unknown'
    return s

def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def extract_xml_field(text: str, tag: str = "seizure_frequency_number") -> str:
    """Extract simple XML tag content; returns None when the tag is missing."""
    if not isinstance(text, str) or "<" not in text:
        return None
    pattern = rf"<{tag}>\s*(.*?)\s*</{tag}>"
    m = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    value = m.group(1).strip()
    return value if value else None

def get_BH_value(text: str) -> float:
    if is_number(text):
        return float(text)
    else:
        try:
            if '{' in text:
                predict = json.loads(llm.extract_json_string(text))
                if type(predict['seizure_frequency_number']) == list:
                    text = predict['seizure_frequency_number'][0]
                else:
                    text = predict['seizure_frequency_number']

            text = text.strip()
            if text in ["unknown", "seizure free", "seizure infrequent", "seizure frequent", "seizure unknown", "seizure infrequency", "seizure frequency", "seizure freedom"]:
                if text in ["seizure free", "seizure freedom"]:
                    return 0
                elif text in ["seizure infrequent", "seizure infrequency"]:
                    return 0.8
                elif text in ["seizure frequent", "seizure frequency"]:
                    return 8
                else:
                    return 1000
            else:
                max_y, mid_y, min_y = parse_label_to_yearly_count(text)
                if mid_y == -1:
                    return 1000
                elif mid_y == -2:
                    return 1000
                else:
                    return mid_y/12
        except Exception as e:
            # assert False, "Error in get_BH_value: " + str(e) + " " + text
            return -1000



def build_instance_eval_records(data, y_true, y_pred):
    """
    Export one row per test instance.
    These rows are enough for later bootstrap resampling without rerunning model parsing.
    """
    purist_true = convert_to_categories(y_true, method="purist")
    purist_pred = convert_to_categories(y_pred, method="purist")

    pragmatic_true = convert_to_categories(y_true, method="pragmatic")
    pragmatic_pred = convert_to_categories(y_pred, method="pragmatic")

    records = []

    for idx, item in enumerate(data):
        record = {
            "row_index": idx,

            # Final numeric values used for evaluation
            "true_value": float(y_true[idx]),
            "pred_value": float(y_pred[idx]),

            # Purist evaluation labels
            "purist_true": purist_true[idx],
            "purist_pred": purist_pred[idx],
            "purist_correct": purist_true[idx] == purist_pred[idx],

            # Pragmatic evaluation labels
            "pragmatic_true": pragmatic_true[idx],
            "pragmatic_pred": pragmatic_pred[idx],
            "pragmatic_correct": pragmatic_true[idx] == pragmatic_pred[idx],
        }

        records.append(record)

    return records
        

# --- 5. Main program ---
# python e_evaluation_synthetic_results.py  --json_path data/results/generated_predictions.jsonl --allow_prediction_range --allow_error_tolerance
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate seizure prediction results")
    parser.add_argument("--json_path", type=str, default="data/results/predictions_only.json",
                        help="Path to JSON or JSONL file with predictions")
    parser.add_argument("--output_path", type=str, default=None,
                        help="Path to output file")
    parser.add_argument(
        "--instance_eval_output_path",
        type=str,
        default=None,
        help="Path to save per-instance evaluation results for bootstrap"
    )
    parser.add_argument("--model_name", type=str, default=None,
                        help="Model name")
    parser.add_argument("--all_results_path", type=str, default="data/results/all_results.json",
                        help="Path to all results file")    
    parser.add_argument("--allow_prediction_range", action="store_true", default=False,
                        help="Allow range in the prediction")
    parser.add_argument("--allow_error_tolerance", action="store_true", default=False,
                        help="Allow 50% error tolerance in the prediction")
    args = parser.parse_args()

    json_path = args.json_path

    ext = os.path.splitext(json_path)[-1].lower()

    if ext == ".jsonl":
        with open(json_path, "r", encoding="utf-8") as f:
            data = [json.loads(line) for line in f if line.strip()]
    else:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    for idx, item in enumerate(data):
        predict_label = None
        max_y, min_y = -1000, -1000
        for i in range(2):
            try:
                if not predict_label:
                    if '<seizure_frequency_number>' in item["predict"] and '</seizure_frequency_number>' in item["predict"]:
                        predict_label = extract_xml_field(item["predict"])
                    elif '{' in item["predict"]:
                        predict = json.loads(llm.extract_json_string(item["predict"]))
                        if type(predict['seizure_frequency_number']) == list:
                            predict_label = predict['seizure_frequency_number'][0]
                        else:
                            predict_label = predict['seizure_frequency_number']
                    else:
                        predict_label = item["predict"]
                if predict_label in ["unknown", "seizure free", "seizure infrequent", "seizure frequent", "seizure unknown", "seizure infrequency", "seizure frequency", "seizure freedom"]:
                    if predict_label in ["seizure free", "seizure freedom"]:
                        item["predict"] = "0"
                    elif predict_label in ["seizure infrequent", "seizure infrequency"]:
                        item["predict"] = "0.8"
                    elif predict_label in ["seizure frequent", "seizure frequency"]:
                        item["predict"] = "8"
                    else:
                        item["predict"] = "1000"
                elif is_number(predict_label):
                    item["predict"] = predict_label
                else:
                    max_y, mid_y, min_y = parse_label_to_yearly_count(predict_label)
                    if mid_y == -1:
                        item["predict"] = "1000"
                    elif mid_y == -2:
                        item["predict"] = "1000"
                    else:
                        item["predict"] = str(mid_y/12)
                break
            except Exception as e:
                # print(e, idx, item)
                item["predict"] = "1000"
                print(e, "before repair: ", predict_label)
                predict_label = repair_predict_label(predict_label)
                print(e, "after repair: ", predict_label)

        if not is_number(item["label"]):
            item["label"] = get_BH_value(item["label"])
        if args.allow_prediction_range:
            if max_y >= float(item["label"]) and min_y <= float(item["label"]):
                item["predict"] = item["label"]
        
        if args.allow_error_tolerance:
            if float(item["label"]) / 1.5 <= float(item["predict"]) <= float(item["label"]) *1.5:
                item["predict"] = item["label"]
            else:
                print(idx, item["label"], item["predict"])
    y_true = [float(item["label"]) for item in data]
    y_pred = [float(item["predict"]) for item in data]

    instance_eval_records = build_instance_eval_records(data, y_true, y_pred)

    if args.instance_eval_output_path:
        output_dir = os.path.dirname(args.instance_eval_output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(args.instance_eval_output_path, "w", encoding="utf-8") as f:
            json.dump(instance_eval_records, f, ensure_ascii=False, indent=2)
        print(f"\nSaved per-instance evaluation results to: {args.instance_eval_output_path}")

    purist_results, purist_report = evaluate_predictions(y_true, y_pred, method="purist")
    pragmatic_results, pragmatic_report = evaluate_predictions(y_true, y_pred, method="pragmatic")

    print("\nOverall Results:")
    print("Purist:", purist_results)
    print("Pragmatic:", pragmatic_results)

    if args.output_path:
        with open(args.output_path, "w", encoding="utf-8") as f:
            json.dump({"purist": purist_results, "pragmatic": pragmatic_results, "purist_report": purist_report, "pragmatic_report": pragmatic_report}, f, ensure_ascii=False, indent=4)

    if args.model_name and args.all_results_path:
        if os.path.exists(args.all_results_path):
            with open(args.all_results_path, "r", encoding="utf-8") as f:
                all_results = json.load(f)
        else:
            all_results = {}
        model_name = args.model_name
        if args.allow_error_tolerance:
            model_name = model_name + " (allow_error_tolerance)"
        if args.allow_prediction_range:
            model_name = model_name + " (allow_prediction_range)"
        all_results[model_name] = {"purist": purist_results, "pragmatic": pragmatic_results, "purist_report": purist_report, "pragmatic_report": pragmatic_report}
        with open(args.all_results_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=4)
