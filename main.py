"""
聚香园餐厅点餐系统
主程序入口

系统角色：
- 顾客（Customer）：扫码绑定桌号进行点餐
- 服务员（Waiter）：协助点餐、确认订单、处理退菜
- 后厨（Chef）：查看分单（凉菜房/热菜房）
- 经理（Manager）：管理菜品和查看营收
"""

import sys
import io

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from src import utils
from src import database as db
from src.customer import customer_menu
from src.waiter import waiter_menu
from src.chef import chef_menu
from src.manager import manager_menu


def print_banner():
    """打印系统横幅"""
    banner = """
    ============================================================
    |                                                          |
    |            ** 聚 香 园 餐 厅 点 餐 系 统 **              |
    |                                                          |
    |          Ju Xiang Yuan Restaurant Order System           |
    |                                                          |
    ============================================================
    """
    print(f"{utils.Fore.CYAN}{banner}{utils.Style.RESET_ALL}")


def check_database():
    """检查数据库连接"""
    print(f"\n{utils.Fore.YELLOW}正在连接数据库...{utils.Style.RESET_ALL}")
    
    try:
        if db.test_connection():
            utils.print_success("数据库连接成功")
            return True
        else:
            utils.print_error("数据库连接失败，请检查配置")
            return False
    except Exception as e:
        utils.print_error(f"数据库连接错误: {e}")
        print("\n请确保：")
        print("1. 已在项目根目录创建 .env 文件")
        print("2. 已配置正确的 SUPABASE_URL 和 SUPABASE_KEY")
        print("3. Supabase项目中已执行 database/schema.sql 创建表结构")
        print("4. 已执行 database/init_data.sql 导入初始数据")
        return False


def main_menu():
    """主菜单"""
    while True:
        utils.clear_screen()
        print_banner()
        
        print(f"\n{utils.Fore.WHITE}请选择您的角色：{utils.Style.RESET_ALL}")
        print("=" * 60)
        print(f"  1. [顾客] - 扫码点餐")
        print(f"  2. [服务员] - 订单管理")
        print(f"  3. [后厨] - 分单制作")
        print(f"  4. [经理] - 菜品营收管理")
        print("-" * 60)
        print(f"  0. 退出系统")
        print("=" * 60)
        
        try:
            choice = int(input(f"\n{utils.Fore.WHITE}请选择 (0-4): {utils.Style.RESET_ALL}").strip())
            
            if choice == 0:
                print(f"\n{utils.Fore.CYAN}感谢使用聚香园点餐系统，再见！{utils.Style.RESET_ALL}\n")
                sys.exit(0)
            elif choice == 1:
                customer_menu()
            elif choice == 2:
                waiter_menu()
            elif choice == 3:
                chef_menu()
            elif choice == 4:
                manager_menu()
            else:
                utils.print_error("无效选择，请输入 0-4")
                utils.pause()
        except ValueError:
            utils.print_error("请输入有效的数字")
            utils.pause()
        except KeyboardInterrupt:
            print(f"\n\n{utils.Fore.CYAN}感谢使用聚香园点餐系统，再见！{utils.Style.RESET_ALL}\n")
            sys.exit(0)


def main():
    """程序主入口"""
    try:
        # 初始化颜色支持（已在utils模块中初始化）
        
        # 显示横幅
        print_banner()
        
        # 检查数据库连接
        if not check_database():
            print("\n按回车键退出...")
            input()
            sys.exit(1)
        
        # 进入主菜单
        utils.pause()
        main_menu()
        
    except KeyboardInterrupt:
        print(f"\n\n{utils.Fore.CYAN}感谢使用聚香园点餐系统，再见！{utils.Style.RESET_ALL}\n")
        sys.exit(0)
    except Exception as e:
        utils.print_error(f"系统错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
