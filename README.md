# UltraCode - Sistema de Programación IA

Sistema completo de programación asistida por IA basado en la arquitectura de Claude Code, implementado con LangChain y Streamlit.

## 🎯 Descripción

UltraCode implementa los **12 pilares fundamentales** de la arquitectura de Claude Code y agrega **5 agentes especializados** para diferentes dominios del desarrollo.

## 📁 Estructura del Proyecto

```
ultracode/
├── app.py                      # Aplicación principal Streamlit
├── demo.py                     # Script de demostración
├── requirements.txt            # Dependencias
├── README.md                   # Documentación
├── index.html                  # Interfaz web alternativa
├── core/                       # Núcleo del sistema
│   ├── __init__.py
│   ├── terminal.py             # Buffer de terminal
│   ├── executor.py             # StreamingToolExecutor
│   ├── permissions.py          # Sistema dual de permisos
│   ├── features.py             # Feature Gates
│   ├── agents.py               # Sistema de sub-agentes
│   ├── query.py                # Query Engine + Budget
│   ├── session.py              # Checkpoint/Restore
│   ├── cache.py                # Prompt Caching
│   ├── deferred.py             # Deferred Loading
│   └── mcp.py                 # Cliente MCP
├── agents/                     # Agentes especializados
│   └── specialized.py          # 5 agentes domain-specific
└── mcp/                       # Servidores MCP
    └── servers.py              # 6 servidores MCP
```

## 🤖 5 Agentes Especializados

### 1. FrontendAgent
**Dominio:** Desarrollo Frontend Moderno

**Expertise:**
- React, Vue, Angular, Svelte, Next.js, Nuxt
- TypeScript, CSS3, TailwindCSS
- Responsive Design, PWA, Animaciones
- Accesibilidad, Performance

**Herramientas generadas:**
- Componentes UI (Button, Input, Card, Modal, Navbar)
- Páginas completas
- Estilos CSS y animaciones
- Configuración PWA

```python
from agents.specialized import FrontendAgent

agent = FrontendAgent()
response = await agent.process("crea un componente Button")
```

### 2. BackendAgent
**Dominio:** Desarrollo Backend y APIs

**Expertise:**
- FastAPI, Django, Flask, Express, NestJS
- PostgreSQL, MongoDB, Redis, GraphQL
- REST APIs, gRPC, Authentication
- Docker, Kubernetes, Microservicios

**Herramientas generadas:**
- APIs REST con endpoints CRUD
- Modelos de datos
- Sistemas de autenticación JWT
- Configuración de bases de datos

```python
from agents.specialized import BackendAgent

agent = BackendAgent()
response = await agent.process("crea un API endpoint con FastAPI", {"framework": "fastapi"})
```

### 3. DevOpsAgent
**Dominio:** DevOps, CI/CD y Cloud

**Expertise:**
- Docker, Kubernetes, Helm, Kustomize
- GitHub Actions, GitLab CI, Jenkins
- AWS, GCP, Azure, Terraform
- Prometheus, Grafana, ELK Stack

**Herramientas generadas:**
- Dockerfiles optimizados
- Manifiestos de Kubernetes
- Pipelines CI/CD
- Infrastructure as Code (Terraform)

```python
from agents.specialized import DevOpsAgent

agent = DevOpsAgent()
response = await agent.process("crea configuración Docker", {"cloud": "aws"})
```

### 4. BlockchainAgent
**Dominio:** Blockchain y Web3

**Expertise:**
- Solidity, Rust, Vyper
- Ethereum, Solana, Polygon, Avalanche
- ERC-20, ERC-721, ERC-1155
- DeFi, NFTs, DAOs, Web3.js

**Herramientas generadas:**
- Smart Contracts (Tokens, NFTs, DeFi)
- Sistemas de staking y governance
- Integración frontend Web3
- Scripts de deploy

```python
from agents.specialized import BlockchainAgent

agent = BlockchainAgent()
response = await agent.process("crea un contrato ERC-20", {"network": "ethereum"})
```

### 5. VideogamesAgent
**Dominio:** Desarrollo de Videojuegos

