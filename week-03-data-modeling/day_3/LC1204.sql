-- Create the table
DROP TABLE IF EXISTS queue;
CREATE TABLE queue (
    person_id INT,
    person_name VARCHAR(20),
    weight INT,
    turn INT
);

INSERT INTO queue VALUES
(5, 'Alice', 250, 1),
(4, 'Bob', 175, 5),
(3, 'Alex', 350, 2),
(6, 'John', 400, 3),
(1, 'Winston', 500, 6),
(2, 'Marie', 200, 4);

-- Your solution
WITH run_total AS (
    SELECT 
        person_name,
        weight,
        turn,
        SUM(weight) OVER (ORDER BY turn) AS running_total
    FROM queue
    ORDER BY turn
)
SELECT person_name 
FROM run_total
WHERE running_total <= 1000
ORDER BY running_total DESC
LIMIT 1;


WITH run_total AS (
    SELECT 
        person_name,
        weight,
        turn,
        SUM(weight) OVER (ORDER BY turn) AS running_total
    FROM queue
    ORDER BY turn
)
SELECT person_name 
FROM run_total
WHERE running_total <= 1000
order by running_total desc
limit 1;