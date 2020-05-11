Лаба с валидацией JWT токенов внутри приложения 

```
➜  jwt-auth git:(master) ✗ ls -1
README.md
identity
token auth.postman_collection.json
token-app
➜  jwt-auth git:(master) ✗
```

Запускаем и собираем приложения локально с помощью skaffold 

```
➜  jwt-auth git:(master) ✗ cd identity
➜  identity git:(master) ✗ skaffold run
Generating tags...
 - identity -> identity:latest
Checking cache...
 - identity: Found. Tagging
Tags used in deployment:
 - identity -> identity:00013068ba75ee432a69bc431e46fd7a60c8af36e860d64b0847fc2e65d1afff
   local images can't be referenced by digest. They are tagged and referenced by a unique ID instead
Starting deploy...
Helm release identity not installed. Installing...
NAME: identity
LAST DEPLOYED: Mon May 11 20:01:05 2020
NAMESPACE: auth
STATUS: deployed
REVISION: 1
NOTES:
TO BE DONE
WARN[0018] error adding label to runtime object: patching resource auth/"identity": jobs.batch "identity" not found
WARN[0019] error adding label to runtime object: patching resource auth/"identity-test-connection": pods "identity-test-connection" not found
Waiting for deployments to stabilize...
 - auth:deployment/identity is ready.
Deployments stabilized in 285.242019ms
You can also run [skaffold run --tail] to get the logs
```


```
➜  identity git:(master) ✗ cd ..
➜  jwt-auth git:(master) ✗ cd token-app
➜  token-app git:(master) ✗ skaffold run
Generating tags...
 - tokenapp -> tokenapp:latest
Checking cache...
 - tokenapp: Found Locally
Tags used in deployment:
 - tokenapp -> tokenapp:b8e6d8de436622429502cf2987ca548f22f9a4d2381fc6078d098e9a3b752cfb
   local images can't be referenced by digest. They are tagged and referenced by a unique ID instead
Starting deploy...
Helm release tokenapp not installed. Installing...
NAME: tokenapp
LAST DEPLOYED: Mon May 11 20:01:39 2020
NAMESPACE: auth
STATUS: deployed
REVISION: 1
NOTES:
TO BE DONE
WARN[0002] error adding label to runtime object: patching resource auth/"tokenapp-test-connection": pods "tokenapp-test-connection" not found
Waiting for deployments to stabilize...
 - auth:deployment/tokenapp is ready.
Deployments stabilized in 283.09054ms
You can also run [skaffold run --tail] to get the logs
➜  token-app git:(master) ✗
```

Смотрим, что все запустилось 

```

NAME                            READY   STATUS    RESTARTS   AGE
pod/identity-6fdd5f6cb7-54h66   1/1     Running   0          95s
pod/identity-postgresql-0       1/1     Running   0          95s
pod/tokenapp-69fc7c5ffd-bqbmb   1/1     Running   0          61s
pod/tokenapp-69fc7c5ffd-cztsh   1/1     Running   0          61s

NAME                                   TYPE        CLUSTER-IP       EXTERNAL-IP   P
ORT(S)          AGE
service/identity                       NodePort    10.108.49.218    <none>        9
000:32698/TCP   95s
service/identity-postgresql            ClusterIP   10.107.204.113   <none>        5
432/TCP         95s
service/identity-postgresql-headless   ClusterIP   None             <none>        5
432/TCP         95s
service/tokenapp                       NodePort    10.100.235.76    <none>        9
000:30945/TCP   61s
```

Для обоих приложений были созданы ингрессы

```
➜  jwt-auth git:(master) ✗ kubectl get ing
NAME       CLASS    HOSTS           ADDRESS        PORTS   AGE
identity   <none>   arch.homework   192.168.64.4   80      118s
tokenapp   <none>   arch.homework   192.168.64.4   80      84s
```

В настройках приложения token-app хранится публичный ключ 

