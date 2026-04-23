#!/usr/bin/env python3
"""
修正抗生素药品的网址，确保与"缺少详细信息的药品列表.md"中的网址一致
"""

import json
from pathlib import Path

# 抗生素药品ID到正确网址的映射
ANTIBIOTIC_URLS = {
    # 注射剂抗生素
    86: "https://www.hnysfww.com/goods.php?id=2328",    # 甲硝唑氯化钠
    77: "https://www.hnysfww.com/goods.php?id=2038",     # 盐酸克林霉素
    224: "https://www.hnysfww.com/goods.php?id=1980",    # 硫酸阿米卡星
    916: "https://www.hnysfww.com/goods.php?id=1977",    # 硫酸庆大霉素
    439: "https://www.hnysfww.com/goods.php?id=2039",    # 克林霉素磷酸酯
    658: "https://www.hnysfww.com/goods.php?id=1916",    # 注射用头孢地嗪钠/5%葡萄糖
    656: "https://www.hnysfww.com/goods.php?id=1907",    # 注射用头孢曲松钠/氯化钠
    398: "https://www.hnysfww.com/goods.php?id=2092",    # 盐酸莫西沙星氯化钠
    281: "https://www.hnysfww.com/goods.php?id=2089",    # 左氧氟沙星氯化钠
    757: "https://www.hnysfww.com/goods.php?id=2092",    # ※▲盐酸莫西沙星氯化钠
    804: "https://www.hnysfww.com/goods.php?id=2115",    # 利奈唑胺葡萄糖
    282: "https://www.hnysfww.com/goods.php?id=2089",    # 左氧氟沙星片
    
    # 口服抗生素
    970: "https://www.hnysfww.com/goods.php?id=2328",    # 甲硝唑片
    495: "https://www.hnysfww.com/goods.php?id=2092",    # 盐酸莫西沙星片
    677: "https://www.hnysfww.com/goods.php?id=2016",    # 阿奇霉素片
}

DATA_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs")

def fix_url(drug_id, correct_url):
    """修正单个药品的网址"""
    file_path = DATA_DIR / f"{drug_id}.json"
    
    if not file_path.exists():
        print(f"❌ 文件不存在: {drug_id}.json")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查当前网址
        current_url = data.get('url', {}).get('hnysfww', '')
        
        if current_url == correct_url:
            print(f"✓ ID {drug_id}: 网址正确，无需修改")
            return True
        
        # 修正网址
        if 'url' not in data:
            data['url'] = {}
        data['url']['hnysfww'] = correct_url
        data['url']['last_updated'] = "2026-03-21"
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ ID {drug_id}: 网址已修正")
        print(f"   原网址: {current_url}")
        print(f"   新网址: {correct_url}")
        return True
        
    except Exception as e:
        print(f"❌ ID {drug_id}: 错误 - {e}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("修正抗生素药品网址")
    print("=" * 80)
    
    success_count = 0
    
    for drug_id, correct_url in ANTIBIOTIC_URLS.items():
        if fix_url(drug_id, correct_url):
            success_count += 1
    
    print("\n" + "=" * 80)
    print(f"处理完成: 成功 {success_count}/{len(ANTIBIOTIC_URLS)}")
    print("=" * 80)

if __name__ == "__main__":
    main()
