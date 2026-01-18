-- 聚香园餐厅点餐系统 - 初始测试数据
-- 适用于 Supabase (PostgreSQL)

-- ============================================
-- 1. 插入桌台数据
-- ============================================
-- 大厅圆桌 10张（每桌限坐6人）
INSERT INTO tables (table_type, capacity, status) VALUES
('大厅圆桌', 6, '空闲'),
('大厅圆桌', 6, '空闲'),
('大厅圆桌', 6, '空闲'),
('大厅圆桌', 6, '空闲'),
('大厅圆桌', 6, '空闲'),
('大厅圆桌', 6, '空闲'),
('大厅圆桌', 6, '空闲'),
('大厅圆桌', 6, '空闲'),
('大厅圆桌', 6, '空闲'),
('大厅圆桌', 6, '空闲');

-- 包间 5间（每桌限坐12人）
INSERT INTO tables (table_type, capacity, status) VALUES
('包间', 12, '空闲'),
('包间', 12, '空闲'),
('包间', 12, '空闲'),
('包间', 12, '空闲'),
('包间', 12, '空闲');

-- ============================================
-- 2. 插入菜品数据
-- ============================================

-- 热菜
INSERT INTO dishes (dish_name, category, price) VALUES
('水煮肉片', '热菜', 58.00),
('宫保鸡丁', '热菜', 42.00),
('麻婆豆腐', '热菜', 28.00),
('红烧肉', '热菜', 48.00),
('糖醋里脊', '热菜', 45.00),
('鱼香肉丝', '热菜', 38.00),
('回锅肉', '热菜', 42.00),
('干煸四季豆', '热菜', 26.00),
('蒜蓉西兰花', '热菜', 22.00),
('清炒时蔬', '热菜', 18.00);

-- 凉菜
INSERT INTO dishes (dish_name, category, price) VALUES
('口水鸡', '凉菜', 38.00),
('凉拌黄瓜', '凉菜', 12.00),
('凉拌木耳', '凉菜', 16.00),
('皮蛋豆腐', '凉菜', 18.00),
('蒜泥白肉', '凉菜', 32.00);

-- 汤羹
INSERT INTO dishes (dish_name, category, price) VALUES
('番茄蛋汤', '汤羹', 18.00),
('紫菜蛋花汤', '汤羹', 16.00),
('酸辣汤', '汤羹', 22.00),
('冬瓜排骨汤', '汤羹', 38.00),
('鸡蛋羹', '汤羹', 15.00);

-- 主食
INSERT INTO dishes (dish_name, category, price) VALUES
('米饭', '主食', 3.00),
('蛋炒饭', '主食', 18.00),
('扬州炒饭', '主食', 22.00),
('葱油拌面', '主食', 15.00),
('担担面', '主食', 20.00);

-- 酒水
INSERT INTO dishes (dish_name, category, price) VALUES
('可乐', '酒水', 8.00),
('雪碧', '酒水', 8.00),
('橙汁', '酒水', 12.00),
('青岛啤酒', '酒水', 10.00),
('茅台', '酒水', 1688.00),
('王老吉', '酒水', 8.00),
('矿泉水', '酒水', 5.00);

-- ============================================
-- 3. 插入口味选项轮次和选项数据
-- ============================================

-- 水煮肉片（dish_id=1）：辣度、油度
INSERT INTO flavor_rounds (dish_id, round_number, round_name) VALUES
(1, 1, '辣度'),
(1, 2, '油度');

INSERT INTO flavor_options (round_id, option_name) VALUES
(1, '微辣'), (1, '中辣'), (1, '特辣'),
(2, '少油'), (2, '正常油');

-- 宫保鸡丁（dish_id=2）：辣度
INSERT INTO flavor_rounds (dish_id, round_number, round_name) VALUES
(2, 1, '辣度');

INSERT INTO flavor_options (round_id, option_name) VALUES
(3, '微辣'), (3, '中辣'), (3, '特辣');

-- 麻婆豆腐（dish_id=3）：辣度、麻度
INSERT INTO flavor_rounds (dish_id, round_number, round_name) VALUES
(3, 1, '辣度'),
(3, 2, '麻度');

INSERT INTO flavor_options (round_id, option_name) VALUES
(4, '微辣'), (4, '中辣'), (4, '特辣'),
(5, '微麻'), (5, '中麻'), (5, '特麻');

