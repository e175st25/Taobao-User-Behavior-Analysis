-- 检查behavior_type有多少种
SELECT
    behavior_type,
    COUNT(*) AS cnt
FROM user_behavior_raw
GROUP BY behavior_type;

-- 检查是否有缺失值
SELECT
SUM(user_id IS NULL) user_null,
SUM(item_id IS NULL) item_null,
SUM(category_id IS NULL) category_null,
SUM(datetime IS NULL) time_null
FROM user_behavior_raw;

-- 检查时间范围
SELECT
MIN(datetime),
MAX(datetime)
FROM user_behavior_raw;

-- 修改时间
UPDATE user_behavior
SET
    datetime = FROM_UNIXTIME(timestamp),
    date = DATE(FROM_UNIXTIME(timestamp)),
    hour = HOUR(FROM_UNIXTIME(timestamp)),
    weekday = WEEKDAY(FROM_UNIXTIME(timestamp));

-- 看异常值有多少
SELECT
    CASE
        WHEN date BETWEEN '2017-11-25' AND '2017-12-03'
            THEN 'valid'
        ELSE 'invalid'
    END AS date_status,
    COUNT(*) AS data_count
FROM user_behavior_raw
GROUP BY date_status;