"""
数据库连接模块
负责连接Supabase云数据库并提供数据操作接口
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client, Client

# 从配置文件导入Supabase配置
try:
    from config import SUPABASE_URL, SUPABASE_KEY
except ImportError:
    # 如果config.py不存在，尝试从环境变量读取
    from dotenv import load_dotenv
    load_dotenv()
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 全局数据库客户端
_supabase_client: Client = None


def get_client() -> Client:
    """获取Supabase客户端实例（单例模式）"""
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("请在.env文件中配置SUPABASE_URL和SUPABASE_KEY")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


def test_connection() -> bool:
    """测试数据库连接"""
    try:
        client = get_client()
        # 尝试查询桌台表
        result = client.table("tables").select("*").limit(1).execute()
        return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False


# ============================================
# 桌台相关操作
# ============================================

def get_all_tables():
    """获取所有桌台信息"""
    client = get_client()
    result = client.table("tables").select("*").order("table_id").execute()
    return result.data


def get_available_tables():
    """获取空闲桌台"""
    client = get_client()
    result = client.table("tables").select("*").eq("status", "空闲").order("table_id").execute()
    return result.data


def get_table_by_id(table_id: int):
    """根据ID获取桌台信息"""
    client = get_client()
    result = client.table("tables").select("*").eq("table_id", table_id).execute()
    return result.data[0] if result.data else None


def update_table_status(table_id: int, status: str):
    """更新桌台状态"""
    client = get_client()
    result = client.table("tables").update({"status": status}).eq("table_id", table_id).execute()
    return result.data


def get_tables_by_status(status: str):
    """根据状态获取桌台"""
    client = get_client()
    result = client.table("tables").select("*").eq("status", status).order("table_id").execute()
    return result.data


# ============================================
# 菜品相关操作
# ============================================

def get_all_dishes():
    """获取所有菜品（包括下架的）"""
    client = get_client()
    result = client.table("dishes").select("*").order("dish_id").execute()
    return result.data


def get_available_dishes():
    """获取在售菜品"""
    client = get_client()
    result = client.table("dishes").select("*").eq("is_available", True).order("category, dish_id").execute()
    return result.data


def get_dish_by_id(dish_id: int):
    """根据ID获取菜品信息"""
    client = get_client()
    result = client.table("dishes").select("*").eq("dish_id", dish_id).execute()
    return result.data[0] if result.data else None


def add_dish(dish_name: str, category: str, price: float):
    """添加新菜品"""
    client = get_client()
    result = client.table("dishes").insert({
        "dish_name": dish_name,
        "category": category,
        "price": price,
        "is_available": True
    }).execute()
    return result.data[0] if result.data else None


def remove_dish(dish_id: int):
    """下架菜品（删除菜品及其口味选项）"""
    client = get_client()
    # 由于设置了ON DELETE CASCADE，删除菜品会自动删除关联的口味轮次和选项
    result = client.table("dishes").delete().eq("dish_id", dish_id).execute()
    return result.data


# ============================================
# 口味选项相关操作
# ============================================

def get_flavor_rounds_by_dish(dish_id: int):
    """获取菜品的口味轮次"""
    client = get_client()
    result = client.table("flavor_rounds").select("*").eq("dish_id", dish_id).order("round_number").execute()
    return result.data


def get_flavor_options_by_round(round_id: int):
    """获取轮次的口味选项"""
    client = get_client()
    result = client.table("flavor_options").select("*").eq("round_id", round_id).order("option_id").execute()
    return result.data


def add_flavor_round(dish_id: int, round_number: int, round_name: str):
    """添加口味轮次"""
    client = get_client()
    result = client.table("flavor_rounds").insert({
        "dish_id": dish_id,
        "round_number": round_number,
        "round_name": round_name
    }).execute()
    return result.data[0] if result.data else None


def add_flavor_option(round_id: int, option_name: str):
    """添加口味选项"""
    client = get_client()
    result = client.table("flavor_options").insert({
        "round_id": round_id,
        "option_name": option_name
    }).execute()
    return result.data[0] if result.data else None


# ============================================
# 账单相关操作
# ============================================

def create_bill(table_id: int):
    """创建新账单"""
    client = get_client()
    result = client.table("bills").insert({
        "table_id": table_id,
        "total_amount": 0,
        "actual_amount": 0,
        "status": "未结账"
    }).execute()
    return result.data[0] if result.data else None


def get_bill_by_id(bill_id: int):
    """根据ID获取账单"""
    client = get_client()
    result = client.table("bills").select("*").eq("bill_id", bill_id).execute()
    return result.data[0] if result.data else None


def get_active_bill_by_table(table_id: int):
    """获取桌台的未结账账单"""
    client = get_client()
    result = client.table("bills").select("*").eq("table_id", table_id).eq("status", "未结账").execute()
    return result.data[0] if result.data else None


def update_bill(bill_id: int, total_amount: float, actual_amount: float, discount_type: str = None):
    """更新账单金额"""
    client = get_client()
    update_data = {
        "total_amount": total_amount,
        "actual_amount": actual_amount
    }
    if discount_type:
        update_data["discount_type"] = discount_type
    result = client.table("bills").update(update_data).eq("bill_id", bill_id).execute()
    return result.data


def settle_bill(bill_id: int, total_amount: float, actual_amount: float, discount_type: str):
    """结算账单"""
    client = get_client()
    from datetime import datetime
    result = client.table("bills").update({
        "total_amount": total_amount,
        "actual_amount": actual_amount,
        "discount_type": discount_type,
        "status": "已结账",
        "settled_at": datetime.now().isoformat()
    }).eq("bill_id", bill_id).execute()
    return result.data


def get_all_settled_bills():
    """获取所有已结账账单"""
    client = get_client()
    result = client.table("bills").select("*").eq("status", "已结账").order("settled_at", desc=True).execute()
    return result.data


# ============================================
# 订单相关操作
# ============================================

def create_order(table_id: int, bill_id: int = None):
    """创建新订单"""
    client = get_client()
    order_data = {
        "table_id": table_id,
        "status": "未确认"
    }
    if bill_id:
        order_data["bill_id"] = bill_id
    result = client.table("orders").insert(order_data).execute()
    return result.data[0] if result.data else None


def get_order_by_id(order_id: int):
    """根据ID获取订单"""
    client = get_client()
    result = client.table("orders").select("*").eq("order_id", order_id).execute()
    return result.data[0] if result.data else None


def get_current_order_by_table(table_id: int):
    """获取桌台的当前未确认订单"""
    client = get_client()
    result = client.table("orders").select("*").eq("table_id", table_id).eq("status", "未确认").execute()
    return result.data[0] if result.data else None


def get_orders_by_bill(bill_id: int):
    """获取账单下的所有订单"""
    client = get_client()
    result = client.table("orders").select("*").eq("bill_id", bill_id).order("order_id").execute()
    return result.data


def get_confirmed_orders_by_table(table_id: int):
    """获取桌台的所有已确认订单"""
    client = get_client()
    result = client.table("orders").select("*").eq("table_id", table_id).eq("status", "已确认").order("order_id").execute()
    return result.data


def confirm_order(order_id: int, bill_id: int):
    """确认订单"""
    client = get_client()
    result = client.table("orders").update({
        "status": "已确认",
        "bill_id": bill_id
    }).eq("order_id", order_id).execute()
    return result.data


# ============================================
# 订单明细相关操作
# ============================================

def add_order_item(order_id: int, dish_id: int, quantity: int, unit_price: float, flavor_choices: str = None):
    """添加订单明细"""
    client = get_client()
    result = client.table("order_items").insert({
        "order_id": order_id,
        "dish_id": dish_id,
        "quantity": quantity,
        "unit_price": unit_price,
        "flavor_choices": flavor_choices,
        "dish_status": "未制作",
        "is_rushed": False
    }).execute()
    return result.data[0] if result.data else None


def get_order_items(order_id: int):
    """获取订单明细"""
    client = get_client()
    result = client.table("order_items").select(
        "*, dishes(dish_name, category)"
    ).eq("order_id", order_id).order("item_id").execute()
    return result.data


def get_order_items_for_kitchen(order_id: int):
    """获取订单明细（后厨用，不包含已退菜）"""
    client = get_client()
    result = client.table("order_items").select(
        "*, dishes(dish_name, category)"
    ).eq("order_id", order_id).neq("dish_status", "已退菜").order("item_id").execute()
    return result.data


def update_dish_status(order_id: int, dish_id: int, new_status: str):
    """更新菜品状态"""
    client = get_client()
    result = client.table("order_items").update({
        "dish_status": new_status
    }).eq("order_id", order_id).eq("dish_id", dish_id).execute()
    return result.data


def rush_dish(order_id: int, dish_id: int):
    """催菜"""
    client = get_client()
    result = client.table("order_items").update({
        "is_rushed": True
    }).eq("order_id", order_id).eq("dish_id", dish_id).execute()
    return result.data


def refund_dish(order_id: int, dish_id: int, reason: str):
    """退菜"""
    client = get_client()
    result = client.table("order_items").update({
        "dish_status": "已退菜",
        "refund_reason": reason
    }).eq("order_id", order_id).eq("dish_id", dish_id).execute()
    return result.data


def get_item_by_order_and_dish(order_id: int, dish_id: int):
    """根据订单ID和菜品ID获取订单明细"""
    client = get_client()
    result = client.table("order_items").select("*").eq("order_id", order_id).eq("dish_id", dish_id).execute()
    return result.data[0] if result.data else None


# ============================================
# 后厨视图相关操作
# ============================================

def get_kitchen_all_orders():
    """获取后厨所有订单"""
    client = get_client()
    result = client.rpc("get_kitchen_all").execute()
    # 如果RPC不可用，使用普通查询
    if not result.data:
        result = client.table("order_items").select(
            "*, orders!inner(order_id, status, created_at), dishes(dish_name, category)"
        ).eq("orders.status", "已确认").neq("dish_status", "已退菜").order("is_rushed", desc=True).order("created_at").execute()
    return result.data


def get_kitchen_cold_orders():
    """获取凉菜房订单（凉菜、酒水）"""
    client = get_client()
    result = client.table("order_items").select(
        "*, orders!inner(order_id, status, created_at), dishes!inner(dish_name, category)"
    ).eq("orders.status", "已确认").in_("dishes.category", ["凉菜", "酒水"]).neq("dish_status", "已退菜").order("is_rushed", desc=True).execute()
    return result.data


def get_kitchen_hot_orders():
    """获取热菜房订单（热菜、汤羹、主食）"""
    client = get_client()
    result = client.table("order_items").select(
        "*, orders!inner(order_id, status, created_at), dishes!inner(dish_name, category)"
    ).eq("orders.status", "已确认").in_("dishes.category", ["热菜", "汤羹", "主食"]).neq("dish_status", "已退菜").order("is_rushed", desc=True).execute()
    return result.data


# ============================================
# 营收统计相关操作
# ============================================

def get_revenue_summary():
    """获取营收统计"""
    client = get_client()
    # 获取所有已结账账单
    bills = client.table("bills").select("*, tables(table_type)").eq("status", "已结账").order("settled_at", desc=True).execute()
    
    result = []
    for bill in bills.data:
        # 获取该账单下的所有订单
        orders = client.table("orders").select("*").eq("bill_id", bill["bill_id"]).eq("status", "已确认").execute()
        
        order_details = []
        for order in orders.data:
            # 获取订单明细
            items = client.table("order_items").select(
                "*, dishes(dish_name, category)"
            ).eq("order_id", order["order_id"]).neq("dish_status", "已退菜").execute()
            
            order_details.append({
                "order_id": order["order_id"],
                "items": items.data
            })
        
        result.append({
            "bill_id": bill["bill_id"],
            "table_id": bill["table_id"],
            "table_type": bill["tables"]["table_type"] if bill.get("tables") else None,
            "total_amount": bill["total_amount"],
            "discount_type": bill["discount_type"],
            "actual_amount": bill["actual_amount"],
            "created_at": bill["created_at"],
            "settled_at": bill["settled_at"],
            "order_details": order_details
        })
    
    return result
