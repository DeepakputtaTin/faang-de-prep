CREATE TABLE likes_by_user (
    user_id     UUID,   -- partition key  (hint: what are we filtering BY?)
    liked_at  TIMESTAMP,  -- clustering key
    post_id     UUID,
    PRIMARY KEY (user_id, liked_at)
)With CLUSTERING order by(liked_at DESC);

-- Pattern 1 (fill this in!)
CREATE TABLE likes_by_post (
    post_id    UUID,   -- filter: "get likes FOR A POST"
    liked_at TIMESTAMP,
    user_id  UUID,
    PRIMARY KEY (post_id, liked_at)
) WITH CLUSTERING ORDER BY (liked_at DESC);

-----

create table fan_out_on_write(
	user_id UUID,
	tweet_id UUID,
	time_stamp TIMESTAMP
	PRIMARY KEY ( tweet_id, time_stamp)
)  WITH CLUSTERING ORDER BY (time_stamp Desc);


create table fan_out_on_read(
	user_id UUID,
	tweet_id UUID,
	time_stamp TIMESTAMP
	PRIMARY KEY (user_id, time_stamp)
)  WITH CLUSTERING ORDER BY (time_stamp Desc);

for Writre: we will be pushing the tweets to write table 
and for read: we will be pullung the tweets of followed users

I would choose fan-out-on read to pull the 20 most recent tweets for user X's timeline

Partition key - user Id,,
cluestering key time_stamp desc