-- 红烧肉（dish_id=4）：甜度
INSERT INTO flavor_rounds (dish_id, round_number, round_name) VALUES
(4, 1, '甜度');

INSERT INTO flavor_options (round_id, option_name) VALUES
(6, '少糖'), (6, '正常糖'), (6, '多糖');

-- 糖醋里脊（dish_id=5）：酸度
INSERT INTO flavor_rounds (dish_id, round_number, round_name) VALUES
(5, 1, '酸度');

INSERT INTO flavor_options (round_id, option_name) VALUES
(7, '微酸'), (7, '正常酸'), (7, '特酸');

-- 鱼香肉丝（dish_id=6）：辣度
INSERT INTO flavor_rounds (dish_id, round_number, round_name) VALUES
(6, 1, '辣度');

INSERT INTO flavor_options (round_id, option_name) VALUES
(8, '微辣'), (8, '中辣'), (8, '特辣');

-- 回锅肉（dish_id=7）：辣度
INSERT INTO flavor_rounds (dish_id, round_number, round_name) VALUES
(7, 1, '辣度');

INSERT INTO flavor_options (round_id, option_name) VALUES
(9, '微辣'), (9, '中辣'), (9, '特辣');

-- 干煸四季豆（dish_id=8）：辣度
INSERT INTO flavor_rounds (dish_id, round_number, round_name) VALUES
(8, 1, '辣度');

INSERT INTO flavor_options (round_id, option_name) VALUES
(10, '不辣'), (10, '微辣'), (10, '中辣');

-- 口水鸡（dish_id=11）：辣度
INSERT INTO flavor_rounds (dish_id, round_number, round_name) VALUES
(11, 1, '辣度');

INSERT INTO flavor_options (round_id, option_name) VALUES
(11, '微辣'), (11, '中辣'), (11, '特辣');

-- 酸辣汤（dish_id=18）：辣度、酸度
INSERT INTO flavor_rounds (dish_id, round_number, round_name) VALUES
(18, 1, '辣度'),
(18, 2, '酸度');

INSERT INTO flavor_options (round_id, option_name) VALUES
(12, '微辣'), (12, '中辣'), (12, '特辣'),
(13, '微酸'), (13, '正常酸'), (13, '多酸');

-- 担担面（dish_id=25）：辣度
INSERT INTO flavor_rounds (dish_id, round_number, round_name) VALUES
(25, 1, '辣度');

INSERT INTO flavor_options (round_id, option_name) VALUES
(14, '微辣'), (14, '中辣'), (14, '特辣');

-- 可乐（dish_id=26）：温度
INSERT INTO flavor_rounds (dish_id, round_number, round_name) VALUES
(26, 1, '温度');

INSERT INTO flavor_options (round_id, option_name) VALUES
(15, '冰'), (15, '常温');

-- 雪碧（dish_id=27）：温度
INSERT INTO flavor_rounds (dish_id, round_number, round_name) VALUES
(27, 1, '温度');

INSERT INTO flavor_options (round_id, option_name) VALUES
(16, '冰'), (16, '常温');

-- 橙汁（dish_id=28）：温度
INSERT INTO flavor_rounds (dish_id, round_number, round_name) VALUES
(28, 1, '温度');

INSERT INTO flavor_options (round_id, option_name) VALUES
(17, '冰'), (17, '常温');

-- 青岛啤酒（dish_id=29）：温度
INSERT INTO flavor_rounds (dish_id, round_number, round_name) VALUES
(29, 1, '温度');

INSERT INTO flavor_options (round_id, option_name) VALUES
(18, '冰'), (18, '常温');

-- 王老吉（dish_id=31）：温度
INSERT INTO flavor_rounds (dish_id, round_number, round_name) VALUES
(31, 1, '温度');

INSERT INTO flavor_options (round_id, option_name) VALUES
(19, '冰'), (19, '常温');

-- 注意：米饭(21)、蛋炒饭(22)、扬州炒饭(23)、葱油拌面(24)、茅台(30)、矿泉水(32)
-- 以及部分热菜蔬菜类(9,10)、凉菜(12,13,14,15)、汤羹(16,17,19,20)不需要口味选项
