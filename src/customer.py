"""
顾客功能模块
实现顾客的所有操作功能
"""

import json
from . import database as db
from . import utils


# 当前绑定的桌台ID
current_table_id = None


def set_current_table(table_id: int):
    """设置当前桌台"""
    global current_table_id
    current_table_id = table_id


def get_current_table():
    """获取当前桌台"""
    return current_table_id


def view_available_tables():
    """查看空闲桌位"""
    utils.print_header("查看空闲桌位")
    
    tables = db.get_available_tables()
    
    if not tables:
        utils.print_warning("当前没有空闲桌位")
        return
    
    data = []
    for t in tables:
        data.append([
            t['table_id'],
            t['table_type'],
            f"{t['capacity']}人",
            t['status']
        ])
    
    utils.print_table(data, ["桌位ID", "桌台类型", "容量", "状态"])


def scan_and_bindtable():
    """扫码绑定桌位（开台）"""
    utils.print_header("扫码绑定桌位")
    
    # 显示空闲桌位
    tables = db.get_available_tables()
    
    if not tables:
        utils.print_warning("当前没有空闲桌位，请稍后再试")
        return
    
    data = []
    for t in tables:
        data.append([
            t['table_id'],
            t['table_type'],
            f"{t['capacity']}人"
        ])
    
    utils.print_table(data, ["桌位ID", "桌台类型", "容量"], "可用桌位：")
    
    # 选择桌位
    table_id = utils.get_int_input("请输入要绑定的桌位ID", min_val=1)
    
    # 验证桌位
    table = db.get_table_by_id(table_id)
    if not table:
        utils.print_error("桌位不存在")
        return
    
    if table['status'] != '空闲':
        utils.print_error(f"该桌位当前状态为【{table['status']}】，无法绑定")
        return
    
    # 开台：更新桌台状态，创建账单和订单
    db.update_table_status(table_id, '就餐中')
    bill = db.create_bill(table_id)
    order = db.create_order(table_id, bill['bill_id'])
    
    # 设置当前桌台
    set_current_table(table_id)
    
    utils.print_success(f"成功绑定桌位 {table_id}（{table['table_type']}）")
    utils.print_info(f"账单ID: {bill['bill_id']}, 订单ID: {order['order_id']}")


def view_menu():
    """查看菜单"""
    utils.print_header("查看菜单")
    
    dishes = db.get_available_dishes()
    
    if not dishes:
        utils.print_warning("菜单暂无菜品")
        return
    
    # 按分类分组显示
    categories = ['热菜', '凉菜', '汤羹', '主食', '酒水']
    
    for category in categories:
        category_dishes = [d for d in dishes if d['category'] == category]
        if category_dishes:
            print(f"\n{utils.Fore.YELLOW}【{category}】{utils.Style.RESET_ALL}")
            data = []
            for d in category_dishes:
                # 获取口味选项
                rounds = db.get_flavor_rounds_by_dish(d['dish_id'])
                flavor_info = "-"
                if rounds:
                    flavor_parts = []
                    for r in rounds:
                        options = db.get_flavor_options_by_round(r['round_id'])
                        option_names = [o['option_name'] for o in options]
                        flavor_parts.append(f"{r['round_name']}({'/'.join(option_names)})")
                    flavor_info = ", ".join(flavor_parts)
                
                data.append([
                    d['dish_id'],
                    d['dish_name'],
                    utils.format_price(d['price']),
                    flavor_info
                ])
            
            utils.print_table(data, ["菜品ID", "菜品名称", "价格", "口味选项"])


def order_dish():
    """点菜/加菜"""
    global current_table_id
    
    utils.print_header("点菜/加菜")
    
    if not current_table_id:
        utils.print_error("请先扫码绑定桌位")
        return
    
    # 检查桌台状态
    table = db.get_table_by_id(current_table_id)
    if not table or table['status'] != '就餐中':
        utils.print_error("桌位状态异常，请重新绑定")
        current_table_id = None
        return
    
    # 获取当前订单
    order = db.get_current_order_by_table(current_table_id)
    if not order:
        # 如果没有未确认订单，创建新订单
        bill = db.get_active_bill_by_table(current_table_id)
        if not bill:
            utils.print_error("账单异常，请联系服务员")
            return
        order = db.create_order(current_table_id, bill['bill_id'])
        utils.print_info(f"创建新订单 ID: {order['order_id']}")
    
    while True:
        # 显示简化菜单
        print("\n当前可点菜品：")
        dishes = db.get_available_dishes()
        data = []
        for d in dishes:
            data.append([d['dish_id'], d['dish_name'], d['category'], utils.format_price(d['price'])])
        utils.print_table(data, ["ID", "名称", "分类", "价格"])
        
        # 选择菜品
        dish_id = utils.get_int_input("请输入菜品ID（输入0结束点菜）")
        if dish_id == 0:
            break
        
        dish = db.get_dish_by_id(dish_id)
        if not dish or not dish.get('is_available', True):
            utils.print_error("菜品不存在或已下架")
            continue
        
        # 处理口味选项
        flavor_choices = []
        rounds = db.get_flavor_rounds_by_dish(dish_id)
        
        if rounds:
            print(f"\n为【{dish['dish_name']}】选择口味：")
            for r in rounds:
                options = db.get_flavor_options_by_round(r['round_id'])
                option_names = [o['option_name'] for o in options]
                
                print(f"\n{r['round_name']}：")
                for i, opt in enumerate(option_names, 1):
                    print(f"  {i}. {opt}")
                
                while True:
                    choice_idx = utils.get_int_input(f"请选择{r['round_name']}", min_val=1, max_val=len(option_names))
                    flavor_choices.append({
                        "轮次": r['round_name'],
                        "选项": option_names[choice_idx - 1]
                    })
                    break
        
        # 选择数量
        quantity = utils.get_int_input("请输入数量", min_val=1, max_val=99)
        
        # 添加到订单
        flavor_json = json.dumps(flavor_choices, ensure_ascii=False) if flavor_choices else None
        db.add_order_item(order['order_id'], dish_id, quantity, dish['price'], flavor_json)
        
        flavor_str = utils.format_flavor_choices(flavor_json)
        utils.print_success(f"已添加: {dish['dish_name']} x{quantity} {flavor_str}")
        
        if not utils.confirm("继续点菜"):
            break
    
    utils.print_info("点菜完成，请通知服务员确认订单")


