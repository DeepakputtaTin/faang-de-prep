CREATE TABLE netflix_scd2(
    surrogate_id SERIAL PRIMARY KEY,
    content_id INT,
	title varchar(20),
	category varchar(20),
	rating varchar(20),
	region varchar(20),
	effective_date date,
	expiry_date date,
	is_current boolean
);

-- creating a trigger-- it will automatically update the old records

create or replace Function netflix_scd2_up_imp()
returns TRIGGER AS $$
begin
 	update netflix_scd2
	 set expiry_date = new.effective_date,
	 is_current = False
	 where content_id = new.content_id
	 AND is_current = true;
	Return New;
END;
$$ language plpgsql;

-- now telling the table to check before you insert anything

create trigger netflix_scd2_updation_trigger
before insert on netflix_scd2
for each row
Execute Function netflix_scd2_up_imp();


-- initial insertion
INSERT INTO netflix_scd2(content_id, title, category, rating, region, effective_date, expiry_date, is_current)
VALUES (1,'Squid Game', 'Drama', 'TV-MA', 'Global', '2021-09-17', '9999-12-31', true);

INSERT INTO netflix_scd2(content_id, title, category, rating, region, effective_date, expiry_date, is_current)
VALUES (1,'Squid Game', 'Award winning Drama', 'TV-MA', 'Global', '2026-02-26', '9999-12-31', true);

select * from netflix_scd2;

-- querying for Q4 2024

select content_id, title, category from netflix_scd2
where effective_date <= '2024-10-01' and expiry_date >'2024-10-01';
