Лаба с валидацией JWT токенов с помощью ambassador-aes 

Установка ambassador-aes (community edition)

```
helm repo add datawire https://getambassador.io
```

```
helm install aes datawire/ambassador -f ambassador_values.yaml
```

Собираем и деплоим приложение simple-app и identity с помощью skaffold

```bash
➜  ambassador-jwt git:(master) ✗ cd identity
➜  identity git:(master) ✗ skaffold run
Generating tags...
 - identity -> identity:latest
Checking cache...
 - identity: Found. Tagging
Tags used in deployment:
 - identity -> identity:e6f05cd0c501d990f9fcde4babe45ff43eeadd6c3e299466d9d5f1fd649fba02
   local images can't be referenced by digest. They are tagged and referenced by a unique ID instead
Starting deploy...
Helm release identity not installed. Installing...
NAME: identity
LAST DEPLOYED: Mon May 11 19:45:28 2020
NAMESPACE: auth
STATUS: deployed
REVISION: 1
NOTES:
TO BE DONE
WARN[0017] error adding label to runtime object: patching resource auth/"identity": jobs.batch "identity" not found
WARN[0018] error adding label to runtime object: patching resource auth/"identity-test-connection": pods "identity-test-connection" not found
Waiting for deployments to stabilize...
 - auth:deployment/identity is ready.
Deployments stabilized in 293.750719ms
You can also run [skaffold run --tail] to get the logs
➜  identity git:(master) ✗
```

```
➜  identity git:(master) ✗ cd ..
➜  ambassador-jwt git:(master) ✗ cd simple-app
➜  simple-app git:(master) ✗ skaffold run
Generating tags...
 - simple-app -> simple-app:latest
Checking cache...
 - simple-app: Found Locally
Tags used in deployment:
 - simple-app -> simple-app:60208809b2d78afb567d82eaf63659519a8a15bf74508671e0bc184d44abf5cd
   local images can't be referenced by digest. They are tagged and referenced by a unique ID instead
Starting deploy...
Helm release simple-app not installed. Installing...
NAME: simple-app
LAST DEPLOYED: Mon May 11 19:46:12 2020
NAMESPACE: auth
STATUS: deployed
REVISION: 1
NOTES:
TO BE DONE
WARN[0002] error adding label to runtime object: patching resource auth/"simple-app-test-connection": pods "simple-app-test-connection" not found
Waiting for deployments to stabilize...
Deployments stabilized in 13.250547ms
You can also run [skaffold run --tail] to get the logs
➜  simple-app git:(master) ✗
```

Проверяем что все запущено 

```
NAME                                       READY   STATUS    RESTARTS   AGE
pod/aes-ambassador-7ddccb867d-gp868        1/1     Running   0          2m41s
pod/aes-ambassador-redis-8bcfc8498-kb2ct   1/1     Running   0          2m41s
pod/identity-7c9b649f4f-kzgzv              1/1     Running   0          97s
pod/identity-postgresql-0                  1/1     Running   0          97s
pod/simple-app-6486f474cd-dsn2h            1/1     Running   0          53s

NAME                                   TYPE        CLUSTER-IP       EXTERNAL-IP   P
ORT(S)                      AGE
service/aes-ambassador                 NodePort    10.102.21.101    <none>        8
0:30588/TCP,443:31496/TCP   2m41s
service/aes-ambassador-admin           ClusterIP   10.98.206.2      <none>        8
877/TCP                     2m41s
service/aes-ambassador-redis           ClusterIP   10.96.124.1      <none>        6
379/TCP                     2m41s
service/identity                       NodePort    10.111.192.24    <none>        9
000:31649/TCP               97s
service/identity-postgresql            ClusterIP   10.107.80.208    <none>        5
432/TCP                     97s
service/identity-postgresql-headless   ClusterIP   None             <none>        5
432/TCP                     97s
service/simple-app                     NodePort    10.101.160.107   <none>        9
000:31538/TCP               53s
```

