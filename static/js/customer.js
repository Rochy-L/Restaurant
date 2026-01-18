// 聚香园餐厅点餐系统 - 顾客端JavaScript

let currentTableId = null;
let currentOrderId = null;
let cart = []; // 购物车
let allDishes = [];

// 页面加载
document.addEventListener('DOMContentLoaded', () => {
    loadAvailableTables();
    loadDishes();
});

// 加载空闲桌位
async function loadAvailableTables() {
    const result = await api('/api/tables/available');
    if (result.success) {
        renderTables(result.data);
    }
}

// 渲染桌位
function renderTables(tables) {
    const grid = document.getElementById('tables-grid');
    if (tables.length === 0) {
        grid.innerHTML = '<p style="text-align:center;color:#999;">暂无空闲桌位</p>';
        return;
    }
    
    grid.innerHTML = tables.map(t => `
        <div class="table-card" onclick="selectTable(${t.table_id}, '${t.table_type}')">
            <div class="table-id">${t.table_id}号桌</div>
            <div class="table-type">${t.table_type} (${t.capacity}人)</div>
            <div class="table-status status-${t.status}">${t.status}</div>
        </div>
    `).join('');
}

// 选择桌位（开台）
async function selectTable(tableId, tableType) {
    const result = await api(`/api/tables/${tableId}/open`, 'POST');
    if (result.success) {
        currentTableId = tableId;
        currentOrderId = result.data.order_id;
        
        document.getElementById('bind-section').style.display = 'none';
        document.getElementById('order-section').style.display = 'block';
        document.getElementById('current-table').textContent = `${tableId}号桌 (${tableType})`;
        
        showToast('开台成功！', 'success');
        loadCurrentOrder();
    } else {
        showToast(result.error || '开台失败', 'error');
    }
}

// 解绑桌位
function unbindTable() {
    currentTableId = null;
    currentOrderId = null;
    cart = [];
    
    document.getElementById('bind-section').style.display = 'block';
    document.getElementById('order-section').style.display = 'none';
    
    loadAvailableTables();
}

// 加载菜品
async function loadDishes() {
    const result = await api('/api/dishes?available=true');
    if (result.success) {
        allDishes = result.data;
        renderMenu(allDishes);
    }
}

// 渲染菜单
function renderMenu(dishes) {
    const list = document.getElementById('menu-list');
    list.innerHTML = dishes.map(d => `
        <div class="menu-item" data-category="${d.category}" data-id="${d.dish_id}">
            <div class="menu-item-info">
                <h4>${d.dish_name}</h4>
                <span class="category">${d.category}</span>
                <div class="price">${formatPrice(d.price)}</div>
            </div>
            <div class="menu-item-actions">
                <button class="btn btn-primary btn-sm" onclick="addToCart(${d.dish_id})">加入</button>
            </div>
        </div>
    `).join('');
}

