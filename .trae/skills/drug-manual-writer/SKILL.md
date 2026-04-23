---
name: "drug-manual-writer"
description: "编写药品手册内容，包括精简版和详细版。根据药品剂型智能筛选内容，提取关键药代动力学参数。Invoke when user asks to write drug manual content or update drug information."
---

# 药品手册编写规范

## 一、精简版编写要求

### 核心原则
- **压缩说明性文字**：去除"请"、"建议"、"应该"等客套用语
- **保留关键信息**：只保留事实性、指令性内容
- **使用简洁格式**：使用编号、符号等结构化表达

### 各字段精简规则

#### 1. 适应症（indications）
- 保留：疾病名称、适用人群、使用场景
- 去除：详细病理描述、发病机制解释
- 示例：
  - ❌ "本品适用于治疗由敏感菌引起的下列感染：包括呼吸道感染、泌尿系统感染等"
  - ✅ "用于敏感菌引起的：⑴呼吸道感染 ⑵泌尿系统感染"

#### 2. 用法用量（dosage）
- **根据剂型智能筛选**：
  - 口服剂型（片、胶囊、颗粒）：只保留口服用法
  - 注射剂型（注射液、粉针）：只保留注射用法
  - 外用剂型（软膏、贴剂）：只保留外用方法
- 保留：剂量、频次、疗程、特殊人群调整
- 去除：给药原理、药理作用解释

#### 3. 禁忌症（contraindications）
- 保留：明确的禁忌人群、疾病、药物相互作用
- 去除：禁忌原因的详细解释
- 示例：
  - ❌ "对本品过敏者禁用，因为可能引起严重的过敏反应"
  - ✅ "对本品过敏者禁用"

#### 4. 不良反应（adverse_reactions）
- 保留：反应名称、发生率分级（常见/偶见/罕见）
- 去除：反应机制的详细解释
- 格式：按系统分类，使用简短描述

#### 5. 药物相互作用（interactions）
- 如无临床意义：简化为"暂未发现有临床意义的药物相互作用"
- 如有：列出相互作用药物及后果

#### 6. 药代动力学（pharmacokinetics）
- **必须提取的关键参数**：
  - 达峰时间（Tmax）
  - 峰浓度（Cmax）
  - 半衰期（t1/2）
  - 生物利用度
  - 蛋白结合率
- **区分药效学和药动学**：
  - ❌ 不要提取：作用机制、受体结合、药效描述
  - ✅ 只提取：吸收、分布、代谢、排泄参数

#### 7. 注意事项（precautions）
- 保留：警告信息、监测要求、特殊人群注意
- 去除：详细的风险解释和临床建议
- 示例：
  - ❌ "肝功能检查异常的患者应慎用，因为可能增加肝脏负担，建议定期监测肝功能指标"
  - ✅ "肝功能异常者慎用"

## 二、详细版编写要求

### 内容完整性
- 保留网站原始内容的完整性
- 不遗漏任何重要信息
- 保持专业术语的准确性

### 剂型智能筛选

#### 口服剂型
包括：片剂、胶囊、颗粒剂、散剂、丸剂、口服溶液等
- **保留**：口服用法、餐前/餐后、用水量
- **去除**：静脉注射、肌内注射、皮下注射等注射用法

#### 注射剂型
包括：注射液、注射用粉针、输液等
- **保留**：给药途径（静注/肌注/皮下）、配制方法、滴速
- **去除**：口服方法、食物影响

#### 外用剂型
包括：软膏、乳膏、贴剂、栓剂、滴眼液等
- **保留**：外用部位、使用方法、使用频次
- **去除**：口服、注射相关内容

#### 特殊剂型
- **缓控释制剂**：强调不可掰开、嚼碎
- **肠溶制剂**：强调餐前服用、不可与抗酸药同服
- **舌下片**：强调舌下含服、不可吞服

## 三、从湖南药事服务网提取数据的方法

### 网页结构分析
湖南药事服务网药品详情页URL格式：`https://www.hnysfww.com/goods.php?id=数字ID`

**关键发现**：药品详细信息通常位于页面第一个`<table>`元素中，而非分散在div或其他结构中。

### 提取步骤

#### 1. 获取页面内容
```python
import requests
from bs4 import BeautifulSoup

url = "https://www.hnysfww.com/goods.php?id=153"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

response = requests.get(url, headers=headers, timeout=30)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')
```

#### 2. 定位药品信息
```python
# 查找包含药品信息的table（通常是第一个）
tables = soup.find_all('table')
if tables:
    text = tables[0].get_text()
```

#### 3. 提取各字段（使用正则表达式）

**适应证/适应症/功能主治**：
```python
# 方法1：先尝试匹配"功能主治"（中成药常用）
match = re.search(r'功能主治(.+?)(?:成份|药理作用|用法用量|不良反应|禁忌|注意事项|贮藏|$)', text, re.DOTALL)
if match:
    indications = clean_text(match.group(1))
else:
    # 方法2：再尝试匹配"适应证"（西药常用）
    match = re.search(r'适应证(.+?)(?:药理作用|用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        indications = clean_text(match.group(1))
```

**重要提示**：中成药通常使用"功能主治"而非"适应证"，提取时需要优先尝试匹配"功能主治"。

