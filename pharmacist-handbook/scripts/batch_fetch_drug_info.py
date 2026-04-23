#!/usr/bin/env python3
"""
批量获取药品信息综合脚本
支持多种数据源：极速数据API、药智网、手动模式
"""

import json
import time
import re
import requests
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote
import argparse

# 路径配置
BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DATA_FILE = BASE_DIR / "pharmacist-handbook/data/drugs.js"
OUTPUT_FILE = BASE_DIR / "pharmacist-handbook/data/drugs.js"
CACHE_FILE = BASE_DIR / "pharmacist-handbook/data/drug_info_cache.json"

# API配置
JISU_API_KEY = ""  # 请在这里填写极速数据API Key
JISU_API_BASE = "https://api.jisuapi.com/medicine"
REQUEST_DELAY = 1


class DrugInfoFetcher:
    """药品信息获取器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or JISU_API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.cache = self.load_cache()
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def load_cache(self) -> Dict:
        """加载缓存"""
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_cache(self):
        """保存缓存"""
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
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
    
    def search_jisu_api(self, drug_name: str) -> Optional[Dict]:
        """从极速数据API搜索药品"""
        if not self.api_key:
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
                    return {
                        'indications': result.get('indication', ''),
                        'dosage': result.get('usage', ''),
                        'contraindications': result.get('contraindication', ''),
                        'adverse_reactions': result.get('adverse', ''),
                        'interactions': result.get('interaction', ''),
                        'pregnancy_category': result.get('pregnancycategory', ''),
                        'pharmacokinetics': result.get('pharmacokinetics', ''),
                        'precautions': result.get('precautions', ''),
                        'source': 'jisu_api'
                    }
            
            return None
            
        except Exception as e:
            print(f"  API请求失败: {e}")
            return None
    
    def search_yaozh(self, drug_name: str, dosage_form: str = "") -> Optional[Dict]:
        """从药智网搜索药品（备用方案）"""
        try:
            keyword = f"{drug_name} {dosage_form}".strip()
            encoded_keyword = quote(keyword)
            search_url = f"https://db.yaozh.com/instruct.html?search={encoded_keyword}"
            
            response = self.session.get(search_url, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return None
            
            html = response.text
            
            # 查找药品详情链接
            pattern = r'href="(/instruct/\d+\.html)"'
            matches = re.findall(pattern, html)
            
            if matches:
                detail_url = f"https://db.yaozh.com{matches[0]}"
                return self.parse_yaozh_detail(detail_url)
            
            return None
            
        except Exception as e:
            print(f"  药智网搜索失败: {e}")
            return None
    
    def parse_yaozh_detail(self, url: str) -> Optional[Dict]:
        """解析药智网药品详情"""
        try:
            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return None
            
            html = response.text
            
            # 提取信息
            info = {
                'indications': self.extract_field(html, ['适应症', '功能主治']),
                'dosage': self.extract_field(html, ['用法用量']),
                'contraindications': self.extract_field(html, ['禁忌']),
                'adverse_reactions': self.extract_field(html, ['不良反应', '副作用']),
                'interactions': self.extract_field(html, ['药物相互作用', '相互作用']),
                'pregnancy_category': self.extract_field(html, ['孕妇及哺乳期妇女用药', '妊娠']),
                'pharmacokinetics': self.extract_field(html, ['药代动力学', '药动学']),
                'precautions': self.extract_field(html, ['注意事项', '警告']),
                'source': 'yaozh'
            }
            
            # 检查是否获取到有效信息
            if any(info.values()):
                return info
            
            return None
            
        except Exception as e:
            print(f"  解析详情失败: {e}")
            return None
    
    def extract_field(self, html: str, keywords: List[str]) -> str:
        """从HTML中提取字段"""
        for keyword in keywords:
            # 尝试多种匹配模式
            patterns = [
                f'{keyword}</dt>\\s*<dd[^>]*>(.*?)</dd>',
                f'{keyword}[：:]\\s*(.*?)(?:<|$)',
                f'<td[^>]*>{keyword}</td>\\s*<td[^>]*>(.*?)</td>',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
                if match:
                    text = match.group(1)
                    # 清理HTML标签
                    text = re.sub('<[^<]+?>', '', text)
                    text = text.strip()
                    if text and text != '暂无':
                        return text
        
        return ''
    
    def process_drug(self, drug: Dict) -> Dict:
        """处理单个药品"""
        drug_name = drug['name']
        dosage_form = drug.get('dosage_form', '')
        
        print(f"正在查询: {drug_name} ({dosage_form})")
        
        # 检查缓存
        cache_key = f"{drug_name}_{dosage_form}"
        if cache_key in self.cache:
            print("  ✓ 从缓存获取")
            drug['manual'] = self.cache[cache_key]
            self.stats['success'] += 1
            return drug
        
        # 尝试从API获取
        info = None
        
        if self.api_key:
            print("  尝试从极速数据API获取...")
            info = self.search_jisu_api(drug_name)
            time.sleep(REQUEST_DELAY)
        
        # 如果API失败，尝试药智网
        if not info:
            print("  尝试从药智网获取...")
            info = self.search_yaozh(drug_name, dosage_form)
            time.sleep(REQUEST_DELAY + 2)  # 药智网需要更长间隔
        
        if info:
            drug['manual'] = info
            self.cache[cache_key] = info
            print("  ✓ 成功获取信息")
            self.stats['success'] += 1
        else:
            print("  ✗ 未获取到信息")
            self.stats['failed'] += 1
        
        return drug
    
    def run(self, limit: int = None, offset: int = 0, source: str = 'auto'):
        """运行批量获取"""
        print("="*60)
        print("批量获取药品信息")
        print("="*60)
        
        # 加载药品数据
        drugs = self.load_drugs()
        print(f"共加载 {len(drugs)} 个药品")
        
        # 筛选需要获取信息的药品
        drugs_without_info = [d for d in drugs if not d.get('manual') or not d['manual'].get('source')]
        print(f"需要获取信息的药品: {len(drugs_without_info)} 个")
        
        # 处理范围
        if offset:
            drugs_without_info = drugs_without_info[offset:]
            print(f"从第 {offset} 个开始处理")
        
        if limit:
            drugs_without_info = drugs_without_info[:limit]
            print(f"本次处理前 {limit} 个药品")
        
        self.stats['total'] = len(drugs_without_info)
        
        print(f"\n数据源: {source}")
        if source == 'api' and not self.api_key:
            print("⚠ 警告: 未配置API Key，将跳过API获取")
        print(f"预计需要 {len(drugs_without_info)} 次请求\n")
        
        # 处理每个药品
        for i, drug in enumerate(drugs_without_info, 1):
            print(f"[{i}/{len(drugs_without_info)}] ", end="")
            drug = self.process_drug(drug)
            
            # 定期保存缓存和进度
            if i % 5 == 0:
                self.save_cache()
                print(f"\n已保存缓存 ({i}/{len(drugs_without_info)})\n")
        
        # 最终保存
        self.save_cache()
        self.save_drugs(drugs)
        
        # 打印统计
        print("\n" + "="*60)
        print("处理完成")
        print(f"总计: {self.stats['total']}")
        print(f"成功: {self.stats['success']}")
        print(f"失败: {self.stats['failed']}")
        print(f"成功率: {self.stats['success']/self.stats['total']*100:.1f}%")
        print("="*60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量获取药品信息')
    parser.add_argument('--api-key', '-k', help='极速数据API Key')
    parser.add_argument('--limit', '-l', type=int, help='处理数量限制')
    parser.add_argument('--offset', '-o', type=int, default=0, help='起始位置')
    parser.add_argument('--source', '-s', choices=['auto', 'api', 'yaozh'], 
                        default='auto', help='数据源选择')
    
    args = parser.parse_args()
    
    fetcher = DrugInfoFetcher(api_key=args.api_key)
    fetcher.run(limit=args.limit, offset=args.offset, source=args.source)


if __name__ == "__main__":
    main()