def view_current_order():
    """查看当前订单明细"""
    global current_table_id
    
    utils.print_header("当前订单明细")
    
    if not current_table_id:
        utils.print_error("请先扫码绑定桌位")
        return
    
    # 获取当前未确认订单
    order = db.get_current_order_by_table(current_table_id)
    
    if not order:
        utils.print_warning("当前没有待确认的订单")
        return
    
    print(f"\n订单ID: {order['order_id']}")
    
    items = db.get_order_items(order['order_id'])
    
    if not items:
        utils.print_warning("订单中暂无菜品")
        return
    
    data = []
    total = 0
    for item in items:
        dish_info = item.get('dishes', {})
        subtotal = item['unit_price'] * item['quantity']
        total += subtotal
        data.append([
            item['dish_id'],
            dish_info.get('dish_name', '-'),
            dish_info.get('category', '-'),
            utils.format_price(item['unit_price']),
            item['quantity'],
            utils.format_flavor_choices(item.get('flavor_choices')),
            utils.format_price(subtotal)
        ])
    
    utils.print_table(data, ["菜品ID", "名称", "分类", "单价", "数量", "口味", "小计"])
    print(f"\n{utils.Fore.GREEN}订单总计: {utils.format_price(total)}")


def rush_dish():
    """催菜"""
    global current_table_id
    
    utils.print_header("催菜")
    
    if not current_table_id:
        utils.print_error("请先扫码绑定桌位")
        return
    
    # 获取该桌的所有已确认订单
    orders = db.get_confirmed_orders_by_table(current_table_id)
    
    if not orders:
        utils.print_warning("暂无可催的订单")
        return
    
    # 显示可催的菜品（未制作或制作中）
    rushable_items = []
    for order in orders:
        items = db.get_order_items(order['order_id'])
        for item in items:
            if item['dish_status'] in ['未制作', '制作中']:
                dish_info = item.get('dishes', {})
                rushable_items.append({
                    'order_id': order['order_id'],
                    'dish_id': item['dish_id'],
                    'dish_name': dish_info.get('dish_name', '-'),
                    'status': item['dish_status'],
                    'is_rushed': item.get('is_rushed', False)
                })
    
    if not rushable_items:
        utils.print_warning("当前没有可催的菜品（所有菜品已完成）")
        return
    
    print("\n可催菜品：")
    data = []
    for item in rushable_items:
        rushed_mark = "【已催】" if item['is_rushed'] else ""
        data.append([
            item['order_id'],
            item['dish_id'],
            item['dish_name'],
            item['status'],
            rushed_mark
        ])
    utils.print_table(data, ["订单ID", "菜品ID", "菜品名称", "状态", "催菜标记"])
    
    # 选择要催的菜
    order_id = utils.get_int_input("请输入订单ID")
    dish_id = utils.get_int_input("请输入菜品ID")
    
    # 验证
    found = False
    for item in rushable_items:
        if item['order_id'] == order_id and item['dish_id'] == dish_id:
            found = True
            if item['is_rushed']:
                utils.print_warning("该菜品已经催过了")
                return
            break
    
    if not found:
        utils.print_error("未找到对应的菜品或该菜品无法催单")
        return
    
    # 催菜
    db.rush_dish(order_id, dish_id)
    utils.print_success("催菜成功，后厨已收到通知")


def customer_menu():
    """顾客主菜单"""
    global current_table_id
    
    while True:
        table_info = f"（当前桌位: {current_table_id}）" if current_table_id else "（未绑定桌位）"
        title = f"顾客端 {table_info}"
        
        options = [
            "查看空闲桌位",
            "扫码绑定桌位（开台）",
            "查看菜单",
            "点菜/加菜",
            "查看当前订单明细",
            "催菜"
        ]
        
        choice = utils.show_menu(title, options)
        
        if choice == 0:
            break
        elif choice == 1:
            view_available_tables()
        elif choice == 2:
            scan_and_bindtable()
        elif choice == 3:
            view_menu()
        elif choice == 4:
            order_dish()
        elif choice == 5:
            view_current_order()
        elif choice == 6:
            rush_dish()
        
        utils.pause()