**药理作用/成份**（用于药代动力学）：
```python
# 方法1：先尝试匹配"成份"（中成药常用）
match = re.search(r'成份/药理作用(.+?)(?:用法用量|不良反应|禁忌|注意事项|贮藏|$)', text, re.DOTALL)
if match:
    pharmacokinetics = clean_text(match.group(1))
else:
    # 方法2：再尝试匹配"药理作用"（西药常用）
    match = re.search(r'药理作用(.+?)(?:用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        pharmacokinetics = clean_text(match.group(1))
```

**重要提示**：中成药通常使用"成份"而非"药理作用"，且可能合并为"成份/药理作用"字段。

**用法用量**：
```python
match = re.search(r'用法与?用量(.+?)(?:不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
if match:
    dosage = clean_text(match.group(1))
```

**禁忌/禁忌症**：
```python
# 匹配"禁忌"或"禁忌症"（两者都常见）
match = re.search(r'禁忌症?(.+?)(?:不良反应|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
if match:
    contraindications = clean_text(match.group(1))
```

**重要提示**：中成药通常使用"禁忌症"，西药通常使用"禁忌"，使用`禁忌症?`可以匹配两种情况。

**不良反应**：
```python
match = re.search(r'不良反应(.+?)(?:药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
if match:
    adverse_reactions = clean_text(match.group(1))
```

**药物相互作用**：
```python
match = re.search(r'药物相互作用(.+?)(?:注意事项|贮藏|$)', text, re.DOTALL)
if match:
    interactions = clean_text(match.group(1))
```

**注意事项**：
```python
match = re.search(r'注意事项(.+?)(?:贮藏|$)', text, re.DOTALL)
if match:
    precautions = clean_text(match.group(1))
```

**妊娠分级**：
```python
# 方法1：查找明确的妊娠分级标记
match = re.search(r'妊娠期用药安全分级\s*([A-Z]\s*级?)', text)
if match:
    pregnancy_category = match.group(1)

# 方法2：从文本中提取
match = re.search(r'妊娠[^。]*?([A-Z])\s*级', text)
if match:
    pregnancy_category = match.group(1)
```

#### 4. 文本清理函数
```python
def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    import re
    text = re.sub(r'\s+', ' ', text)  # 合并多个空白字符
    text = text.replace('\xa0', ' ').replace('\u3000', ' ')  # 替换特殊空格
    return text.strip()
```

### 中成药与西药字段差异对照表

| 字段 | 西药常用 | 中成药常用 | 提取策略 |
|------|---------|-----------|---------|
| 适应症 | 适应证/适应症 | 功能主治 | 优先匹配"功能主治"，再匹配"适应证" |
| 药理作用 | 药理作用 | 成份/药理作用 | 优先匹配"成份/药理作用"，再匹配"药理作用" |
| 禁忌 | 禁忌 | 禁忌症 | 使用`禁忌症?`同时匹配两种情况 |
| 不良反应 | 不良反应 | 不良反应 | 相同 |
| 注意事项 | 注意事项 | 注意事项 | 相同 |

### 重要提示
1. **必须使用正则表达式**：网站内容不是结构化的HTML字段，而是连续的文本流
2. **字段顺序**：适应证 → 药理作用 → 用法用量 → 禁忌 → 不良反应 → 药物相互作用 → 注意事项 → 贮藏
3. **匹配模式**：使用非贪婪匹配`(.+?)`和正向肯定查找`(?=...)`来精确定位字段边界
4. **清理文本**：提取后必须清理多余的空白字符和特殊字符
5. **中成药特殊处理**：中成药的字段名称与西药不同，需要优先尝试中成药字段名

### 批量处理流程
1. 从"缺少详细信息的药品列表.md"解析药品ID和网址
2. 检查每个药品JSON文件的当前状态
3. 对缺失信息的药品，从网站获取数据
4. 更新JSON文件并标记来源为"湖南药事服务网"
5. 添加url.hnysfww字段记录数据来源网址

### 药代动力学参数提取示例

**原始文本**：
```
口服后吸收迅速，约2小时达血药峰浓度（Cmax为1.5μg/ml），
半衰期约为8小时，主要经肝脏代谢，经肾脏排泄。
```

**提取结果**：
- Tmax：约2小时
- Cmax：1.5μg/ml
- 半衰期：约8小时
- 代谢：肝脏
- 排泄：肾脏

## 四、输出格式

### JSON结构
```json
{
  "manual": {
    "indications": "精简版适应症",
    "full_indications": "详细版适应症",
    "dosage": "精简版用法用量（按剂型筛选）",
    "full_dosage": "详细版用法用量（按剂型筛选）",
    "contraindications": "精简版禁忌症",
    "full_contraindications": "详细版禁忌症",
    "adverse_reactions": "精简版不良反应",
    "full_adverse_reactions": "详细版不良反应",
    "interactions": "精简版药物相互作用",
    "full_interactions": "详细版药物相互作用",
    "pregnancy_category": "妊娠分级",
    "pharmacokinetics": "精简版药代动力学（关键参数）",
    "full_pharmacokinetics": "详细版药代动力学",
    "precautions": "精简版注意事项",
    "full_precautions": "详细版注意事项"
  }
}
```

## 五、质量控制

1. **精简版字数控制**：每个字段不超过200字
2. **关键信息完整性**：确保精简版包含所有必要信息
3. **剂型匹配验证**：确认用法用量与剂型匹配
4. **药动学参数验证**：确保提取的是药动学而非药效学
