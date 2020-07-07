Устанавливаем кафку (вместе с включенным коннектором и сопутсвующими сервисами) и дебезиум

Создаем неймспейс и добавляем helm репозиторий

```bash
➜  debezium git:(master) ✗ kubectl create namespace cdc
namespace/cdc created
➜  debezium git:(master) ✗ kubectl config set-context --current --namespace=cdc
Context "minikube" modified.
➜  debezium git:(master) ✗ helm repo add incubator http://storage.googleapis.com/kubernetes-charts-incubator


"incubator" has been added to your repositories
➜  debezium git:(master) ✗ helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "incubator" chart repository
Update Complete. ⎈ Happy Helming!⎈
➜  debezium git:(master) ✗
```

Ставим кафку. 

```
(python3) ➜  debezium git:(master) ✗ helm install kafka incubator/kafka --set external.enabled=true
NAME: kafka
LAST DEPLOYED: Wed Jul  1 18:51:46 2020
...
  kafka.cluster.local:31090
  kafka.cluster.local:31091
  kafka.cluster.local:31092
```

Ставим kafka-connect
```
(python3) ➜  debezium git:(master) ✗ kubectl apply -f kafka-connect.yaml
deployment.apps/kafkaconnect-deploy created
service/kafkaconnect-service created
```
На 30500 порту начнет весть REST API для взаимодействия.

Запускаем поду с клиентом кафки
```
➜  debezium git:(master) ✗ kubectl apply -f kafka-client.yaml
pod/kafka-client created
```

Создаем необходимые топики коннектора CDC:
```
(python3) ➜  debezium git:(master) ✗ kubectl exec kafka-client -- kafka-topics --zookeeper kafka-zookeeper:2181 --topic connect-offsets --create --partitions 1 --replication-factor 1

Created topic "connect-offsets".
```

```
(python3) ➜  debezium git:(master) ✗ kubectl exec kafka-client -- kafka-topics --zookeeper kafka-zookeeper:2181 --topic connect-configs --create --partitions 1 --replication-factor 1

Created topic "connect-configs".
```

```
(python3) ➜  debezium git:(master) ✗ kubectl exec kafka-client -- kafka-topics --zookeeper kafka-zookeeper:2181 --topic connect-status --create --partitions 1 --replication-factor 1

Created topic "connect-status".
```

Запускаем БД (postgresql) c нужной конфигурацией:
```
(python3) ➜  debezium git:(master) ✗ kubectl create configmap --from-file=extended.conf postgresql-config

configmap/postgresql-config created
```

```
(python3) ➜  debezium git:(master) ✗ helm install  postgres --set extendedConfConfigMap=postgresql-config --set service.type=NodePort --set service.nodePort=30600 --set postgresqlPassword=passw0rd stable/postgresql

NAME: postgres
LAST DEPLOYED: Wed Jul  1 19:09:48 2020
NAMESPACE: cdc
```

Добавим табличку в postgresql 
```
psql postgresql://postgres:passw0rd@192.168.176.128:30600/postgres
psql (12.2, server 11.8)
Type "help" for help.
```

```
CREATE TABLE product (
    id bigint primary key,
    name varchar,
    price bigint,
    color varchar
);

INSERT INTO product (id, name, price, color) VALUES 
   (1, 'samokat', 500, 'red'), 
   (2, 'velosiped', 500, 'white'),
   (3, 'roliki', 600, 'red')
;
```

Создаем коннектор, который будет считывать изменения из таблички product.
```
(python3) ➜  debezium git:(master) ✗ minikube ip
192.168.176.128
(python3) ➜  debezium git:(master) ✗ curl -X POST \
  http://192.168.176.128:30500/connectors \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "product-connector",
    "config": {
            "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
            "plugin.name": "pgoutput",
            "database.hostname": "postgres-postgresql",
            "database.port": "5432",
            "database.user": "postgres",
            "database.password": "passw0rd",
            "database.dbname": "postgres",
            "database.server.name": "postgres",
            "table.whitelist": "public.product"
      }
}'

{"name":"product-connector","config":{"connector.class":"io.debezium.connector.postgresql.PostgresConnector","plugin.name":"pgoutput","database.hostname":"postgres-postgresql","database.port":"5432","database.user":"postgres","database.password":"passw0rd","database.dbname":"postgres","database.server.name":"postgres","table.whitelist":"public.product","name":"product-connector"},"tasks":[],"type":"source"}%                                  (python3) ➜  debezium git:(master) ✗
```

Проверяем, что топик добавился:
```
(python3) ➜  debezium git:(master) ✗ kubectl exec kafka-client -- kafka-topics --zookeeper kafka-zookeeper:2181 --list
__consumer_offsets
connect-configs
connect-offsets
connect-status
postgres.public.product
```

Теперь может слушать события, которые приходят в этот топик:
```
kubectl exec kafka-client -- kafka-console-consumer --topic postgres.public.containers --from-beginning --bootstrap-server kafka:9092 | jq
```

```
postgres=# select * from product;
 id |   name    | price | color
----+-----------+-------+-------
  1 | samokat   |   500 | red
  2 | velosiped |   500 | white
  3 | roliki    |   600 | red
(3 rows)

postgres=# update product set price = price + 10 where color = 'red';
UPDATE 2
```

```
  "payload": {
    "before": null,
    "after": {
      "id": 1,
      "name": "samokat",
      "price": 510,
      "color": "red"
    },
    
  "payload": {
    "before": null,
    "after": {
      "id": 3,
      "name": "roliki",
      "price": 610,
      "color": "red"
    },
```