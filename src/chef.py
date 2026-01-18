"""
后厨功能模块
实现后厨的所有操作功能
"""

from . import database as db
from . import utils


def display_kitchen_items(items: list, title: str):
    """显示后厨订单列表"""
    utils.print_header(title)
    
    if not items:
        utils.print_warning("暂无待处理的订单")
        return
    
    data = []
    for item in items:
        # 处理不同的数据结构
        if 'orders' in item:
            order_id = item['orders']['order_id']
        else:
            order_id = item.get('order_id', '-')
        
        if 'dishes' in item:
            dish_name = item['dishes']['dish_name']
            category = item['dishes']['category']
        else:
            dish_name = item.get('dish_name', '-')
            category = item.get('category', '-')
        
        # 催菜高亮显示
        is_rushed = item.get('is_rushed', False)
        
        row = [
            order_id,
            item.get('dish_id', '-'),
            dish_name,
            category,
            utils.format_price(item.get('unit_price', 0)),
            item.get('quantity', 0),
            utils.format_flavor_choices(item.get('flavor_choices')),
        ]
        
        # 状态显示（带催菜高亮）
        status = item.get('dish_status', '-')
        if is_rushed and status in ['未制作', '制作中']:
            row.append(f"{utils.Back.YELLOW}{utils.Fore.BLACK}【催】{status}{utils.Style.RESET_ALL}")
        else:
            row.append(utils.format_status(status))
        
        data.append(row)
    
    headers = ["订单ID", "菜品ID", "菜品名称", "分类", "单价", "数量", "口味", "状态"]
    
    # 使用原始print来处理颜色
    from tabulate import tabulate
    print(tabulate(data, headers=headers, tablefmt="pretty", stralign="left"))


def view_all_orders():
    """查看所有下单"""
    utils.print_header("查看所有下单")
    
    try:
        # 获取所有已确认订单的菜品
        client = db.get_client()
        result = client.table("order_items").select(
            "*, orders!inner(order_id, status, created_at), dishes(dish_name, category)"
        ).eq("orders.status", "已确认").neq("dish_status", "已退菜").order("is_rushed", desc=True).execute()
        
        items = result.data
        display_kitchen_items(items, "所有下单")
        
    except Exception as e:
        utils.print_error(f"查询失败: {e}")


def view_cold_orders():
    """查看凉菜房订单（凉菜、酒水）"""
    utils.print_header("凉菜房订单")
    print(f"{utils.Fore.CYAN}（凉菜、酒水）")
    
    try:
        items = db.get_kitchen_cold_orders()
        display_kitchen_items(items, "凉菜房订单")
        
    except Exception as e:
        utils.print_error(f"查询失败: {e}")


def view_hot_orders():
    """查看热菜房订单（热菜、汤羹、主食）"""
    utils.print_header("热菜房订单")
    print(f"{utils.Fore.CYAN}（热菜、汤羹、主食）")
    
    try:
        items = db.get_kitchen_hot_orders()
        display_kitchen_items(items, "热菜房订单")
        
    except Exception as e:
        utils.print_error(f"查询失败: {e}")


def view_by_station():
    """按工作站查看分单"""
    utils.print_header("查看分单")
    
    options = ["凉菜房（凉菜、酒水）", "热菜房（热菜、汤羹、主食）"]
    
    print("\n请选择工作站：")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    print("  0. 返回")
    
    choice = utils.get_int_input("请选择", min_val=0, max_val=2)
    
    if choice == 0:
        return
    elif choice == 1:
        view_cold_orders()
    elif choice == 2:
        view_hot_orders()


def update_dish_status():
    """更新菜品状态"""
    utils.print_header("更新菜品状态")
    
    # 先显示所有待处理的订单
    try:
        client = db.get_client()
        result = client.table("order_items").select(
            "*, orders!inner(order_id, status), dishes(dish_name, category)"
        ).eq("orders.status", "已确认").in_("dish_status", ["未制作", "制作中"]).order("is_rushed", desc=True).execute()
        
        items = result.data
        
        if not items:
            utils.print_warning("暂无待更新状态的菜品")
            return
        
        print("\n待处理菜品：")
        data = []
        for item in items:
            order_id = item['orders']['order_id']
            dish_name = item['dishes']['dish_name']
            is_rushed = item.get('is_rushed', False)
            status = item['dish_status']
            
            rushed_mark = "【催】" if is_rushed else ""
            data.append([
                order_id,
                item['dish_id'],
                dish_name,
                item['quantity'],
                status,
                rushed_mark
            ])
        
        utils.print_table(data, ["订单ID", "菜品ID", "菜品名称", "数量", "当前状态", "催菜"])
        
    except Exception as e:
        utils.print_error(f"查询失败: {e}")
        return
    
    # 输入要更新的菜品
    order_id = utils.get_int_input("请输入订单ID（输入0取消）")
    if order_id == 0:
        return
    
    dish_id = utils.get_int_input("请输入菜品ID")
    
    # 验证
    item = db.get_item_by_order_and_dish(order_id, dish_id)
    if not item:
        utils.print_error("未找到对应的菜品")
        return
    
    if item['dish_status'] not in ['未制作', '制作中']:
        utils.print_error(f"该菜品状态为【{item['dish_status']}】，无法更新")
        return
    
    # 选择新状态
    current_status = item['dish_status']
    print(f"\n当前状态: {current_status}")
    print("\n请选择新状态：")
    
    if current_status == '未制作':
        options = ['制作中', '已完成']
    else:  # 制作中
        options = ['已完成']
    
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    print("  0. 取消")
    
    choice = utils.get_int_input("请选择", min_val=0, max_val=len(options))
    
    if choice == 0:
        return
    
    new_status = options[choice - 1]
    
    # 更新状态
    db.update_dish_status(order_id, dish_id, new_status)
    utils.print_success(f"菜品状态已更新为【{new_status}】")


