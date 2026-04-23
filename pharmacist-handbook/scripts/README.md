# 药品信息获取方案

## 方案一：使用极速数据API（推荐）

### 优点
- 有免费版（100次/天）
- API接口稳定
- 数据格式规范

### 使用步骤
1. 访问 https://www.jisuapi.com/api/medicine/ 注册账号
2. 申请药品信息API，获取API Key
3. 运行脚本：
```bash
python fetch_drug_info_jisu.py <你的API_KEY> [数量限制] [起始位置]
```

### 示例
```bash
# 获取前10个药品的信息
python fetch_drug_info_jisu.py your_api_key_here 10

# 从第100个开始，获取50个
python fetch_drug_info_jisu.py your_api_key_here 50 100
```

---

## 方案二：从药智网爬取（备用）

### 说明
- 药智网搜索需要登录，直接爬取可能受限
- 可以尝试直接访问已知药品详情页

### 使用步骤
```bash
python scrape_yaozh.py [数量限制] [起始位置]
```

### 注意事项
- 请求间隔设置为3秒，避免被封
- 可能需要处理验证码或登录

---

## 方案三：手动录入（最可靠）

### 方式1：交互式录入
```bash
python add_drug_manual.py
```
按提示逐个输入药品信息

### 方式2：批量导入
1. 参考模板文件 `../data/manual_drug_info_template.json`
2. 创建自己的JSON文件
3. 运行导入脚本：
```bash
python import_manual_drug_info.py <你的json文件>
```

### JSON格式示例
```json
[
  {
    "name": "苯海索",
    "dosage_form": "片",
    "manual": {
      "indications": "适应症内容...",
      "dosage": "用法用量内容...",
      "contraindications": "禁忌内容...",
      "adverse_reactions": "不良反应内容...",
      "interactions": "药物相互作用内容...",
      "pregnancy_category": "FDA妊娠分级...",
      "pharmacokinetics": "药代动力学内容...",
      "precautions": "注意事项内容...",
      "source": "药智网"
    }
  }
]
```

---

## 方案四：从现有Markdown文件导入

如果已有药品手册的Markdown文件（如苯海索.md），可以：

1. 创建Markdown解析脚本
2. 提取表格中的信息
3. 转换为JSON格式
4. 使用批量导入脚本导入

---

## 数据结构说明

药品信息存储在 `manual` 字段中：

```javascript
{
  "name": "药品名",
  "dosage_form": "剂型",
  "manual": {
    "indications": "适应症",
    "dosage": "用法用量",
    "contraindications": "禁忌",
    "adverse_reactions": "不良反应",
    "interactions": "药物相互作用",
    "pregnancy_category": "FDA妊娠分级",
    "pharmacokinetics": "药代动力学",
    "precautions": "注意事项",
    "source": "数据来源"
  }
}
```

---

## 建议

1. **快速开始**：先申请极速数据API，获取常用药品信息
2. **补充完善**：对API未覆盖的药品，手动录入
3. **定期更新**：建立定期更新机制，保持数据新鲜度
4. **数据备份**：定期备份 drugs.js 文件

---

## 注意事项

1. 所有脚本都会自动保存进度，可以中断后继续
2. 数据文件 `drugs.js` 会被覆盖，建议先备份
3. API调用有频率限制，请注意控制请求速度
4. 手动录入的数据建议单独保存JSON文件备份
