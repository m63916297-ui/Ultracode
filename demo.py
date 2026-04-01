"""
UltraCode Demo Script
====================
Demostración del sistema de agentes y MCP servers.
"""

import asyncio
from agents.specialized import (
    AgentFactory,
    FrontendAgent,
    BackendAgent,
    DevOpsAgent,
    BlockchainAgent,
    VideogamesAgent,
)
from mcp.servers import MCPServerRegistry


async def demo_agents():
    """Demuestra los agentes especializados"""
    print("=" * 60)
    print("UltraCode Agent System Demo")
    print("=" * 60)

    # Crear agentes usando la fábrica
    agents = AgentFactory.get_all_agents()

    print("\n📋 Agentes disponibles:")
    for name, agent in agents.items():
        print(f"  - {name}: {agent.description}")
        print(f"    Experto en: {', '.join(agent.expertise[:3])}...")

    # Demostrar FrontendAgent
    print("\n" + "=" * 60)
    print("🎨 FrontendAgent Demo")
    print("=" * 60)

    frontend = agents["frontend"]
    response = await frontend.process("crea un componente Button con variants")

    print(f"\nAgente: {response.agent}")
    print(f"Herramientas usadas: {', '.join(response.tools_used)}")
    print(f"Tareas completadas: {len(response.tasks)}")
    print("\n📄 Código generado (primeros 500 chars):")
    print(response.content[:500] + "...")

    # Demostrar BackendAgent
    print("\n" + "=" * 60)
    print("⚙️ BackendAgent Demo")
    print("=" * 60)

    backend = agents["backend"]
    response = await backend.process("crea un API endpoint REST con FastAPI")

    print(f"\nAgente: {response.agent}")
    print(f"Framework: {response.metadata.get('framework')}")
    print("\n📄 Código generado (primeros 500 chars):")
    print(response.content[:500] + "...")

    # Demostrar DevOpsAgent
    print("\n" + "=" * 60)
    print("🚀 DevOpsAgent Demo")
    print("=" * 60)

    devops = agents["devops"]
    response = await devops.process("crea configuración Docker")

    print(f"\nAgente: {response.agent}")
    print("\n📄 Código generado (primeros 500 chars):")
    print(response.content[:500] + "...")

    # Demostrar BlockchainAgent
    print("\n" + "=" * 60)
    print("⛓️ BlockchainAgent Demo")
    print("=" * 60)

    blockchain = agents["blockchain"]
    response = await blockchain.process("crea un contrato ERC-20 token")

    print(f"\nAgente: {response.agent}")
    print("\n📄 Código generado (primeros 500 chars):")
    print(response.content[:500] + "...")

    # Demostrar VideogamesAgent
    print("\n" + "=" * 60)
    print("🎮 VideogamesAgent Demo")
    print("=" * 60)

    videogames = agents["videogames"]
    response = await videogames.process(
        "crea un controlador de jugador", {"engine": "unity"}
    )

    print(f"\nAgente: {response.agent}")
    print(f"Motor: {response.metadata.get('engine')}")
    print("\n📄 Código generado (primeros 500 chars):")
    print(response.content[:500] + "...")


async def demo_mcp_servers():
    """Demuestra los servidores MCP"""
    print("\n" + "=" * 60)
    print("🔌 MCP Servers Demo")
    print("=" * 60)

    registry = MCPServerRegistry()

    # Mostrar herramientas disponibles
    all_tools = registry.get_all_tools()
    print(f"\n📦 Total de herramientas disponibles: {len(all_tools)}")

    # Agrupar por servidor
    by_server = {}
    for tool in all_tools:
        server = tool["server"]
        if server not in by_server:
            by_server[server] = []
        by_server[server].append(tool["name"])

    for server, tools in by_server.items():
        print(f"\n🖥️ {server.upper()} Server:")
        for tool in tools[:5]:
            print(f"   - {tool}")
        if len(tools) > 5:
            print(f"   ... y {len(tools) - 5} más")

    # Demostrar Git Server
    print("\n" + "-" * 40)
    print("📂 Git MCP Server Demo")
    print("-" * 40)

    git_server = registry.get_server("git")
    result = await git_server.call_tool("git_status", {})

    print("\nEstado del repositorio Git:")
    if "error" not in result:
        print(f"  Branch: {result.get('branch', 'N/A')}")
        print(
            f"  Archivos modificados: {len(result.get('files', {}).get('modified', []))}"
        )
        print(f"  Archivos staged: {len(result.get('files', {}).get('staged', []))}")
    else:
        print(f"  Error: {result.get('error')}")

    # Demostrar System Server
    print("\n" + "-" * 40)
    print("💻 System MCP Server Demo")
    print("-" * 40)

    system_server = registry.get_server("system")
    result = await system_server.call_tool("sys_info", {})

    print("\nInformación del sistema:")
    if "error" not in result:
        print(f"  SO: {result.get('os', 'N/A')}")
        print(f"  Versión: {result.get('os_version', 'N/A')}")
        print(f"  Arquitectura: {result.get('architecture', 'N/A')}")
    else:
        print(f"  Error: {result.get('error')}")


async def demo_query_engine():
    """Demuestra el Query Engine"""
    print("\n" + "=" * 60)
    print("🔍 Query Engine Demo")
    print("=" * 60)

    from core.query import QueryEngine, BudgetTracker
    from core.executor import StreamingToolExecutor
    from core.permissions import DualPermissionSystem

    # Crear componentes
    permissions = DualPermissionSystem()
    executor = StreamingToolExecutor(permissions)
    tracker = BudgetTracker(limit=10.00)
    engine = QueryEngine(executor, permissions, tracker)

    print("\n📊 Componentes creados:")
    print(f"  - Query Engine: ✓")
    print(f"  - Streaming Tool Executor: ✓")
    print(f"  - Dual Permission System: ✓")
    print(f"  - Budget Tracker: ${tracker.limit}")

    # Ver herramientas disponibles
    tools = executor.get_tools()
    print(f"\n🔧 Herramientas disponibles: {len(tools)}")
    for tool in tools[:5]:
        safe = "✓" if tool.is_concurrency_safe else "○"
        print(f"  {safe} {tool.name}")

    # Verificar permisos
    print("\n🛡️ Verificación de permisos:")
    result = await permissions.check("rm -rf /")
    print(f"  'rm -rf /' -> {'❌ DENEGADO' if not result.allowed else '✓ PERMITIDO'}")
    print(f"  Razón: {result.reason}")
    print(f"  Track: {result.track}")


async def main():
    """Función principal de demostración"""
    print("\n" + "🎯" * 30)
    print("\n   UltraCode - Sistema de Programación IA")
    print("   Basado en la Arquitectura de Claude Code")
    print("\n" + "🎯" * 30)

    try:
        # Ejecutar demos
        await demo_agents()
        await demo_mcp_servers()
        await demo_query_engine()

        print("\n" + "=" * 60)
        print("✅ Demo completada exitosamente!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error en la demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