```yaml
-- ➜  jwt-auth git:(master) ✗ cat token-app/tokenapp-chart/values.yaml
replicaCount: 2

fullnameOverride: "tokenapp"

image: "tokenapp:0.1.0"

service:
  type: NodePort
  port: 9000

postgresql:
  enabled: true
  postgresqlUsername: myuser
  postgresqlPassword: passwd
  postgresqlDatabase: mytokenapp
  persistence:
    size: 0.1Gi
  service:
    port: "5432"

ingress:
  enabled: true
  hosts:
    - host: arch.homework
      paths: ["/users/me/token"]

jwt:
  publicKey: |
    -----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCvrcv0G8cVPtFWSHv+FZUmvDk3
    UFqdbe8h5w+ke/8oBJilOGrcu6lm8KNwnQelg3tYEXWUP36qeIhvhkqwNQyrXpR3
    t0iYHg1aq+YloRvFpaebo3BuRz07r6XwY+LpQqePt+MtXVtzIRcX+Z5s/D50sMWN
    38oF7fxJs2ZqLAcP4wIDAQAB
    -----END PUBLIC KEY-----
```

В настройках identity cервиса приватный и публичный

```yaml
-- ➜  jwt-auth git:(master) ✗ cat identity/identity-chart/values.yaml
replicaCount: 1

fullnameOverride: "identity"

image: "identity:0.1.0"

service:
  type: NodePort
  port: 9000

postgresql:
  enabled: true
  postgresqlUsername: identityuser
  postgresqlPassword: identitypasswd
  postgresqlDatabase: identitydb
  persistence:
    size: 0.1Gi
  service:
    port: "5432"

ingress:
  enabled: true
  hosts:
    - host: arch.homework
      paths: ["/login", "/register"]

jwt:
  privateKey: |
    -----BEGIN RSA PRIVATE KEY-----
    MIICXgIBAAKBgQCvrcv0G8cVPtFWSHv+FZUmvDk3UFqdbe8h5w+ke/8oBJilOGrc
    u6lm8KNwnQelg3tYEXWUP36qeIhvhkqwNQyrXpR3t0iYHg1aq+YloRvFpaebo3Bu
    Rz07r6XwY+LpQqePt+MtXVtzIRcX+Z5s/D50sMWN38oF7fxJs2ZqLAcP4wIDAQAB
    AoGBAJoWLA9d1c4SnPW6+dYwA/RHnz+e4Pu4Esh/q76va2skLOathz039Ctv4UrC
    0JQhsKvcFG8FCgpnUfPPq+7FeOfaMMmMnY/PSODgY0UKZIatUVDICF56ppsc53RH
    QzpAQxM/3CmEm4eG5fz/T4vIdoN0JHDfKI8YMiF7CMLLO3qhAkEA1n3cobZSMU9q
    Jlt7MGdt90inJxeAIR0b/EpxukDw2hBIy/eKJtLfXxZqhiYOSp5cjgLniS5Kn/S6
    MWg+NquVawJBANGtHF++vFUc2m9qamP6ZHIdOpQyEO+HYFwVL3vhAiDmf9DxgE+6
    JREiw/+GCZhT6XNX+3cxc1l/GIVk8WlvFWkCQQCwp4iHR3n6UsXCQaX7/7N57sR8
    VcaZfzgFWerA06uKbc8G7iFCSHrf/b5OLhmnKzZfX9UCDrY3d3/CIXDb5gVxAkAw
    bBkUZ3kY8tvjRSEiy62syOFBXjqZBpuTSHU516HlNTYpa8xlHSj4Rx4agbrvidlt
    ANGbGjl4XqisDb7OyY+ZAkEAl83BiQfgSkKBzLL2LJ6e6mBOMNA5kHS7mDo4Am2T
    GP3MLf9lNEhKMnZkPM/w7uAN+JyNSc67ue1jezhYSanBSA==
    -----END RSA PRIVATE KEY-----
  publicKey: |
    -----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCvrcv0G8cVPtFWSHv+FZUmvDk3
    UFqdbe8h5w+ke/8oBJilOGrcu6lm8KNwnQelg3tYEXWUP36qeIhvhkqwNQyrXpR3
    t0iYHg1aq+YloRvFpaebo3BuRz07r6XwY+LpQqePt+MtXVtzIRcX+Z5s/D50sMWN
    38oF7fxJs2ZqLAcP4wIDAQAB
    -----END PUBLIC KEY-----
```


