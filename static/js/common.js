// 聚香园餐厅点餐系统 - 公共JavaScript

// API请求封装
async function api(url, method = 'GET', data = null) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (data) {
        options.body = JSON.stringify(data);
    }
    try {
        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, error: error.message };
    }
}

// Toast提示
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = 'toast show ' + type;
    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}

// 模态框
function showModal(title, body, footer = '') {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = body;
    document.getElementById('modal-footer').innerHTML = footer;
    document.getElementById('modal').classList.add('show');
}

function closeModal() {
    document.getElementById('modal').classList.remove('show');
}

// 格式化价格
function formatPrice(price) {
    return '¥' + parseFloat(price).toFixed(2);
}

// 格式化口味选择
function formatFlavors(flavorsJson) {
    if (!flavorsJson) return '-';
    try {
        const flavors = JSON.parse(flavorsJson);
        if (!flavors || flavors.length === 0) return '-';
        return flavors.map(f => `${f.轮次}:${f.选项}`).join(', ');
    } catch {
        return '-';
    }
}

// 通用标签页切换
function switchTabGeneric(tabName, prefix = '') {
    // 隐藏所有标签内容
    document.querySelectorAll('.tab-content').forEach(el => {
        el.classList.remove('active');
    });
    // 移除所有标签的active状态
    document.querySelectorAll('.tab').forEach(el => {
        el.classList.remove('active');
    });
    
    // 显示选中的标签内容
    const tabContent = document.getElementById(prefix + tabName + '-tab');
    if (tabContent) {
        tabContent.classList.add('active');
    }
    
    // 设置标签active状态
    event.target.classList.add('active');
}

// 分类过滤通用函数
function filterByCategory(category, containerSelector, itemSelector, categoryAttr = 'data-category') {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    document.querySelectorAll(itemSelector).forEach(item => {
        if (category === 'all' || item.getAttribute(categoryAttr) === category) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}
