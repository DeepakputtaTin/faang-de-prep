CREATE TABLE dim_customer_scd2 (
    surrogate_id SERIAL PRIMARY KEY,
    customer_id INT,
	name varchar(20),
	city varchar(20),
	effective_date date,
	expiry_date date,
	is_current boolean
    -- YOUR CODE HERE: add name, city columns
    -- YOUR CODE HERE: add effective_date, expiry_date, is_current columns
);

insert into dim_customer_scd2(customer_id, name, city, effective_date, expiry_date, is_current )
	values 
	( 101, 'Alice', 'New York', '2026-02-25', '9999-12-31', true )

select * from dim_customer_scd2;

-- if alice moved to Kansas City

update dim_customer_scd2 set expiry_date = '2026-02-25',  is_current = False
	Where customer_id = 1 ;


insert into dim_customer_scd2(customer_id, name, city, effective_date, expiry_date, is_current )
	values 
	( 101, 'Alice', 'Kansas City', '2026-02-25', '9999-12-31', true );

Select * from dim_customer_scd2 where customer_id = 101 and is_current = true;


-- creating a trigger
CREATE OR REPLACE FUNCTION handle_scd2()

returns TRIGGER AS $$

Begin

	-- When a new row is inserted, expire the current active row
	UPDATE dim_customer_scd2
	SET expiry_date = new.effective_date,
		is_current = FALSE
	where customer_id = new.customer_id
	AND is_current = true;

	Return New;
END;
$$ Language plpgsql;

-- attaching trigger to the table

create trigger scd2_trigger
before INSERT on dim_customer_scd2
for each row
Execute Function handle_scd2()

INSERT INTO dim_customer_scd2(customer_id, name, city, effective_date, expiry_date, is_current)
VALUES (102, 'Bob', 'London', '2024-01-01', '9999-12-31', TRUE);

INSERT INTO dim_customer_scd2(customer_id, name, city, effective_date, expiry_date, is_current)
VALUES (102, 'Bob', 'Paris', '2025-06-01', '9999-12-31', TRUE);


INSERT INTO dim_customer_scd2(customer_id, name, city, effective_date, expiry_date, is_current)
VALUES (103, 'Carol', 'Berlin', '2024-01-01', '9999-12-31', TRUE);

INSERT INTO dim_customer_scd2(customer_id, name, city, effective_date, expiry_date, is_current)
VALUES (103, 'Carol', 'Munich', '2025-09-01', '9999-12-31', TRUE);

select * from dim_customer_scd2;

SELECT * FROM dim_customer_scd2 ORDER BY customer_id, effective_date;