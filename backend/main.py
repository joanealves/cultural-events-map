from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Cultural Events Map API")

# Adicionar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de Evento
class Event(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    category: str
    latitude: float
    longitude: float
    date: str
    time: str
    address: str
    image_url: Optional[str] = None

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    return conn

# Criar tabela de eventos
def create_events_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            category TEXT,
            latitude REAL,
            longitude REAL,
            date TEXT,
            time TEXT,
            address TEXT,
            image_url TEXT
        )
    ''')
    conn.close()

# Inicializar tabela
create_events_table()

# Rota para criar evento
@app.post("/events/", response_model=Event)
def create_event(event: Event):
    conn = get_db_connection()
    event.id = str(uuid4())
    
    conn.execute('''
        INSERT INTO events 
        (id, title, description, category, latitude, longitude, date, time, address, image_url) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        event.id, event.title, event.description, event.category, 
        event.latitude, event.longitude, event.date, event.time, 
        event.address, event.image_url
    ))
    conn.commit()
    conn.close()
    
    return event

# Rota para listar eventos
@app.get("/events/", response_model=List[Event])
def list_events(category: Optional[str] = None):
    conn = get_db_connection()
    
    if category:
        cursor = conn.execute('SELECT * FROM events WHERE category = ?', (category,))
    else:
        cursor = conn.execute('SELECT * FROM events')
    
    events = [
        Event(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            category=row['category'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            date=row['date'],
            time=row['time'],
            address=row['address'],
            image_url=row['image_url']
        ) for row in cursor.fetchall()
    ]
    
    conn.close()
    return events

# Rota para buscar evento por ID
@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: str):
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return Event(
        id=row['id'],
        title=row['title'],
        description=row['description'],
        category=row['category'],
        latitude=row['latitude'],
        longitude=row['longitude'],
        date=row['date'],
        time=row['time'],
        address=row['address'],
        image_url=row['image_url']
    )

# Script para popular banco de dados inicial
def populate_initial_events():
    conn = get_db_connection()
    
    # Eventos de exemplo em São Paulo
    initial_events = [
        Event(
            title="Festival de Música MPB",
            description="Grande festival com artistas nacionais",
            category="Música",
            latitude=-23.5505,
            longitude=-46.6333,
            date="2024-07-15",
            time="19:00",
            address="Parque do Ibirapuera",
            image_url="https://example.com/music-festival.jpg"
        ),
        Event(
            title="Exposição de Arte Contemporânea",
            description="Mostra de artistas emergentes",
            category="Arte",
            latitude=-23.5870,
            longitude=-46.6829,
            date="2024-08-10",
            time="14:00",
            address="MASP - Museu de Arte de São Paulo",
            image_url="https://example.com/art-expo.jpg"
        ),
        Event(
            title="Teatro ao Vivo: Peça Contemporânea",
            description="Espetáculo inovador de teatro brasileiro",
            category="Teatro",
            latitude=-23.5450,
            longitude=-46.6388,
            date="2024-07-20",
            time="20:30",
            address="Teatro Municipal de São Paulo",
            image_url="https://example.com/theater.jpg"
        )
    ]
    
    for event in initial_events:
        event.id = str(uuid4())
        conn.execute('''
            INSERT OR REPLACE INTO events 
            (id, title, description, category, latitude, longitude, date, time, address, image_url) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.id, event.title, event.description, event.category, 
            event.latitude, event.longitude, event.date, event.time, 
            event.address, event.image_url
        ))
    
    conn.commit()
    conn.close()

# Descomentar para popular banco de dados na primeira execução
# populate_initial_events()

# Rodar com: uvicorn main:app --reload