drop table  if exists orders;
CREATE TABLE orders AS
    SELECT * FROM (VALUES
        (1, 101, DATE '2024-01-01', 50),
        (2, 101, DATE '2024-01-02', 30),
        (3, 101, DATE '2024-01-03', 70),
        (4, 101, DATE '2024-01-05', 20),
        (5, 102, DATE '2024-01-01', 40),
        (6, 102, DATE '2024-01-02', 60),
        (7, 102, DATE '2024-01-03', 80),
        (8, 102, DATE '2024-01-04', 90)
    ) t(order_id, customer_id, order_date, amount)

select * from orders;

with row_num as(

	select order_id, customer_id, order_date, amount,
	Row_Number() over (Partition by customer_id order by order_date) as rn
	From orders
),
sub as(
	select order_id, customer_id, order_date, amount,
	order_date - (rn || ' days')::interval as grp
	from row_num
),
threeinrow as(
	select customer_id, sum(amount), count(*) as cnt, grp
	from sub
	group by customer_id, grp

)
select * from threeinrow
where cnt >= 3;