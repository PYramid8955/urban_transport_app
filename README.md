# Urban Transport App

An advanced routing engine designed to generate efficient transit paths from complex graph-based maps using hierarchical abstraction and heuristic optimization.

---

## Backend Architecture

The backend utilizes a multi-layered approach to handle large-scale graph data and solve complex routing problems.

### 1. Hierarchical Graph Abstraction
To optimize pathfinding, the system avoids processing the entire raw graph at once:
* **Clustering:** The initial graph is partitioned into distinct, almost same-sized clusters, (the nodes in each cluster are connected to eachother).
* **Hub Identification:** The algorithm identifies "hubs" within these clusters to serve as primary connection points.
* **Recursive Abstraction:** An abstracted graph is built using these hubs. This process repeats until a single top-level cluster connects the entire network.

> Due to project requirements excluding Dijkstra’s algorithm (and not only), A* is used for pathfinding. While A* is typically used for point-to-point queries, it is utilized here during the initial phase to calculate Betweenness Centrality.
---

## Frontend and Features

The frontend provides an intuitive interface for both commuters and system administrators.

### User Features
* **Route Visualization:** Users can view the global network of routes and stations.
* **Navigation:** Calculates the fastest route between Station A and Station B.

### Admin Mode
The administrative interface allows for real-time grid management:
* **Dynamic Rerouting:** Admins can delete specific edges to simulate road construction or closures. The system automatically recalculates and redirects affected routes.
* **Bus Distribution (Min-Cost Flow):** The app solves the Min-Cost Flow problem to determine the most efficient way to distribute buses from garages to active routes.



---

## Access Credentials

To access the administrative features and the Min-Cost Flow visualization, use the following credentials:

| Field | Value |
| :--- | :--- |
| **Username** | `owner` |
| **Password** | `pass12` |


---
## ⚙️ Setup & Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/PYramid8955/Urban_Transport_App.git
cd Urban_Transport_App
````

---

### 2️⃣ Create a Virtual Environment inside the project

Create the virtual environment in the root folder of the project:

#### 🔹 On macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 🔹 On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

After activation, your terminal should display `(venv)`.

---

### 3️⃣ Install Requirements

Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

---

## 🚀 Running the Project

The server must be started **inside the `backend` folder**.

```bash
cd backend
uvicorn app.api.v1.api:app --reload
```

* `--reload` enables automatic reload when code changes.
* `app.api.v1.api:app` points to the FastAPI application instance.

---

## 🌐 Access the Application

Once the server is running, open your browser and go to:

```
http://localhost:8000
```

### 📚 Interactive API Documentation

FastAPI automatically generates interactive documentation:

* Swagger UI:

  ```
  http://127.0.0.1:8000/docs
  ```

* ReDoc:

  ```
  http://127.0.0.1:8000/redoc
  ```

You can test all endpoints directly from `/docs`.

---
