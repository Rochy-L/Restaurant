// 聚香园餐厅点餐系统 - 服务员端JavaScript

let selectedTableId = null;
let selectedTableStatus = null;
let currentOrderId = null;
let allDishes = [];

// 页面加载
document.addEventListener('DOMContentLoaded', () => {
    loadTables();
    loadDishes();
});

// 加载所有桌位
async function loadTables() {
    const result = await api('/api/tables');
    if (result.success) {
        renderTablesList(result.data);
    }
}

function refreshTables() {
    loadTables();
    showToast('已刷新', 'success');
}

// 渲染桌位列表
function renderTablesList(tables) {
    const list = document.getElementById('tables-list');
    list.innerHTML = tables.map(t => `
        <div class="table-item ${selectedTableId === t.table_id ? 'selected' : ''}" 
             onclick="selectTableItem(${t.table_id}, '${t.status}', '${t.table_type}')">
            <div><strong>${t.table_id}号桌</strong> (${t.table_type})</div>
            <div class="table-status status-${t.status}">${t.status}</div>
        </div>
    `).join('');
}

// 选择桌位
async function selectTableItem(tableId, status, tableType) {
    selectedTableId = tableId;
    selectedTableStatus = status;
    
    document.querySelectorAll('.table-item').forEach(el => el.classList.remove('selected'));
    event.currentTarget.classList.add('selected');
    
    document.getElementById('no-table-selected').style.display = 'none';
    document.getElementById('table-panel').style.display = 'block';
    
    document.getElementById('selected-table-id').textContent = tableId + '号 (' + tableType + ')';
    document.getElementById('selected-table-status').textContent = status;
    
    // 根据状态显示按钮
    document.getElementById('btn-open').style.display = status === '空闲' ? '' : 'none';
    document.getElementById('btn-clean').style.display = status === '待清理' ? '' : 'none';
    
    // 加载订单信息
    if (status === '就餐中') {
        await loadCurrentOrder();
        loadConfirmedOrders();
        loadCheckoutSummary();
    }
    
    renderWaiterMenu();
}

// 开台
async function openTable() {
    const result = await api(`/api/tables/${selectedTableId}/open`, 'POST');
    if (result.success) {
        showToast('开台成功！', 'success');
        currentOrderId = result.data.order_id;
        loadTables();
        selectTableItem(selectedTableId, '就餐中', '');
    } else {
        showToast(result.error || '开台失败', 'error');
    }
}

// 清理桌台
async function cleanTable() {
    const result = await api(`/api/tables/${selectedTableId}/status`, 'PUT', { status: '空闲' });
    if (result.success) {
        showToast('清理完成！', 'success');
        loadTables();
        selectedTableId = null;
        document.getElementById('table-panel').style.display = 'none';
        document.getElementById('no-table-selected').style.display = 'block';
    } else {
        showToast(result.error || '操作失败', 'error');
    }
}

// 加载菜品
async function loadDishes() {
    const result = await api('/api/dishes?available=true');
    if (result.success) {
        allDishes = result.data;
    }
}

// 渲染菜单
function renderWaiterMenu() {
    const container = document.getElementById('waiter-menu');
    container.innerHTML = allDishes.map(d => `
        <div class="menu-item" data-category="${d.category}">
            <div class="menu-item-info">
                <h4>${d.dish_name}</h4>
                <span class="category">${d.category}</span>
                <div class="price">${formatPrice(d.price)}</div>
            </div>
            <button class="btn btn-primary btn-sm" onclick="addDish(${d.dish_id})">点菜</button>
        </div>
    `).join('');
}

// 点菜
async function addDish(dishId) {
    if (selectedTableStatus !== '就餐中') {
        showToast('请先开台', 'error');
        return;
    }
    
    const dish = allDishes.find(d => d.dish_id === dishId);
    const flavorsResult = await api(`/api/dishes/${dishId}/flavors`);
    
    if (flavorsResult.success && flavorsResult.data.length > 0) {
        showAddDishModal(dish, flavorsResult.data);
    } else {
        await submitDishOrder(dishId, [], 1);
    }
}

