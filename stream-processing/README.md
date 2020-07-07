Создаем неймспейс и переключаемся на него:

```
(python3) ➜  ksql git:(master) ✗ kubectl create namespace ksql
namespace/ksql created
(python3) ➜  ksql git:(master) ✗ kubectl config set-context --current --namespace=ksql
Context "minikube" modified.
```

Запускаем confluent platform, вместе с кафкой, ksql, zookeeper, kafka connect и т.д.
```
➜  ksql git:(master) ✗ helm repo add confluentinc https://confluentinc.github.io/cp-helm-charts/
"confluentinc" has been added to your repositories
➜  stream-processing git:(master) ✗ helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "confluentinc" chart repository
Update Complete. ⎈ Happy Helming!⎈
➜  ksql git:(master) ✗ helm install cp confluentinc/cp-helm-charts -f cp_values.yaml
```

Запускаем под с клиентом для кафки, чтобы можно было удобно посылать сообщения и т.д.
```
➜  ksql git:(master) ✗
➜  ksql git:(master) ✗ kubectl apply -f kafka-client.yaml
pod/kafka-client created
```

Запускаем под с cli под ksql.
```
kubectl run ksql http://cp-cp-ksql-server:8088  --rm -it --image=confluentinc/cp-ksqldb-cli:5.5.0
```

Создаем топик заказ: User
```
kubectl exec kafka-client -- kafka-topics --zookeeper cp-cp-zookeeper:2181 --topic user --create --partitions 1 --replication-factor 2
```

Смотрим топики в ksql:
```
ksql> show topics
>;

 Kafka Topic                | Partitions | Partition Replicas
--------------------------------------------------------------
 cp-cp-kafka-connect-config | 1          | 3
 cp-cp-kafka-connect-offset | 25         | 3
 cp-cp-kafka-connect-status | 5          | 3
 user                       | 1          | 2
--------------------------------------------------------------
ksql>
```

Кидаем туда несколько сообщений (событий) в топик user
```
kubectl exec -it kafka-client -- kafka-console-producer --broker-list cp-cp-kafka-headless:9092 --property key.separator=, --property parse.key=true --topic user
>12,{"userId": 12, "lastName": "Ivanov", "firstName": "Ivan"}
13,{"userId": 13, "lastName": "Petrov", "firstName": "Petr"}
14,{"userId": 14, "lastName": "Vasiliev", "firstName": "Vasiliy"}
>>>%
```

Создаем табличку user
```
CREATE TABLE user (
    userId BIGINT,
    firstName VARCHAR,
    lastName VARCHAR
  ) WITH (
    KAFKA_TOPIC='user',
    VALUE_FORMAT='JSON'
  );
```

Смотрим табличку (видим, что он перечитал все сообщения с самого начала)
```
ksql> select * from user emit changes;
+-----------------+-----------------+-----------------+-----------------+-----------------+
|ROWTIME          |ROWKEY           |USERID           |FIRSTNAME        |LASTNAME         |
+-----------------+-----------------+-----------------+-----------------+-----------------+
|1593969749822    |12               |12               |Ivan             |Ivanov           |
|1593969749827    |13               |13               |Petr             |Petrov           |
|1593969749827    |14               |14               |Vasiliy          |Vasiliev         |
```

Добавляем еще событий в топик:
```
➜  ksql git:(master) ✗ kubectl exec -it kafka-client -- kafka-console-producer --broker-list cp-cp-kafka-headless:9092 --property key.separator=, --property parse.key=true --topic user
>14,{"userId": 14, "lastName": "Vasiliev", "firstName": "Vasilius"}
>13,{"userId": 13, "lastName": "Petrov", "firstName": "Pyotr"}
>
```

Перечитываем табличку:
```
ksql> select * from user emit changes;
+-----------------+-----------------+-----------------+-----------------+-----------------+
|ROWTIME          |ROWKEY           |USERID           |FIRSTNAME        |LASTNAME         |
+-----------------+-----------------+-----------------+-----------------+-----------------+
|1593969749822    |12               |12               |Ivan             |Ivanov           |
|1593969949481    |14               |14               |Vasilius         |Vasiliev         |
|1593971099342    |13               |13               |Pyotr            |Petrov           |
```


Создаем топик заказ: Order
```
kubectl exec kafka-client -- kafka-topics --zookeeper cp-cp-zookeeper:2181 --topic order --create --partitions 1 --replication-factor 2
```

Смотрим топики:
```
ksql> show topics;

 Kafka Topic                | Partitions | Partition Replicas
--------------------------------------------------------------
 cp-cp-kafka-connect-config | 1          | 3
 cp-cp-kafka-connect-offset | 25         | 3
 cp-cp-kafka-connect-status | 5          | 3
 order                      | 1          | 2
 user                       | 1          | 2
--------------------------------------------------------------
ksql>
```

