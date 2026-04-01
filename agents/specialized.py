"""
UltraCode Specialized Agents
==========================
Agentes especializados para diferentes dominios del desarrollo.
"""

import asyncio
import re
import json
import uuid
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum


# ============================================================
# Base Agent Class
# ============================================================


class AgentStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    ERROR = "error"


@dataclass
class Task:
    id: str
    description: str
    status: str = "pending"
    result: Any = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentResponse:
    content: str
    agent: str
    tools_used: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class BaseAgent:
    name: str = "BaseAgent"
    description: str = "Base agent"
    expertise: List[str] = []

    def __init__(self):
        self.status = AgentStatus.IDLE
        self.tasks: List[Task] = []
        self.history: List[AgentResponse] = []

    async def process(self, prompt: str, context: Dict = None) -> AgentResponse:
        raise NotImplementedError

    def create_task(self, description: str) -> Task:
        task = Task(id=str(uuid.uuid4())[:8], description=description)
        self.tasks.append(task)
        return task

    def complete_task(self, task_id: str, result: Any):
        for task in self.tasks:
            if task.id == task_id:
                task.status = "completed"
                task.result = result
                break


# ============================================================
# FRONTEND AGENT
# ============================================================


class FrontendAgent(BaseAgent):
    """
    Agente Especialista en Frontend Development.
    Dominios: React, Vue, Angular, Svelte, CSS, TypeScript
    """

    name = "FrontendAgent"
    description = "Especialista en desarrollo frontend moderno"
    expertise = [
        "React",
        "Vue",
        "Angular",
        "Svelte",
        "Next.js",
        "Nuxt",
        "TypeScript",
        "CSS3",
        "Tailwind",
        "Responsive Design",
        "PWA",
        "Animaciones",
        "Accesibilidad",
        "Performance",
    ]

    async def process(self, prompt: str, context: Dict = None) -> AgentResponse:
        self.status = AgentStatus.PROCESSING
        context = context or {}

        tasks = []
        content_parts = []
        tools_used = []

        prompt_lower = prompt.lower()

        if "component" in prompt_lower or "componente" in prompt_lower:
            task = self.create_task("Crear componente UI")
            tasks.append(task)
            component = self._extract_name(prompt)
            code = self._generate_component(
                component, context.get("framework", "react")
            )
            content_parts.append(code)
            tools_used.extend(["Read", "Write", "Grep"])
            task.status = "completed"

        elif "page" in prompt_lower or "página" in prompt_lower:
            task = self.create_task("Crear página")
            tasks.append(task)
            content_parts.append(self._generate_page())
            tools_used.extend(["Write", "Glob"])
            task.status = "completed"

        elif "style" in prompt_lower or "css" in prompt_lower:
            task = self.create_task("Generar estilos")
            content_parts.append(self._generate_styles())
            tools_used.append("Write")
            task.status = "completed"

        elif "responsive" in prompt_lower:
            task = self.create_task("Hacer responsive")
            content_parts.append(self._generate_responsive())
            tools_used.append("Write")
            task.status = "completed"

        elif "animation" in prompt_lower or "animación" in prompt_lower:
            task = self.create_task("Crear animaciones")
            content_parts.append(self._generate_animations())
            tools_used.append("Write")
            task.status = "completed"

        elif "pwa" in prompt_lower:
            task = self.create_task("Configurar PWA")
            content_parts.append(self._generate_pwa())
            tools_used.extend(["Write", "Bash"])
            task.status = "completed"

        else:
            content_parts.append(self._generate_frontend_code(prompt))
            tools_used.append("Write")

        self.status = AgentStatus.IDLE

        return AgentResponse(
            content="\n\n".join(content_parts),
            agent=self.name,
            tools_used=tools_used,
            tasks=tasks,
            metadata={"framework": context.get("framework", "react")},
        )

    def _extract_name(self, prompt: str) -> str:
        patterns = [
            r"componente\s+(\w+)",
            r"component\s+(\w+)",
            r"crea.*?(\w+)\s+button",
            r"(\w+)\s+component",
        ]
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1).title()
        return "MyComponent"

    def _generate_component(self, name: str, framework: str) -> str:
        return f"""// {name} Component - Generated by FrontendAgent
import React, {{ useState }} from 'react';

interface {name}Props {{
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  children?: React.ReactNode;
  onClick?: () => void;
}}

export const {name}: React.FC<{name}Props> = ({{
  variant = 'primary',
  size = 'md',
  children,
  onClick
}}) => {{
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200';
  
  const variants = {{
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700',
    outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50'
  }};
  
  const sizes = {{
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  }};
  
  return (
    <button
      className=`${{baseStyles}} ${{variants[variant]}} ${{sizes[size]}}`
      onClick={{onClick}}
    >
      {{children}}
    </button>
  );
}};

export default {name};
"""

    def _generate_page(self) -> str:
        return """// Page Component - Generated by FrontendAgent
import React from 'react';

export default function GeneratedPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="text-xl font-bold text-blue-600">Logo</span>
            </div>
            <div className="flex items-center space-x-4">
              <a href="#" className="text-gray-600 hover:text-gray-900">Inicio</a>
              <a href="#" className="text-gray-600 hover:text-gray-900">Sobre</a>
              <a href="#" className="text-gray-600 hover:text-gray-900">Contacto</a>
            </div>
          </div>
        </nav>
      </header>
      <main className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <h1 className="text-4xl font-extrabold text-gray-900">Bienvenido</h1>
      </main>
    </div>
  );
};
"""

    def _generate_styles(self) -> str:
        return """/* Generated Styles by FrontendAgent */
:root {
  --primary: #3b82f6;
  --secondary: #6b7280;
  --transition: 200ms;
}

.container { max-width: 1200px; margin: 0 auto; }

/* Responsive */
@media (min-width: 640px) { .container { padding: 0 2rem; } }
@media (min-width: 1024px) { .container { padding: 0 4rem; } }

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeIn 0.3s ease-out; }
"""

    def _generate_responsive(self) -> str:
        return """/* Responsive Design - Mobile First */
.grid {
  display: grid;
  gap: 1rem;
}

@media (min-width: 640px) { .grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .grid { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 1280px) { .grid { grid-template-columns: repeat(4, 1fr); } }

/* Breakpoints */
.mobile-only { display: block; }
.tablet-only { display: none; }
.desktop-only { display: none; }

@media (min-width: 768px) {
  .mobile-only { display: none; }
  .tablet-only { display: block; }
}

@media (min-width: 1024px) {
  .tablet-only { display: none; }
  .desktop-only { display: block; }
}
"""

    def _generate_animations(self) -> str:
        return """/* Animations - Generated by FrontendAgent */

@keyframes spin { to { transform: rotate(360deg); } }
.animate-spin { animation: spin 1s linear infinite; }

@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.animate-pulse { animation: pulse 2s infinite; }

@keyframes bounce {
  0%, 100% { transform: translateY(-25%); }
  50% { transform: translateY(0); }
}
.animate-bounce { animation: bounce 1s infinite; }

@keyframes slideIn {
  from { transform: translateX(-100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
.animate-slide-in { animation: slideIn 0.3s ease-out; }

.hover-lift { transition: transform 0.2s, box-shadow 0.2s; }
.hover-lift:hover { transform: translateY(-2px); box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1); }
"""

    def _generate_pwa(self) -> str:
        return """// PWA Configuration - Generated by FrontendAgent
{
  "name": "UltraCode App",
  "short_name": "UltraCode",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}

// Service Worker
const CACHE_NAME = 'ultracode-v1';
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(['/', '/static/js/main.js'])));
});
self.addEventListener('fetch', e => {
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});
"""

    def _generate_frontend_code(self, prompt: str) -> str:
        return f"""// Frontend Code - Generated by FrontendAgent
// Prompt: {prompt}

import React, {{ useState, useEffect }} from 'react';

export default function App() {{
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {{
    setLoading(false);
  }}, []);
  
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">UltraCode Generated</h1>
        {{loading ? (
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        ) : (
          <p className="text-gray-600">Listo para implementar: {prompt[:50]}...</p>
        )}}
      </div>
    </div>
  );
}};
"""


