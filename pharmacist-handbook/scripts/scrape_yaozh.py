#!/usr/bin/env python3
"""
从药智网公开页面爬取药品说明书信息
"""

import json
import time
import re
import requests
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote

# 路径配置
BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DATA_FILE = BASE_DIR / "pharmacist-handbook/data/drugs.js"
OUTPUT_FILE = BASE_DIR / "pharmacist-handbook/data/drugs.js"

# 请求配置
REQUEST_DELAY = 3  # 请求间隔，避免被封
MAX_RETRY = 3  # 最大重试次数


class YaozhScraper:
    """药智网爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
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
    
    def search_drug(self, drug_name: str, dosage_form: str = "") -> Optional[str]:
        """搜索药品，返回详情页URL"""
        try:
            # 构建搜索关键词
            keyword = f"{drug_name} {dosage_form}".strip()
            encoded_keyword = quote(keyword)
            
            search_url = f"https://db.yaozh.com/instruct.html?search={encoded_keyword}"
            
            response = self.session.get(search_url, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"  搜索失败: HTTP {response.status_code}")
                return None
            
            # 解析搜索结果，获取第一个药品的链接
            html = response.text
            
            # 查找药品详情链接 - 匹配搜索结果中的链接
            # 药智网搜索结果中的链接格式: /instruct/数字.html
            pattern = r'href="(/instruct/\d+\.html)"'
            matches = re.findall(pattern, html)
            
            if matches:
                # 返回第一个匹配的结果
                return f"https://db.yaozh.com{matches[0]}"
            
            return None
            
        except Exception as e:
            print(f"  搜索出错: {e}")
            return None
    
    def fetch_drug_detail(self, url: str) -> Optional[Dict]:
        """获取药品详情"""
        for retry in range(MAX_RETRY):
            try:
                response = self.session.get(url, timeout=15)
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    print(f"  请求失败: HTTP {response.status_code}")
                    time.sleep(REQUEST_DELAY)
                    continue
                
                return self.parse_drug_detail(response.text)
                
            except Exception as e:
                print(f"  请求出错 (重试 {retry+1}/{MAX_RETRY}): {e}")
                time.sleep(REQUEST_DELAY * (retry + 1))
        
        return None
    
    def parse_drug_detail(self, html: str) -> Optional[Dict]:
        """解析药品详情页面"""
        try:
            info = {
                'indications': '',
                'dosage': '',
                'contraindications': '',
                'adverse_reactions': '',
                'interactions': '',
                'pregnancy_category': '',
                'pharmacokinetics': '',
                'precautions': '',
                'source': 'yaozh'
            }
            
            # 提取各个字段 - 使用更灵活的正则表达式
            # 适应症
            indications_match = re.search(
                r'【适应症】\s*</dt>\s*<dd[^>]*>(.*?)</dd>',
                html, re.DOTALL | re.IGNORECASE
            )
            if indications_match:
                info['indications'] = self.clean_text(indications_match.group(1))
            
            # 用法用量
            dosage_match = re.search(
                r'【用法用量】\s*</dt>\s*<dd[^>]*>(.*?)</dd>',
                html, re.DOTALL | re.IGNORECASE
            )
            if dosage_match:
                info['dosage'] = self.clean_text(dosage_match.group(1))
            
            # 禁忌
            contraindications_match = re.search(
                r'【禁忌】\s*</dt>\s*<dd[^>]*>(.*?)</dd>',
                html, re.DOTALL | re.IGNORECASE
            )
            if contraindications_match:
                info['contraindications'] = self.clean_text(contraindications_match.group(1))
            
            # 不良反应
            adverse_match = re.search(
                r'【不良反应】\s*</dt>\s*<dd[^>]*>(.*?)</dd>',
                html, re.DOTALL | re.IGNORECASE
            )
            if adverse_match:
                info['adverse_reactions'] = self.clean_text(adverse_match.group(1))
            
            # 药物相互作用
            interactions_match = re.search(
                r'【药物相互作用】\s*</dt>\s*<dd[^>]*>(.*?)</dd>',
                html, re.DOTALL | re.IGNORECASE
            )
            if interactions_match:
                info['interactions'] = self.clean_text(interactions_match.group(1))
            
            # FDA妊娠分级
            pregnancy_match = re.search(
                r'【(?:FDA妊娠分级|妊娠分级)】\s*</dt>\s*<dd[^>]*>(.*?)</dd>',
                html, re.DOTALL | re.IGNORECASE
            )
            if pregnancy_match:
                info['pregnancy_category'] = self.clean_text(pregnancy_match.group(1))
            
            # 药代动力学
            pharma_match = re.search(
                r'【药代动力学】\s*</dt>\s*<dd[^>]*>(.*?)</dd>',
                html, re.DOTALL | re.IGNORECASE
            )
            if pharma_match:
                info['pharmacokinetics'] = self.clean_text(pharma_match.group(1))
            
            # 注意事项
            precautions_match = re.search(
                r'【注意事项】\s*</dt>\s*<dd[^>]*>(.*?)</dd>',
                html, re.DOTALL | re.IGNORECASE
            )
            if precautions_match:
                info['precautions'] = self.clean_text(precautions_match.group(1))
            
            # 检查是否获取到有效数据
            if any(v for k, v in info.items() if k != 'source'):
                return info
            
            return None
            
        except Exception as e:
            print(f"  解析出错: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符
        text = text.replace('\n', ' ').replace('\r', '').replace('\t', ' ')
        # 去除首尾空格
        text = text.strip()
        
        return text
    
    def process_drug(self, drug: Dict) -> Dict:
        """处理单个药品"""
        drug_name = drug['name']
        dosage_form = drug.get('dosage_form', '')
        
        print(f"正在查询: {drug_name} {dosage_form}")
        
        # 检查缓存
        cache_key = f"{drug_name}_{dosage_form}"
        if cache_key in self.cache:
            print("  ✓ 从缓存获取")
            drug['manual'] = self.cache[cache_key]
            return drug
        
        # 搜索药品
        detail_url = self.search_drug(drug_name, dosage_form)
        if not detail_url:
            print("  ✗ 未找到药品页面")
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
            return drug
        
        print(f"  找到详情页: {detail_url}")
        
        # 获取详情
        info = self.fetch_drug_detail(detail_url)
        time.sleep(REQUEST_DELAY)
        
        if info:
            drug['manual'] = info
            self.cache[cache_key] = info
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
            print("  ✗ 未获取到有效信息")
        
        return drug
    
    def run(self, limit: int = None, offset: int = 0):
        """运行爬虫"""
        print("="*60)
        print("药智网药品信息爬虫")
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
        
        # 处理每个药品
        success_count = 0
        for i, drug in enumerate(drugs, 1):
            print(f"\n[{i}/{len(drugs)}] ", end="")
            
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
                print(f"\n已保存进度 ({i}/{len(drugs)})")
        
        # 最终保存
        self.save_drugs(drugs)
        
        print("\n" + "="*60)
        print("爬取完成")
        print(f"成功获取: {success_count}/{len(drugs)}")
        print("="*60)


def main():
    """主函数"""
    import sys
    
    scraper = YaozhScraper()
    
    # 解析命令行参数
    limit = None
    offset = 0
    
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            pass
    
    if len(sys.argv) > 2:
        try:
            offset = int(sys.argv[2])
        except ValueError:
            pass
    
    scraper.run(limit=limit, offset=offset)


if __name__ == "__main__":
    main()
