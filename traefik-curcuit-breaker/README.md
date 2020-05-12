Демонстрация работы curcuit breaker-а в API Gateway на примере Traefik 


Устанавливаем traefik

```bash
helm repo add traefik https://containous.github.io/traefik-helm-chart
```

```bash
helm repo update
```

```bash
helm install traefik traefik/traefik -f traefik-values.yaml
```

Деплоим приложение, которое будет эмулировать плохое поведение

```
➜  traefik-curcuit-breaker git:(master) ✗ cd app
➜  app git:(master) ✗ skaffold run
Generating tags...
 - app -> app:latest
Checking cache...
 - app: Found Locally
Tags used in deployment:
 - app -> app:21881dc08938db59a2650080f3720b6460057acb3d78613d967f7b753d9040b6
   local images can't be referenced by digest. They are tagged and referenced by a unique ID instead
Starting deploy...
Release "app" has been upgraded. Happy Helming!
NAME: app
LAST DEPLOYED: Thu May  7 13:14:04 2020
NAMESPACE: auth
STATUS: deployed
REVISION: 17
NOTES:
TO BE DONE
WARN[0002] error adding label to runtime object: patching resource auth/"app-test-connection": pods "app-test-connection" not found
Waiting for deployments to stabilize...
Deployments stabilized in 9.521415ms
You can also run [skaffold run --tail] to get the logs
➜  app git:(master) ✗
```

Поднимется приложение, в котором процент запросов отдаться с 500ками, часть запросов будет очень долгими (>10c)

Настройки процента запросов находится в values-файле 

```
➜  app git:(master) ✗ cat app-chart/values.yaml
replicaCount: 2

fullnameOverride: "app"

image: "app:0.1.0"

service:
  type: NodePort
  port: 9000

rate:
  fail: 0.01
  slow: 0.01
```



Настройки сurcuit breaker-а находятся в traefik/traefik-midl.yaml

```
➜  traefik-curcuit-breaker git:(master) ✗ cat traefik/traefik-midl.yaml
apiVersion: traefik.containo.us/v1alpha1
kind: Middleware
metadata:
  name: curcuit-breaker
spec:
  circuitBreaker:
    expression: ResponseCodeRatio(500, 600, 0, 600) > 0.25
```

Описание настроек и возможностей можно посмотреть тут - https://docs.traefik.io/middlewares/circuitbreaker/


Запускаем slapper на порт traefik-а, увеличиваем с помощью клавиши j,k рпс до 200

```
➜ ambassador-gw git:(master) ✗ ./slapper http://192.168.64.4:32611/probe
```

Видим картинку

<img src="README.assets/Снимок экрана 2020-05-07 в 12.47.41.png">

Меняем в values rate.fail на 0.3 и репдеплоим приложение через skaffold run, что через некоторое время трафик с приложения уходит и gw начинается отдавать 503

<img src="README.assets/Снимок экрана 2020-05-07 в 12.57.43.png">

Как только возвращаем значение назад, на 0.01 приложения постепенно приходит в порядок.

<img src="README.assets/Снимок экрана 2020-05-07 в 12.57.17.png">