Кидаем туда несколько сообщений (событий).
```
➜  ksql git:(master) ✗ kubectl exec -it kafka-client -- kafka-console-producer --broker-list cp-cp-kafka-headless:9092 --property key.separator=, --property parse.key=true --topic order
>42,{"orderId": 42, "userId": 12, "status": "CREATED"}
43,{"orderId": 43, "userId": 13, "status": "CREATED"}
44,{"orderId": 44, "userId": 14, "status": "CREATED"}
45,{"orderId": 45, "userId": 15, "status": "CREATED"}
46,{"orderId": 46, "userId": 16, "status": "CREATED"}
46,{"orderId": 46, "userId": 16, "status": "UPDATED"}
>>>>>>
```

Прочитаем топик:
```
ksql> print 'order' from beginning;
Key format: JSON or KAFKA_STRING
Value format: JSON or KAFKA_STRING
rowtime: 7/5/20 6:06:14 PM UTC, key: 42, value: {"orderId": 42, "userId": 12, "status": "CREATED"}
rowtime: 7/5/20 6:06:14 PM UTC, key: 43, value: {"orderId": 43, "userId": 13, "status": "CREATED"}
rowtime: 7/5/20 6:06:14 PM UTC, key: 44, value: {"orderId": 44, "userId": 14, "status": "CREATED"}
rowtime: 7/5/20 6:06:14 PM UTC, key: 45, value: {"orderId": 45, "userId": 15, "status": "CREATED"}
rowtime: 7/5/20 6:06:14 PM UTC, key: 46, value: {"orderId": 46, "userId": 16, "status": "CREATED"}
rowtime: 7/5/20 6:06:14 PM UTC, key: 46, value: {"orderId": 46, "userId": 16, "status": "UPDATED"}

```

Создаем стрим 'order'
```
CREATE STREAM order (
    orderId BIGINT,
    userId BIGINT,
    status VARCHAR
  ) WITH (
    KAFKA_TOPIC='order',
    VALUE_FORMAT='JSON'
  );
```
```
ksql> CREATE STREAM order (
>    orderId BIGINT,
>    userId BIGINT,
>    status VARCHAR
>  ) WITH (
>    KAFKA_TOPIC='order',
>    VALUE_FORMAT='JSON'
>  );
>

 Message
----------------
 Stream created
----------------
```

Запустим 
```
ksql> select * from order emit changes;
```

Добавим еще одно событие в топик
```
>>>>>>47,{"orderId": 47, "userId": 17, "status": "CREATED"}
>
```

Видим, что событие пришло в стрим:
```
ksql> select * from order emit changes;
+-----------------+-----------------+-----------------+-----------------+-----------------+
|ROWTIME          |ROWKEY           |ORDERID          |USERID           |STATUS           |
+-----------------+-----------------+-----------------+-----------------+-----------------+
|1593972609088    |47               |47               |17               |CREATED          |
```





Создаем топик с событиями от сервиса "лояльности"

```
kubectl exec kafka-client -- kafka-topics --zookeeper cp-cp-zookeeper:2181 --topic loyalty --create --partitions 1 --replication-factor 2
```

Кидаем в топик про лояльность несколько сообщений:
```
kubectl exec -it kafka-client -- kafka-console-producer --broker-list cp-cp-kafka-headless:9092 --property key.separator=, --property parse.key=true --topic loyalty

42,{"loyaltyCardNumber": "42-1231", "orderId": 42}
43,{"loyaltyCardNumber": "43-1331", "orderId": 43}
44,{"loyaltyCardNumber": "44-1431", "orderId": 44}
45,{"loyaltyCardNumber": "45-1531", "orderId": 45}
46,{"loyaltyCardNumber": "46-1631", "orderId": 46}
```



Создаем стрим loyalty

```sql
CREATE STREAM loyal_orders
WITH (
    kafka_topic='loyal_orders',
    partitions=1,
    replicas=2,
    value_format='JSON'
)
AS
SELECT
l.loyaltyCardNumber as loyaltyCardNumber, o.orderId as orderId, cast(o.userId as string) as userId
FROM
loyalty l join order o within 1 hours on l.orderId = o.orderId
WHERE
o.status = 'CREATED'
;
```


```
>    replicas=2,
>    value_format='JSON'
>)
>AS
>SELECT
>  l.loyaltyCardNumber as loyaltyCardNumber, o.orderId as orderId, o.userId as userId
>FROM
>loyalty l join order o within 1 hours on l.orderId = o.orderId
>WHERE
>o.status = 'CREATED'
>;
>

 Message
--------------------------------------------
 Created query with ID CSAS_LOYAL_ORDERS_19
--------------------------------------------
ksql>
```

