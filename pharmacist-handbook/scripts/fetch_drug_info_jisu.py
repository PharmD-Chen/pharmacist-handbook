#!/usr/bin/env python3
"""
从极速数据API获取药品详细信息
API文档: https://www.jisuapi.com/api/medicine/
"""

import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional

# 路径配置
BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DATA_FILE = BASE_DIR / "pharmacist-handbook/data/drugs.js"
OUTPUT_FILE = BASE_DIR / "pharmacist-handbook/data/drugs.js"

# API配置 - 需要申请API Key
# 免费版: 100次/天
# 可在 https://www.jisuapi.com/api/medicine/ 申请
JISU_API_KEY = ""  # 请在这里填写极速数据API Key
JISU_API_BASE = "https://api.jisuapi.com/medicine"

# 请求间隔
REQUEST_DELAY = 1


class JisuDrugInfoFetcher:
    """极速数据药品信息获取器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or JISU_API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.cache = {}
    
    def load_drugs(self) -> List[Dict]:
        """加载药品数据"""
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        start = content.find('[')
        end = content.rfind(']')
        return json.loads(content[start:end+1])
    
    def save_drugs(self, drugs: List[Dict]):
        """保存药品数据"""
        import datetime
        
        js_content = "// 药品数据文件\n"
        js_content += f"// 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        js_content += f"// 药品数量: {len(drugs)}\n\n"
        js_content += "const DRUGS_DATA = "
        js_content += json.dumps(drugs, ensure_ascii=False, indent=2)
        js_content += ";\n"
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"✓ 数据已保存: {OUTPUT_FILE}")
    
    def search_drug(self, drug_name: str) -> Optional[Dict]:
        """搜索药品信息"""
        if not self.api_key:
            print("  ✗ 未配置API Key")
            return None
        
        try:
            url = f"{JISU_API_BASE}/query"
            params = {
                'appkey': self.api_key,
                'name': drug_name
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('status') == 0:
                result = data.get('result', {})
                if result:
                    return self.parse_api_response(result)
            else:
                print(f"  API错误: {data.get('msg', '未知错误')}")
            
            return None
            
        except Exception as e:
            print(f"  请求失败: {e}")
            return None
    
    def parse_api_response(self, data: Dict) -> Dict:
        """解析API响应"""
        return {
            'indications': data.get('indication', ''),
            'dosage': data.get('usage', ''),
            'contraindications': data.get('contraindication', ''),
            'adverse_reactions': data.get('adverse', ''),
            'interactions': data.get('interaction', ''),
            'pregnancy_category': data.get('pregnancycategory', ''),
            'pharmacokinetics': data.get('pharmacokinetics', ''),
            'precautions': data.get('precautions', ''),
            'source': 'jisu_api'
        }
    
    def process_drug(self, drug: Dict) -> Dict:
        """处理单个药品"""
        drug_name = drug['name']
        
        print(f"正在查询: {drug_name}")
        
        # 检查缓存
        if drug_name in self.cache:
            print("  ✓ 从缓存获取")
            drug['manual'] = self.cache[drug_name]
            return drug
        
        # 搜索药品
        info = self.search_drug(drug_name)
        time.sleep(REQUEST_DELAY)
        
        if info:
            drug['manual'] = info
            self.cache[drug_name] = info
            print("  ✓ 成功获取信息")
        else:
            drug['manual'] = {
                'indications': '',
                'dosage': '',
                'contraindications': '',
                'adverse_reactions': '',
                'interactions': '',
                'pregnancy_category': '',
                'pharmacokinetics': '',
                'precautions': '',
                'source': ''
            }
            print("  ✗ 未获取到信息")
        
        return drug
    
    def run(self, limit: int = None, offset: int = 0):
        """运行获取"""
        if not self.api_key:
            print("="*60)
            print("错误: 未配置API Key")
            print("="*60)
            print("\n请按以下步骤操作:")
            print("1. 访问 https://www.jisuapi.com/api/medicine/")
            print("2. 注册账号并申请药品信息API")
            print("3. 将API Key填入脚本中的 JISU_API_KEY 变量")
            print("\n或者使用命令行参数传入:")
            print("  python fetch_drug_info_jisu.py <API_KEY>")
            return
        
        print("="*60)
        print("极速数据药品信息获取")
        print("="*60)
        
        # 加载药品数据
        drugs = self.load_drugs()
        print(f"共加载 {len(drugs)} 个药品")
        
        # 处理范围
        if offset:
            drugs = drugs[offset:]
            print(f"从第 {offset} 个开始处理")
        
        if limit:
            drugs = drugs[:limit]
            print(f"本次处理前 {limit} 个药品")
        
        print(f"\n注意: 免费版API限制100次/天")
        print(f"预计需要 {len(drugs)} 次API调用\n")
        
        # 处理每个药品
        success_count = 0
        for i, drug in enumerate(drugs, 1):
            print(f"[{i}/{len(drugs)}] ", end="")
            
            # 检查是否已有信息
            if drug.get('manual') and drug['manual'].get('source'):
                print(f"{drug['name']} - 已有数据，跳过")
                success_count += 1
                continue
            
            drug = self.process_drug(drug)
            
            if drug['manual'].get('source'):
                success_count += 1
            
            # 定期保存
            if i % 10 == 0:
                self.save_drugs(drugs)
                print(f"\n已保存进度 ({i}/{len(drugs)})\n")
        
        # 最终保存
        self.save_drugs(drugs)
        
        print("\n" + "="*60)
        print("处理完成")
        print(f"成功获取: {success_count}/{len(drugs)}")
        print("="*60)


def main():
    """主函数"""
    import sys
    
    # 从命令行获取API Key
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    fetcher = JisuDrugInfoFetcher(api_key=api_key)
    
    # 解析其他参数
    limit = None
    offset = 0
    
    if len(sys.argv) > 2:
        try:
            limit = int(sys.argv[2])
        except ValueError:
            pass
    
    if len(sys.argv) > 3:
        try:
            offset = int(sys.argv[3])
        except ValueError:
            pass
    
    fetcher.run(limit=limit, offset=offset)


if __name__ == "__main__":
    main()
