"""
经理功能模块
实现经理的所有操作功能
"""

import json
from . import database as db
from . import utils


def view_all_dishes():
    """查看所有菜品"""
    utils.print_header("查看所有菜品")
    
    dishes = db.get_all_dishes()
    
    if not dishes:
        utils.print_warning("暂无菜品")
        return
    
    # 按分类分组
    categories = ['热菜', '凉菜', '汤羹', '主食', '酒水']
    
    for category in categories:
        category_dishes = [d for d in dishes if d['category'] == category]
        if category_dishes:
            print(f"\n{utils.Fore.YELLOW}【{category}】{utils.Style.RESET_ALL}")
            data = []
            for d in category_dishes:
                status = "上架" if d.get('is_available', True) else "已下架"
                status_color = utils.Fore.GREEN if d.get('is_available', True) else utils.Fore.RED
                
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
                    f"{status_color}{status}{utils.Style.RESET_ALL}",
                    flavor_info
                ])
            
            utils.print_table(data, ["菜品ID", "菜品名称", "价格", "状态", "口味选项"])


def add_dish():
    """添加菜品"""
    utils.print_header("添加菜品")
    
    # 输入菜品基本信息
    dish_name = utils.get_input("请输入菜品名称")
    if not dish_name:
        utils.print_error("菜品名称不能为空")
        return
    
    # 选择分类
    categories = ['热菜', '凉菜', '汤羹', '主食', '酒水']
    category = utils.get_choice("请选择菜品分类", categories)
    
    # 输入价格
    price = utils.get_float_input("请输入菜品价格", min_val=0)
    
    # 添加菜品
    dish = db.add_dish(dish_name, category, price)
    
    if not dish:
        utils.print_error("添加菜品失败")
        return
    
    utils.print_success(f"菜品添加成功，菜品ID: {dish['dish_id']}")
    
    # 询问是否添加口味选项
    if not utils.confirm("是否为该菜品添加口味选项"):
        return
    
    # 添加口味轮次
    round_number = 1
    while True:
        print(f"\n添加第 {round_number} 轮口味选项：")
        round_name = utils.get_input(f"请输入轮次名称（如：辣度、温度等，输入空跳过）")
        
        if not round_name:
            break
        
        # 添加轮次
        flavor_round = db.add_flavor_round(dish['dish_id'], round_number, round_name)
        
        if not flavor_round:
            utils.print_error("添加轮次失败")
            continue
        
        # 添加选项
        print(f"为【{round_name}】添加选项（至少2个）：")
        option_count = 0
        while True:
            option_name = utils.get_input(f"请输入选项{option_count + 1}名称（输入空结束）")
            
            if not option_name:
                if option_count < 2:
                    utils.print_warning("每轮至少需要2个选项")
                    continue
                break
            
            db.add_flavor_option(flavor_round['round_id'], option_name)
            option_count += 1
            utils.print_success(f"已添加选项: {option_name}")
        
        round_number += 1
        
        if not utils.confirm("是否继续添加下一轮口味选项"):
            break
    
    utils.print_success(f"菜品【{dish_name}】配置完成")


def remove_dish():
    """下架菜品"""
    utils.print_header("下架菜品")
    
    # 显示所有在售菜品
    dishes = [d for d in db.get_all_dishes() if d.get('is_available', True)]
    
    if not dishes:
        utils.print_warning("暂无可下架的菜品")
        return
    
    data = []
    for d in dishes:
        data.append([d['dish_id'], d['dish_name'], d['category'], utils.format_price(d['price'])])
    
    utils.print_table(data, ["菜品ID", "菜品名称", "分类", "价格"], "在售菜品：")
    
    # 选择要下架的菜品
    dish_id = utils.get_int_input("请输入要下架的菜品ID（输入0取消）")
    
    if dish_id == 0:
        return
    
    # 验证
    dish = db.get_dish_by_id(dish_id)
    if not dish:
        utils.print_error("菜品不存在")
        return
    
    if not dish.get('is_available', True):
        utils.print_error("该菜品已经下架")
        return
    
    # 确认
    print(f"\n要下架的菜品信息：")
    print(f"  菜品ID: {dish['dish_id']}")
    print(f"  菜品名称: {dish['dish_name']}")
    print(f"  菜品分类: {dish['category']}")
    print(f"  菜品价格: {utils.format_price(dish['price'])}")
    
    utils.print_warning("注意：下架后该菜品及其所有口味选项将被永久删除！")
    
    if not utils.confirm(f"确认下架菜品【{dish['dish_name']}】"):
        utils.print_info("已取消下架")
        return
    
    # 下架（删除）
    db.remove_dish(dish_id)
    utils.print_success(f"菜品【{dish['dish_name']}】已下架")


