# System Architecture

The Smart Cafeteria Management System follows a client-server architecture with a clear separation between the frontend (React Native/Expo) and the backend (Node.js/Express).

```mermaid
flowchart TD

    %% Client Layer
    subgraph Client
        A[Mobile App - Expo]
        B[Web Dashboard - Expo]
    end

    %% Backend Layer
    subgraph Backend (Node.js + Express)
        D[Express Server]
        E[Auth Middleware]
        F[Role Middleware]

        subgraph Controllers
            G[Auth]
            H[Booking]
            I[Menu]
            J[Crowd]
            K[Admin]
            L[Staff]
        end
    end

    %% Database
    M[(MongoDB Atlas)]

    %% Flow
    A -->|HTTPS| D
    B -->|HTTPS| D

    D --> E --> F
    F --> G
    F --> H
    F --> I
    F --> J
    F --> K
    F --> L

    G --> M
    H --> M
    I --> M
    J --> M
    K --> M
    L --> M


```

## Component Description

1.  **Frontend (Client Layer)**:
    *   Built with React Native & Expo.
    *   Handles UI rendering, user interactions, and state management (Context API).
    *   Communicates with the backend via RESTful API calls using Axios.

2.  **Backend (Server Layer)**:
    *   Node.js runtime with Express framework.
    *   **Middleware**: Handles JWT authentication (`auth.js`) and role-based access control (`roleCheck.js`).
    *   **Controllers**: Contain business logic for different modules (Auth, Booking, Menu, etc.).
    *   **Routes**: Define API endpoints and map them to controllers.

3.  **Database (Data Layer)**:
    *   MongoDB Atlas (Cloud NoSQL Database).
    *   Stores data for Users, Bookings, Menu Items, Slots, and Queues.
    *   Mongoose ODM is used for schema definition and data validation.
