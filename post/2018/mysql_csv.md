## import into mysql from csv

```mysql
CREATE TABLE "geohash_popularity" (
  "geohash" char(6) NOT NULL DEFAULT '',
  "top_k" text,
  "city_id" int(11) DEFAULT NULL,
  PRIMARY KEY ("geohash")
);

LOAD DATA LOCAL INFILE 'geohash_popularity_ddb_format.csv'
INTO TABLE geohash_popularity
FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(@dummy, geohash, top_k, city_id);
```





```mysql
CREATE TABLE "merchant_features" (
  "merchant_id" char(20) NOT NULL DEFAULT '',
  "value" text,
  "city_id" int(11) DEFAULT NULL,
  PRIMARY KEY ("merchant_id")
);


LOAD DATA LOCAL INFILE 'merchant_features_engg.csv'
INTO TABLE merchant_features
FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(@dummy, merchant_id, city_id, value);

```



```mysql
CREATE TABLE "keyword_merchant_features" (
  "merchant_id" char(20) NOT NULL DEFAULT '',
  "value" text,
  "city_id" int(11) DEFAULT NULL,
  "keyword" varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY ("merchant_id")
);


LOAD DATA LOCAL INFILE 'keyword_merchant_features_engg.csv'
INTO TABLE keyword_merchant_features
FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(@dummy, keyword, merchant_id, city_id, value);

```







