# 🚀 CRAIG_2_MVP

### 🧠 Overview
This project follows a **microservices architecture**.  

---

### 🧩 System Architecture
The architecture consists of several **standalone services** that communicate over a shared, private network.  
An **API Gateway** acts as the single entry point, handling routing and serving as the primary security checkpoint.

| Service Name        | Description                                                                 | Technology Stack         | Database     |
|----------------------|------------------------------------------------------------------------------|--------------------------|--------------|
| 🛡️ **Gateway Service**   | The single entry point for all client requests. Handles routing, rate limiting, and request aggregation. | Python / Django          | N/A          |
| 👤 **User Service**      | The central authority for identity. Manages user registration, login, and the creation/signing of JWT access tokens. | Python / Django          | PostgreSQL   |
| 🛍️ **Product Service**   | A sample CRUD service for managing products. Authorizes requests by validating JWTs issued by the User Service. | Python / Django          | MySQL        |
| 🏗️ **Asset Service**     | A sample CRUD service for managing assets.  | Go / Gin                 | MongoDB      |
| ⚡ **Caching Service**   | A shared, high-speed cache. Used for rate limiting, session storage, or caching API responses. | Redis                    | N/A          |