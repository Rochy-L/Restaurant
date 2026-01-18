// 聚香园餐厅点餐系统 - 经理端JavaScript

let allDishes = [];
let currentCategory = 'all';

// 页面加载
document.addEventListener('DOMContentLoaded', () => {
    loadAllDishes();
    loadRevenue();
});

// 切换标签
function switchManagerTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
    
    if (tabName === 'revenue') loadRevenue();
}

// ========== 菜品管理 ==========

// 加载所有菜品
async function loadAllDishes() {
    const result = await api('/api/dishes?available=false');
    if (result.success) {
        allDishes = result.data;
        renderDishesTable();
    }
}

// 渲染菜品表格
function renderDishesTable() {
    const tbody = document.getElementById('dishes-table');
    const filteredDishes = currentCategory === 'all' 
        ? allDishes 
        : allDishes.filter(d => d.category === currentCategory);
    
    tbody.innerHTML = filteredDishes.map(d => `
        <tr>
            <td>${d.dish_id}</td>
            <td>${d.dish_name}</td>
            <td>${d.category}</td>
            <td>${formatPrice(d.price)}</td>
            <td><span style="color:${d.is_available ? 'var(--success)' : 'var(--danger)'}">${d.is_available ? '上架' : '已下架'}</span></td>
            <td>
                ${d.is_available ? `<button class="btn btn-sm btn-danger" onclick="deleteDish(${d.dish_id}, '${d.dish_name}')">下架</button>` : ''}
            </td>
        </tr>
    `).join('');
}

// 过滤菜品
function filterDishes(category) {
    currentCategory = category;
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    renderDishesTable();
}

// 显示添加菜品模态框
function showAddDishModal() {
    document.getElementById('dish-name').value = '';
    document.getElementById('dish-category').value = '热菜';
    document.getElementById('dish-price').value = '';
    document.getElementById('flavor-rounds').innerHTML = '';
    document.getElementById('add-dish-modal').classList.add('show');
}

function closeAddDishModal() {
    document.getElementById('add-dish-modal').classList.remove('show');
}

// 添加口味轮次
let flavorRoundCount = 0;
function addFlavorRound() {
    flavorRoundCount++;
    const container = document.getElementById('flavor-rounds');
    const roundDiv = document.createElement('div');
    roundDiv.className = 'flavor-round-item';
    roundDiv.style.cssText = 'border:1px solid #ddd;padding:10px;margin:10px 0;border-radius:5px;';
    roundDiv.innerHTML = `
        <div class="form-group">
            <label>轮次${flavorRoundCount}名称 (如: 辣度、温度)</label>
            <input type="text" class="round-name" required>
        </div>
        <div class="form-group">
            <label>选项 (用逗号分隔，如: 微辣,中辣,特辣)</label>
            <input type="text" class="round-options" required>
        </div>
        <button type="button" class="btn btn-sm btn-danger" onclick="this.parentElement.remove()">删除此轮</button>
    `;
    container.appendChild(roundDiv);
}

// 提交添加菜品
async function submitDish() {
    const name = document.getElementById('dish-name').value.trim();
    const category = document.getElementById('dish-category').value;
    const price = parseFloat(document.getElementById('dish-price').value);
    
    if (!name || !price) {
        showToast('请填写完整信息', 'error');
        return;
    }
    
    // 收集口味轮次
    const flavorRounds = [];
    document.querySelectorAll('.flavor-round-item').forEach(item => {
        const roundName = item.querySelector('.round-name').value.trim();
        const optionsStr = item.querySelector('.round-options').value.trim();
        if (roundName && optionsStr) {
            flavorRounds.push({
                name: roundName,
                options: optionsStr.split(',').map(s => s.trim()).filter(s => s)
            });
        }
    });
    
    const result = await api('/api/dishes', 'POST', {
        dish_name: name,
        category: category,
        price: price,
        flavor_rounds: flavorRounds
    });
    
    if (result.success) {
        showToast('菜品添加成功！', 'success');
        closeAddDishModal();
        flavorRoundCount = 0;
        loadAllDishes();
    } else {
        showToast(result.error || '添加失败', 'error');
    }
}

// 下架菜品
async function deleteDish(dishId, dishName) {
    if (!confirm(`确定要下架【${dishName}】吗？\n\n注意：下架后该菜品及其口味选项将被永久删除！`)) {
        return;
    }
    
    const result = await api(`/api/dishes/${dishId}`, 'DELETE');
    if (result.success) {
        showToast('菜品已下架', 'success');
        loadAllDishes();
    } else {
        showToast(result.error || '操作失败', 'error');
    }
}

// ========== 营收统计 ==========

async function loadRevenue() {
    const result = await api('/api/revenue');
    
    if (!result.success) {
        showToast('加载营收数据失败', 'error');
        return;
    }
    
    const data = result.data;
    
    // 更新汇总卡片
    document.getElementById('bill-count').textContent = data.bills.length;
    document.getElementById('total-sum').textContent = formatPrice(data.total_sum);
    document.getElementById('actual-sum').textContent = formatPrice(data.actual_sum);
    document.getElementById('discount-sum').textContent = formatPrice(data.total_sum - data.actual_sum);
    
    // 渲染账单列表
    const container = document.getElementById('bills-list');
    
    if (data.bills.length === 0) {
        container.innerHTML = '<p style="text-align:center;color:#999;padding:30px;">暂无账单记录</p>';
        return;
    }
    
    container.innerHTML = data.bills.map(bill => `
        <div class="bill-item" onclick="this.classList.toggle('expanded')">
            <div class="bill-header">
                <div>
                    <strong>账单 #${bill.bill_id}</strong>
                    <span style="margin-left:15px;">${bill.table_id}号桌</span>
                    <span style="margin-left:15px;color:#999;">${bill.settled_at ? new Date(bill.settled_at).toLocaleString() : '-'}</span>
                </div>
                <div>
                    ${bill.discount_type ? `<span style="color:var(--warning);">${bill.discount_type}</span>` : ''}
                    <strong style="margin-left:15px;color:var(--primary);">${formatPrice(bill.actual_amount)}</strong>
                </div>
            </div>
            <div class="bill-details">
                ${bill.orders.map(order => `
                    <div style="margin-bottom:10px;">
                        <strong>订单 #${order.order_id}</strong>
                        <ul>
                            ${order.items.map(item => `
                                <li>${item.dishes?.dish_name || '-'} x${item.quantity} = ${formatPrice(item.unit_price * item.quantity)}</li>
                            `).join('')}
                        </ul>
                    </div>
                `).join('')}
                <div style="border-top:1px solid #ddd;padding-top:10px;margin-top:10px;">
                    <span>原价: ${formatPrice(bill.total_amount)}</span>
                    ${bill.discount_type ? `<span style="margin-left:15px;">折扣: ${bill.discount_type}</span>` : ''}
                    <strong style="margin-left:15px;">实付: ${formatPrice(bill.actual_amount)}</strong>
                </div>
            </div>
        </div>
    `).join('');
}
