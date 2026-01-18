"""
服务员功能模块
实现服务员的所有操作功能
"""

import json
from . import database as db
from . import utils


# 当前操作的桌台ID
current_table_id = None


def set_current_table(table_id: int):
    """设置当前操作桌台"""
    global current_table_id
    current_table_id = table_id


def get_current_table():
    """获取当前操作桌台"""
    return current_table_id


def view_all_tables():
    """查看全部桌位"""
    utils.print_header("查看全部桌位")
    
    tables = db.get_all_tables()
    
    if not tables:
        utils.print_warning("暂无桌位信息")
        return
    
    data = []
    for t in tables:
        status_display = t['status']
        if t['status'] == '就餐中':
            status_display = f"{utils.Fore.GREEN}{t['status']}{utils.Style.RESET_ALL}"
        elif t['status'] == '待清理':
            status_display = f"{utils.Fore.YELLOW}{t['status']}{utils.Style.RESET_ALL}"
        
        data.append([
            t['table_id'],
            t['table_type'],
            f"{t['capacity']}人",
            status_display
        ])
    
    utils.print_table(data, ["桌位ID", "桌台类型", "容量", "状态"])


def manage_table_status():
    """管理桌位状态（清理桌台）"""
    utils.print_header("管理桌位状态")
    
    # 显示待清理的桌台
    tables = db.get_tables_by_status('待清理')
    
    if not tables:
        utils.print_warning("当前没有待清理的桌台")
        return
    
    data = []
    for t in tables:
        data.append([
            t['table_id'],
            t['table_type'],
            f"{t['capacity']}人",
            t['status']
        ])
    
    utils.print_table(data, ["桌位ID", "桌台类型", "容量", "状态"], "待清理桌台：")
    
    # 选择要清理的桌台
    table_id = utils.get_int_input("请输入要清理的桌位ID（输入0取消）")
    
    if table_id == 0:
        return
    
    # 验证
    table = db.get_table_by_id(table_id)
    if not table:
        utils.print_error("桌位不存在")
        return
    
    if table['status'] != '待清理':
        utils.print_error(f"该桌位状态为【{table['status']}】，不是待清理状态")
        return
    
    # 更新状态
    db.update_table_status(table_id, '空闲')
    utils.print_success(f"桌位 {table_id} 已清理完成，状态已更新为【空闲】")


def open_table():
    """开台"""
    utils.print_header("开台")
    
    # 显示空闲桌位
    tables = db.get_available_tables()
    
    if not tables:
        utils.print_warning("当前没有空闲桌位")
        return
    
    data = []
    for t in tables:
        data.append([
            t['table_id'],
            t['table_type'],
            f"{t['capacity']}人"
        ])
    
    utils.print_table(data, ["桌位ID", "桌台类型", "容量"], "空闲桌位：")
    
    # 选择桌位
    table_id = utils.get_int_input("请输入要开台的桌位ID（输入0取消）")
    
    if table_id == 0:
        return
    
    # 验证
    table = db.get_table_by_id(table_id)
    if not table:
        utils.print_error("桌位不存在")
        return
    
    if table['status'] != '空闲':
        utils.print_error(f"该桌位状态为【{table['status']}】，无法开台")
        return
    
    # 开台
    db.update_table_status(table_id, '就餐中')
    bill = db.create_bill(table_id)
    order = db.create_order(table_id, bill['bill_id'])
    
    # 设置当前桌台
    set_current_table(table_id)
    
    utils.print_success(f"桌位 {table_id}（{table['table_type']}）开台成功")
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
                data.append([
                    d['dish_id'],
                    d['dish_name'],
                    utils.format_price(d['price'])
                ])
            
            utils.print_table(data, ["菜品ID", "菜品名称", "价格"])


def select_table():
    """选择操作桌台"""
    utils.print_header("选择操作桌台")
    
    # 显示就餐中的桌台
    tables = db.get_tables_by_status('就餐中')
    
    if not tables:
        utils.print_warning("当前没有就餐中的桌台")
        return False
    
    data = []
    for t in tables:
        data.append([
            t['table_id'],
            t['table_type'],
            f"{t['capacity']}人"
        ])
    
    utils.print_table(data, ["桌位ID", "桌台类型", "容量"], "就餐中的桌台：")
    
    table_id = utils.get_int_input("请输入要操作的桌位ID（输入0取消）")
    
    if table_id == 0:
        return False
    
    table = db.get_table_by_id(table_id)
    if not table:
        utils.print_error("桌位不存在")
        return False
    
    if table['status'] != '就餐中':
        utils.print_error(f"该桌位状态为【{table['status']}】，请选择就餐中的桌位")
        return False
    
    set_current_table(table_id)
    utils.print_success(f"已选择桌位 {table_id}")
    return True


