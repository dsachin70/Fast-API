# Fast-API

# Vibeosys FastAPI Assignment

## How to Run

1. Install dependencies  
   `pip install -r requirements.txt`

2. Start the server  
   `uvicorn main:app --reload`

3. API Endpoints:
- `GET /product/list`
- `GET /product/{pid}/info`
- `POST /product/add`
- `PUT /product/{pid}/update`

Database: MySQL  
ORM: SQLAlchemy  
Validation: Pydantic
