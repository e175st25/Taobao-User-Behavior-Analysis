 -- user_id一共有多少个
 SELECT COUNT(DISTINCT user_id) FROM user_behavior_raw
 where date BETWEEN '2017-11-25' AND '2017-12-03'

 -- item_id 一共有多少个
SELECT COUNT(DISTINCT item_id)
FROM user_behavior_raw
where date BETWEEN '2017-11-25' AND '2017-12-03'

-- category_id一共有多少个
SELECT COUNT(DISTINCT category_id)
FROM user_behavior_raw
where date BETWEEN '2017-11-25' AND '2017-12-03'

-- 行为分布
select behavior_type,
count(*) cnt
from user_behavior_raw
where date BETWEEN '2017-11-25' AND '2017-12-03'
group by behavior_type

-- 时间分析
select date, behavior_type,
count(*) cnt
from user_behavior_raw
where date BETWEEN '2017-11-25' AND '2017-12-03'
group by date, behavior_type

-- 每个商品被多少人重复浏览过
select item_id, count(*) as repeat_view_users
from (
select user_id, behavior_type, item_id
from user_behavior_raw
where date BETWEEN '2017-11-25' AND '2017-12-03' and behavior_type = 'pv'
group by user_id, item_id
having count(*)>1
) tab
group by item_id
order by repeat_view_users desc;

-- 按照用户-品类-商品细分的各行为统计表(基本表，需要python进一步处理)
select user_id, item_id,
category_id, behavior_type,
count(behavior_type)
min(datetime) first_behavior_time,
max(datetime) last_behavior_time
from user_behavior_raw
where date BETWEEN '2017-11-25' AND '2017-12-03'
group by user_id, category_id, item_id, behavior_type

-- 按照category-item
select category_id, behavior_type, item_id,
count(behavior_type)
from user_behavior_raw
where date BETWEEN '2017-11-25' AND '2017-12-03'
group by category_id, item_id, behavior_type

-- 每日每小时行为数据（用于分析趋势）
select date, hour, behavior_type,
       count(*) behavior_count
from user_behavior_raw
where date BETWEEN '2017-11-25' AND '2017-12-03'
group by date, hour, behavior_type
order by date, hour

-- 日趋势
select date, behavior_type,
count(*) behavior_count
from user_behavior_raw
where date BETWEEN '2017-11-25' AND '2017-12-03'
group by date, behavior_type
order by date

-- 每小时活跃用户
select date, hour, count(distinct user_id) active_user
from user_behavior_raw
where date BETWEEN '2017-11-25' AND '2017-12-03'
group by date, hour
order by date, hour