with recursive emp as(

	select employee_id,employee_name, cast(employee_name as Text) as path, manager_id, 1 as depth
	 from employees
	where employee_id = 101
	Union all

	select e.employee_id, e.employee_name,  concat(emp.path, '->', e.employee_name), e.manager_id, emp.depth +1
	from employees e
	Join emp on e.employee_id = emp.manager_id
	where emp.depth < 20
)

select * from emp;