# ============================================================
# BACKEND AGENT
# ============================================================


class BackendAgent(BaseAgent):
    """
    Agente Especialista en Backend Development.
    Dominios: Python, Node.js, APIs REST, GraphQL, Bases de datos
    """

    name = "BackendAgent"
    description = "Especialista en desarrollo backend y APIs"
    expertise = [
        "FastAPI",
        "Django",
        "Flask",
        "Express",
        "NestJS",
        "PostgreSQL",
        "MongoDB",
        "Redis",
        "GraphQL",
        "REST APIs",
        "gRPC",
        "Authentication",
        "Microservices",
        "Docker",
        "Kubernetes",
        "Caching",
    ]

    async def process(self, prompt: str, context: Dict = None) -> AgentResponse:
        self.status = AgentStatus.PROCESSING
        context = context or {}

        tasks = []
        content_parts = []
        tools_used = []
        framework = context.get("framework", "fastapi")

        prompt_lower = prompt.lower()

        if "api" in prompt_lower or "endpoint" in prompt_lower:
            task = self.create_task("Crear API endpoint")
            tasks.append(task)
            content_parts.append(self._generate_api(framework))
            tools_used.extend(["Write", "Read"])
            task.status = "completed"

        elif "model" in prompt_lower or "modelo" in prompt_lower:
            task = self.create_task("Crear modelo de datos")
            tasks.append(task)
            content_parts.append(self._generate_model())
            tools_used.append("Write")
            task.status = "completed"

        elif "auth" in prompt_lower or "login" in prompt_lower:
            task = self.create_task("Implementar autenticación")
            tasks.append(task)
            content_parts.append(self._generate_auth(framework))
            tools_used.extend(["Write", "Bash"])
            task.status = "completed"

        elif "crud" in prompt_lower:
            task = self.create_task("Generar CRUD")
            tasks.append(task)
            content_parts.append(self._generate_crud())
            tools_used.append("Write")
            task.status = "completed"

        elif "database" in prompt_lower or "migrate" in prompt_lower:
            task = self.create_task("Configurar base de datos")
            tasks.append(task)
            content_parts.append(self._generate_database())
            tools_used.extend(["Write", "Bash"])
            task.status = "completed"

        elif "docker" in prompt_lower:
            task = self.create_task("Crear Dockerfile")
            tasks.append(task)
            content_parts.append(self._generate_dockerfile())
            tools_used.append("Write")
            task.status = "completed"

        else:
            content_parts.append(self._generate_backend_code(prompt, framework))
            tools_used.append("Write")

        self.status = AgentStatus.IDLE

        return AgentResponse(
            content="\n\n".join(content_parts),
            agent=self.name,
            tools_used=tools_used,
            tasks=tasks,
            metadata={"framework": framework},
        )

    def _generate_api(self, framework: str) -> str:
        if framework == "fastapi":
            return '''# FastAPI Endpoint - Generated by BackendAgent
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

app = FastAPI(title="UltraCode API", version="1.0.0")

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool = True

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

@app.get("/")
async def root():
    return {"message": "UltraCode API", "version": "1.0.0"}

@app.get("/items", response_model=List[Item])
async def get_items(skip: int = 0, limit: int = 100):
    """Obtiene lista de items con paginación"""
    return []

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """Obtiene un item por ID"""
    return {"id": item_id, "name": "Sample", "price": 0.0}

@app.post("/items", response_model=Item, status_code=201)
async def create_item(item: ItemCreate):
    """Crea un nuevo item"""
    return {"id": 1, **item.model_dump(), "created_at": datetime.now()}

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemCreate):
    """Actualiza un item"""
    return {"id": item_id, **item.model_dump(), "created_at": datetime.now()}

@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    """Elimina un item"""
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        else:
            return self._generate_api("fastapi")

    def _generate_model(self) -> str:
        return """# Database Models - Generated by BackendAgent
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = relationship("Item", back_populates="owner")

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    in_stock = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="items")
"""

    def _generate_auth(self, framework: str) -> str:
        return """# Authentication - Generated by BackendAgent
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"username": username}
"""

    def _generate_crud(self) -> str:
        return """# CRUD Operations - Generated by BackendAgent
from typing import List, Optional, TypeVar, Generic
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")

class CRUDBase(Generic[ModelType]):
    def __init__(self, model):
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: ModelType, obj_in: dict) -> ModelType:
        for key, value in obj_in.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

# Usage:
# crud_item = CRUDBase(Item)
# items = crud_item.get_multi(db)
# item = crud_item.get(db, id=1)
# new_item = crud_item.create(db, {"name": "Test", "price": 9.99})
"""

    def _generate_database(self) -> str:
        return """# Database Configuration - Generated by BackendAgent
DATABASE_URL = "postgresql://user:password@localhost:5432/dbname"

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Alembic migrations:
# alembic init alembic
# alembic revision --autogenerate -m "Initial"
# alembic upgrade head
"""

    def _generate_dockerfile(self) -> str:
        return """# Dockerfile - Generated by BackendAgent
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser --disabled-password --gecos '' appuser
USER appuser

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=postgresql://user:password@db:5432/dbname

HEALTHCHECK --interval=30s --timeout=30s CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

    def _generate_backend_code(self, prompt: str, framework: str) -> str:
        return f"""# Backend Code - Generated by BackendAgent
# Framework: {framework}
# Prompt: {prompt}

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="UltraCode Backend", version="1.0.0")

@app.get("/health")
async def health_check():
    return {{"status": "healthy"}}

@app.get("/")
async def root():
    return {{"message": "UltraCode Backend API"}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""


# ============================================================
# DEVOPS AGENT
# ============================================================


class DevOpsAgent(BaseAgent):
    """
    Agente Especialista en DevOps y Cloud.
    Dominios: Docker, Kubernetes, CI/CD, AWS, GCP, Terraform
    """

    name = "DevOpsAgent"
    description = "Especialista en DevOps, CI/CD y Cloud"
    expertise = [
        "Docker",
        "Kubernetes",
        "Helm",
        "Kustomize",
        "GitHub Actions",
        "GitLab CI",
        "Jenkins",
        "AWS",
        "GCP",
        "Azure",
        "Terraform",
        "Prometheus",
        "Grafana",
        "ELK",
        "Ansible",
        "Security",
    ]

    async def process(self, prompt: str, context: Dict = None) -> AgentResponse:
        self.status = AgentStatus.PROCESSING
        context = context or {}

        tasks = []
        content_parts = []
        tools_used = []

        prompt_lower = prompt.lower()

        if "docker" in prompt_lower or "container" in prompt_lower:
            task = self.create_task("Generar Docker configuration")
            tasks.append(task)
            content_parts.append(self._generate_docker())
            tools_used.append("Write")
            task.status = "completed"

        elif (
            "kubernetes" in prompt_lower
            or "k8s" in prompt_lower
            or "helm" in prompt_lower
        ):
            task = self.create_task("Crear Kubernetes manifests")
            tasks.append(task)
            content_parts.append(self._generate_kubernetes())
            tools_used.append("Write")
            task.status = "completed"

        elif "ci/cd" in prompt_lower or "github actions" in prompt_lower:
            task = self.create_task("Configurar pipeline CI/CD")
            tasks.append(task)
            content_parts.append(self._generate_cicd())
            tools_used.append("Write")
            task.status = "completed"

        elif "terraform" in prompt_lower or "iac" in prompt_lower:
            task = self.create_task("Crear Terraform infrastructure")
            tasks.append(task)
            content_parts.append(self._generate_terraform())
            tools_used.append("Write")
            task.status = "completed"

        elif (
            "monitoring" in prompt_lower
            or "prometheus" in prompt_lower
            or "grafana" in prompt_lower
        ):
            task = self.create_task("Configurar monitoring stack")
            tasks.append(task)
            content_parts.append(self._generate_monitoring())
            tools_used.append("Write")
            task.status = "completed"

        elif "deploy" in prompt_lower:
            task = self.create_task("Generar deployment config")
            tasks.append(task)
            content_parts.append(self._generate_deployment())
            tools_used.extend(["Write", "Bash"])
            task.status = "completed"

        else:
            content_parts.append(self._generate_devops_config(prompt))
            tools_used.append("Write")

        self.status = AgentStatus.IDLE

        return AgentResponse(
            content="\n\n".join(content_parts),
            agent=self.name,
            tools_used=tools_used,
            tasks=tasks,
            metadata={"provider": context.get("cloud", "aws")},
        )

    def _generate_docker(self) -> str:
        return """# Dockerfile - Generated by DevOpsAgent
# Multi-stage Build

# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:18-alpine AS production
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
WORKDIR /app
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
USER nodejs
EXPOSE 3000
ENV NODE_ENV=production
CMD ["node", "dist/server.js"]

---
# docker-compose.yml
version: "3.8"
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
    restart: unless-stopped

volumes:
  postgres_data:
"""

    def _generate_kubernetes(self) -> str:
        return """# Kubernetes Manifests - Generated by DevOpsAgent

---
apiVersion: v1
kind: Namespace
metadata:
  name: production
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: production
data:
  NODE_ENV: "production"
  LOG_LEVEL: "info"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      containers:
      - name: app
        image: myapp:latest
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: app-service
  namespace: production
spec:
  selector:
    app: app
  ports:
  - port: 80
    targetPort: 3000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
"""

    def _generate_cicd(self) -> str:
        return """# GitHub Actions CI/CD - Generated by DevOpsAgent

name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  quality:
    name: Code Quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      - name: Install dependencies
        run: npm ci
      - name: ESLint
        run: npm run lint
      - name: Unit tests
        run: npm run test

  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: quality
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
"""

    def _generate_terraform(self) -> str:
        return """# Terraform IaC - Generated by DevOpsAgent

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "my-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"
  
  name = "ultracode-vpc"
  cidr = var.vpc_cidr
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
  
  enable_nat_gateway     = true
  one_nat_gateway_per_az = true
}

variable "aws_region" {
  default = "us-east-1"
}

variable "vpc_cidr" {
  default = "10.0.0.0/16"
}
"""

    def _generate_monitoring(self) -> str:
        return """# Monitoring Stack - Generated by DevOpsAgent

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: 'prometheus'
        static_configs:
          - targets: ['localhost:9090']
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:10.2
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: grafana-secrets
              key: admin-password
"""

    def _generate_deployment(self) -> str:
        return """# Deployment Configuration - Generated by DevOpsAgent

# Pre-deployment checks
PRE_DEPLOYMENT:
  - name: Run migrations
    command: npm run migrate:prod
    timeout: 300s
  - name: Health check
    command: curl -f http://localhost:3000/health

# Deployment Strategy: Blue-Green
DEPLOYMENT_STRATEGY:
  type: blue-green
  health_check:
    path: /health
    port: 3000
    interval: 10s
    healthy_threshold: 2
    unhealthy_threshold: 3

# Rollback
ROLLBACK:
  automatic: true
  trigger:
    - error_rate > 5%
    - p99_latency > 2000ms
    - health_check_failures > 3
"""

    def _generate_devops_config(self, prompt: str) -> str:
        return f"""# DevOps Configuration - Generated by DevOpsAgent
# Prompt: {prompt}

# Recomendaciones:
# 1. Dockerizar la aplicación
# 2. Crear manifiestos de Kubernetes
# 3. Configurar pipeline CI/CD
# 4. Desplegar infraestructura con Terraform
# 5. Configurar monitoring y alerting
"""


# ============================================================
# BLOCKCHAIN AGENT
# ============================================================


class BlockchainAgent(BaseAgent):
    """
    Agente Especialista en Blockchain y Web3.
    Dominios: Solidity, Ethereum, NFTs, DeFi, Smart Contracts
    """

    name = "BlockchainAgent"
    description = "Especialista en Blockchain y Smart Contracts"
    expertise = [
        "Solidity",
        "Rust",
        "Vyper",
        "Ethereum",
        "Solana",
        "Polygon",
        "Avalanche",
        "ERC-20",
        "ERC-721",
        "ERC-1155",
        "DeFi",
        "NFTs",
        "DAOs",
        "Web3.js",
        "Ethers.js",
        "IPFS",
        "Smart Contracts",
        "Hardhat",
        "Foundry",
    ]

    async def process(self, prompt: str, context: Dict = None) -> AgentResponse:
        self.status = AgentStatus.PROCESSING
        context = context or {}

        tasks = []
        content_parts = []
        tools_used = []

        prompt_lower = prompt.lower()

        if (
            "nft" in prompt_lower
            or "erc-721" in prompt_lower
            or "erc-1155" in prompt_lower
        ):
            task = self.create_task("Generar Smart Contract NFT")
            tasks.append(task)
            content_parts.append(self._generate_nft())
            tools_used.append("Write")
            task.status = "completed"

        elif "token" in prompt_lower or "erc-20" in prompt_lower:
            task = self.create_task("Generar Smart Contract Token")
            tasks.append(task)
            content_parts.append(self._generate_token())
            tools_used.append("Write")
            task.status = "completed"

        elif "defi" in prompt_lower or "swap" in prompt_lower or "dex" in prompt_lower:
            task = self.create_task("Generar Smart Contract DeFi")
            tasks.append(task)
            content_parts.append(self._generate_defi())
            tools_used.append("Write")
            task.status = "completed"

        elif "dao" in prompt_lower or "governance" in prompt_lower:
            task = self.create_task("Generar Smart Contract DAO")
            tasks.append(task)
            content_parts.append(self._generate_dao())
            tools_used.append("Write")
            task.status = "completed"

        elif (
            "web3" in prompt_lower
            or "frontend" in prompt_lower
            or "connect" in prompt_lower
        ):
            task = self.create_task("Generar código Web3 frontend")
            tasks.append(task)
            content_parts.append(self._generate_web3())
            tools_used.append("Write")
            task.status = "completed"

        elif "deploy" in prompt_lower or "migration" in prompt_lower:
            task = self.create_task("Generar script de deploy")
            tasks.append(task)
            content_parts.append(self._generate_deploy())
            tools_used.append("Write")
            task.status = "completed"

        else:
            content_parts.append(self._generate_smart_contract(prompt))
            tools_used.append("Write")

        self.status = AgentStatus.IDLE

        return AgentResponse(
            content="\n\n".join(content_parts),
            agent=self.name,
            tools_used=tools_used,
            tasks=tasks,
            metadata={"network": context.get("network", "ethereum")},
        )

    def _generate_token(self) -> str:
        return """// ERC-20 Token - Generated by BlockchainAgent
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract UltraToken is ERC20, ERC20Burnable, Ownable {
    uint256 public constant TOTAL_SUPPLY = 1000000 * 10 ** decimals();
    
    constructor(address initialOwner)
        ERC20("UltraToken", "ULT")
        Ownable(initialOwner)
    {
        _mint(initialOwner, TOTAL_SUPPLY);
    }
    
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
}
"""

    def _generate_nft(self) -> str:
        return """// ERC-721 NFT - Generated by BlockchainAgent
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract UltraNFT is ERC721, ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    
    Counters.Counter private _tokenIdCounter;
    uint256 public mintPrice = 0.05 ether;
    uint256 public maxSupply = 10000;
    uint256 public maxPerWallet = 5;
    
    mapping(address => uint256) public mintedPerWallet;
    
    constructor(address initialOwner, string memory baseURI)
        ERC721("UltraNFT", "ULTN")
        Ownable(initialOwner)
    {
        _setBaseURI(baseURI);
    }
    
    function mint(address to) external payable {
        require(msg.value >= mintPrice, "Insufficient payment");
        require(_tokenIdCounter.current() < maxSupply, "Max supply reached");
        require(mintedPerWallet[msg.sender] < maxPerWallet, "Max per wallet");
        
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        mintedPerWallet[msg.sender]++;
        _safeMint(to, tokenId);
    }
    
    function setMintPrice(uint256 newPrice) external onlyOwner {
        mintPrice = newPrice;
    }
    
    function withdraw() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
    
    function tokenURI(uint256 tokenId)
        public view override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }
}
"""

    def _generate_defi(self) -> str:
        return """// DeFi Staking - Generated by BlockchainAgent
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract SimpleStaking is ReentrancyGuard {
    struct StakeInfo {
        uint256 amount;
        uint256 startTime;
        uint256 rewards;
    }
    
    IERC20 public stakingToken;
    IERC20 public rewardToken;
    uint256 public rewardRate = 100;
    
    mapping(address => StakeInfo) public stakes;
    
    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event RewardClaimed(address indexed user, uint256 reward);
    
    constructor(address _stakingToken, address _rewardToken) {
        stakingToken = IERC20(_stakingToken);
        rewardToken = IERC20(_rewardToken);
    }
    
    function stake(uint256 amount) external nonReentrant {
        require(amount > 0, "Cannot stake 0");
        
        uint256 pendingRewards = calculateRewards(msg.sender);
        stakingToken.transferFrom(msg.sender, address(this), amount);
        
        if (stakes[msg.sender].amount > 0) {
            stakes[msg.sender].rewards += pendingRewards;
        }
        
        stakes[msg.sender].amount += amount;
        stakes[msg.sender].startTime = block.timestamp;
        
        emit Staked(msg.sender, amount);
    }
    
    function unstake(uint256 amount) external nonReentrant {
        require(stakes[msg.sender].amount >= amount, "Insufficient balance");
        
        uint256 pendingRewards = calculateRewards(msg.sender);
        stakes[msg.sender].amount -= amount;
        stakes[msg.sender].rewards = 0;
        stakes[msg.sender].startTime = block.timestamp;
        
        stakingToken.transfer(msg.sender, amount);
        
        if (pendingRewards > 0) {
            rewardToken.transfer(msg.sender, pendingRewards);
            emit RewardClaimed(msg.sender, pendingRewards);
        }
        
        emit Unstaked(msg.sender, amount);
    }
    
    function calculateRewards(address user) public view returns (uint256) {
        if (stakes[user].amount == 0) return 0;
        uint256 timeStaked = block.timestamp - stakes[user].startTime;
        return (stakes[user].amount * rewardRate * timeStaked) / (365 days * 1000);
    }
}
"""

    def _generate_dao(self) -> str:
        return """// DAO Governance - Generated by BlockchainAgent
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";
import "@openzeppelin/contracts/governance/Governor.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorCountingSimple.sol";

contract UltraDAO is Governor, GovernorCountingSimple, ERC20Votes {
    uint256 public votingDelay;
    uint256 public votingPeriod;
    uint256 public proposalThreshold;
    
    constructor(
        IVotes _token,
        uint256 _votingDelay,
        uint256 _votingPeriod,
        uint256 _proposalThreshold
    )
        Governor("UltraDAO")
        ERC20Votes()
    {
        votingDelay = _votingDelay;
        votingPeriod = _votingPeriod;
        proposalThreshold = _proposalThreshold;
    }
    
    function votingDelay() public view override returns (uint256) {
        return votingDelay;
    }
    
    function votingPeriod() public view override returns (uint256) {
        return votingPeriod;
    }
    
    function proposalThreshold() public view override returns (uint256) {
        return proposalThreshold;
    }
    
    function propose(
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        string memory description
    ) public override returns (uint256) {
        require(
            getVotes(msg.sender, block.timestamp - 1) >= proposalThreshold,
            "Below proposal threshold"
        );
        return super.propose(targets, values, calldatas, description);
    }
}
"""

    def _generate_web3(self) -> str:
        return """// Web3 Integration - Generated by BlockchainAgent

import { ethers } from "ethers";

class Web3Service {
  constructor() {
    this.provider = null;
    this.signer = null;
    this.address = null;
  }
  
  async connect() {
    if (typeof window.ethereum !== "undefined") {
      const accounts = await window.ethereum.request({
        method: "eth_requestAccounts"
      });
      this.provider = new ethers.BrowserProvider(window.ethereum);
      this.signer = await this.provider.getSigner();
      this.address = await this.signer.getAddress();
      return { success: true, address: this.address };
    }
    return { success: false, error: "MetaMask not installed" };
  }
  
  async disconnect() {
    this.provider = null;
    this.signer = null;
    this.address = null;
  }
  
  async getContract(address, abi) {
    if (!this.provider) throw new Error("Wallet not connected");
    return new ethers.Contract(address, abi, this.provider);
  }
  
  async getWriteContract(address, abi) {
    if (!this.signer) throw new Error("Wallet not connected");
    return new ethers.Contract(address, abi, this.signer);
  }
  
  formatAddress(address) {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  }
}

export const web3Service = new Web3Service();
"""

    def _generate_deploy(self) -> str:
        return """// Deploy Script - Generated by BlockchainAgent

const hre = require("hardhat");

async function main() {
  console.log("Deploying contracts...");
  
  const UltraToken = await hre.ethers.getContractFactory("UltraToken");
  const token = await UltraToken.deploy("0xYourOwnerAddress");
  await token.waitForDeployment();
  
  console.log("UltraToken deployed to:", await token.getAddress());
  
  const UltraNFT = await hre.ethers.getContractFactory("UltraNFT");
  const nft = await UltraNFT.deploy("0xYourOwnerAddress", "https://api.example.com/");
  await nft.waitForDeployment();
  
  console.log("UltraNFT deployed to:", await nft.getAddress());
  
  // Save deployment addresses
  const fs = require("fs");
  const deployments = {
    UltraToken: await token.getAddress(),
    UltraNFT: await nft.getAddress()
  };
  fs.writeFileSync("deployments.json", JSON.stringify(deployments, null, 2));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
"""

    def _generate_smart_contract(self, prompt: str) -> str:
        return f"""// Smart Contract - Generated by BlockchainAgent
// Prompt: {prompt}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract UltraContract is ReentrancyGuard, Ownable {{
    uint256 public value;
    address public beneficiary;
    bool public isActive;
    
    event ValueUpdated(uint256 newValue);
    
    constructor(address _owner) Ownable(_owner) {{
        isActive = false;
    }}
    
    function setValue(uint256 _value) external onlyOwner {{
        value = _value;
        emit ValueUpdated(_value);
    }}
    
    function activate() external onlyOwner {{
        isActive = true;
    }}
    
    receive() external payable {{}}
}}
"""


# ============================================================
# VIDEOGAMES AGENT
# ============================================================


class VideogamesAgent(BaseAgent):
    """
    Agente Especialista en Videojuegos.
    Dominios: Unity, Unreal, Godot, Phaser, Three.js
    """

    name = "VideogamesAgent"
    description = "Especialista en desarrollo de videojuegos"
    expertise = [
        "Unity",
        "Unreal Engine",
        "Godot",
        "GDScript",
        "C#",
        "C++",
        "Blueprints",
        "Three.js",
        "Phaser",
        "PixiJS",
        "GameMaker",
        "Physics",
        "AI",
        "Shaders",
        "Particles",
        "Networking",
        "Multiplayer",
        "Mobile Games",
    ]

    async def process(self, prompt: str, context: Dict = None) -> AgentResponse:
        self.status = AgentStatus.PROCESSING
        context = context or {}

        tasks = []
        content_parts = []
        tools_used = []
        engine = context.get("engine", "unity")

        prompt_lower = prompt.lower()

        if "player" in prompt_lower or "character" in prompt_lower:
            task = self.create_task("Generar controlador de jugador")
            tasks.append(task)
            content_parts.append(self._generate_player_controller(engine))
            tools_used.append("Write")
            task.status = "completed"

        elif "game" in prompt_lower or "manager" in prompt_lower:
            task = self.create_task("Generar sistema de juego")
            tasks.append(task)
            content_parts.append(self._generate_game_manager())
            tools_used.append("Write")
            task.status = "completed"

        elif "ui" in prompt_lower or "hud" in prompt_lower:
            task = self.create_task("Generar sistema UI/HUD")
            tasks.append(task)
            content_parts.append(self._generate_ui())
            tools_used.append("Write")
            task.status = "completed"

        elif "enemy" in prompt_lower or "npc" in prompt_lower or "ia" in prompt_lower:
            task = self.create_task("Generar IA de enemigo")
            tasks.append(task)
            content_parts.append(self._generate_enemy_ai())
            tools_used.append("Write")
            task.status = "completed"

        elif "particle" in prompt_lower or "effect" in prompt_lower:
            task = self.create_task("Generar efectos visuales")
            tasks.append(task)
            content_parts.append(self._generate_particles())
            tools_used.append("Write")
            task.status = "completed"

        elif "platformer" in prompt_lower:
            task = self.create_task("Generar plataforma 2D")
            tasks.append(task)
            content_parts.append(self._generate_platformer())
            tools_used.append("Write")
            task.status = "completed"

        else:
            content_parts.append(self._generate_game_code(prompt, engine))
            tools_used.append("Write")

        self.status = AgentStatus.IDLE

        return AgentResponse(
            content="\n\n".join(content_parts),
            agent=self.name,
            tools_used=tools_used,
            tasks=tasks,
            metadata={"engine": engine},
        )

    def _generate_player_controller(self, engine: str) -> str:
        return """// PlayerController.cs - Generated by VideogamesAgent
using UnityEngine;
using UnityEngine.InputSystem;

[RequireComponent(typeof(CharacterController))]
public class PlayerController : MonoBehaviour
{
    [Header("Movement Settings")]
    [SerializeField] private float moveSpeed = 8f;
    [SerializeField] private float sprintSpeed = 12f;
    [SerializeField] private float jumpHeight = 3f;
    [SerializeField] private float gravity = -9.81f;
    
    private CharacterController controller;
    private Vector3 velocity;
    private bool isGrounded;
    
    private Vector2 moveInput;
    private bool jumpPressed;
    private bool sprintPressed;
    
    private void Awake()
    {
        controller = GetComponent<CharacterController>();
    }
    
    private void Update()
    {
        isGrounded = controller.isGrounded;
        if (isGrounded && velocity.y < 0)
        {
            velocity.y = -2f;
        }
        
        velocity.y += gravity * Time.deltaTime;
        
        Vector3 move = transform.right * moveInput.x + transform.forward * moveInput.y;
        float currentSpeed = sprintPressed ? sprintSpeed : moveSpeed;
        
        controller.Move(move * currentSpeed * Time.deltaTime);
        controller.Move(velocity * Time.deltaTime);
    }
    
    public void OnMove(InputAction.CallbackContext context)
    {
        moveInput = context.ReadValue<Vector2>();
    }
    
    public void OnJump(InputAction.CallbackContext context)
    {
        if (context.performed && isGrounded)
        {
            velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
        }
    }
    
    public void OnSprint(InputAction.CallbackContext context)
    {
        sprintPressed = context.performed;
    }
}
"""

    def _generate_game_manager(self) -> str:
        return """// GameManager.cs - Generated by VideogamesAgent
using UnityEngine;
using UnityEngine.SceneManagement;
using System.Collections.Generic;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }
    
    public enum GameState { MainMenu, Playing, Paused, GameOver, Victory }
    
    [SerializeField] private GameState currentState = GameState.MainMenu;
    
    private int score = 0;
    private int highScore = 0;
    
    public System.Action<GameState> OnStateChanged;
    public System.Action<int> OnScoreChanged;
    
    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        Instance = this;
        highScore = PlayerPrefs.GetInt("HighScore", 0);
    }
    
    public void SetState(GameState newState)
    {
        currentState = newState;
        OnStateChanged?.Invoke(newState);
        
        switch (newState)
        {
            case GameState.Playing:
                Time.timeScale = 1f;
                break;
            case GameState.Paused:
                Time.timeScale = 0f;
                break;
        }
    }
    
    public void AddScore(int points)
    {
        score += points;
        OnScoreChanged?.Invoke(score);
    }
    
    public void GameOver()
    {
        if (score > highScore)
        {
            highScore = score;
            PlayerPrefs.SetInt("HighScore", highScore);
        }
        SetState(GameState.GameOver);
    }
    
    public void RestartLevel()
    {
        Time.timeScale = 1f;
        SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
    }
}
"""

    def _generate_ui(self) -> str:
        return """// UIManager.cs - Generated by VideogamesAgent
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class UIManager : MonoBehaviour
{
    [Header("HUD Elements")]
    [SerializeField] private TextMeshProUGUI scoreText;
    [SerializeField] private TextMeshProUGUI healthText;
    [SerializeField] private Image healthBar;
    [SerializeField] private Image experienceBar;
    
    [Header("Panels")]
    [SerializeField] private GameObject mainMenuPanel;
    [SerializeField] private GameObject gameOverPanel;
    [SerializeField] private GameObject pausePanel;
    
    private void Start()
    {
        if (GameManager.Instance != null)
        {
            GameManager.Instance.OnScoreChanged += UpdateScore;
            GameManager.Instance.OnStateChanged += HandleStateChanged;
        }
    }
    
    public void UpdateScore(int newScore)
    {
        if (scoreText != null)
        {
            scoreText.text = $"Score: {newScore}";
        }
    }
    
    public void UpdateHealth(float current, float max)
    {
        if (healthBar != null)
        {
            healthBar.fillAmount = current / max;
        }
        if (healthText != null)
        {
            healthText.text = $"{current}/{max}";
        }
    }
    
    private void HandleStateChanged(GameManager.GameState state)
    {
        mainMenuPanel?.SetActive(state == GameManager.GameState.MainMenu);
        gameOverPanel?.SetActive(state == GameManager.GameState.GameOver);
        pausePanel?.SetActive(state == GameManager.GameState.Paused);
    }
    
    public void ShowMainMenu()
    {
        GameManager.Instance.SetState(GameManager.GameState.MainMenu);
    }
    
    public void StartGame()
    {
        GameManager.Instance.SetState(GameManager.GameState.Playing);
    }
    
    public void PauseGame()
    {
        GameManager.Instance.SetState(GameManager.GameState.Paused);
    }
}
"""

    def _generate_enemy_ai(self) -> str:
        return """// EnemyAI.cs - Generated by VideogamesAgent
using UnityEngine;
using System.Collections;

public enum EnemyState { Idle, Patrol, Chase, Attack, Hurt, Dead }

public class EnemyAI : MonoBehaviour
{
    [Header("Settings")]
    [SerializeField] private float moveSpeed = 3f;
    [SerializeField] private float chaseSpeed = 5f;
    [SerializeField] private float detectionRange = 15f;
    [SerializeField] private float attackRange = 2f;
    
    [SerializeField] private Transform player;
    [SerializeField] private Transform[] patrolPoints;
    
    private EnemyState currentState = EnemyState.Patrol;
    private int currentHealth = 100;
    private int currentPatrolIndex = 0;
    
    private CharacterController controller;
    private Animator animator;
    
    private void Awake()
    {
        controller = GetComponent<CharacterController>();
        animator = GetComponent<Animator>();
    }
    
    private void Start()
    {
        if (player == null)
        {
            GameObject playerObj = GameObject.FindGameObjectWithTag("Player");
            if (playerObj != null) player = playerObj.transform;
        }
    }
    
    private void Update()
    {
        if (currentState == EnemyState.Dead) return;
        
        bool playerInRange = IsPlayerInRange();
        
        switch (currentState)
        {
            case EnemyState.Patrol:
                HandlePatrol(playerInRange);
                break;
            case EnemyState.Chase:
                HandleChase(playerInRange);
                break;
            case EnemyState.Attack:
                HandleAttack(playerInRange);
                break;
        }
    }
    
    private void HandlePatrol(bool playerInRange)
    {
        if (playerInRange)
        {
            currentState = EnemyState.Chase;
            return;
        }
        
        if (patrolPoints != null && patrolPoints.Length > 0)
        {
            Transform target = patrolPoints[currentPatrolIndex];
            Vector3 direction = (target.position - transform.position).normalized;
            direction.y = 0;
            
            transform.rotation = Quaternion.Slerp(
                transform.rotation,
                Quaternion.LookRotation(direction),
                Time.deltaTime * 5f
            );
            
            controller.Move(direction * moveSpeed * Time.deltaTime);
            
            if (Vector3.Distance(transform.position, target.position) < 1f)
            {
                currentPatrolIndex = (currentPatrolIndex + 1) % patrolPoints.Length;
            }
        }
    }
    
    private void HandleChase(bool playerInRange)
    {
        if (!playerInRange)
        {
            currentState = EnemyState.Patrol;
            return;
        }
        
        Vector3 direction = (player.position - transform.position).normalized;
        direction.y = 0;
        
        transform.rotation = Quaternion.Slerp(
            transform.rotation,
            Quaternion.LookRotation(direction),
            Time.deltaTime * 8f
        );
        
        if (Vector3.Distance(transform.position, player.position) <= attackRange)
        {
            currentState = EnemyState.Attack;
            return;
        }
        
        controller.Move(direction * chaseSpeed * Time.deltaTime);
    }
    
    private void HandleAttack(bool playerInRange)
    {
        if (!playerInRange || Vector3.Distance(transform.position, player.position) > attackRange + 1f)
        {
            currentState = EnemyState.Chase;
            return;
        }
        
        animator?.SetTrigger("Attack");
    }
    
    private bool IsPlayerInRange()
    {
        if (player == null) return false;
        return Vector3.Distance(transform.position, player.position) <= detectionRange;
    }
    
    public void TakeDamage(int amount)
    {
        currentHealth -= amount;
        if (currentHealth <= 0)
        {
            currentState = EnemyState.Dead;
            animator?.SetTrigger("Death");
        }
        else
        {
            currentState = EnemyState.Hurt;
            animator?.SetTrigger("Hurt");
        }
    }
}
"""

    def _generate_particles(self) -> str:
        return """// ParticleEffects.cs - Generated by VideogamesAgent
using UnityEngine;

public class ParticleEffects : MonoBehaviour
{
    [Header("Prefabs")]
    [SerializeField] private GameObject explosionPrefab;
    [SerializeField] private GameObject hitSparkPrefab;
    [SerializeField] private GameObject dustTrailPrefab;
    [SerializeField] private GameObject healEffectPrefab;
    
    public void PlayExplosion(Vector3 position, float scale = 1f)
    {
        if (explosionPrefab != null)
        {
            GameObject effect = Instantiate(explosionPrefab, position, Quaternion.identity);
            effect.transform.localScale = Vector3.one * scale;
            
            ParticleSystem ps = effect.GetComponent<ParticleSystem>();
            float lifetime = ps != null ? ps.main.duration + 1f : 2f;
            Destroy(effect, lifetime);
        }
    }
    
    public void PlayHitSpark(Vector3 position, Vector3 normal)
    {
        if (hitSparkPrefab != null)
        {
            GameObject effect = Instantiate(hitSparkPrefab, position, Quaternion.LookRotation(normal));
            Destroy(effect, 0.5f);
        }
    }
    
    public void PlayDustTrail(Vector3 position)
    {
        if (dustTrailPrefab != null)
        {
            GameObject effect = Instantiate(dustTrailPrefab, position, Quaternion.identity);
            Destroy(effect, 1f);
        }
    }
    
    public void PlayHealEffect(Transform target)
    {
        if (healEffectPrefab != null)
        {
            GameObject effect = Instantiate(healEffectPrefab, target.position, Quaternion.identity);
            effect.transform.SetParent(target);
            Destroy(effect, 2f);
        }
    }
    
    public static void ScreenShake(float intensity, float duration)
    {
        Camera mainCamera = Camera.main;
        if (mainCamera == null) return;
        
        Vector3 originalPos = mainCamera.transform.position;
        float elapsed = 0f;
        
        while (elapsed < duration)
        {
            float x = Random.Range(-1f, 1f) * intensity;
            float y = Random.Range(-1f, 1f) * intensity;
            
            mainCamera.transform.position = originalPos + new Vector3(x, y, 0);
            
            elapsed += Time.deltaTime;
            intensity *= 0.95f;
            
            // Use coroutine in actual Unity
        }
        
        mainCamera.transform.position = originalPos;
    }
}
"""

    def _generate_platformer(self) -> str:
        return """// Platformer2D.cs - Generated by VideogamesAgent
using UnityEngine;
using UnityEngine.InputSystem;

public class Platformer2D : MonoBehaviour
{
    [Header("Movement")]
    [SerializeField] private float moveSpeed = 8f;
    [SerializeField] private float jumpForce = 12f;
    [SerializeField] private float gravity = -30f;
    
    private Rigidbody2D rb;
    private SpriteRenderer sprite;
    private Animator animator;
    
    private Vector2 moveInput;
    private bool isGrounded;
    private bool isJumping;
    
    private void Awake()
    {
        rb = GetComponent<Rigidbody2D>();
        sprite = GetComponent<SpriteRenderer>();
        animator = GetComponent<Animator>();
    }
    
    private void FixedUpdate()
    {
        // Horizontal movement
        rb.velocity = new Vector2(moveInput.x * moveSpeed, rb.velocity.y);
        
        // Jump
        if (isJumping && isGrounded)
        {
            rb.velocity = new Vector2(rb.velocity.x, jumpForce);
            isJumping = false;
        }
        
        // Apply gravity
        if (!isGrounded)
        {
            rb.velocity += Vector2.up * gravity * Time.fixedDeltaTime;
        }
        
        // Update animator
        animator?.SetFloat("Speed", Mathf.Abs(rb.velocity.x));
        animator?.SetBool("IsGrounded", isGrounded);
        
        // Flip sprite
        if (moveInput.x > 0.01f)
            sprite.flipX = false;
        else if (moveInput.x < -0.01f)
            sprite.flipX = true;
    }
    
    public void OnMove(InputAction.CallbackContext context)
    {
        moveInput = context.ReadValue<Vector2>();
    }
    
    public void OnJump(InputAction.CallbackContext context)
    {
        if (context.performed && isGrounded)
        {
            isJumping = true;
        }
    }
    
    private void OnCollisionEnter2D(Collision2D collision)
    {
        if (collision.gameObject.CompareTag("Ground"))
        {
            isGrounded = true;
        }
    }
    
    private void OnCollisionExit2D(Collision2D collision)
    {
        if (collision.gameObject.CompareTag("Ground"))
        {
            isGrounded = false;
        }
    }
}
"""

    def _generate_game_code(self, prompt: str, engine: str) -> str:
        return f"""// Game Code - Generated by VideogamesAgent
// Engine: {engine}
// Prompt: {prompt}

// Framework específico según el motor seleccionado
"""


# ============================================================
# Agent Factory
# ============================================================


class AgentFactory:
    """Fábrica de agentes"""

    @staticmethod
    def get_agent(agent_type: str) -> BaseAgent:
        agents = {
            "frontend": FrontendAgent,
            "backend": BackendAgent,
            "devops": DevOpsAgent,
            "blockchain": BlockchainAgent,
            "videogames": VideogamesAgent,
        }

        agent_class = agents.get(agent_type.lower())
        if agent_class:
            return agent_class()

        raise ValueError(f"Unknown agent type: {agent_type}")

    @staticmethod
    def get_all_agents() -> Dict[str, BaseAgent]:
        return {
            "frontend": FrontendAgent(),
            "backend": BackendAgent(),
            "devops": DevOpsAgent(),
            "blockchain": BlockchainAgent(),
            "videogames": VideogamesAgent(),
        }