// 分类过滤
function filterCategory(category) {
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    document.querySelectorAll('.menu-item').forEach(item => {
        if (category === 'all' || item.dataset.category === category) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// 加入购物车
async function addToCart(dishId) {
    const dish = allDishes.find(d => d.dish_id === dishId);
    if (!dish) return;
    
    // 获取口味选项
    const flavorsResult = await api(`/api/dishes/${dishId}/flavors`);
    
    if (flavorsResult.success && flavorsResult.data.length > 0) {
        // 有口味选项，显示选择框
        showFlavorModal(dish, flavorsResult.data);
    } else {
        // 无口味选项，直接加入
        addItemToCart(dish, []);
    }
}

// 显示口味选择模态框
function showFlavorModal(dish, flavorRounds) {
    let html = `<p><strong>${dish.dish_name}</strong> - ${formatPrice(dish.price)}</p>`;
    
    flavorRounds.forEach((round, idx) => {
        html += `
            <div class="form-group">
                <label>${round.round_name}</label>
                <select id="flavor-${idx}" required>
                    ${round.options.map(opt => `<option value="${opt}">${opt}</option>`).join('')}
                </select>
            </div>
        `;
    });
    
    html += `
        <div class="form-group">
            <label>数量</label>
            <input type="number" id="dish-qty" value="1" min="1" max="99">
        </div>
    `;
    
    const footer = `
        <button class="btn" onclick="closeModal()">取消</button>
        <button class="btn btn-primary" onclick="confirmAddToCart(${dish.dish_id}, ${JSON.stringify(flavorRounds).replace(/"/g, '&quot;')})">确认</button>
    `;
    
    showModal('选择口味', html, footer);
}

// 确认加入购物车
function confirmAddToCart(dishId, flavorRounds) {
    const dish = allDishes.find(d => d.dish_id === dishId);
    const quantity = parseInt(document.getElementById('dish-qty').value) || 1;
    
    const flavors = flavorRounds.map((round, idx) => ({
        轮次: round.round_name,
        选项: document.getElementById(`flavor-${idx}`).value
    }));
    
    addItemToCart(dish, flavors, quantity);
    closeModal();
}

// 添加到购物车
function addItemToCart(dish, flavors, quantity = 1) {
    cart.push({
        dish_id: dish.dish_id,
        dish_name: dish.dish_name,
        price: dish.price,
        quantity: quantity,
        flavors: flavors
    });
    
    updateCartDisplay();
    showToast(`已添加 ${dish.dish_name}`, 'success');
}

// 更新购物车显示
function updateCartDisplay() {
    const count = cart.reduce((sum, item) => sum + item.quantity, 0);
    document.getElementById('cart-count').textContent = count;
    
    const list = document.getElementById('cart-list');
    if (cart.length === 0) {
        list.innerHTML = '<p style="text-align:center;color:#999;">购物车为空</p>';
        document.getElementById('cart-total').textContent = '¥0.00';
        return;
    }
    
    let total = 0;
    list.innerHTML = cart.map((item, idx) => {
        const subtotal = item.price * item.quantity;
        total += subtotal;
        const flavorStr = item.flavors.length > 0 
            ? item.flavors.map(f => `${f.轮次}:${f.选项}`).join(', ')
            : '';
        return `
            <div class="cart-item">
                <div>
                    <strong>${item.dish_name}</strong> x${item.quantity}
                    ${flavorStr ? `<br><small style="color:#999;">${flavorStr}</small>` : ''}
                </div>
                <div>
                    <span>${formatPrice(subtotal)}</span>
                    <button class="btn btn-sm btn-danger" onclick="removeFromCart(${idx})">删除</button>
                </div>
            </div>
        `;
    }).join('');
    
    document.getElementById('cart-total').textContent = formatPrice(total);
}

// 从购物车删除
function removeFromCart(index) {
    cart.splice(index, 1);
    updateCartDisplay();
}

// 切换标签
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
    
    if (tabName === 'orders') {
        loadConfirmedOrders();
    }
}

// 提交订单
async function submitOrder() {
    if (cart.length === 0) {
        showToast('购物车为空', 'error');
        return;
    }
    
    // 逐个添加菜品到订单
    for (const item of cart) {
        await api(`/api/orders/${currentOrderId}/items`, 'POST', {
            dish_id: item.dish_id,
            quantity: item.quantity,
            flavors: item.flavors
        });
    }
    
    cart = [];
    updateCartDisplay();
    showToast('已提交，请等待服务员确认', 'success');
    loadCurrentOrder();
}

// 加载当前订单
async function loadCurrentOrder() {
    if (!currentTableId) return;
    
    const result = await api(`/api/tables/${currentTableId}/current-order`);
    if (result.success) {
        currentOrderId = result.data.order.order_id;
    }
}

// 加载已确认订单
async function loadConfirmedOrders() {
    if (!currentTableId) return;
    
    const result = await api(`/api/tables/${currentTableId}/confirmed-orders`);
    const list = document.getElementById('orders-list');
    
    if (!result.success || result.data.length === 0) {
        list.innerHTML = '<p style="text-align:center;color:#999;">暂无已确认订单</p>';
        return;
    }
    
    let html = '';
    result.data.forEach(orderData => {
        html += `<div class="order-group">
            <h4>订单 #${orderData.order.order_id}</h4>
            <table class="data-table">
                <thead><tr><th>菜品</th><th>口味</th><th>数量</th><th>状态</th><th>操作</th></tr></thead>
                <tbody>`;
        
        orderData.items.forEach(item => {
            const canRush = ['未制作', '制作中'].includes(item.dish_status) && !item.is_rushed;
            html += `
                <tr>
                    <td>${item.dishes?.dish_name || '-'}</td>
                    <td>${formatFlavors(item.flavor_choices)}</td>
                    <td>${item.quantity}</td>
                    <td><span class="status-badge status-${item.dish_status}">${item.is_rushed ? '【催】' : ''}${item.dish_status}</span></td>
                    <td>
                        ${canRush ? `<button class="btn btn-sm btn-warning" onclick="rushDish(${orderData.order.order_id}, ${item.dish_id})">催菜</button>` : ''}
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
    });
    
    list.innerHTML = html;
}

// 催菜
async function rushDish(orderId, dishId) {
    const result = await api(`/api/orders/${orderId}/items/${dishId}/rush`, 'POST');
    if (result.success) {
        showToast('催菜成功！', 'success');
        loadConfirmedOrders();
    } else {
        showToast(result.error || '催菜失败', 'error');
    }
}
