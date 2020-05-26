```mermaid
sequenceDiagram
participant User
participant Gateway
participant Message Broker
participant User Service
participant Loyalty Service
participant Notification Service

User ->>+ Gateway: POST /register
Gateway ->>- Message Broker: publish
activate Message Broker
Note right of Message Broker: RegistrationRequested
Message Broker -->>- User Service:  consume
activate User Service
User Service ->>- Message Broker: publish
activate Message Broker
Note right of Message Broker: UserCreated
Message Broker -->> Gateway: consume
activate Gateway
Gateway ->> User Service: GET /users/{id}
User Service -->> Gateway: user info
Gateway -->> User: Response
deactivate Gateway
Message Broker -->> Notification Service: consume
activate Notification Service
Message Broker -->>- Loyalty Service: consume
activate Loyalty Service
Loyalty Service ->> User Service: GET /users/{id}
User Service -->> Loyalty Service: user_info
Loyalty Service ->> Message Broker: publish
deactivate Loaylty Service
activate Message Broker
Note right of Message Broker: LoyaltyCardCreated
Message Broker -->> Notification Service: consume
deactivate Message Broker
par [Get user info]
  Notification Service ->> User Service: GET /users/{userId}
and [Get card info]
  Notification Service ->> Loyalty Service: GET /cards/{cardId}
end
User Service -->> Notification Service: User info
Loyalty Service -->> Notification Service: Card Info
Notification Service ->> Notification Service: send email
deactivate Notification Service
```
