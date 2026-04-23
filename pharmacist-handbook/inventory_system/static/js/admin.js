// 管理后台JavaScript

const API_BASE = window.location.origin;
let currentPage = 1;
let inventoryData = [];
let maintenanceData = [];
let inventoryChart = null;
let shelfChart = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    loadStatistics();
    loadShelves();
    loadInventoryRecords();
    loadMaintenanceRecords();
    initMobilePage();
});

// 导航切换
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const targetPage = this.dataset.page;
            
            // 更新导航状态
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
            
            // 切换页面
            document.querySelectorAll('.page').forEach(page => {
                page.classList.remove('active');
            });
            document.getElementById('page-' + targetPage).classList.add('active');
            
            // 更新标题
            const titles = {
                'dashboard': '数据概览',
                'inventory': '盘点记录',
                'maintenance': '养护记录',
                'shelves': '货架管理',
                'mobile': '移动端入口'
            };
            document.getElementById('page-title').textContent = titles[targetPage];
        });
    });
}

// 加载统计数据
async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE}/api/statistics`);
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            document.getElementById('stat-total-inventory').textContent = data.total_inventory;
            document.getElementById('stat-today-inventory').textContent = data.today_inventory;
            document.getElementById('stat-total-maintenance').textContent = data.total_maintenance;
            document.getElementById('stat-total-shelves').textContent = data.total_shelves;
            
            // 加载图表数据
            loadChartsData();
            // 加载最近记录
            loadRecentInventory();
        }
    } catch (error) {
        console.error('加载统计数据失败:', error);
    }
}

// 加载图表数据
async function loadChartsData() {
    try {
        // 获取盘点记录
        const response = await fetch(`${API_BASE}/api/inventory/all`);
        const result = await response.json();
        
        if (result.success) {
            const records = result.data;
            
            // 处理最近7天的数据
            const last7Days = getLast7Days();
            const dailyCounts = last7Days.map(date => {
                return records.filter(r => r.inventory_date.startsWith(date)).length;
            });
            
            // 初始化盘点趋势图
            const ctx1 = document.getElementById('inventoryChart').getContext('2d');
            if (inventoryChart) {
                inventoryChart.destroy();
            }
            inventoryChart = new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: last7Days.map(d => d.slice(5)), // 只显示月-日
                    datasets: [{
                        label: '盘点数量',
                        data: dailyCounts,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });
            
            // 处理货架分布数据
            const shelfCounts = {};
            records.forEach(r => {
                shelfCounts[r.shelf_name] = (shelfCounts[r.shelf_name] || 0) + 1;
            });
            
            const ctx2 = document.getElementById('shelfChart').getContext('2d');
            if (shelfChart) {
                shelfChart.destroy();
            }
            shelfChart = new Chart(ctx2, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(shelfCounts),
                    datasets: [{
                        data: Object.values(shelfCounts),
                        backgroundColor: [
                            '#667eea', '#11998e', '#f093fb', '#f5576c', 
                            '#ffd93d', '#6bcf7f', '#4d96ff', '#ff6b6b'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right'
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('加载图表数据失败:', error);
    }
}

// 获取最近7天日期
function getLast7Days() {
    const dates = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        dates.push(date.toISOString().split('T')[0]);
    }
    return dates;
}

// 加载最近盘点记录
async function loadRecentInventory() {
    try {
        const response = await fetch(`${API_BASE}/api/inventory/all`);
        const result = await response.json();
        
        if (result.success) {
            const tbody = document.getElementById('recent-inventory-tbody');
            const recent = result.data.slice(0, 5);
            
            if (recent.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="loading-cell">暂无记录</td></tr>';
                return;
            }
            
            tbody.innerHTML = recent.map(record => `
                <tr>
                    <td>${record.inventory_date}</td>
                    <td>${record.shelf_name}</td>
                    <td>${record.drug_name}</td>
                    <td>${record.specification || '-'}</td>
                    <td>${record.batch_number || '-'}</td>
                    <td>${record.quantity}</td>
                    <td>${record.operator}</td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('加载最近记录失败:', error);
    }
}