**Expertise:**
- Unity (C#), Unreal Engine (C++/Blueprints)
- Godot (GDScript)
- Three.js, Phaser, PixiJS
- Physics, AI, Shaders, Multiplayer

**Herramientas generadas:**
- Controladores de jugador
- Sistemas de juego (GameManager)
- IAs de enemigos
- Efectos visuales y partículas

```python
from agents.specialized import VideogamesAgent

agent = VideogamesAgent()
response = await agent.process("crea un controlador de jugador", {"engine": "unity"})
```

## 🔌 6 Servidores MCP

### 1. GitMCPServer
**Operaciones de Git:**
- `git_status` - Estado del repositorio
- `git_log` - Historial de commits
- `git_branch` - Gestión de ramas
- `git_diff` - Ver diferencias
- `git_search` - Buscar en historial
- `git_blame` - Ver quién modificó cada línea

### 2. DockerMCPServer
**Gestión de Docker:**
- `docker_ps` - Lista contenedores
- `docker_images` - Lista imágenes
- `docker_logs` - Ver logs
- `docker_exec` - Ejecutar comandos
- `docker_stats` - Estadísticas de recursos

### 3. DatabaseMCPServer
**Operaciones de BD:**
- `db_query` - Ejecutar consultas SQL
- `db_tables` - Listar tablas
- `db_schema` - Obtener esquema
- `db_explain` - Plan de ejecución

### 4. SystemMCPServer
**Operaciones del sistema:**
- `sys_info` - Información del sistema
- `sys_processes` - Lista de procesos
- `sys_disk` - Uso de disco
- `sys_network` - Conexiones de red
- `sys_kill` - Terminar proceso

### 5. SearchMCPServer
**Búsquedas avanzadas:**
- `search_files` - Buscar archivos
- `search_content` - Buscar en contenido
- `search_regex` - Búsqueda con regex
- `search_replace` - Buscar y reemplazar

### 6. LinterMCPServer
**Análisis de código:**
- `lint_file` - Analizar archivo
- `lint_project` - Analizar proyecto

## 🏗️ Los 12 Pilares de la Arquitectura

| Pilar | Componente | Descripción |
|-------|-----------|-------------|
| 1 | Escala del Proyecto | ~512K líneas TypeScript, 80+ herramientas |
| 2 | Motor Ink/ UI | Terminal con renderizado estilo React |
| 3 | Permisos Duales | Track 1 (Glob/Regex) + Track 2 (ML) |
| 4 | Streaming Executor | Ejecución concurrente con `isConcurrencySafe` |
| 5 | Feature Gates | KAIROS, COORDINATOR, VOICE, PROACTIVE |
| 6 | Sub-Agentes | In-process, Git Worktree, Remote |
| 7 | Deferred Loading | Resultados en `/tmp/` |
| 8 | Query Engine | 2 capas (Externa + Interna) |
| 9 | Integración MCP | stdio, SSE, WebSocket |
| 10 | Checkpoint/Restore | Persistencia de sesiones |
| 11 | Prompt Caching | Cache de 5 minutos |
| 12 | Spinner Verbs | 36 verbos animados |

## 🚀 Instalación

```bash
# Clonar o navegar al directorio
cd ultracode

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# O instalar manualmente
pip install streamlit langchain langchain-anthropic
```

## 🎮 Uso

### Ejecutar la aplicación Streamlit:
```bash
streamlit run app.py
```

### Ejecutar la demo:
```bash
python demo.py
```

### Usar agentes programáticamente:

```python
import asyncio
from agents.specialized import AgentFactory

async def main():
    # Obtener todos los agentes
    agents = AgentFactory.get_all_agents()
    
    # Usar un agente específico
    frontend = agents["frontend"]
    response = await frontend.process("crea un componente Button")
    print(response.content)
    
    # O usar la fábrica directamente
    backend = AgentFactory.get_agent("backend")
    response = await backend.process("crea un API endpoint")

asyncio.run(main())
```

### Usar MCP Servers:

```python
import asyncio
from mcp.servers import MCPServerRegistry

async def main():
    registry = MCPServerRegistry()
    
    # Listar herramientas
    tools = registry.get_all_tools()
    print(f"Total: {len(tools)} herramientas")
    
    # Llamar herramienta
    result = await registry.call_tool("git", "git_status", {})
    print(result)

asyncio.run(main())
```

## 📋 Comandos de Terminal (en app.py)

- `help` - Mostrar ayuda
- `tools` - Listar herramientas
- `budget` - Ver presupuesto
- `agents` - Ver estado de agentes
- `permissions` - Ver permisos
- `cache` - Ver stats de cache
- `mcp` - Ver servidores MCP
- `checkpoint` - Guardar sesión
- `restore` - Restaurar sesión
- `clear` - Limpiar terminal

## 🔐 Sistema de Permisos

### Track 1 - Reglas Deterministas:
```python
from core.permissions import DualPermissionSystem, PermissionAction

system = DualPermissionSystem()
system.track1.add_rule(
    "*.env",
    PermissionAction.DENY,
    "Archivo de variables de entorno"
)
```

### Track 2 - Clasificador ML:
```python
result = await system.check(
    "rm -rf node_modules",
    context={"active_tools": ["Read"]}
)
```

## 🤝 Sistema de Agentes

```python
from core.agents import SubAgentSystem, AgentMode

system = SubAgentSystem(max_agents=5)

# Crear sub-agente
agent = system.spawn(AgentMode.IN_PROCESS)

# Enviar mensaje
system.send_message(
    from_id="main",
    to_id=agent.id,
    content={"task": "analizar código"}
)

# Broadcast
system.broadcast("main", {"event": "update"})
```

## 📊 Módulos Core

| Módulo | Descripción |
|--------|------------|
| `terminal.py` | Buffer de terminal con streaming |
| `executor.py` | StreamingToolExecutor con concurrencia |
| `permissions.py` | Sistema dual de permisos |
| `features.py` | Feature Gates |
| `agents.py` | Sistema de sub-agentes |
| `query.py` | Query Engine + Budget Tracker |
| `session.py` | Checkpoint/Restore |
| `cache.py` | Prompt Caching |
| `deferred.py` | Deferred Loading |
| `mcp.py` | Cliente MCP |

## 🎨 Spinner Verbs

```
Analyzing, Baking, Crafting, Designing, Engineering,
Fabricating, Generating, Implementing, Indexing, Navigating,
Optimizing, Processing, Rendering, Scaffolding, Searching,
Synthesizing, Transpiling, Validating, Architecting, Building,
Compiling, Computing, Configuring, Constructing, Developing,
Executing, Exploring, Fetching, Formatting, Inspecting,
Loading, Mapping, Orchestrating, Parsing, Querying,
Resolving, Scanning, Streaming, Tracing, Warming up
```

## 📄 Licencia

MIT License