def assist_order():
    """协助点菜/加菜"""
    global current_table_id
    
    utils.print_header("协助点菜/加菜")
    
    if not current_table_id:
        if not select_table():
            return
    
    # 检查桌台状态
    table = db.get_table_by_id(current_table_id)
    if not table or table['status'] != '就餐中':
        utils.print_error("桌位状态异常")
        current_table_id = None
        return
    
    # 获取当前订单
    order = db.get_current_order_by_table(current_table_id)
    if not order:
        # 如果没有未确认订单，创建新订单
        bill = db.get_active_bill_by_table(current_table_id)
        if not bill:
            utils.print_error("账单异常")
            return
        order = db.create_order(current_table_id, bill['bill_id'])
        utils.print_info(f"创建新订单 ID: {order['order_id']}")
    
    print(f"\n当前操作桌位: {current_table_id}, 订单ID: {order['order_id']}")
    
    while True:
        # 显示简化菜单
        print("\n可点菜品：")
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


def view_current_order():
    """查看当前订单明细"""
    global current_table_id
    
    utils.print_header("查看当前订单明细")
    
    if not current_table_id:
        if not select_table():
            return
    
    # 获取当前未确认订单
    order = db.get_current_order_by_table(current_table_id)
    
    if not order:
        utils.print_warning("当前没有待确认的订单")
        return
    
    print(f"\n桌位: {current_table_id}, 订单ID: {order['order_id']}")
    
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


def confirm_order():
    """确认订单"""
    global current_table_id
    
    utils.print_header("确认订单")
    
    if not current_table_id:
        if not select_table():
            return
    
    # 获取当前未确认订单
    order = db.get_current_order_by_table(current_table_id)
    
    if not order:
        utils.print_warning("当前没有待确认的订单")
        return
    
    # 显示订单明细
    print(f"\n桌位: {current_table_id}, 订单ID: {order['order_id']}")
    
    items = db.get_order_items(order['order_id'])
    
    if not items:
        utils.print_warning("订单中没有菜品，无法确认")
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
            utils.format_price(item['unit_price']),
            item['quantity'],
            utils.format_flavor_choices(item.get('flavor_choices')),
            utils.format_price(subtotal)
        ])
    
    utils.print_table(data, ["菜品ID", "名称", "单价", "数量", "口味", "小计"])
    print(f"\n{utils.Fore.GREEN}订单总计: {utils.format_price(total)}")
    
    # 确认
    if not utils.confirm("确认将此订单提交给后厨"):
        utils.print_info("已取消确认")
        return
    
    # 获取账单
    bill = db.get_active_bill_by_table(current_table_id)
    if not bill:
        utils.print_error("账单异常")
        return
    
    # 确认订单
    db.confirm_order(order['order_id'], bill['bill_id'])
    
    utils.print_success(f"订单 {order['order_id']} 已确认，已提交给后厨")
    utils.print_info("如需加菜，请创建新订单")


def refund_dish():
    """退菜"""
    global current_table_id
    
    utils.print_header("退菜")
    
    if not current_table_id:
        if not select_table():
            return
    
    # 获取该桌的所有已确认订单
    orders = db.get_confirmed_orders_by_table(current_table_id)
    
    if not orders:
        utils.print_warning("暂无可退菜的订单")
        return
    
    # 显示可退的菜品（未制作或制作中）
    refundable_items = []
    for order in orders:
        items = db.get_order_items(order['order_id'])
        for item in items:
            if item['dish_status'] in ['未制作', '制作中']:
                dish_info = item.get('dishes', {})
                refundable_items.append({
                    'order_id': order['order_id'],
                    'dish_id': item['dish_id'],
                    'dish_name': dish_info.get('dish_name', '-'),
                    'quantity': item['quantity'],
                    'unit_price': item['unit_price'],
                    'status': item['dish_status']
                })
    
    if not refundable_items:
        utils.print_warning("当前没有可退的菜品（所有菜品已完成或已退）")
        return
    
    print("\n可退菜品：")
    data = []
    for item in refundable_items:
        data.append([
            item['order_id'],
            item['dish_id'],
            item['dish_name'],
            item['quantity'],
            utils.format_price(item['unit_price']),
            item['status']
        ])
    utils.print_table(data, ["订单ID", "菜品ID", "菜品名称", "数量", "单价", "状态"])
    
    # 选择要退的菜
    order_id = utils.get_int_input("请输入订单ID")
    dish_id = utils.get_int_input("请输入菜品ID")
    
    # 验证
    found = False
    for item in refundable_items:
        if item['order_id'] == order_id and item['dish_id'] == dish_id:
            found = True
            break
    
    if not found:
        utils.print_error("未找到对应的菜品或该菜品无法退单")
        return
    
    # 填写退菜理由
    reason = utils.get_input("请输入退菜理由")
    if not reason:
        utils.print_error("必须填写退菜理由")
        return
    
    # 确认
    if not utils.confirm(f"确认退菜【{item['dish_name']}】"):
        return
    
    # 退菜
    db.refund_dish(order_id, dish_id, reason)
    utils.print_success(f"退菜成功: {item['dish_name']}")


