# 🚀 CRAIG_2_MVP

### 🧠 Overview
This project follows a **microservices architecture**.  

---

### 🧩 System Architecture
The architecture consists of several **standalone services** that communicate over a shared, private network.  
An **API Gateway** acts as the single entry point, handling routing and serving as the primary security checkpoint.


| Service Name          | Description                                                                 | Technology Stack               | Database     |
|------------------------|------------------------------------------------------------------------------|--------------------------------|--------------|
| 🛡️ Gateway Service     | The single entry point for all client requests. Handles routing, rate limiting, and request aggregation. | Python / Django                | N/A          |
| 👤 User Service         | Manages user registration, login, and JWT token creation. Acts as the authentication authority. | Python / Django                | PostgreSQL   |
| 🛍️ Product Service      | Handles product CRUD operations. Validates JWTs issued by the User Service. | Python / Django                | MySQL        |
| 🏗️ Asset Service        | Manages asset CRUD operations. Demonstrates polyglot capability using Go.   | Go / Gin                       | MongoDB      |
| 📦 Inventory Service    | Handles inventory CRUD operations using Node.js. Demonstrates polyglot setup. | JavaScript / Node.js (Express) | MongoDB      |
| ⚡ Caching Service      | Provides high-speed caching for rate limiting, sessions, and API responses. | Redis                          | N/A          |