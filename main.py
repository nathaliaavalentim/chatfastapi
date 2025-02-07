from fastapi import FastAPI, Depends, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import bcrypt
import os

#Configs
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://usuario:senha@cluster0.ztduj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

#MongoDB
client = MongoClient(MONGO_URI)
db = client["atendimento_db"]

#FastAPI
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def setup_mongo():
    db.users.create_index("username", unique=True)
    db.chats.create_index("client_id", unique=True)
    db.contacts.create_index("client_id", unique=True)
    print("Banco de dados configurado corretamente.")

setup_mongo()

class User(BaseModel):
    username: str
    password: str
    role: str

class Message(BaseModel):
    sender: str
    receiver: str
    content: str
    timestamp: datetime = datetime.utcnow()

class ChatSession(BaseModel):
    client_id: str
    analyst_id: Optional[str] = None
    messages: List[Message] = []
    status: str = "open"

class Contact(BaseModel):
    client_id: str
    name: str
    email: str
    phone: str
    address: Optional[str] = None

#Token
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#Autenticação
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.users.find_one({"username": form_data.username})
    if not user or not bcrypt.checkpw(form_data.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

# CRUD de Contatos
@app.post("/contacts/")
def create_contact(contact: Contact, user: dict = Depends(get_current_user)):
    if db.contacts.find_one({"client_id": contact.client_id}):
        raise HTTPException(status_code=400, detail="Contato já existe para este cliente")
    db.contacts.insert_one(contact.dict())
    return {"message": "Contato criado com sucesso"}

@app.get("/contacts/{client_id}")
def get_contact(client_id: str, user: dict = Depends(get_current_user)):
    contact = db.contacts.find_one({"client_id": client_id})
    if not contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    contact["_id"] = str(contact["_id"])  # Convertendo ObjectId para string
    return contact

@app.put("/contacts/{client_id}")
def update_contact(client_id: str, contact: Contact, user: dict = Depends(get_current_user)):
    existing_contact = db.contacts.find_one({"client_id": client_id})
    if not existing_contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    db.contacts.update_one({"client_id": client_id}, {"$set": contact.dict()})
    return {"message": "Contato atualizado com sucesso"}

@app.delete("/contacts/{client_id}")
def delete_contact(client_id: str, user: dict = Depends(get_current_user)):
    result = db.contacts.delete_one({"client_id": client_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    return {"message": "Contato excluído com sucesso"}
