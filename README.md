# 聚香园餐厅点餐系统

《数据库应用》课程设计项目 - 中餐厅扫码点餐管理系统

## 项目简介

一家名为"聚香园"的中餐厅点餐系统，支持顾客入座后扫码点餐、加菜、退菜，并能管理桌台的占用情况。

## 系统角色

| 角色 | 功能说明 |
|------|----------|
| 顾客（Customer） | 扫码绑定桌号进行点餐 |
| 服务员（Waiter） | 协助点餐、确认订单、处理退菜、结账 |
| 后厨（Chef） | 查看分单（凉菜房/热菜房）、更新菜品状态 |
| 经理（Manager） | 管理菜品和查看营收统计 |

## 技术栈

- **数据库**: Supabase (PostgreSQL云数据库)
- **后端语言**: Python 3.8+
- **主要依赖**: 
  - supabase-py (数据库客户端)
  - tabulate (表格美化)
  - colorama (控制台颜色)

## 项目结构

```
order/
├── main.py                 # 主程序入口
├── requirements.txt        # Python依赖
├── config_example.txt      # 配置示例
├── README.md              # 项目说明
├── database/
│   ├── schema.sql         # 数据库表结构
│   └── init_data.sql      # 初始测试数据
└── src/
    ├── __init__.py
    ├── database.py        # 数据库操作模块
    ├── utils.py           # 工具函数模块
    ├── customer.py        # 顾客功能模块
    ├── waiter.py          # 服务员功能模块
    ├── chef.py            # 后厨功能模块
    └── manager.py         # 经理功能模块
```

## 安装与配置

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 配置Supabase

1. 访问 [Supabase](https://supabase.com/) 并注册账户
2. 创建新项目
3. 在项目根目录创建 `.env` 文件：

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-key
```

### 3. 初始化数据库

在Supabase SQL编辑器中执行以下SQL脚本：

1. 先执行 `database/schema.sql` 创建表结构
2. 再执行 `database/init_data.sql` 导入初始数据

### 4. 运行系统

```bash
python main.py
```

## 数据库设计

### ER图主要实体

- **桌台(tables)**: 桌位ID、桌台类型、容量、状态
- **菜品(dishes)**: 菜品ID、名称、分类、价格
- **口味轮次(flavor_rounds)**: 关联菜品的口味选项轮次
- **口味选项(flavor_options)**: 具体口味选项
- **账单(bills)**: 账单ID、桌位、金额、折扣
- **订单(orders)**: 订单ID、桌位、账单、状态
- **订单明细(order_items)**: 菜品详情、口味选择、制作状态

### 表关系

```
tables (1) ←→ (n) bills
tables (1) ←→ (n) orders
bills (1) ←→ (n) orders
orders (1) ←→ (n) order_items
dishes (1) ←→ (n) order_items
dishes (1) ←→ (n) flavor_rounds
flavor_rounds (1) ←→ (n) flavor_options
```

## 功能说明

### 顾客功能
- 查看空闲桌位
- 扫码绑定桌位（开台）
- 查看菜单（含口味选项）
- 点菜/加菜（支持多轮口味选择）
- 查看当前订单明细
- 催菜

### 服务员功能
- 查看全部桌位
- 管理桌位状态（清理桌台）
- 开台
- 查看菜单
- 协助点菜/加菜
- 查看当前订单明细
- 确认订单（提交后厨）
- 退菜（填写理由）
- 结账（支持八折/抹零）

### 后厨功能
- 查看所有下单
- 查看分单（凉菜房：凉菜、酒水；热菜房：热菜、汤羹、主食）
- 更新菜品状态（未制作→制作中→已完成）
- 催菜高亮显示

### 经理功能
- 菜品管理
  - 查看所有菜品
  - 添加菜品（含口味选项配置）
  - 下架菜品
- 营收统计
  - 汇总报表
  - 详细明细

## 业务流程

```
1. 开台: 顾客扫码/服务员开台 → 桌台状态变为"就餐中" → 创建账单和订单

2. 点餐: 选择菜品 → 选择口味 → 选择数量 → 加入当前订单

3. 确认订单: 服务员确认 → 订单提交后厨 → 创建新订单（用于加菜）

4. 后厨制作: 查看分单 → 开始制作 → 完成制作

5. 结账: 汇总所有订单 → 选择折扣 → 结算 → 桌台状态变为"待清理"

6. 清台: 服务员清理 → 桌台状态变为"空闲"
```

## 注意事项

1. 订单需要服务员确认后才会提交给后厨
2. 只有"未制作"或"制作中"状态的菜品可以退菜或催菜
3. 结账前需确保没有未确认的订单
4. 下架菜品会永久删除该菜品及其口味选项

## 作者

数据库应用课程设计作品
