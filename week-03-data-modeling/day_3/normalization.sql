CREATE TABLE normilazation_d3 (
	emp_id int primary key,
	emp_name varchar(20),
	dept_name varchar(20),
	dept_local varchar(10),
	salary int,
	mgr_id int,
	mgr_name varchar(20)
-- here emp_id, dept_name, manager_id are composite keys
);

insert into normilazation_d3 values
	(1, 'Alice', 'Engineering', 'NYC', 95000, 10, 'Bob'),
	(2, 'Carol', ' Marketing', 'LA', 75000, 11, 'Dave' ),
	(3, 'Eve', 'Engineering', 'NYC', 88000, 10, 'Bob'),
	(4, 'Frank', 'Marketing', 'LA', 72000, 11, 'Dave');

UPDATE normilazation_d3 
SET dept_name = TRIM(dept_name);

--establishing 3NF
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS managers;
create table departments(dept_id SERIAL primary key, dept_name varchar(20), dept_loc varchar(10));

create table managers(mgr_id int primary key, mgr_name varchar(20));
create table employees(emp_id int primary key , emp_name varchar(20), dept_id INT REFERENCES departments(dept_id), mgr_id INT REFERENCES managers(mgr_id), salary int );

--
TRUNCATE TABLE employees CASCADE;
TRUNCATE TABLE departments CASCADE;
TRUNCATE TABLE managers CASCADE;
SELECT n.emp_id, n.emp_name, d.dept_id, n.mgr_id, n.salary
FROM normilazation_d3 n
JOIN departments d ON d.dept_name = n.dept_name;
\


SELECT * FROM departments;

SELECT n.emp_id, n.emp_name, d.dept_id, n.mgr_id, n.salary
FROM normilazation_d3 n
JOIN departments d ON d.dept_name = n.dept_name;

-- Step 1: Check what's in the flat table
SELECT DISTINCT dept_name, dept_local, 
       LENGTH(dept_name) as name_length
FROM normilazation_d3; 


insert into departments (dept_id, dept_name,dept_loc )
select ROW_NUMBER() OVER (ORDER BY dept_name) AS dept_id, dept_name, dept_local
FROM (
    SELECT DISTINCT TRIM(dept_name) AS dept_name, dept_local
    FROM normilazation_d3
)
as distinct_depts;

select * from departments;

insert into managers(mgr_id, mgr_name)
select distinct mgr_id, mgr_name
from normilazation_d3;

insert into employees(emp_id, emp_name, dept_id, mgr_id, salary)
select distinct n.emp_id, n.emp_name, d.dept_id, n.mgr_id, n.salary
FROM normilazation_d3 n
join departments d on d.dept_name = n.dept_name;
select * from employees;

select 
	e.emp_id,
	e.emp_name,
	d.dept_name,
	d.dept_loc,
	m.mgr_id,
	m.mgr_name
	from employees e
	join departments d on d.dept_id = e.dept_id
	join managers m on m.mgr_id = e.mgr_id;

	