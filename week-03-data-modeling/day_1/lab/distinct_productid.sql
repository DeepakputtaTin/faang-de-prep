-- Create tables

--Warm-up: Find product_ids with inconsistent names/suppliers in fact_sales
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_products;

CREATE TABLE fact_sales (
    sale_id INT PRIMARY KEY,
    product_id INT,
    product_name VARCHAR,
    supplier_name VARCHAR,
    quantity INT,
    revenue DECIMAL
);

-- Inserting data with intentional inconsistencies
INSERT INTO fact_sales VALUES
(1, 101, 'Nike Shoes', 'Nike', 2, 150.00),
(2, 101, 'Nike Shoe', 'Nike', 1, 75.00),   -- same product_id, different name!
(3, 102, 'Zara Shirt', 'Zara', 3, 135.00),
(4, 102, 'Zara Shirt', 'Zara', 1, 45.00),  -- clean
(5, 103, 'Gucci Bag', 'Gucci', 1, 320.00),
(6, 101, 'Nike Shoes', 'Nike Corp', 2, 180.00),  -- same product_id, different supplier!
(7, 103, 'Gucci Bag', 'Gucci Italia', 1, 220.00); -- same product_id, different supplier!


--
with cte1 as(
select product_id, count(Distinct product_name) as name_count from fact_sales
group by product_id
),
cte2 as(  
select product_id, count(Distinct supplier_name) as supplier_diff from fact_sales
group by product_id
)

select c1.product_id,
		c1.name_count,
		c2.supplier_diff
from cte1 c1
join cte2 c2 on c1.product_id = c2.product_id
where c1.name_count > 1 or c2.supplier_diff > 1

--

select product_id,
		count(Distinct product_name) as name_count,
		count(Distinct supplier_name) as supplier_diff
from fact_sales
group by product_id
having count(Distinct product_name) > 1 
		or count(distinct supplier_name) > 1
