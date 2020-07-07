CREATE TABLE user (
    userId BIGINT,
    firstName VARCHAR,
    lastName VARCHAR
  ) WITH (
    KAFKA_TOPIC='user',
    VALUE_FORMAT='JSON'
  );

CREATE STREAM order (
    orderId BIGINT,
    userId BIGINT,
    status VARCHAR
  ) WITH (
    KAFKA_TOPIC='order',
    VALUE_FORMAT='JSON'
  );

CREATE STREAM loyalty (
    orderId BIGINT,
    loyaltyCardNumber VARCHAR
  ) WITH (
    KAFKA_TOPIC='loyalty',
    VALUE_FORMAT='JSON'
  );


CREATE STREAM loyal_orders
WITH (
    kafka_topic='loyal_orders',
    partitions=1,
    replicas=2,
    value_format='JSON'
) AS
SELECT
  l.loyaltyCardNumber as loyaltyCardNumber,
  o.orderId as orderId,
  cast(o.userId as string) as userId
FROM
  loyalty l join order o within 1 hours on l.orderId = o.orderId
WHERE
  o.status = 'CREATED'
;


CREATE STREAM loyal_orders_with_user
WITH (
    kafka_topic='loyal_orders_with_user',
    partitions=1,
    replicas=2,
    value_format='JSON'
) AS
SELECT
   l.loyaltyCardNumber as loyaltyCardNumber,
   l.orderId as orderId,
   l.userId as userId,
   u.firstName as firstName,
   u.lastName as lastName
FROM loyal_orders l JOIN user u on u.rowkey = l.userId
;