def view_revenue():
    """营收统计"""
    utils.print_header("营收统计")
    
    # 获取所有已结账账单
    bills = db.get_all_settled_bills()
    
    if not bills:
        utils.print_warning("暂无已结账账单")
        return
    
    total_sum = 0
    actual_sum = 0
    
    print("\n" + "=" * 80)
    
    for bill in bills:
        print(f"\n{utils.Fore.CYAN}账单ID: {bill['bill_id']}{utils.Style.RESET_ALL}")
        print(f"桌位ID: {bill['table_id']}")
        print(f"结账时间: {bill.get('settled_at', '-')}")
        
        # 获取该账单的所有订单
        orders = db.get_orders_by_bill(bill['bill_id'])
        confirmed_orders = [o for o in orders if o['status'] == '已确认']
        
        if confirmed_orders:
            for order in confirmed_orders:
                print(f"\n  订单ID: {order['order_id']}")
                items = db.get_order_items(order['order_id'])
                
                data = []
                for item in items:
                    if item['dish_status'] != '已退菜':
                        dish_info = item.get('dishes', {})
                        subtotal = item['unit_price'] * item['quantity']
                        data.append([
                            f"  {item['dish_id']}",
                            dish_info.get('dish_name', '-'),
                            dish_info.get('category', '-'),
                            utils.format_price(item['unit_price']),
                            item['quantity'],
                            utils.format_flavor_choices(item.get('flavor_choices')),
                            utils.format_price(subtotal)
                        ])
                
                if data:
                    utils.print_table(data, ["菜品ID", "名称", "分类", "单价", "数量", "口味", "小计"])
        
        print(f"\n  账单总额: {utils.format_price(bill['total_amount'])}")
        if bill.get('discount_type'):
            print(f"  折扣方式: {bill['discount_type']}")
        print(f"  {utils.Fore.GREEN}实际消费: {utils.format_price(bill['actual_amount'])}{utils.Style.RESET_ALL}")
        print("-" * 80)
        
        total_sum += float(bill['total_amount'])
        actual_sum += float(bill['actual_amount'])
    
    # 汇总
    print("\n" + "=" * 80)
    print(f"{utils.Fore.YELLOW}营收汇总{utils.Style.RESET_ALL}")
    print("=" * 80)
    print(f"账单数量: {len(bills)}")
    print(f"总额合计: {utils.format_price(total_sum)}")
    print(f"{utils.Fore.GREEN}实际营收: {utils.format_price(actual_sum)}{utils.Style.RESET_ALL}")
    print(f"折扣总额: {utils.format_price(total_sum - actual_sum)}")
    print("=" * 80)


def view_revenue_summary():
    """营收汇总报表"""
    utils.print_header("营收汇总报表")
    
    bills = db.get_all_settled_bills()
    
    if not bills:
        utils.print_warning("暂无已结账账单")
        return
    
    data = []
    total_sum = 0
    actual_sum = 0
    
    for bill in bills:
        discount = bill.get('discount_type', '-') or '-'
        data.append([
            bill['bill_id'],
            bill['table_id'],
            bill.get('settled_at', '-')[:19] if bill.get('settled_at') else '-',
            utils.format_price(bill['total_amount']),
            discount,
            utils.format_price(bill['actual_amount'])
        ])
        total_sum += float(bill['total_amount'])
        actual_sum += float(bill['actual_amount'])
    
    utils.print_table(data, ["账单ID", "桌位ID", "结账时间", "总额", "折扣", "实付"])
    
    print(f"\n{'='*60}")
    print(f"账单总数: {len(bills)}")
    print(f"总额合计: {utils.format_price(total_sum)}")
    print(f"{utils.Fore.GREEN}实际营收: {utils.format_price(actual_sum)}{utils.Style.RESET_ALL}")
    print(f"折扣总额: {utils.format_price(total_sum - actual_sum)}")


def manage_dishes_menu():
    """菜品管理子菜单"""
    while True:
        options = [
            "查看所有菜品",
            "添加菜品",
            "下架菜品"
        ]
        
        choice = utils.show_menu("菜品管理", options)
        
        if choice == 0:
            break
        elif choice == 1:
            view_all_dishes()
        elif choice == 2:
            add_dish()
        elif choice == 3:
            remove_dish()
        
        utils.pause()


def revenue_menu():
    """营收统计子菜单"""
    while True:
        options = [
            "营收汇总报表",
            "营收明细查看"
        ]
        
        choice = utils.show_menu("营收统计", options)
        
        if choice == 0:
            break
        elif choice == 1:
            view_revenue_summary()
        elif choice == 2:
            view_revenue()
        
        utils.pause()


def manager_menu():
    """经理主菜单"""
    while True:
        options = [
            "菜品管理",
            "营收统计"
        ]
        
        choice = utils.show_menu("经理端", options)
        
        if choice == 0:
            break
        elif choice == 1:
            manage_dishes_menu()
        elif choice == 2:
            revenue_menu()
