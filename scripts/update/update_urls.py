#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

# 从报告中提取的42个药品及其网址
drug_urls = {
    "丙戊酸钠注射用浓溶液": "https://www.hnysfww.com/goods.php?id=857",
    "人血白蛋白": "https://www.hnysfww.com/goods.php?id=3510",
    "※▲依达拉奉右莰醇注射用浓溶液": "https://www.hnysfww.com/goods.php?id=13176",
    "※▲先诺特韦片/利托那韦片组合包装": "https://www.hnysfww.com/goods.php?id=13601",
    "可溶性止血纱布": "",  # 无网址
    "复方阿胶浆": "https://www.hnysfww.com/goods.php?id=6435",
    "外用人表皮生长因子": "https://www.hnysfww.com/goods.php?id=3551",
    "注射用伏立康唑": "https://www.hnysfww.com/goods.php?id=2180",
    "注射用六氟化硫微泡": "https://www.hnysfww.com/goods.php?id=3332",
    "注射用双羟萘酸曲普瑞林": "https://www.hnysfww.com/goods.php?id=1282",
    "※▲注射用右兰索拉唑": "https://www.hnysfww.com/goods.php?id=13730",
    "注射用哌拉西林钠他唑巴坦钠": "https://www.hnysfww.com/goods.php?id=1949",
    "※注射用头孢哌酮钠舒巴坦钠": "https://www.hnysfww.com/goods.php?id=1944",
    "注射用头孢噻肟钠他唑巴坦钠": "https://www.hnysfww.com/goods.php?id=1951",
    "※▲注射用头孢比罗酯钠": "https://www.hnysfww.com/goods.php?id=1931",
    "※▲注射用尤瑞克林": "https://www.hnysfww.com/goods.php?id=3659",
    "注射用尿激酶": "https://www.hnysfww.com/goods.php?id=1146",
    "注射用戈那瑞林": "https://www.hnysfww.com/goods.php?id=1278",
    "※▲注射用曲克芦丁": "https://www.hnysfww.com/goods.php?id=379",
    "注射用氨曲南": "https://www.hnysfww.com/goods.php?id=1973",
    "注射用生长抑素": "https://www.hnysfww.com/goods.php?id=663",
    "注射用甲磺酸齐拉西酮": "https://www.hnysfww.com/goods.php?id=782",
    "注射用甲苯磺酸奥马环素": "https://www.hnysfww.com/goods.php?id=13087",
    "※▲注射用盐酸万古霉素": "https://www.hnysfww.com/goods.php?id=2041",
    "注射用盐酸表柔比星": "https://www.hnysfww.com/goods.php?id=2518",
    "注射用胶原酶": "https://www.hnysfww.com/goods.php?id=3662",
    "注射用胸腺五肽": "https://www.hnysfww.com/goods.php?id=3627",
    "注射用舒巴坦钠": "https://www.hnysfww.com/goods.php?id=1933",
    "※注射用英夫利西单抗": "https://www.hnysfww.com/goods.php?id=3565",
    "注射用醋酸地加瑞克": "https://www.hnysfww.com/goods.php?id=12868",
    "注射用阿昔洛韦": "https://www.hnysfww.com/goods.php?id=2234",
    "活血止痛膏": "https://www.hnysfww.com/goods.php?id=5695",
    "盐酸美金刚口溶膜": "https://www.hnysfww.com/goods.php?id=910",
    "硫酸镁": "",  # 无网址
    "碘酊": "https://www.hnysfww.com/goods.php?id=2432",
    "祛风骨痛凝胶膏": "https://www.hnysfww.com/goods.php?id=13041",
    "米诺地尔酊": "https://www.hnysfww.com/goods.php?id=239",
    "葡萄糖粉剂": "",  # 无网址
    "蓖麻油": "https://www.hnysfww.com/goods.php?id=578",
    "※▲连榆烧伤膏": "https://www.hnysfww.com/goods.php?id=13325",
    "阿立哌唑口溶膜": "https://www.hnysfww.com/goods.php?id=786",
    "青霉素皮试剂": "",  # 无网址
}

# 读取原文件
with open('pharmacist-handbook/data/drugs_without_manual.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 更新每个药品的网址
updated_count = 0
for drug_name, url in drug_urls.items():
    if not url:
        continue
    
    # 构建正则表达式匹配该药品的行
    # 格式: 序号. 药品名 | 剂型 | 完整名称 [网址]
    pattern = rf'^(\d+\.\s+{re.escape(drug_name)}\s+\|\s+[^\|]+\|\s+.+?)(?:\s+https://\S+)?$'
    
    def replace_url(match):
        return f"{match.group(1)} {url}"
    
    new_content, count = re.subn(pattern, replace_url, content, flags=re.MULTILINE)
    if count > 0:
        content = new_content
        updated_count += 1
        print(f"已更新: {drug_name}")

# 写回文件
with open('pharmacist-handbook/data/drugs_without_manual.txt', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n共更新了 {updated_count} 个药品的网址")