def quick_complete():
    """快速完成菜品"""
    utils.print_header("快速完成菜品")
    
    # 显示制作中的菜品
    try:
        client = db.get_client()
        result = client.table("order_items").select(
            "*, orders!inner(order_id, status), dishes(dish_name, category)"
        ).eq("orders.status", "已确认").eq("dish_status", "制作中").order("is_rushed", desc=True).execute()
        
        items = result.data
        
        if not items:
            utils.print_warning("暂无制作中的菜品")
            return
        
        print("\n制作中的菜品：")
        data = []
        for item in items:
            order_id = item['orders']['order_id']
            dish_name = item['dishes']['dish_name']
            is_rushed = item.get('is_rushed', False)
            rushed_mark = "【催】" if is_rushed else ""
            data.append([
                order_id,
                item['dish_id'],
                dish_name,
                item['quantity'],
                rushed_mark
            ])
        
        utils.print_table(data, ["订单ID", "菜品ID", "菜品名称", "数量", "催菜"])
        
    except Exception as e:
        utils.print_error(f"查询失败: {e}")
        return
    
    # 快速标记完成
    order_id = utils.get_int_input("请输入订单ID（输入0取消）")
    if order_id == 0:
        return
    
    dish_id = utils.get_int_input("请输入菜品ID")
    
    # 验证
    item = db.get_item_by_order_and_dish(order_id, dish_id)
    if not item:
        utils.print_error("未找到对应的菜品")
        return
    
    if item['dish_status'] != '制作中':
        utils.print_error(f"该菜品状态为【{item['dish_status']}】，不是制作中状态")
        return
    
    # 更新状态
    db.update_dish_status(order_id, dish_id, '已完成')
    utils.print_success("菜品已标记为【已完成】")


def start_cooking():
    """开始制作菜品"""
    utils.print_header("开始制作菜品")
    
    # 显示未制作的菜品
    try:
        client = db.get_client()
        result = client.table("order_items").select(
            "*, orders!inner(order_id, status), dishes(dish_name, category)"
        ).eq("orders.status", "已确认").eq("dish_status", "未制作").order("is_rushed", desc=True).execute()
        
        items = result.data
        
        if not items:
            utils.print_warning("暂无未制作的菜品")
            return
        
        print("\n未制作的菜品：")
        data = []
        for item in items:
            order_id = item['orders']['order_id']
            dish_name = item['dishes']['dish_name']
            category = item['dishes']['category']
            is_rushed = item.get('is_rushed', False)
            rushed_mark = "【催】" if is_rushed else ""
            data.append([
                order_id,
                item['dish_id'],
                dish_name,
                category,
                item['quantity'],
                utils.format_flavor_choices(item.get('flavor_choices')),
                rushed_mark
            ])
        
        utils.print_table(data, ["订单ID", "菜品ID", "菜品名称", "分类", "数量", "口味", "催菜"])
        
    except Exception as e:
        utils.print_error(f"查询失败: {e}")
        return
    
    # 开始制作
    order_id = utils.get_int_input("请输入订单ID（输入0取消）")
    if order_id == 0:
        return
    
    dish_id = utils.get_int_input("请输入菜品ID")
    
    # 验证
    item = db.get_item_by_order_and_dish(order_id, dish_id)
    if not item:
        utils.print_error("未找到对应的菜品")
        return
    
    if item['dish_status'] != '未制作':
        utils.print_error(f"该菜品状态为【{item['dish_status']}】，不是未制作状态")
        return
    
    # 更新状态
    db.update_dish_status(order_id, dish_id, '制作中')
    utils.print_success("菜品已开始制作")


def chef_menu():
    """后厨主菜单"""
    while True:
        options = [
            "查看所有下单",
            "查看分单（凉菜房/热菜房）",
            "开始制作菜品",
            "更新菜品状态",
            "快速完成菜品"
        ]
        
        choice = utils.show_menu("后厨端", options)
        
        if choice == 0:
            break
        elif choice == 1:
            view_all_orders()
        elif choice == 2:
            view_by_station()
        elif choice == 3:
            start_cooking()
        elif choice == 4:
            update_dish_status()
        elif choice == 5:
            quick_complete()
        
        utils.pause()