Применяем манифесты для амбассадора
```
➜  ambassador-jwt git:(master) ✗ kubectl apply -f ambassador/
filterpolicy.getambassador.io/myapp-filter-policy unchanged
host.getambassador.io/hello-world unchanged
mapping.getambassador.io/identity-mapping unchanged
filter.getambassador.io/myapp-jwt-filter unchanged
mapping.getambassador.io/simple-app-mapping unchanged
```

Это определение нужно только, чтобы ambassador-aes мог обслуживать без HTTPS
```yaml
-- ➜  ambassador git:(master) ✗ cat host.yaml
apiVersion: getambassador.io/v2
kind: Host
metadata:
  name: hello-world
spec:
  hostname: hello.world
  acmeProvider:
    authority: none
  requestPolicy:
    insecure:
      action: Route
```

Роуты для сервиса идентификации
```yaml
-- ➜  ambassador git:(master) ✗ cat identity-mapping.yaml
apiVersion: getambassador.io/v2
kind:  Mapping
metadata:
  name:  identity-mapping
spec:
  prefix: /auth
  service: identity:9000
```

Роуты для приложения 
```yaml
-- ➜  ambassador git:(master) ✗ cat simple-app-mapping.yaml
apiVersion: getambassador.io/v2
kind:  Mapping
metadata:
  name:  simple-app-mapping
spec:
  prefix: /users/me
  service: simple-app:9000
  rewrite: ""
```

Rewrite: "" означает, что приложение должно отвечать по роуту /users/me

Описание фильтра
```
➜  ambassador git:(master) ✗ cat jwt-filter.yaml
apiVersion: getambassador.io/v2
kind: Filter
metadata:
  name: "myapp-jwt-filter"
spec:
  JWT:
    jwksURI: "http://identity:9000/.well-known/jwks.json"
    insecureTLS: true
    renegotiateTLS: freelyAsClient
    validAlgorithms:
    - "RS256"
    requireAudience: false
    requireIssuer: false
    requireIssuedAt: false
    requireExpiresAt: false
    requireNotBefore: false
    injectRequestHeaders:
    - name: "X-Token-String"
      value: "{{ .token.Raw }}"
    - name: "X-User-Id"
      value: "{{ .token.Claims.sub }}"
    - name: "X-Email"
      value: "{{ .token.Claims.email }}"
    - name: "X-Last-Name"
      value: "{{ .token.Claims.family_name }}"
    - name: "X-First-Name"
      value: "{{ .token.Claims.given_name }}"
```
Самая важная настройка 
jwksURI: "http://identity:9000/.well-known/jwks.json" 

Identity сервис должен отдавать jwks - публичный ключ для jwt токена 

```
➜  ambassador git:(master) ✗ curl -v http://192.168.64.4:30588/auth/.well-known/jwks.json
*   Trying 192.168.64.4...
* TCP_NODELAY set
* Connected to 192.168.64.4 (192.168.64.4) port 30588 (#0)
> GET /auth/.well-known/jwks.json HTTP/1.1
> Host: 192.168.64.4:30588
> User-Agent: curl/7.64.1
> Accept: */*
>
< HTTP/1.1 200 OK
< content-type: application/json
< content-length: 277
< server: envoy
< date: Mon, 11 May 2020 16:53:48 GMT
< x-envoy-upstream-service-time: 2
<
{
  "keys": [
    {
      "e": "AQAB",
      "kid": "1",
      "kty": "RSA",
      "n": "r63L9BvHFT7RVkh7_hWVJrw5N1BanW3vIecPpHv_KASYpThq3LupZvCjcJ0HpYN7WBF1lD9-qniIb4ZKsDUMq16Ud7dImB4NWqvmJaEbxaWnm6Nwbkc9O6-l8GPi6UKnj7fjLV1bcyEXF_mebPw-dLDFjd_KBe38SbNmaiwHD-M"
    }
  ]
}
* Connection #0 to host 192.168.64.4 left intact
* Closing connection 0
```

Файл с политикой применения фильтра 
```yaml
-- ➜  ambassador git:(master) ✗ cat filter-policy.yaml
apiVersion: getambassador.io/v2
kind: FilterPolicy
metadata:
  name: "myapp-filter-policy"
spec:
  rules:
  - host: "*"
    path: "/users/me"
    filters:
    - name: "myapp-jwt-filter"
```