// 显示点菜模态框
function showAddDishModal(dish, flavorRounds) {
    let html = `<p><strong>${dish.dish_name}</strong> - ${formatPrice(dish.price)}</p>`;
    
    flavorRounds.forEach((round, idx) => {
        html += `
            <div class="form-group">
                <label>${round.round_name}</label>
                <select id="flavor-${idx}">
                    ${round.options.map(opt => `<option value="${opt}">${opt}</option>`).join('')}
                </select>
            </div>
        `;
    });
    
    html += `<div class="form-group"><label>数量</label><input type="number" id="dish-qty" value="1" min="1"></div>`;
    
    const footer = `
        <button class="btn" onclick="closeModal()">取消</button>
        <button class="btn btn-primary" onclick="confirmDishOrder(${dish.dish_id}, ${JSON.stringify(flavorRounds).replace(/"/g, '&quot;')})">确认</button>
    `;
    
    showModal('点菜 - ' + dish.dish_name, html, footer);
}

// 确认点菜
async function confirmDishOrder(dishId, flavorRounds) {
    const quantity = parseInt(document.getElementById('dish-qty').value) || 1;
    const flavors = flavorRounds.map((round, idx) => ({
        轮次: round.round_name,
        选项: document.getElementById(`flavor-${idx}`).value
    }));
    
    await submitDishOrder(dishId, flavors, quantity);
    closeModal();
}

// 提交点菜
async function submitDishOrder(dishId, flavors, quantity) {
    if (!currentOrderId) {
        await loadCurrentOrder();
    }
    
    const result = await api(`/api/orders/${currentOrderId}/items`, 'POST', {
        dish_id: dishId,
        quantity: quantity,
        flavors: flavors
    });
    
    if (result.success) {
        showToast('点菜成功！', 'success');
        loadCurrentOrderItems();
    } else {
        showToast(result.error || '点菜失败', 'error');
    }
}

// 加载当前订单
async function loadCurrentOrder() {
    const result = await api(`/api/tables/${selectedTableId}/current-order`);
    if (result.success) {
        currentOrderId = result.data.order.order_id;
        renderCurrentOrderItems(result.data.items);
    }
}

function loadCurrentOrderItems() {
    loadCurrentOrder();
}

// 渲染当前订单项
function renderCurrentOrderItems(items) {
    const container = document.getElementById('current-order-items');
    if (!items || items.length === 0) {
        container.innerHTML = '<p style="text-align:center;color:#999;">暂无待确认菜品</p>';
        return;
    }
    
    let total = 0;
    container.innerHTML = `
        <table class="data-table">
            <thead><tr><th>菜品</th><th>口味</th><th>单价</th><th>数量</th><th>小计</th></tr></thead>
            <tbody>
                ${items.map(item => {
                    const subtotal = item.unit_price * item.quantity;
                    total += subtotal;
                    return `<tr>
                        <td>${item.dishes?.dish_name || '-'}</td>
                        <td>${formatFlavors(item.flavor_choices)}</td>
                        <td>${formatPrice(item.unit_price)}</td>
                        <td>${item.quantity}</td>
                        <td>${formatPrice(subtotal)}</td>
                    </tr>`;
                }).join('')}
            </tbody>
            <tfoot><tr><td colspan="4" style="text-align:right;"><strong>合计:</strong></td><td><strong>${formatPrice(total)}</strong></td></tr></tfoot>
        </table>
    `;
}

// 确认订单
async function confirmCurrentOrder() {
    if (!currentOrderId) {
        showToast('没有待确认订单', 'error');
        return;
    }
    
    const result = await api(`/api/orders/${currentOrderId}/confirm`, 'POST');
    if (result.success) {
        showToast('订单已确认，已提交后厨！', 'success');
        currentOrderId = null;
        loadCurrentOrder();
        loadConfirmedOrders();
    } else {
        showToast(result.error || '确认失败', 'error');
    }
}

