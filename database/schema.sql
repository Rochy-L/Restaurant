-- 聚香园餐厅点餐系统数据库设计
-- 适用于 Supabase (PostgreSQL)

-- ============================================
-- 1. 桌台表 (tables)
-- ============================================
CREATE TABLE tables (
    table_id SERIAL PRIMARY KEY,
    table_type VARCHAR(20) NOT NULL CHECK (table_type IN ('大厅圆桌', '包间')),
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    status VARCHAR(20) NOT NULL DEFAULT '空闲' CHECK (status IN ('空闲', '就餐中', '待清理'))
);

COMMENT ON TABLE tables IS '餐厅桌台信息表';
COMMENT ON COLUMN tables.table_id IS '桌位ID';
COMMENT ON COLUMN tables.table_type IS '桌台类型：大厅圆桌/包间';
COMMENT ON COLUMN tables.capacity IS '桌台容量';
COMMENT ON COLUMN tables.status IS '桌台状态：空闲/就餐中/待清理';

-- ============================================
-- 2. 菜品分类枚举
-- ============================================
-- 菜品分类：热菜、凉菜、汤羹、主食、酒水

-- ============================================
-- 3. 菜品表 (dishes)
-- ============================================
CREATE TABLE dishes (
    dish_id SERIAL PRIMARY KEY,
    dish_name VARCHAR(100) NOT NULL,
    category VARCHAR(20) NOT NULL CHECK (category IN ('热菜', '凉菜', '汤羹', '主食', '酒水')),
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    is_available BOOLEAN NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE dishes IS '菜品信息表';
COMMENT ON COLUMN dishes.dish_id IS '菜品ID';
COMMENT ON COLUMN dishes.dish_name IS '菜品名称';
COMMENT ON COLUMN dishes.category IS '菜品分类：热菜/凉菜/汤羹/主食/酒水';
COMMENT ON COLUMN dishes.price IS '菜品价格';
COMMENT ON COLUMN dishes.is_available IS '是否上架';

-- ============================================
-- 4. 口味选项轮次表 (flavor_rounds)
-- ============================================
CREATE TABLE flavor_rounds (
    round_id SERIAL PRIMARY KEY,
    dish_id INTEGER NOT NULL REFERENCES dishes(dish_id) ON DELETE CASCADE,
    round_number INTEGER NOT NULL CHECK (round_number > 0),
    round_name VARCHAR(50) NOT NULL,
    UNIQUE(dish_id, round_number)
);

COMMENT ON TABLE flavor_rounds IS '菜品口味选项轮次表';
COMMENT ON COLUMN flavor_rounds.round_id IS '轮次ID';
COMMENT ON COLUMN flavor_rounds.dish_id IS '关联菜品ID';
COMMENT ON COLUMN flavor_rounds.round_number IS '轮次序号';
COMMENT ON COLUMN flavor_rounds.round_name IS '轮次名称（如：辣度、温度等）';

-- ============================================
-- 5. 口味选项表 (flavor_options)
-- ============================================
CREATE TABLE flavor_options (
    option_id SERIAL PRIMARY KEY,
    round_id INTEGER NOT NULL REFERENCES flavor_rounds(round_id) ON DELETE CASCADE,
    option_name VARCHAR(50) NOT NULL
);

COMMENT ON TABLE flavor_options IS '具体口味选项表';
COMMENT ON COLUMN flavor_options.option_id IS '选项ID';
COMMENT ON COLUMN flavor_options.round_id IS '关联轮次ID';
COMMENT ON COLUMN flavor_options.option_name IS '选项名称（如：微辣、中辣等）';

-- ============================================
-- 6. 账单表 (bills)
-- ============================================
CREATE TABLE bills (
    bill_id SERIAL PRIMARY KEY,
    table_id INTEGER NOT NULL REFERENCES tables(table_id),
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    actual_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    discount_type VARCHAR(20) CHECK (discount_type IN ('八折', '抹零', NULL)),
    status VARCHAR(20) NOT NULL DEFAULT '未结账' CHECK (status IN ('未结账', '已结账')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    settled_at TIMESTAMP
);

COMMENT ON TABLE bills IS '账单表';
COMMENT ON COLUMN bills.bill_id IS '账单ID';
COMMENT ON COLUMN bills.table_id IS '关联桌位ID';
COMMENT ON COLUMN bills.total_amount IS '账单总额';
COMMENT ON COLUMN bills.actual_amount IS '实际消费额（折扣后）';
COMMENT ON COLUMN bills.discount_type IS '折扣类型：八折/抹零';
COMMENT ON COLUMN bills.status IS '账单状态';
COMMENT ON COLUMN bills.created_at IS '创建时间';
COMMENT ON COLUMN bills.settled_at IS '结账时间';

-- ============================================
-- 7. 订单表 (orders)
-- ============================================
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    table_id INTEGER NOT NULL REFERENCES tables(table_id),
    bill_id INTEGER REFERENCES bills(bill_id),
    status VARCHAR(20) NOT NULL DEFAULT '未确认' CHECK (status IN ('未确认', '已确认')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE orders IS '订单表';
COMMENT ON COLUMN orders.order_id IS '订单ID';
COMMENT ON COLUMN orders.table_id IS '关联桌位ID';
COMMENT ON COLUMN orders.bill_id IS '关联账单ID';
COMMENT ON COLUMN orders.status IS '订单状态：未确认/已确认';
COMMENT ON COLUMN orders.created_at IS '创建时间';

-- ============================================
-- 8. 订单明细表 (order_items)
-- ============================================
CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    dish_id INTEGER NOT NULL REFERENCES dishes(dish_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL,
    flavor_choices TEXT, -- JSON格式存储口味选择，如 '[{"轮次":"辣度","选项":"微辣"},{"轮次":"油度","选项":"少油"}]'
    dish_status VARCHAR(20) NOT NULL DEFAULT '未制作' CHECK (dish_status IN ('未制作', '制作中', '已完成', '已退菜')),
    is_rushed BOOLEAN NOT NULL DEFAULT FALSE,
    refund_reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE order_items IS '订单明细表';
COMMENT ON COLUMN order_items.item_id IS '明细ID';
COMMENT ON COLUMN order_items.order_id IS '关联订单ID';
COMMENT ON COLUMN order_items.dish_id IS '关联菜品ID';
COMMENT ON COLUMN order_items.quantity IS '菜品数量';
COMMENT ON COLUMN order_items.unit_price IS '下单时单价';
COMMENT ON COLUMN order_items.flavor_choices IS '口味选择（JSON格式）';
COMMENT ON COLUMN order_items.dish_status IS '菜品状态：未制作/制作中/已完成/已退菜';
COMMENT ON COLUMN order_items.is_rushed IS '是否催菜';
COMMENT ON COLUMN order_items.refund_reason IS '退菜理由';
COMMENT ON COLUMN order_items.created_at IS '创建时间';

-- ============================================
-- 9. 创建索引
-- ============================================
CREATE INDEX idx_tables_status ON tables(status);
CREATE INDEX idx_dishes_category ON dishes(category);
CREATE INDEX idx_dishes_available ON dishes(is_available);
CREATE INDEX idx_orders_table_id ON orders(table_id);
CREATE INDEX idx_orders_bill_id ON orders(bill_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_dish_status ON order_items(dish_status);
CREATE INDEX idx_order_items_is_rushed ON order_items(is_rushed);
CREATE INDEX idx_bills_table_id ON bills(table_id);
CREATE INDEX idx_bills_status ON bills(status);

-- ============================================
-- 10. 视图：菜单视图（显示在售菜品及口味选项）
-- ============================================
CREATE OR REPLACE VIEW v_menu AS
SELECT 
    d.dish_id,
    d.dish_name,
    d.category,
    d.price,
    COALESCE(
        (SELECT json_agg(
            json_build_object(
                'round_number', fr.round_number,
                'round_name', fr.round_name,
                'options', (
                    SELECT json_agg(fo.option_name ORDER BY fo.option_id)
                    FROM flavor_options fo
                    WHERE fo.round_id = fr.round_id
                )
            ) ORDER BY fr.round_number
        )
        FROM flavor_rounds fr
        WHERE fr.dish_id = d.dish_id
        ), '[]'::json
    ) AS flavor_rounds
FROM dishes d
WHERE d.is_available = TRUE
ORDER BY d.category, d.dish_id;

-- ============================================
-- 11. 视图：后厨分单视图 - 凉菜房
-- ============================================
CREATE OR REPLACE VIEW v_kitchen_cold AS
SELECT 
    oi.item_id,
    o.order_id,
    oi.dish_id,
    d.dish_name,
    d.category,
    oi.unit_price,
    oi.quantity,
    oi.flavor_choices,
    oi.dish_status,
    oi.is_rushed,
    o.created_at AS order_time
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN dishes d ON oi.dish_id = d.dish_id
WHERE o.status = '已确认'
  AND d.category IN ('凉菜', '酒水')
  AND oi.dish_status != '已退菜'
ORDER BY oi.is_rushed DESC, o.created_at ASC;

-- ============================================
-- 12. 视图：后厨分单视图 - 热菜房
-- ============================================
CREATE OR REPLACE VIEW v_kitchen_hot AS
SELECT 
    oi.item_id,
    o.order_id,
    oi.dish_id,
    d.dish_name,
    d.category,
    oi.unit_price,
    oi.quantity,
    oi.flavor_choices,
    oi.dish_status,
    oi.is_rushed,
    o.created_at AS order_time
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN dishes d ON oi.dish_id = d.dish_id
WHERE o.status = '已确认'
  AND d.category IN ('热菜', '汤羹', '主食')
  AND oi.dish_status != '已退菜'
ORDER BY oi.is_rushed DESC, o.created_at ASC;

-- ============================================
-- 13. 视图：后厨全部订单视图
-- ============================================
CREATE OR REPLACE VIEW v_kitchen_all AS
SELECT 
    oi.item_id,
    o.order_id,
    oi.dish_id,
    d.dish_name,
    d.category,
    oi.unit_price,
    oi.quantity,
    oi.flavor_choices,
    oi.dish_status,
    oi.is_rushed,
    o.created_at AS order_time
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN dishes d ON oi.dish_id = d.dish_id
WHERE o.status = '已确认'
  AND oi.dish_status != '已退菜'
ORDER BY oi.is_rushed DESC, o.created_at ASC;

-- ============================================
-- 14. 视图：营收统计视图
-- ============================================
CREATE OR REPLACE VIEW v_revenue_summary AS
SELECT 
    b.bill_id,
    b.table_id,
    t.table_type,
    b.total_amount,
    b.discount_type,
    b.actual_amount,
    b.created_at,
    b.settled_at,
    (
        SELECT json_agg(
            json_build_object(
                'order_id', o.order_id,
                'items', (
                    SELECT json_agg(
                        json_build_object(
                            'dish_id', oi.dish_id,
                            'dish_name', d.dish_name,
                            'category', d.category,
                            'unit_price', oi.unit_price,
                            'quantity', oi.quantity,
                            'flavor_choices', oi.flavor_choices,
                            'subtotal', oi.unit_price * oi.quantity
                        )
                    )
                    FROM order_items oi
                    JOIN dishes d ON oi.dish_id = d.dish_id
                    WHERE oi.order_id = o.order_id
                      AND oi.dish_status != '已退菜'
                )
            )
        )
        FROM orders o
        WHERE o.bill_id = b.bill_id
          AND o.status = '已确认'
    ) AS order_details
FROM bills b
JOIN tables t ON b.table_id = t.table_id
WHERE b.status = '已结账'
ORDER BY b.settled_at DESC;
