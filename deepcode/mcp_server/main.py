from __future__ import annotations
import asyncio
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP

server = FastMCP(
    "deepcode-mcp",
    prompt="DeepCode MCP tools expose code synthesis workflows over MCP.",
)


def _safe_import_workflows() -> Dict[str, Any]:
    try:
        from workflows import agent_orchestration_engine as orchestration
        from workflows import code_implementation_workflow as impl
        return {"orchestration": orchestration, "impl": impl}
    except Exception:
        return {}


@server.tool()
async def deepcode_generate_from_paper(source: str, options: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Generate a codebase from a research paper (URL or local file path)."""
    modules = _safe_import_workflows()
    if not modules:
        return {"status": "error", "message": "DeepCode workflows not available"}
    try:
        res = await asyncio.to_thread(modules["orchestration"].process_input, input_source=source, input_type="paper", enable_indexing=True)
        return {"status": "ok", "result": res}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@server.tool()
async def deepcode_text2web(requirements: str, options: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Generate a web application from textual requirements."""
    modules = _safe_import_workflows()
    if not modules:
        return {"status": "error", "message": "DeepCode workflows not available"}
    try:
        res = await asyncio.to_thread(modules["impl"].run_code_implementation_workflow, requirements=requirements, target="web")
        return {"status": "ok", "result": res}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@server.tool()
async def deepcode_text2backend(requirements: str, options: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Generate a backend application from textual requirements."""
    modules = _safe_import_workflows()
    if not modules:
        return {"status": "error", "message": "DeepCode workflows not available"}
    try:
        res = await asyncio.to_thread(modules["impl"].run_code_implementation_workflow, requirements=requirements, target="backend")
        return {"status": "ok", "result": res}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    from mcp.server.sse import SseServerTransport
    import uvicorn
    app = SseServerTransport.as_fastapi(server)

    @app.get("/health")
    async def health():
        return {"status": "ok", "name": "deepcode-mcp"}

    uvicorn.run(app, host="127.0.0.1", port=8765)