def checkout():
    """结账"""
    global current_table_id
    
    utils.print_header("结账")
    
    if not current_table_id:
        if not select_table():
            return
    
    # 检查是否有未确认订单
    pending_order = db.get_current_order_by_table(current_table_id)
    if pending_order:
        items = db.get_order_items(pending_order['order_id'])
        if items:
            utils.print_warning("当前还有未确认的订单，请先确认或清空后再结账")
            return
    
    # 获取账单
    bill = db.get_active_bill_by_table(current_table_id)
    if not bill:
        utils.print_error("未找到有效账单")
        return
    
    # 获取所有已确认订单
    orders = db.get_orders_by_bill(bill['bill_id'])
    confirmed_orders = [o for o in orders if o['status'] == '已确认']
    
    if not confirmed_orders:
        utils.print_warning("没有已确认的订单，无法结账")
        return
    
    # 汇总账单
    print(f"\n{'='*60}")
    print(f"账单ID: {bill['bill_id']}")
    print(f"桌位: {current_table_id}")
    print(f"{'='*60}")
    
    total_amount = 0
    all_items = []
    
    for order in confirmed_orders:
        print(f"\n订单ID: {order['order_id']}")
        items = db.get_order_items(order['order_id'])
        
        data = []
        for item in items:
            if item['dish_status'] != '已退菜':
                dish_info = item.get('dishes', {})
                subtotal = item['unit_price'] * item['quantity']
                total_amount += subtotal
                all_items.append(item)
                data.append([
                    item['dish_id'],
                    dish_info.get('dish_name', '-'),
                    utils.format_price(item['unit_price']),
                    item['quantity'],
                    utils.format_price(subtotal)
                ])
        
        if data:
            utils.print_table(data, ["菜品ID", "名称", "单价", "数量", "小计"])
    
    print(f"\n{'='*60}")
    print(f"{utils.Fore.CYAN}账单总额: {utils.format_price(total_amount)}")
    print(f"{'='*60}")
    
    if not utils.confirm("确认结账"):
        utils.print_info("已取消结账")
        return
    
    # 折扣处理
    print("\n请选择折扣方式：")
    print("  1. 整单打8折")
    print("  2. 抹零")
    print("  3. 不打折")
    
    discount_choice = utils.get_int_input("请选择", min_val=1, max_val=3)
    
    discount_type = None
    actual_amount = total_amount
    
    if discount_choice == 1:
        discount_type = "八折"
        actual_amount = total_amount * 0.8
    elif discount_choice == 2:
        discount_type = "抹零"
        actual_amount = int(total_amount)  # 去掉小数部分
    
    # 更新账单并结算
    db.settle_bill(bill['bill_id'], total_amount, actual_amount, discount_type)
    
    # 更新桌台状态
    db.update_table_status(current_table_id, '待清理')
    
    print(f"\n{'='*60}")
    print(f"{utils.Fore.GREEN}结账成功！")
    print(f"{'='*60}")
    print(f"账单总额: {utils.format_price(total_amount)}")
    if discount_type:
        print(f"折扣方式: {discount_type}")
    print(f"{utils.Fore.GREEN}实际消费: {utils.format_price(actual_amount)}")
    print(f"{'='*60}")
    
    # 清除当前桌台
    current_table_id = None


def waiter_menu():
    """服务员主菜单"""
    global current_table_id
    
    while True:
        table_info = f"（当前桌位: {current_table_id}）" if current_table_id else "（未选择桌位）"
        title = f"服务员端 {table_info}"
        
        options = [
            "查看全部桌位",
            "管理桌位状态（清理桌台）",
            "开台",
            "选择操作桌台",
            "查看菜单",
            "协助点菜/加菜",
            "查看当前订单明细",
            "确认订单",
            "退菜",
            "结账"
        ]
        
        choice = utils.show_menu(title, options)
        
        if choice == 0:
            current_table_id = None
            break
        elif choice == 1:
            view_all_tables()
        elif choice == 2:
            manage_table_status()
        elif choice == 3:
            open_table()
        elif choice == 4:
            select_table()
        elif choice == 5:
            view_menu()
        elif choice == 6:
            assist_order()
        elif choice == 7:
            view_current_order()
        elif choice == 8:
            confirm_order()
        elif choice == 9:
            refund_dish()
        elif choice == 10:
            checkout()
        
        utils.pause()