// 加载已确认订单
async function loadConfirmedOrders() {
    const result = await api(`/api/tables/${selectedTableId}/confirmed-orders`);
    const container = document.getElementById('confirmed-orders');
    
    if (!result.success || result.data.length === 0) {
        container.innerHTML = '<p style="text-align:center;color:#999;">暂无已确认订单</p>';
        return;
    }
    
    let html = '';
    result.data.forEach(orderData => {
        html += `<div class="order-group" style="margin-bottom:20px;">
            <h4>订单 #${orderData.order.order_id}</h4>
            <table class="data-table">
                <thead><tr><th>菜品</th><th>口味</th><th>数量</th><th>状态</th><th>操作</th></tr></thead>
                <tbody>`;
        
        orderData.items.forEach(item => {
            const canRefund = ['未制作', '制作中'].includes(item.dish_status);
            html += `
                <tr ${item.dish_status === '已退菜' ? 'style="opacity:0.5;text-decoration:line-through;"' : ''}>
                    <td>${item.dishes?.dish_name || '-'}</td>
                    <td>${formatFlavors(item.flavor_choices)}</td>
                    <td>${item.quantity}</td>
                    <td><span class="status-badge status-${item.dish_status}">${item.is_rushed ? '【催】' : ''}${item.dish_status}</span></td>
                    <td>
                        ${canRefund ? `<button class="btn btn-sm btn-danger" onclick="showRefundModal(${orderData.order.order_id}, ${item.dish_id}, '${item.dishes?.dish_name}')">退菜</button>` : ''}
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
    });
    
    container.innerHTML = html;
}

// 退菜
function showRefundModal(orderId, dishId, dishName) {
    const html = `
        <p>确定要退掉 <strong>${dishName}</strong> 吗？</p>
        <div class="form-group">
            <label>退菜理由（必填）</label>
            <textarea id="refund-reason" rows="3" required></textarea>
        </div>
    `;
    const footer = `
        <button class="btn" onclick="closeModal()">取消</button>
        <button class="btn btn-danger" onclick="confirmRefund(${orderId}, ${dishId})">确认退菜</button>
    `;
    showModal('退菜', html, footer);
}

async function confirmRefund(orderId, dishId) {
    const reason = document.getElementById('refund-reason').value.trim();
    if (!reason) {
        showToast('请填写退菜理由', 'error');
        return;
    }
    
    const result = await api(`/api/orders/${orderId}/items/${dishId}/refund`, 'POST', { reason });
    if (result.success) {
        showToast('退菜成功！', 'success');
        closeModal();
        loadConfirmedOrders();
        loadCheckoutSummary();
    } else {
        showToast(result.error || '退菜失败', 'error');
    }
}

// 加载结账汇总
async function loadCheckoutSummary() {
    const result = await api(`/api/tables/${selectedTableId}/confirmed-orders`);
    const container = document.getElementById('checkout-summary');
    
    if (!result.success || result.data.length === 0) {
        container.innerHTML = '<p style="text-align:center;color:#999;">暂无可结账订单</p>';
        return;
    }
    
    let total = 0;
    let html = '<h4>消费明细</h4>';
    
    result.data.forEach(orderData => {
        html += `<div><strong>订单 #${orderData.order.order_id}</strong></div><ul>`;
        orderData.items.forEach(item => {
            if (item.dish_status !== '已退菜') {
                const subtotal = item.unit_price * item.quantity;
                total += subtotal;
                html += `<li>${item.dishes?.dish_name} x${item.quantity} = ${formatPrice(subtotal)}</li>`;
            }
        });
        html += '</ul>';
    });
    
    html += `<h3 style="margin-top:20px;">总计: <span style="color:var(--primary);">${formatPrice(total)}</span></h3>`;
    container.innerHTML = html;
}

// 结账
async function doCheckout() {
    const discountRadio = document.querySelector('input[name="discount"]:checked');
    const discountType = discountRadio ? discountRadio.value : null;
    
    const result = await api(`/api/tables/${selectedTableId}/checkout`, 'POST', {
        discount_type: discountType || null
    });
    
    if (result.success) {
        const data = result.data;
        let msg = `结账成功！\n总额: ${formatPrice(data.total_amount)}`;
        if (data.discount_type) {
            msg += `\n折扣: ${data.discount_type}`;
        }
        msg += `\n实付: ${formatPrice(data.actual_amount)}`;
        
        showModal('结账成功', `
            <div style="text-align:center;">
                <h2 style="color:var(--success);">✓ 结账成功</h2>
                <p>总额: ${formatPrice(data.total_amount)}</p>
                ${data.discount_type ? `<p>折扣: ${data.discount_type}</p>` : ''}
                <h3>实付: <span style="color:var(--primary);">${formatPrice(data.actual_amount)}</span></h3>
            </div>
        `, '<button class="btn btn-primary" onclick="closeModal();loadTables();location.reload();">确定</button>');
    } else {
        showToast(result.error || '结账失败', 'error');
    }
}

// 切换标签
function switchWaiterTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
    
    if (tabName === 'current') loadCurrentOrder();
    if (tabName === 'confirmed') loadConfirmedOrders();
    if (tabName === 'checkout') loadCheckoutSummary();
}
