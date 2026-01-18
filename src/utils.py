"""
工具函数模块
提供通用的输入输出和格式化功能
"""

import os
import json
from tabulate import tabulate
from colorama import init, Fore, Back, Style

# 初始化colorama
init(autoreset=True)


def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"{Fore.CYAN}{Style.BRIGHT}  {title}")
    print("=" * 60)


def print_success(message: str):
    """打印成功信息"""
    print(f"{Fore.GREEN}[OK] {message}")


def print_error(message: str):
    """打印错误信息"""
    print(f"{Fore.RED}[X] {message}")


def print_warning(message: str):
    """打印警告信息"""
    print(f"{Fore.YELLOW}[!] {message}")


def print_info(message: str):
    """打印提示信息"""
    print(f"{Fore.BLUE}-> {message}")


def print_highlight(message: str):
    """打印高亮信息（用于催菜等）"""
    print(f"{Back.YELLOW}{Fore.BLACK}{Style.BRIGHT} {message} {Style.RESET_ALL}")


def print_table(data: list, headers: list, title: str = None):
    """打印表格"""
    if title:
        print(f"\n{Fore.CYAN}{title}")
    if data:
        print(tabulate(data, headers=headers, tablefmt="pretty", stralign="left"))
    else:
        print_warning("暂无数据")


def get_input(prompt: str) -> str:
    """获取用户输入"""
    return input(f"{Fore.WHITE}{prompt}: ").strip()


def get_int_input(prompt: str, min_val: int = None, max_val: int = None) -> int:
    """获取整数输入"""
    while True:
        try:
            value = int(input(f"{Fore.WHITE}{prompt}: ").strip())
            if min_val is not None and value < min_val:
                print_error(f"请输入不小于 {min_val} 的数字")
                continue
            if max_val is not None and value > max_val:
                print_error(f"请输入不大于 {max_val} 的数字")
                continue
            return value
        except ValueError:
            print_error("请输入有效的数字")


def get_float_input(prompt: str, min_val: float = None) -> float:
    """获取浮点数输入"""
    while True:
        try:
            value = float(input(f"{Fore.WHITE}{prompt}: ").strip())
            if min_val is not None and value < min_val:
                print_error(f"请输入不小于 {min_val} 的数字")
                continue
            return value
        except ValueError:
            print_error("请输入有效的数字")


def get_choice(prompt: str, options: list) -> str:
    """获取选择输入"""
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    while True:
        try:
            choice = int(input(f"{Fore.WHITE}请选择 (1-{len(options)}): ").strip())
            if 1 <= choice <= len(options):
                return options[choice - 1]
            print_error(f"请输入 1 到 {len(options)} 之间的数字")
        except ValueError:
            print_error("请输入有效的数字")


def confirm(prompt: str) -> bool:
    """确认操作"""
    while True:
        choice = input(f"{Fore.WHITE}{prompt} (y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            return True
        elif choice in ['n', 'no', '否']:
            return False
        print_error("请输入 y 或 n")


def pause():
    """暂停，等待用户按键"""
    input(f"\n{Fore.CYAN}按回车键继续...")


def format_price(price: float) -> str:
    """格式化价格"""
    return f"¥{price:.2f}"


def format_flavor_choices(flavor_json: str) -> str:
    """格式化口味选择显示"""
    if not flavor_json:
        return "-"
    try:
        choices = json.loads(flavor_json)
        if not choices:
            return "-"
        return ", ".join([f"{c['轮次']}:{c['选项']}" for c in choices])
    except:
        return flavor_json


def format_status(status: str, is_rushed: bool = False) -> str:
    """格式化菜品状态显示"""
    if is_rushed and status in ['未制作', '制作中']:
        return f"{Back.YELLOW}{Fore.BLACK}【催】{status}{Style.RESET_ALL}"
    
    status_colors = {
        '未制作': Fore.YELLOW,
        '制作中': Fore.BLUE,
        '已完成': Fore.GREEN,
        '已退菜': Fore.RED
    }
    color = status_colors.get(status, Fore.WHITE)
    return f"{color}{status}{Style.RESET_ALL}"


def show_menu(title: str, options: list) -> int:
    """显示菜单并获取选择"""
    print_header(title)
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    print(f"  0. 返回上级菜单")
    print("-" * 60)
    
    while True:
        try:
            choice = int(input(f"{Fore.WHITE}请选择操作: ").strip())
            if 0 <= choice <= len(options):
                return choice
            print_error(f"请输入 0 到 {len(options)} 之间的数字")
        except ValueError:
            print_error("请输入有效的数字")
