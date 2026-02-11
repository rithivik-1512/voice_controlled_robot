# System Architecture

The Smart Cafeteria Management System follows a client-server architecture with a clear separation between the frontend (React Native/Expo) and the backend (Node.js/Express).

```mermaid
graph TD
    subgraph Client
        A[Mobile App (Expo)]
        B[Web Dashboard (Expo)]
    end

    subgraph Backend
        C[API Gateway / Load Balancer]
        D[Express Server]
        E[Auth Middleware]
        F[Role Check Middleware]
        
        subgraph Controllers
            G[Auth Controller]
            H[Booking Controller]
            I[Menu Controller]
            J[Crowd Controller]
            K[Admin Controller]
            L[Staff Controller]
        end
    end

    subgraph Database
        M[(MongoDB Atlas)]
    end

    %% Client to Backend
    A -->|HTTPS / JSON| D
    B -->|HTTPS / JSON| D

    %% Backend Flow
    D --> E
    E --> F
    F --> G & H & I & J & K & L

    %% Controller to DB
    G -->|User Data| M
    H -->|Bookings| M
    I -->|Menu Items| M
    J -->|Crowd Stats| M
    K -->|Admin Stats| M
    L -->|Order Status| M

    %% External Services (if any)
    %% H -.-> N[Payment Gateway]
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
