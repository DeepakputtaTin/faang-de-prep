-- Write your PostgreSQL query statement below
SELECT TO_CHAR(trans_date, 'YYYY-MM') AS month,
        country,
        count(*) as trans_count,

        sum(case when state = 'approved' then 1 else 0 end) as approved_count,
        sum(amount) as trans_total_amount,
        sum(case when state = 'approved' then amount ELSE 0 end) as approved_total_amount
FROM Transactions
Group by month, country