Ну и как это все работает в связке можно посмотреть, запустив тесты newman

IDToken, который получается после залогинивания пользователя, передается в заголовок Authorization: Bearer <IDToken>

```
➜  jwt-auth git:(master) ✗ newman run token\ auth.postman_collection.json
newman

token auth

→ регистрация
  POST http://arch.homework/register [200 OK, 174B, 54ms]
  ✓  [INFO] Request: {
	"login": "Eleazar_Rowe92",
	"password": "FrGLiFZ0eqOsWoP",
	"email": "Vella81@yahoo.com",
	"first_name": "Bernadine",
	"last_name": "Jakubowski"
}

  ✓  [INFO] Response: {
  "id": 2
}


→ логин
  POST http://arch.homework/login [200 OK, 624B, 127ms]
  ✓  [INFO] Request: {"login": "Eleazar_Rowe92", "password": "FrGLiFZ0eqOsWoP"}
  ✓  [INFO] Response: {
  "IDtoken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJlbWFpbCI6IlZlbGxhODFAeWFob28uY29tIiwic3ViIjoyLCJpc3MiOiJodHRwOi8vYXJjaC5ob21ld29yayIsImZhbWlseV9uYW1lIjoiSmFrdWJvd3NraSIsImdpdmVuX25hbWUiOiJCZXJuYWRpbmUiLCJleHAiOjE1ODkyMTc2ODF9.UU9mxfFWzMqG2P_H-Ely1PF7nLdP5n_6Vae064w4N9zHug_AIPjKWo2eezcknGljLtRkyzVpLfwFCk8g-rb8VMm8rXq-IuLCDxPOpRZrQtXaWORhXiqCd-ojsJkzAMmRKaDClmqiDURsUm9Hj4Podet2jTDIYeI-G8_SrWl_L_w"
}


→ проверить данные о пользователе
  GET http://arch.homework/users/me/token [200 OK, 327B, 41ms]
  ✓  [INFO] Request: [object Object]
  ✓  [INFO] Response: {
  "email": "Vella81@yahoo.com",
  "exp": 1589217681,
  "family_name": "Jakubowski",
  "given_name": "Bernadine",
  "iss": "http://arch.homework",
  "sub": 2
}

  ✓  test token data

┌─────────────────────────┬───────────────────┬───────────────────┐
│                         │          executed │            failed │
├─────────────────────────┼───────────────────┼───────────────────┤
│              iterations │                 1 │                 0 │
├─────────────────────────┼───────────────────┼───────────────────┤
│                requests │                 3 │                 0 │
├─────────────────────────┼───────────────────┼───────────────────┤
│            test-scripts │                 6 │                 0 │
├─────────────────────────┼───────────────────┼───────────────────┤
│      prerequest-scripts │                 4 │                 0 │
├─────────────────────────┼───────────────────┼───────────────────┤
│              assertions │                 7 │                 0 │
├─────────────────────────┴───────────────────┴───────────────────┤
│ total run duration: 330ms                                       │
├─────────────────────────────────────────────────────────────────┤
│ total data received: 589B (approx)                              │
├─────────────────────────────────────────────────────────────────┤
│ average response time: 74ms [min: 41ms, max: 127ms, s.d.: 37ms] │
└─────────────────────────────────────────────────────────────────┘
➜  jwt-auth git:(master) ✗
```