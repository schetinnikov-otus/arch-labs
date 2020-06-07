Прежде всего создадим неймспейс для развертывания приложения 

```
(python3) ➜  product git:(master) ✗ kubectl config set-context --current --namespace=loadtest
Context "minikube" modified.
```
```
cd product
skaffold run
```

Чтобы мониторить метрики приложения развернем прометеус и nginx.
```

(python3) ➜  loadtest git:(master) ✗ kubectl create namespace monitoring
namespace/monitoring created

(python3) ➜  loadtest git:(master) ✗ helm install prom stable/prometheus-operator -f monitoring/prometheus.yaml -n monitoring
manifest_sorter.go:192: info: skipping unknown hook: "crd-install"
manifest_sorter.go:192: info: skipping unknown hook: "crd-install"
manifest_sorter.go:192: info: skipping unknown hook: "crd-install"
manifest_sorter.go:192: info: skipping unknown hook: "crd-install"
manifest_sorter.go:192: info: skipping unknown hook: "crd-install"
manifest_sorter.go:192: info: skipping unknown hook: "crd-install"
...
(python3) ➜  product git:(master) ✗ kubectl create namespace ingress
namespace/ingress created

(python3) ➜  loadtest git:(master) ✗ helm install ing stable/nginx-ingress -f ingress/nginx-ingress.yaml -n ingress
NAME: ing
LAST DEPLOYED: Fri Jun  5 16:45:03 2020
NAMESPACE: ingress
STATUS: deployed
REVISION: 1
```

Удостоверимся, что приложение работает. 
```

(python3) ➜  loadtest git:(master) ✗ curl http://arch.homework/search\?q\=too
{
  "products": []
}
```

Посмотрим, сколько записей в БД:
```
➜  ~ kubectl port-forward service/product-postgresql 54321:5432
Forwarding from 127.0.0.1:54321 -> 5432
Forwarding from [::1]:54321 -> 5432

(python3) ➜  loadtest git:(master) ✗ psql postgresql://productuser:productpasswd@127.0.0.1:54321/productdb
psql (12.2, server 11.7)
Type "help" for help.

productdb=> select count(*) from products;
 count
-------
     0
(1 row)

productdb=>
```

Добавим записей в БД с помощью скрипта:
```
kubectl run -it --rm loaddata --image=product:latest --image-pull-policy=Never --env="DATABASE_URI=postgresql+psycopg2://productuser:productpasswd@product-postgresql:5432/productdb" --command -- /bin/sh
/usr/src/app # cd src
/usr/src/app/src # export FLASK_APP=commands.py
/usr/src/app/src # flask add_products --count 7000
Left: 6000
Left: 5000
Left: 4000
Left: 3000
Left: 2000
Left: 1000
Left: 0
/usr/src/app/src #

(python3) ➜  product git:(master) ✗ psql postgresql://productuser:productpasswd@127.0.0.1:54321/productdb
psql (12.2, server 11.7)
Type "help" for help.

productdb=> select count(*) from products;
 count
--------
 7000
(1 row)

productdb=>


productdb=> select * from products where id = 2000;
-[ RECORD 1 ]----------------------------------------------------------------------------------------------------------------------------------------------
id          | 2000
name        | consumer less student
description | Whether difference work character sister level just peace.Population nearly million center arm everyone without.Away employee both either by.
```

Запускаем графану и импортируем в нее дашборд с основными графиками
```
➜  ~ kubectl port-forward -n monitoring service/prom-grafana 9000:80
Forwarding from 127.0.0.1:9000 -> 3000
Forwarding from [::1]:9000 -> 3000
```


Устанавливаем locust
```
pip install locust
```


Попробуем нагрузить
```
locust -f locustfile.py --headless -u 100000 -r 10 --run-time 10m --host http://arch.homework --step-load --step-users 25 --step-time 15s
```

-r - с какой скоростью (пользователи в секунду) добавляем пользователей 

--run-time - длительность теста

--step-load - делаем ступенчатую нагрузку

--step-users - добавляем по 25 пользователей на каждую ступень 

--step-time - длительность ступеньки

![Снимок экрана 2020-06-05 в 18.22.35](README.assets/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202020-06-05%20%D0%B2%2018.22.35.png)

