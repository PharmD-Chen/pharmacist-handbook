// 药品数据加载器 - 分批加载
// 生成于 2026-04-23

// 药品索引（轻量级，优先加载）
let drugIndex = [];

// 已加载的详细数据缓存
const drugDetailCache = {};

// 批次映射表（药品ID -> 批次号）
const drugBatchMap = {};

// 初始化批次映射
function initBatchMap() {
  const batchSize = 100;
  for (let i = 0; i < 1054; i++) {
    drugBatchMap[i + 1] = Math.floor(i / batchSize) + 1;
  }
}

// 加载索引
async function loadDrugIndex() {
  try {
    const response = await fetch('data/drugs/drugs_index.js');
    const text = await response.text();
    const match = text.match(/const drugIndex = (\[.*?\]);/s);
    if (match) {
      drugIndex = JSON.parse(match[1]);
      console.log('✅ 药品索引加载完成:', drugIndex.length, '条');
      initBatchMap();
      return drugIndex;
    }
  } catch (e) {
    console.error('❌ 加载药品索引失败:', e);
  }
  return [];
}

// 按需加载药品详情
async function loadDrugDetail(drugId) {
  // 检查缓存
  if (drugDetailCache[drugId]) {
    return drugDetailCache[drugId];
  }
  
  // 确定批次
  const batchNum = drugBatchMap[drugId];
  if (!batchNum) {
    console.error('未找到药品批次:', drugId);
    return null;
  }
  
  try {
    const response = await fetch(`data/drugs/drugs_detail_${batchNum}.js`);
    const text = await response.text();
    const match = text.match(/const drugDetailBatch\d+ = (\[.*?\]);/s);
    if (match) {
      const batch = JSON.parse(match[1]);
      // 缓存整个批次
      batch.forEach(drug => {
        drugDetailCache[drug.id] = drug;
      });
      return drugDetailCache[drugId];
    }
  } catch (e) {
    console.error('❌ 加载药品详情失败:', drugId, e);
  }
  return null;
}

// 预加载相邻批次（优化体验）
async function preloadAdjacentBatches(currentBatch) {
  const adjacent = [currentBatch - 1, currentBatch + 1];
  for (const batchNum of adjacent) {
    if (batchNum > 0 && batchNum <= 11 && !window[`drugDetailBatch${batchNum}`]) {
      try {
        const script = document.createElement('script');
        script.src = `data/drugs/drugs_detail_${batchNum}.js`;
        script.async = true;
        document.head.appendChild(script);
      } catch (e) {
        console.log('预加载批次失败:', batchNum);
      }
    }
  }
}

// 导出接口
window.DrugDataLoader = {
  loadIndex: loadDrugIndex,
  loadDetail: loadDrugDetail,
  preloadAdjacent: preloadAdjacentBatches,
  get index() { return drugIndex; },
  get cache() { return drugDetailCache; }
};