// 加载货架列表
async function loadShelves() {
    try {
        const response = await fetch(`${API_BASE}/api/shelves`);
        const result = await response.json();
        
        if (result.success) {
            // 更新筛选下拉框
            const filterSelect = document.getElementById('filter-shelf');
            filterSelect.innerHTML = '<option value="">全部货架</option>';
            
            result.data.forEach(shelf => {
                const option = document.createElement('option');
                option.value = shelf.id;
                option.textContent = `${shelf.name} - ${shelf.description}`;
                filterSelect.appendChild(option);
            });
            
            // 更新货架管理表格
            const tbody = document.getElementById('shelves-tbody');
            tbody.innerHTML = result.data.map(shelf => `
                <tr>
                    <td>${shelf.id}</td>
                    <td>${shelf.name}</td>
                    <td>${shelf.description || '-'}</td>
                    <td>${shelf.created_at}</td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="deleteShelf(${shelf.id})">删除</button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('加载货架失败:', error);
    }
}

// 加载盘点记录
async function loadInventoryRecords() {
    try {
        const response = await fetch(`${API_BASE}/api/inventory/all`);
        const result = await response.json();
        
        if (result.success) {
            inventoryData = result.data;
            renderInventoryTable(inventoryData);
        }
    } catch (error) {
        console.error('加载盘点记录失败:', error);
    }
}

// 渲染盘点表格
function renderInventoryTable(data) {
    const tbody = document.getElementById('inventory-tbody');
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="loading-cell">暂无记录</td></tr>';
        return;
    }
    
    tbody.innerHTML = data.map(record => `
        <tr>
            <td>${record.id}</td>
            <td>${record.inventory_date}</td>
            <td>${record.shelf_name}</td>
            <td>${record.drug_name}</td>
            <td>${record.specification || '-'}</td>
            <td>${record.batch_number || '-'}</td>
            <td>${record.quantity}</td>
            <td>${record.operator}</td>
        </tr>
    `).join('');
}

// 加载养护记录
async function loadMaintenanceRecords() {
    try {
        const response = await fetch(`${API_BASE}/api/maintenance/all`);
        const result = await response.json();
        
        if (result.success) {
            maintenanceData = result.data;
            renderMaintenanceTable(maintenanceData);
        }
    } catch (error) {
        console.error('加载养护记录失败:', error);
    }
}

// 渲染养护表格
function renderMaintenanceTable(data) {
    const tbody = document.getElementById('maintenance-tbody');
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="loading-cell">暂无记录</td></tr>';
        return;
    }
    
    tbody.innerHTML = data.map(record => `
        <tr>
            <td>${record.id}</td>
            <td>${record.maintenance_date}</td>
            <td>${record.drug_name}</td>
            <td>${record.specification || '-'}</td>
            <td>${record.batch_number || '-'}</td>
            <td>${record.quantity}</td>
            <td>${record.maintenance_type}</td>
            <td>${record.operator}</td>
            <td>${record.notes || '-'}</td>
        </tr>
    `).join('');
}

// 筛选盘点记录
function filterInventory() {
    const shelfId = document.getElementById('filter-shelf').value;
    const date = document.getElementById('filter-date').value;
    
    let filtered = inventoryData;
    
    if (shelfId) {
        filtered = filtered.filter(r => r.shelf_id === parseInt(shelfId));
    }
    
    if (date) {
        filtered = filtered.filter(r => r.inventory_date.startsWith(date));
    }
    
    renderInventoryTable(filtered);
}

// 筛选养护记录
function filterMaintenance() {
    const type = document.getElementById('filter-maintenance-type').value;
    
    let filtered = maintenanceData;
    
    if (type) {
        filtered = filtered.filter(r => r.maintenance_type === type);
    }
    
    renderMaintenanceTable(filtered);
}

// 导出盘点记录
function exportInventory() {
    const csvContent = convertToCSV(inventoryData);
    downloadCSV(csvContent, '盘点记录.csv');
}

// 导出养护记录
function exportMaintenance() {
    const csvContent = convertToCSV(maintenanceData);
    downloadCSV(csvContent, '养护记录.csv');
}

// 转换为CSV
function convertToCSV(data) {
    if (data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const rows = data.map(obj => headers.map(h => obj[h] || '').join(','));
    return [headers.join(','), ...rows].join('\n');
}

// 下载CSV
function downloadCSV(content, filename) {
    const blob = new Blob(['\ufeff' + content], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

// 显示添加货架弹窗
function showAddShelfModal() {
    document.getElementById('add-shelf-modal').classList.add('show');
}

// 关闭弹窗
function closeModal() {
    document.getElementById('add-shelf-modal').classList.remove('show');
    // 清空输入
    document.getElementById('new-shelf-name').value = '';
    document.getElementById('new-shelf-desc').value = '';
}

// 添加货架
async function addShelf() {
    const name = document.getElementById('new-shelf-name').value.trim();
    const description = document.getElementById('new-shelf-desc').value.trim();
    
    if (!name) {
        alert('请输入货架编号');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/shelves`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('货架添加成功');
            closeModal();
            loadShelves();
            loadStatistics();
        } else {
            alert(result.message || '添加失败');
        }
    } catch (error) {
        console.error('添加货架失败:', error);
        alert('添加失败，请重试');
    }
}

// 删除货架
async function deleteShelf(id) {
    if (!confirm('确定要删除这个货架吗？')) {
        return;
    }
    
    // TODO: 实现删除API
    alert('删除功能开发中...');
}

// 刷新数据
function refreshData() {
    loadStatistics();
    loadInventoryRecords();
    loadMaintenanceRecords();
    loadShelves();
    alert('数据已刷新');
}

// 分页
function changePage(delta) {
    currentPage += delta;
    if (currentPage < 1) currentPage = 1;
    document.getElementById('page-info').textContent = `第 ${currentPage} 页`;
}

// 初始化移动端页面
function initMobilePage() {
    // 获取本机IP
    fetch(`${API_BASE}/api/shelves`)
        .then(() => {
            // 生成二维码
            const mobileUrl = `${API_BASE}/mobile`;
            document.getElementById('mobile-url').textContent = mobileUrl;
            
            // 使用QRCode.js生成二维码
            new QRCode(document.getElementById('qrcode'), {
                text: mobileUrl,
                width: 200,
                height: 200,
                colorDark: '#2c3e50',
                colorLight: '#ffffff',
                correctLevel: QRCode.CorrectLevel.M
            });
            
            // 显示网络信息
            document.getElementById('network-info').innerHTML = `
                <strong>服务器地址：</strong>${window.location.hostname}<br>
                <strong>访问端口：</strong>5000<br>
                <strong>移动端地址：</strong>${mobileUrl}
            `;
        })
        .catch(error => {
            console.error('获取网络信息失败:', error);
            document.getElementById('network-info').textContent = '无法获取网络信息';
        });
}
