#!/usr/bin/env python3
"""
从药智网获取药品详细信息
支持API调用和网页爬虫两种方式
"""

import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional
import re

# 路径配置
BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DATA_FILE = BASE_DIR / "pharmacist-handbook/data/drugs.js"
OUTPUT_FILE = BASE_DIR / "pharmacist-handbook/data/drugs_with_info.js"

# 药智网API配置（需要申请API Key）
YAOZH_API_KEY = ""  # 请在这里填写药智网API Key
YAOZH_API_BASE = "https://api.yaozh.com/v1"

# 请求间隔（避免请求过快）
REQUEST_DELAY = 1


class DrugInfoFetcher:
    """药品信息获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.drug_info_cache = {}
    
    def load_drugs_data(self) -> List[Dict]:
        """加载药品数据"""
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取JSON数组
        start = content.find('[')
        end = content.rfind(']')
        if start == -1 or end == -1:
            raise ValueError("无法找到药品数据")
        
        return json.loads(content[start:end+1])
    
    def fetch_from_api(self, drug_name: str) -> Optional[Dict]:
        """从药智网API获取药品信息"""
        if not YAOZH_API_KEY:
            return None
        
        try:
            url = f"{YAOZH_API_BASE}/drug/search"
            params = {
                'apikey': YAOZH_API_KEY,
                'keyword': drug_name,
                'type': 'name'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('code') == 200 and data.get('data'):
                return self.parse_api_response(data['data'][0])
            
            return None
            
        except Exception as e:
            print(f"  API请求失败: {e}")
            return None
    
    def fetch_from_web(self, drug_name: str, dosage_form: str = "") -> Optional[Dict]:
        """从药智网网页获取药品信息"""
        try:
            # 构建搜索URL
            search_keyword = f"{drug_name} {dosage_form}".strip()
            search_url = f"https://db.yaozh.com/instruct.html"
            
            params = {
                'search': search_keyword
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                # 解析HTML获取第一个药品详情链接
                # 这里简化处理，实际需要解析HTML
                return self.parse_web_response(response.text, drug_name)
            
            return None
            
        except Exception as e:
            print(f"  网页请求失败: {e}")
            return None
    
    def parse_api_response(self, data: Dict) -> Dict:
        """解析API响应数据"""
        return {
            'indications': data.get('indications', ''),
            'dosage': data.get('usage_dosage', ''),
            'contraindications': data.get('contraindications', ''),
            'adverse_reactions': data.get('adverse_reactions', ''),
            'interactions': data.get('interactions', ''),
            'pregnancy_category': data.get('pregnancy_category', ''),
            'pharmacokinetics': data.get('pharmacokinetics', ''),
            'precautions': data.get('precautions', ''),
            'source': 'yaozh_api'
        }
    
    def parse_web_response(self, html: str, drug_name: str) -> Optional[Dict]:
        """解析网页响应"""
        # 这里需要根据实际网页结构解析
        # 简化处理，返回空数据
        return None
    
    def fetch_drug_info(self, drug: Dict) -> Dict:
        """获取单个药品的详细信息"""
        drug_name = drug['name']
        dosage_form = drug.get('dosage_form', '')
        
        print(f"正在查询: {drug_name} {dosage_form}")
        
        # 检查缓存
        cache_key = f"{drug_name}_{dosage_form}"
        if cache_key in self.drug_info_cache:
            print(f"  ✓ 从缓存获取")
            return self.drug_info_cache[cache_key]
        
        # 尝试API获取
        info = None
        if YAOZH_API_KEY:
            info = self.fetch_from_api(drug_name)
            time.sleep(REQUEST_DELAY)
        
        # API失败则尝试网页获取
        if not info:
            info = self.fetch_from_web(drug_name, dosage_form)
            time.sleep(REQUEST_DELAY)
        
        # 如果都失败，返回空数据
        if not info:
            info = {
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
        
        self.drug_info_cache[cache_key] = info
        return info
    
    def process_all_drugs(self, limit: int = None):
        """处理所有药品"""
        print("="*60)
        print("开始获取药品详细信息")
        print("="*60)
        
        # 加载药品数据
        drugs = self.load_drugs_data()
        print(f"共加载 {len(drugs)} 个药品")
        
        if limit:
            drugs = drugs[:limit]
            print(f"本次处理前 {limit} 个药品")
        
        # 获取每个药品的信息
        success_count = 0
        for i, drug in enumerate(drugs, 1):
            print(f"\n[{i}/{len(drugs)}] ", end="")
            
            info = self.fetch_drug_info(drug)
            drug['manual'] = info
            
            if info.get('source'):
                success_count += 1
                print(f"  ✓ 成功获取")
            else:
                print(f"  ✗ 未获取到数据")
        
        # 保存结果
        self.save_drugs_data(drugs)
        
        print("\n" + "="*60)
        print("处理完成")
        print(f"成功获取: {success_count}/{len(drugs)}")
        print(f"输出文件: {OUTPUT_FILE}")
        print("="*60)
    
    def save_drugs_data(self, drugs: List[Dict]):
        """保存药品数据"""
        import datetime
        
        js_content = "// 药品数据文件（含详细信息）\n"
        js_content += f"// 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        js_content += f"// 药品数量: {len(drugs)}\n\n"
        js_content += "const DRUGS_DATA = "
        js_content += json.dumps(drugs, ensure_ascii=False, indent=2)
        js_content += ";\n"
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"\n✓ 数据已保存: {OUTPUT_FILE}")


def main():
    """主函数"""
    fetcher = DrugInfoFetcher()
    
    # 处理所有药品（可以设置limit参数限制数量用于测试）
    fetcher.process_all_drugs(limit=None)


if __name__ == "__main__":
    main()
