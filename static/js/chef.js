// 聚香园餐厅点餐系统 - 后厨端JavaScript

let currentStation = 'all';

// 页面加载
document.addEventListener('DOMContentLoaded', () => {
    loadKitchenOrders();
    // 每30秒自动刷新
    setInterval(loadKitchenOrders, 30000);
});

// 切换工作站
function switchStation(station) {
    currentStation = station;
    document.querySelectorAll('.station-tab').forEach(el => el.classList.remove('active'));
    event.target.classList.add('active');
    loadKitchenOrders();
}

// 刷新订单
function refreshOrders() {
    loadKitchenOrders();
    showToast('已刷新', 'success');
}

// 加载后厨订单
async function loadKitchenOrders() {
    const result = await api(`/api/kitchen/orders?station=${currentStation}`);
    const container = document.getElementById('kitchen-orders');
    
    if (!result.success) {
        container.innerHTML = '<p style="text-align:center;color:#999;">加载失败</p>';
        return;
    }
    
    const orders = result.data;
    
    if (orders.length === 0) {
        container.innerHTML = '<p style="text-align:center;color:#999;padding:50px;">暂无待处理订单</p>';
        return;
    }
    
    container.innerHTML = orders.map(item => {
        const isRushed = item.is_rushed;
        const orderId = item.orders?.order_id || item.order_id;
        const tableId = item.orders?.table_id || '-';
        const dishName = item.dishes?.dish_name || '-';
        const category = item.dishes?.category || '-';
        
        return `
            <div class="kitchen-order-card ${isRushed ? 'rushed' : ''}">
                <div class="order-card-header">
                    <span class="order-id">订单 #${orderId}</span>
                    <span class="table-id">${tableId}号桌</span>
                </div>
                <div class="dish-name">${dishName}</div>
                <div class="dish-info">
                    <span>${category}</span> | 
                    <span>数量: ${item.quantity}</span>
                    ${item.flavor_choices ? `<br>口味: ${formatFlavors(item.flavor_choices)}` : ''}
                </div>
                <div>
                    <span class="status-badge status-${item.dish_status}">${item.dish_status}</span>
                    ${isRushed ? '<span style="color:var(--warning);font-weight:bold;margin-left:10px;">🔔 催菜!</span>' : ''}
                </div>
                <div class="order-card-actions">
                    ${item.dish_status === '未制作' ? `
                        <button class="btn btn-warning btn-sm" onclick="updateStatus(${orderId}, ${item.dish_id}, '制作中')">开始制作</button>
                        <button class="btn btn-success btn-sm" onclick="updateStatus(${orderId}, ${item.dish_id}, '已完成')">直接完成</button>
                    ` : ''}
                    ${item.dish_status === '制作中' ? `
                        <button class="btn btn-success" onclick="updateStatus(${orderId}, ${item.dish_id}, '已完成')">完成出餐</button>
                    ` : ''}
                    ${item.dish_status === '已完成' ? `<span style="color:var(--success);">✓ 已出餐</span>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

// 更新菜品状态
async function updateStatus(orderId, dishId, newStatus) {
    const result = await api(`/api/kitchen/items/${orderId}/${dishId}/status`, 'PUT', {
        status: newStatus
    });
    
    if (result.success) {
        showToast(`状态已更新为: ${newStatus}`, 'success');
        loadKitchenOrders();
    } else {
        showToast(result.error || '更新失败', 'error');
    }
}
