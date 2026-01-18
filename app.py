"""
聚香园餐厅点餐系统 - Flask Web应用
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime

# 导入数据库模块
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import database as db

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# ============================================
# 页面路由
# ============================================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/customer')
def customer_page():
    """顾客页面"""
    return render_template('customer.html')

@app.route('/waiter')
def waiter_page():
    """服务员页面"""
    return render_template('waiter.html')

@app.route('/chef')
def chef_page():
    """后厨页面"""
    return render_template('chef.html')

@app.route('/manager')
def manager_page():
    """经理页面"""
    return render_template('manager.html')

# ============================================
# API路由 - 桌台管理
# ============================================

@app.route('/api/tables', methods=['GET'])
def get_tables():
    """获取所有桌台"""
    try:
        tables = db.get_all_tables()
        return jsonify({'success': True, 'data': tables})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tables/available', methods=['GET'])
def get_available_tables():
    """获取空闲桌台"""
    try:
        tables = db.get_available_tables()
        return jsonify({'success': True, 'data': tables})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tables/<int:table_id>/status', methods=['PUT'])
def update_table_status(table_id):
    """更新桌台状态"""
    try:
        data = request.json
        status = data.get('status')
        db.update_table_status(table_id, status)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tables/<int:table_id>/open', methods=['POST'])
def open_table(table_id):
    """开台"""
    try:
        table = db.get_table_by_id(table_id)
        if not table:
            return jsonify({'success': False, 'error': '桌位不存在'})
        if table['status'] != '空闲':
            return jsonify({'success': False, 'error': f'桌位状态为{table["status"]}，无法开台'})
        
        db.update_table_status(table_id, '就餐中')
        bill = db.create_bill(table_id)
        order = db.create_order(table_id, bill['bill_id'])
        
        return jsonify({
            'success': True, 
            'data': {
                'table_id': table_id,
                'bill_id': bill['bill_id'],
                'order_id': order['order_id']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============================================
# API路由 - 菜品管理
# ============================================

@app.route('/api/dishes', methods=['GET'])
def get_dishes():
    """获取所有菜品"""
    try:
        available_only = request.args.get('available', 'true').lower() == 'true'
        if available_only:
            dishes = db.get_available_dishes()
        else:
            dishes = db.get_all_dishes()
        return jsonify({'success': True, 'data': dishes})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dishes/<int:dish_id>/flavors', methods=['GET'])
def get_dish_flavors(dish_id):
    """获取菜品口味选项"""
    try:
        rounds = db.get_flavor_rounds_by_dish(dish_id)
        result = []
        for r in rounds:
            options = db.get_flavor_options_by_round(r['round_id'])
            result.append({
                'round_id': r['round_id'],
                'round_number': r['round_number'],
                'round_name': r['round_name'],
                'options': [o['option_name'] for o in options]
            })
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dishes', methods=['POST'])
def add_dish():
    """添加菜品"""
    try:
        data = request.json
        dish = db.add_dish(data['dish_name'], data['category'], data['price'])
        
        # 添加口味选项
        if 'flavor_rounds' in data:
            for i, round_data in enumerate(data['flavor_rounds'], 1):
                flavor_round = db.add_flavor_round(dish['dish_id'], i, round_data['name'])
                for option in round_data['options']:
                    db.add_flavor_option(flavor_round['round_id'], option)
        
        return jsonify({'success': True, 'data': dish})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dishes/<int:dish_id>', methods=['DELETE'])
def delete_dish(dish_id):
    """下架菜品"""
    try:
        db.remove_dish(dish_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============================================
# API路由 - 订单管理
# ============================================

@app.route('/api/tables/<int:table_id>/current-order', methods=['GET'])
def get_current_order(table_id):
    """获取当前订单"""
    try:
        order = db.get_current_order_by_table(table_id)
        if not order:
            # 创建新订单
            bill = db.get_active_bill_by_table(table_id)
            if bill:
                order = db.create_order(table_id, bill['bill_id'])
            else:
                return jsonify({'success': False, 'error': '没有有效账单'})
        
        items = db.get_order_items(order['order_id'])
        return jsonify({
            'success': True, 
            'data': {
                'order': order,
                'items': items
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/orders/<int:order_id>/items', methods=['POST'])
def add_order_item(order_id):
    """添加订单项"""
    try:
        data = request.json
        dish = db.get_dish_by_id(data['dish_id'])
        if not dish:
            return jsonify({'success': False, 'error': '菜品不存在'})
        
        flavor_json = json.dumps(data.get('flavors', []), ensure_ascii=False) if data.get('flavors') else None
        item = db.add_order_item(
            order_id, 
            data['dish_id'], 
            data['quantity'], 
            dish['price'],
            flavor_json
        )
        return jsonify({'success': True, 'data': item})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/orders/<int:order_id>/confirm', methods=['POST'])
def confirm_order(order_id):
    """确认订单"""
    try:
        order = db.get_order_by_id(order_id)
        if not order:
            return jsonify({'success': False, 'error': '订单不存在'})
        
        bill = db.get_active_bill_by_table(order['table_id'])
        if not bill:
            return jsonify({'success': False, 'error': '账单不存在'})
        
        db.confirm_order(order_id, bill['bill_id'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tables/<int:table_id>/confirmed-orders', methods=['GET'])
def get_confirmed_orders(table_id):
    """获取已确认订单"""
    try:
        orders = db.get_confirmed_orders_by_table(table_id)
        result = []
        for order in orders:
            items = db.get_order_items(order['order_id'])
            result.append({
                'order': order,
                'items': items
            })
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============================================
# API路由 - 催菜/退菜
# ============================================

@app.route('/api/orders/<int:order_id>/items/<int:dish_id>/rush', methods=['POST'])
def rush_dish(order_id, dish_id):
    """催菜"""
    try:
        db.rush_dish(order_id, dish_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/orders/<int:order_id>/items/<int:dish_id>/refund', methods=['POST'])
def refund_dish(order_id, dish_id):
    """退菜"""
    try:
        data = request.json
        reason = data.get('reason', '')
        if not reason:
            return jsonify({'success': False, 'error': '请填写退菜理由'})
        db.refund_dish(order_id, dish_id, reason)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============================================
# API路由 - 后厨
# ============================================

@app.route('/api/kitchen/orders', methods=['GET'])
def get_kitchen_orders():
    """获取后厨订单"""
    try:
        station = request.args.get('station', 'all')
        client = db.get_client()
        
        if station == 'cold':
            categories = ['凉菜', '酒水']
        elif station == 'hot':
            categories = ['热菜', '汤羹', '主食']
        else:
            categories = None
        
        query = client.table("order_items").select(
            "*, orders!inner(order_id, status, created_at, table_id), dishes!inner(dish_name, category)"
        ).eq("orders.status", "已确认").neq("dish_status", "已退菜")
        
        if categories:
            query = query.in_("dishes.category", categories)
        
        result = query.order("is_rushed", desc=True).execute()
        return jsonify({'success': True, 'data': result.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/kitchen/items/<int:order_id>/<int:dish_id>/status', methods=['PUT'])
def update_dish_status(order_id, dish_id):
    """更新菜品状态"""
    try:
        data = request.json
        new_status = data.get('status')
        db.update_dish_status(order_id, dish_id, new_status)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============================================
# API路由 - 结账
# ============================================

@app.route('/api/tables/<int:table_id>/checkout', methods=['POST'])
def checkout(table_id):
    """结账"""
    try:
        data = request.json
        discount_type = data.get('discount_type')  # '八折', '抹零', None
        
        bill = db.get_active_bill_by_table(table_id)
        if not bill:
            return jsonify({'success': False, 'error': '没有有效账单'})
        
        # 计算总额
        orders = db.get_orders_by_bill(bill['bill_id'])
        total_amount = 0
        
        for order in orders:
            if order['status'] == '已确认':
                items = db.get_order_items(order['order_id'])
                for item in items:
                    if item['dish_status'] != '已退菜':
                        total_amount += float(item['unit_price']) * item['quantity']
        
        # 计算实际金额
        if discount_type == '八折':
            actual_amount = total_amount * 0.8
        elif discount_type == '抹零':
            actual_amount = int(total_amount)
        else:
            actual_amount = total_amount
        
        # 结算
        db.settle_bill(bill['bill_id'], total_amount, actual_amount, discount_type)
        db.update_table_status(table_id, '待清理')
        
        return jsonify({
            'success': True,
            'data': {
                'bill_id': bill['bill_id'],
                'total_amount': total_amount,
                'discount_type': discount_type,
                'actual_amount': actual_amount
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============================================
# API路由 - 营收统计
# ============================================

@app.route('/api/revenue', methods=['GET'])
def get_revenue():
    """获取营收统计"""
    try:
        bills = db.get_all_settled_bills()
        result = []
        total_sum = 0
        actual_sum = 0
        
        for bill in bills:
            orders = db.get_orders_by_bill(bill['bill_id'])
            order_details = []
            
            for order in orders:
                if order['status'] == '已确认':
                    items = db.get_order_items(order['order_id'])
                    valid_items = [i for i in items if i['dish_status'] != '已退菜']
                    order_details.append({
                        'order_id': order['order_id'],
                        'items': valid_items
                    })
            
            result.append({
                'bill_id': bill['bill_id'],
                'table_id': bill['table_id'],
                'total_amount': float(bill['total_amount']),
                'discount_type': bill['discount_type'],
                'actual_amount': float(bill['actual_amount']),
                'settled_at': bill['settled_at'],
                'orders': order_details
            })
            
            total_sum += float(bill['total_amount'])
            actual_sum += float(bill['actual_amount'])
        
        return jsonify({
            'success': True,
            'data': {
                'bills': result,
                'total_sum': total_sum,
                'actual_sum': actual_sum
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============================================
# 启动应用
# ============================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  聚香园餐厅点餐系统 - Web版")
    print("  访问地址: http://localhost:5000")
    print("=" * 60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