Смотрим, что топик loyal_orders cоздался

```
ksql> show topics;

 Kafka Topic                | Partitions | Partition Replicas
--------------------------------------------------------------
 cp-cp-kafka-connect-config | 1          | 3
 cp-cp-kafka-connect-offset | 25         | 3
 cp-cp-kafka-connect-status | 5          | 3
 loyal_orders               | 1          | 2
 loyalty                    | 1          | 2
 order                      | 1          | 2
 user                       | 1          | 2
--------------------------------------------------------------
ksql>
```

Добавляем событий в оба топика:

```
>%                                                                                       ➜  ksql git:(master) ✗ kubectl exec -it kafka-client -- kafka-console-producer --broker-list cp-cp-kafka-headless:9092 --property key.separator=, --property parse.key=true --topic order
>62,{"orderId": 62, "userId": 12, "status": "CREATED"}
63,{"orderId": 63, "userId": 13, "status": "CREATED"}
64,{"orderId": 64, "userId": 14, "status": "CREATED"}
65,{"orderId": 65, "userId": 15, "status": "UPDATED"}
>>>>%                                                                                    ➜  ksql git:(master) ✗ kubectl exec -it kafka-client -- kafka-console-producer --broker-list cp-cp-kafka-headless:9092 --property key.separator=, --property parse.key=true --topic loyalty
>62,{"loyaltyCardNumber": "52-1231", "orderId": 62}
>63,{"loyaltyCardNumber": "53-1331", "orderId": 63}
>65,{"loyaltyCardNumber": "55-1531", "orderId": 65}
>64,{"loyaltyCardNumber": "55-1531", "orderId": 64}
>66,{"loyaltyCardNumber": "56-1631", "orderId": 66}
```

Смотрим, какие события попали в стрим:
```
ksql> select * from loyal_orders emit changes;
+-----------------+-----------------+-----------------+-----------------+-----------------+
|ROWTIME          |ROWKEY           |LOYALTYCARDNUMBER|ORDERID          |USERID           |
+-----------------+-----------------+-----------------+-----------------+-----------------+
|1593974732644    |62               |52-1231          |62               |12               |
|1593974753446    |63               |53-1331          |63               |13               |
|1593974781726    |64               |55-1531          |64               |14               |
```

Как видим событие с типом UPDATED не попали, также как и события у которых нет "пары". 

Проверяем, что они же попали в топик в кафку:

```
ksql> print 'loyal_orders' from beginning;
Key format: KAFKA_BIGINT or KAFKA_DOUBLE or KAFKA_STRING
Value format: JSON or KAFKA_STRING
rowtime: 7/5/20 6:45:32 PM UTC, key: 62, value: {"LOYALTYCARDNUMBER":"52-1231","ORDERID":62,"USERID":12}
rowtime: 7/5/20 6:45:53 PM UTC, key: 63, value: {"LOYALTYCARDNUMBER":"53-1331","ORDERID":63,"USERID":13}
rowtime: 7/5/20 6:46:21 PM UTC, key: 64, value: {"LOYALTYCARDNUMBER":"55-1531","ORDERID":64,"USERID":14}
```


Теперь обогатим loyal_orders данными пользователя. Для этого создадим stream, который это делает

```
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
```

Теперь в топик будут скидываться события, когда создался заказ и была готова карточка лояльности, вместе с данными по пользователю. 

Добавим 
```
➜  ksql git:(master) ✗ kubectl exec -it kafka-client -- kafka-console-producer --broker-list cp-cp-kafka-headless:9092 --property key.separator=, --property parse.key=true --topic order
>72,{"orderId": 72, "userId": 12, "status": "CREATED"}
73,{"orderId": 73, "userId": 13, "status": "CREATED"}
74,{"orderId": 74, "userId": 14, "status": "CREATED"}
75,{"orderId": 75, "userId": 15, "status": "UPDATED"}
>>>>%                                                                                    ➜  ksql git:(master) ✗
➜  ksql git:(master) ✗ kubectl exec -it kafka-client -- kafka-console-producer --broker-list cp-cp-kafka-headless:9092 --property key.separator=, --property parse.key=true --topic loyalty
>72,{"loyaltyCardNumber": "52-1231", "orderId": 72}
>
```

```
ksql> print 'loyal_orders_with_user' ;
Key format: JSON or KAFKA_STRING
Value format: JSON or KAFKA_STRING
rowtime: 7/5/20 7:53:31 PM UTC, key: 12, value: {"LOYALTYCARDNUMBER":"52-1231","ORDERID":72,"USERID":"12","FIRSTNAME":"Ivan","LASTNAME":"Ivanov"}

```