Запускаем тесты и смотрим, как все работает 

```
➜  ambassador-jwt git:(master) ✗ newman run --env-var "baseUrl=http://192.168.64.4:30588" gw\ token\ auth.postman_collection.json
newman

gw token auth

→ регистрация
  POST http://192.168.64.4:30588/auth/register [200 OK, 172B, 58ms]
  ✓  [INFO] Request: {
	"login": "Trey.Becker",
	"password": "dYzcw2j6kmwtT3U",
	"email": "Dereck31@gmail.com",
	"first_name": "Amani",
	"last_name": "Schroeder"
}

  ✓  [INFO] Response: {
  "id": 2
}


→ логин
  POST http://192.168.64.4:30588/auth/login [200 OK, 577B, 36ms]
  ✓  [INFO] Request: {"login": "Trey.Becker", "password": "dYzcw2j6kmwtT3U"}
  ✓  [INFO] Response: {
  "IDtoken": "eyJ0eXAiOiJKV1QiLCJraWQiOiIxIiwiYWxnIjoiUlMyNTYifQ.eyJmYW1pbHlfbmFtZSI6IlNjaHJvZWRlciIsImVtYWlsIjoiRGVyZWNrMzFAZ21haWwuY29tIiwiZ2l2ZW5fbmFtZSI6IkFtYW5pIiwiaXNzIjoiaHR0cDovL2FyY2guaG9tZXdvcmsiLCJzdWIiOjIsImV4cCI6MTU4OTIxNzA4MX0.LjBgIMb2Uw0BLO9FwnMOeKzNk2H2gEx1AithxKyd6JvmPv53uMXn3RB5P521lhDFssj-urqg6I5k9b7TgLLfANbhadXQferfS74KP7q1pr1kDQ9Ef9wHH66dIhTOKPNMTjM0gI6ZkFcR6UwsDd4MNnHIC_JrOh8fa3wH7ab4buY"
}


→ JWKS
  GET http://192.168.64.4:30588/auth/.well-known/jwks.json [200 OK, 435B, 5ms]
  ✓  [INFO] Request: [object Object]
  ✓  [INFO] Response: {
  "keys": [
    {
      "e": "AQAB",
      "kid": "1",
      "kty": "RSA",
      "n": "r63L9BvHFT7RVkh7_hWVJrw5N1BanW3vIecPpHv_KASYpThq3LupZvCjcJ0HpYN7WBF1lD9-qniIb4ZKsDUMq16Ud7dImB4NWqvmJaEbxaWnm6Nwbkc9O6-l8GPi6UKnj7fjLV1bcyEXF_mebPw-dLDFjd_KBe38SbNmaiwHD-M"
    }
  ]
}


→ проверить данные о пользователе
  GET http://192.168.64.4:30588/users/me [200 OK, 263B, 11ms]
  ✓  [INFO] Request: [object Object]
  ✓  [INFO] Response: {
  "email": "Dereck31@gmail.com",
  "first_name": "Amani",
  "id": "2",
  "last_name": "Schroeder"
}

  ✓  test token data

┌─────────────────────────┬──────────────────┬──────────────────┐
│                         │         executed │           failed │
├─────────────────────────┼──────────────────┼──────────────────┤
│              iterations │                1 │                0 │
├─────────────────────────┼──────────────────┼──────────────────┤
│                requests │                4 │                0 │
├─────────────────────────┼──────────────────┼──────────────────┤
│            test-scripts │                7 │                0 │
├─────────────────────────┼──────────────────┼──────────────────┤
│      prerequest-scripts │                5 │                0 │
├─────────────────────────┼──────────────────┼──────────────────┤
│              assertions │                9 │                0 │
├─────────────────────────┴──────────────────┴──────────────────┤
│ total run duration: 234ms                                     │
├───────────────────────────────────────────────────────────────┤
│ total data received: 814B (approx)                            │
├───────────────────────────────────────────────────────────────┤
│ average response time: 27ms [min: 5ms, max: 58ms, s.d.: 21ms] │
└───────────────────────────────────────────────────────────────┘
➜  ambassador-jwt git:(master) ✗
```