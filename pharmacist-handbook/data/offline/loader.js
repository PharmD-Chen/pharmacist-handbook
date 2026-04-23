// 离线版数据加载器
const DrugDataLoader = {
    index: null,
    cache: {},
    
    // 加载索引
    async loadIndex() {
        if (this.index) return this.index;
        
        try {
            const response = await fetch('data/offline/drug-index.json');
            this.index = await response.json();
            return this.index;
        } catch (error) {
            console.error('加载索引失败:', error);
            // 回退到主数据文件
            return typeof drugIndex !== 'undefined' ? drugIndex : [];
        }
    },
    
    // 根据首字母加载分组数据
    async loadGroup(initial) {
        const key = initial.toUpperCase();
        
        if (this.cache[key]) return this.cache[key];
        
        try {
            const response = await fetch(`data/offline/drugs-${key}.json`);
            const data = await response.json();
            this.cache[key] = data;
            return data;
        } catch (error) {
            console.error(`加载分组 ${key} 失败:`, error);
            return [];
        }
    },
    
    // 获取单个药品详情
    async getDrugDetail(drugId) {
        // 先查找索引
        if (!this.index) {
            await this.loadIndex();
        }
        
        const drugInfo = this.index.find(d => d.id === drugId);
        if (!drugInfo) return null;
        
        // 加载对应分组
        const initial = (drugInfo.pinyin_initials || 'other')[0].toUpperCase();
        const group = await this.loadGroup(initial);
        
        return group.find(d => d.id === drugId);
    },
    
    // 搜索药品
    async searchDrugs(query) {
        if (!this.index) {
            await this.loadIndex();
        }
        
        const lowerQuery = query.toLowerCase();
        return this.index.filter(drug => {
            return (drug.name && drug.name.toLowerCase().includes(lowerQuery)) ||
                   (drug.full_name && drug.full_name.toLowerCase().includes(lowerQuery)) ||
                   (drug.pinyin && drug.pinyin.toLowerCase().includes(lowerQuery));
        });
    }
};

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DrugDataLoader };
}
