// 移动端JavaScript

// 全局变量
let html5QrCode = null;
let html5QrCodeMaintenance = null;
let currentDrug = null;
let currentDrugMaintenance = null;
let isScanning = false;
let isScanningMaintenance = false;

// API基础URL
const API_BASE = window.location.origin;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    loadShelves();
    initInventoryPage();
    initMaintenancePage();
    loadRecentRecords();
    loadRecentMaintenanceRecords();
});

// 标签页切换
function initTabs() {
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            
            // 切换标签状态
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // 切换页面
            document.querySelectorAll('.page').forEach(page => {
                page.classList.remove('active');
            });
            document.getElementById(targetTab + '-page').classList.add('active');
            
            // 停止扫码
            if (isScanning) {
                stopScan();
            }
            if (isScanningMaintenance) {
                stopScanMaintenance();
            }
        });
    });
}

// 加载货架列表
async function loadShelves() {
    try {
        const response = await fetch(`${API_BASE}/api/shelves`);
        const result = await response.json();
        
        if (result.success) {
            const select = document.getElementById('shelf-select');
            select.innerHTML = '<option value="">请选择货架</option>';
            
            result.data.forEach(shelf => {
                const option = document.createElement('option');
                option.value = shelf.id;
                option.textContent = `${shelf.name} - ${shelf.description}`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载货架失败:', error);
        showToast('加载货架失败', 'error');
    }
}

// ==================== 盘点页面功能 ====================

function initInventoryPage() {
    // 开始扫码
    document.getElementById('start-scan').addEventListener('click', startScan);
    
    // 停止扫码
    document.getElementById('stop-scan').addEventListener('click', stopScan);
    
    // 手动解析
    document.getElementById('btn-parse').addEventListener('click', () => {
        const code = document.getElementById('manual-trace-code').value.trim();
        if (code) {
            parseTraceCode(code);
        } else {
            showToast('请输入追溯码', 'error');
        }
    });
    
    // 提交盘点
    document.getElementById('btn-submit').addEventListener('click', submitInventory);
}

// 开始扫码
async function startScan() {
    try {
        html5QrCode = new Html5Qrcode("reader");
        
        await html5QrCode.start(
            { facingMode: "environment" },
            { fps: 10, qrbox: { width: 250, height: 250 } },
            onScanSuccess,
            onScanFailure
        );
        
        isScanning = true;
        document.getElementById('start-scan').style.display = 'none';
        document.getElementById('stop-scan').style.display = 'block';
        
    } catch (error) {
        console.error('启动扫码失败:', error);
        showToast('无法访问摄像头，请检查权限', 'error');
    }
}

// 停止扫码
async function stopScan() {
    if (html5QrCode && isScanning) {
        await html5QrCode.stop();
        html5QrCode = null;
        isScanning = false;
    }
    
    document.getElementById('start-scan').style.display = 'block';
    document.getElementById('stop-scan').style.display = 'none';
}

// 扫码成功回调
function onScanSuccess(decodedText, decodedResult) {
    console.log('扫码成功:', decodedText);
    
    // 停止扫码
    stopScan();
    
    // 填充到输入框
    document.getElementById('manual-trace-code').value = decodedText;
    
    // 解析追溯码
    parseTraceCode(decodedText);
    
    // 震动反馈
    if (navigator.vibrate) {
        navigator.vibrate(200);
    }
}

// 扫码失败回调
function onScanFailure(error) {
    // 静默处理，持续扫描
}

// 解析追溯码
async function parseTraceCode(traceCode) {
    showToast('正在解析...', 'success');
    
    try {
        const response = await fetch(`${API_BASE}/api/parse-trace-code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ trace_code: traceCode })
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentDrug = result.data;
            
            // 如果是新药品，先创建记录
            if (!result.exists) {
                // 显示药品信息编辑界面，让用户补充信息
                showDrugEditForm(result.data);
            } else {
                // 显示药品信息
                showDrugInfo(result.data);
            }
            
            showToast('解析成功', 'success');
        } else {
            showToast(result.message || '解析失败', 'error');
        }
    } catch (error) {
        console.error('解析追溯码失败:', error);
        showToast('解析失败，请重试', 'error');
    }
}

// 显示药品信息
function showDrugInfo(drug) {
    document.getElementById('drug-name').textContent = drug.name || '未知药品';
    document.getElementById('drug-spec').textContent = drug.specification || '-';
    document.getElementById('drug-manufacturer').textContent = drug.manufacturer || '-';
    document.getElementById('drug-batch').textContent = drug.batch_number || '-';
    document.getElementById('drug-expiry').textContent = drug.expiry_date || '-';
    
    document.getElementById('drug-info').style.display = 'block';
    document.getElementById('quantity-section').style.display = 'block';
    document.getElementById('btn-submit').disabled = false;
}

// 显示药品编辑表单（新药品）
function showDrugEditForm(drug) {
    // 简化处理：直接显示信息，让用户手动输入缺失信息
    showDrugInfo(drug);
    showToast('请补充药品信息', 'success');
}

// 数量调整
function changeQuantity(delta) {
    const input = document.getElementById('quantity');
    let value = parseInt(input.value) || 0;
    value += delta;
    if (value < 1) value = 1;
    input.value = value;
}

// 数字键盘
function appendNumber(num) {
    const input = document.getElementById('quantity');
    let value = input.value;
    if (value === '0' || value === '1') {
        value = num.toString();
    } else {
        value += num.toString();
    }
    input.value = parseInt(value) || 1;
}

function clearNumber() {
    document.getElementById('quantity').value = 1;
}

function backspaceNumber() {
    const input = document.getElementById('quantity');
    let value = input.value;
    if (value.length > 1) {
        value = value.slice(0, -1);
    } else {
        value = '1';
    }
    input.value = parseInt(value) || 1;
}

// 提交盘点
async function submitInventory() {
    const shelfId = document.getElementById('shelf-select').value;
    const quantity = parseInt(document.getElementById('quantity').value);
    const operator = document.getElementById('operator').value.trim();
    
    if (!shelfId) {
        showToast('请选择货架', 'error');
        return;
    }
    
    if (!currentDrug) {
        showToast('请先扫描或输入追溯码', 'error');
        return;
    }
    
    if (!operator) {
        showToast('请输入操作人姓名', 'error');
        return;
    }
    
    // 如果药品不存在，先创建
    let drugId = currentDrug.id;
    if (!drugId) {
        try {
            const createResponse = await fetch(`${API_BASE}/api/drugs`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentDrug)
            });
            const createResult = await createResponse.json();
            if (createResult.success) {
                drugId = createResult.data.id;
            }
        } catch (error) {
            showToast('创建药品记录失败', 'error');
            return;
        }
    }
    
    // 提交盘点记录
    try {
        const response = await fetch(`${API_BASE}/api/inventory`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                shelf_id: shelfId,
                drug_id: drugId,
                quantity: quantity,
                operator: operator
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('盘点提交成功', 'success');
            
            // 重置表单
            resetInventoryForm();
            
            // 刷新记录
            loadRecentRecords();
        } else {
            showToast(result.message || '提交失败', 'error');
        }
    } catch (error) {
        console.error('提交盘点失败:', error);
        showToast('提交失败，请重试', 'error');
    }
}

// 重置盘点表单
function resetInventoryForm() {
    document.getElementById('manual-trace-code').value = '';
    document.getElementById('quantity').value = 1;
    document.getElementById('drug-info').style.display = 'none';
    document.getElementById('quantity-section').style.display = 'none';
    document.getElementById('btn-submit').disabled = true;
    currentDrug = null;
}

// 加载最近盘点记录
async function loadRecentRecords() {
    try {
        const response = await fetch(`${API_BASE}/api/inventory/all`);
        const result = await response.json();
        
        if (result.success) {
            const container = document.getElementById('recent-records');
            
            if (result.data.length === 0) {
                container.innerHTML = '<p class="empty-tip">暂无记录</p>';
                return;
            }
            
            // 只显示最近5条
            const recent = result.data.slice(0, 5);
            
            container.innerHTML = recent.map(record => `
                <div class="record-item">
                    <div class="record-header">
                        <span class="record-title">${record.drug_name}</span>
                        <span class="record-time">${record.inventory_date.split(' ')[1]}</span>
                    </div>
                    <div class="record-details">
                        货架: ${record.shelf_name} | 数量: ${record.quantity} | 操作人: ${record.operator}
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('加载记录失败:', error);
    }
}

// ==================== 养护页面功能 ====================

function initMaintenancePage() {
    // 开始扫码
    document.getElementById('start-scan-maintenance').addEventListener('click', startScanMaintenance);
    
    // 停止扫码
    document.getElementById('stop-scan-maintenance').addEventListener('click', stopScanMaintenance);
    
    // 手动解析
    document.getElementById('btn-parse-maintenance').addEventListener('click', () => {
        const code = document.getElementById('manual-trace-code-maintenance').value.trim();
        if (code) {
            parseTraceCodeMaintenance(code);
        } else {
            showToast('请输入追溯码', 'error');
        }
    });
    
    // 添加批号
    document.getElementById('btn-add-batch').addEventListener('click', addBatchItem);
    
    // 提交养护
    document.getElementById('btn-submit-maintenance').addEventListener('click', submitMaintenance);
}

// 开始扫码（养护）
async function startScanMaintenance() {
    try {
        html5QrCodeMaintenance = new Html5Qrcode("reader-maintenance");
        
        await html5QrCodeMaintenance.start(
            { facingMode: "environment" },
            { fps: 10, qrbox: { width: 250, height: 250 } },
            onScanSuccessMaintenance,
            onScanFailureMaintenance
        );
        
        isScanningMaintenance = true;
        document.getElementById('start-scan-maintenance').style.display = 'none';
        document.getElementById('stop-scan-maintenance').style.display = 'block';
        
    } catch (error) {
        console.error('启动扫码失败:', error);
        showToast('无法访问摄像头，请检查权限', 'error');
    }
}

// 停止扫码（养护）
async function stopScanMaintenance() {
    if (html5QrCodeMaintenance && isScanningMaintenance) {
        await html5QrCodeMaintenance.stop();
        html5QrCodeMaintenance = null;
        isScanningMaintenance = false;
    }
    
    document.getElementById('start-scan-maintenance').style.display = 'block';
    document.getElementById('stop-scan-maintenance').style.display = 'none';
}

// 扫码成功回调（养护）
function onScanSuccessMaintenance(decodedText, decodedResult) {
    console.log('扫码成功:', decodedText);
    stopScanMaintenance();
    document.getElementById('manual-trace-code-maintenance').value = decodedText;
    parseTraceCodeMaintenance(decodedText);
    
    if (navigator.vibrate) {
        navigator.vibrate(200);
    }
}

// 扫码失败回调（养护）
function onScanFailureMaintenance(error) {
    // 静默处理
}

// 解析追溯码（养护）
async function parseTraceCodeMaintenance(traceCode) {
    showToast('正在解析...', 'success');
    
    try {
        const response = await fetch(`${API_BASE}/api/parse-trace-code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ trace_code: traceCode })
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentDrugMaintenance = result.data;
            
            if (!result.exists) {
                // 创建新药品
                const createResponse = await fetch(`${API_BASE}/api/drugs`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(currentDrugMaintenance)
                });
                const createResult = await createResponse.json();
                if (createResult.success) {
                    currentDrugMaintenance = createResult.data;
                }
            }
            
            showDrugInfoMaintenance(currentDrugMaintenance);
            showToast('解析成功', 'success');
        } else {
            showToast(result.message || '解析失败', 'error');
        }
    } catch (error) {
        console.error('解析追溯码失败:', error);
        showToast('解析失败，请重试', 'error');
    }
}

// 显示药品信息（养护）
function showDrugInfoMaintenance(drug) {
    document.querySelector('.drug-name-maintenance').textContent = drug.name || '未知药品';
    document.getElementById('drug-spec-maintenance').textContent = drug.specification || '-';
    document.getElementById('drug-batch-maintenance').textContent = drug.batch_number || '-';
    
    document.getElementById('drug-info-maintenance').style.display = 'block';
    document.getElementById('batch-section').style.display = 'block';
    document.getElementById('btn-submit-maintenance').disabled = false;
    
    // 添加第一个批号输入
    addBatchItem();
}

// 添加批号输入项
function addBatchItem() {
    const batchList = document.getElementById('batch-list');
    
    const batchItem = document.createElement('div');
    batchItem.className = 'batch-item';
    batchItem.innerHTML = `
        <input type="text" class="form-input batch-number" placeholder="批号">
        <input type="number" class="form-input batch-quantity" placeholder="数量" min="0">
        <button type="button" class="btn-remove-batch" onclick="this.parentElement.remove()">×</button>
    `;
    
    batchList.appendChild(batchItem);
}

// 提交养护记录
async function submitMaintenance() {
    const operator = document.getElementById('operator-maintenance').value.trim();
    const maintenanceType = document.getElementById('maintenance-type').value;
    const notes = document.getElementById('maintenance-notes').value.trim();
    
    if (!currentDrugMaintenance) {
        showToast('请先扫描或输入追溯码', 'error');
        return;
    }
    
    if (!operator) {
        showToast('请输入操作人姓名', 'error');
        return;
    }
    
    // 收集批号数据
    const batchItems = document.querySelectorAll('.batch-item');
    const batchData = [];
    
    batchItems.forEach(item => {
        const batchNumber = item.querySelector('.batch-number').value.trim();
        const quantity = parseInt(item.querySelector('.batch-quantity').value) || 0;
        
        if (batchNumber && quantity > 0) {
            batchData.push({ batchNumber, quantity });
        }
    });
    
    if (batchData.length === 0) {
        showToast('请至少输入一个批号的数量', 'error');
        return;
    }
    
    // 提交每条批号记录
    try {
        for (const batch of batchData) {
            const response = await fetch(`${API_BASE}/api/maintenance`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    drug_id: currentDrugMaintenance.id,
                    batch_number: batch.batchNumber,
                    quantity: batch.quantity,
                    maintenance_type: maintenanceType,
                    notes: notes,
                    operator: operator
                })
            });
        }
        
        showToast('养护记录提交成功', 'success');
        
        // 重置表单
        resetMaintenanceForm();
        
        // 刷新记录
        loadRecentMaintenanceRecords();
        
    } catch (error) {
        console.error('提交养护记录失败:', error);
        showToast('提交失败，请重试', 'error');
    }
}

// 重置养护表单
function resetMaintenanceForm() {
    document.getElementById('manual-trace-code-maintenance').value = '';
    document.getElementById('drug-info-maintenance').style.display = 'none';
    document.getElementById('batch-section').style.display = 'none';
    document.getElementById('batch-list').innerHTML = '';
    document.getElementById('maintenance-notes').value = '';
    document.getElementById('btn-submit-maintenance').disabled = true;
    currentDrugMaintenance = null;
}

// 加载最近养护记录
async function loadRecentMaintenanceRecords() {
    try {
        const response = await fetch(`${API_BASE}/api/maintenance/all`);
        const result = await response.json();
        
        if (result.success) {
            const container = document.getElementById('recent-maintenance-records');
            
            if (result.data.length === 0) {
                container.innerHTML = '<p class="empty-tip">暂无记录</p>';
                return;
            }
            
            // 只显示最近5条
            const recent = result.data.slice(0, 5);
            
            container.innerHTML = recent.map(record => `
                <div class="record-item">
                    <div class="record-header">
                        <span class="record-title">${record.drug_name}</span>
                        <span class="record-time">${record.maintenance_date.split(' ')[1]}</span>
                    </div>
                    <div class="record-details">
                        批号: ${record.batch_number || '-'} | 数量: ${record.quantity} | 类型: ${record.maintenance_type}
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('加载养护记录失败:', error);
    }
}

// ==================== 工具函数 ====================

// 显示提示消息
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
