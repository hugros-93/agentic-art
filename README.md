# agentic-art

A local, multi-agent painting system where LLM agents collaborate to turn a natural-language request into a structured painting and a rendered image.

The project uses **LangChain**, **LangGraph**, **MCP**, **Ollama**, **Pydantic**, **SVG/CairoSVG**, and **OpenTelemetry** to provide a modular foundation for experimenting with collaborative AI agents that can perform real drawing operations.

---

# Table of content

- [Project Idea](#project-idea)
- [Goals](#goals)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Core Components](#core-components)
- [Agent Responsibilities](#agent-responsibilities)
- [LangChain](#langchain)
- [LangGraph](#langgraph)
- [MCP](#mcp)
- [Pydantic](#pydantic)
- [Rendering](#rendering)
- [Observability](#observability)
- [Request IDs and Traces](#request-ids-and-traces)
- [Configuration](#configuration)
- [Getting Started](#getting-started)
- [Running the Application](#running-the-application)
- [Running the MCP Server Separately](#running-the-mcp-server-separately)
- [Running Tests](#running-tests)
- [Code Quality](#code-quality)
- [Running Jaeger](#running-jaeger)
- [OpenTelemetry Smoke Test](#opentelemetry-smoke-test)
- [Troubleshooting](#troubleshooting)
- [Current Canvas Model](#current-canvas-model)
- [Current Agent Context](#current-agent-context)
- [Design Principles](#design-principles)
- [Development Philosophy](#development-philosophy)
- [License](#license)

--

# Project Idea

The goal is to explore how multiple specialized AI agents can collaborate on a visual creation task.

Instead of asking one LLM:

> "Draw a sunset over mountains."

the system decomposes the task into specialized responsibilities.

```text
User Request
     │
     ▼
┌──────────┐
│ Director │
└────┬─────┘
     │ PaintingPlan
     ▼
┌──────────┐
│  Artist  │
└────┬─────┘
     │ Drawing operations
     ▼
┌──────────┐
│  Render  │
└────┬─────┘
     │ PNG + canvas
     ▼
┌──────────┐
│  Critic  │
└────┬─────┘
     │
     ├── approved ───────► END
     │
     └── not approved ───► Artist
```

The Artist does not directly manipulate image pixels.

Instead, it uses structured drawing tools exposed through an **MCP server**:

- `add_circle`
- `add_rectangle`
- `add_line`
- `remove_shape`
- `get_canvas`

The painting therefore exists as a structured canvas containing geometric shapes.

This makes the painting deterministic, inspectable, reproducible, and easy to validate.

---

# Goals

The project is designed around several goals.

### Local-first

LLMs run locally through [Ollama](https://ollama.com/), avoiding a dependency on hosted model APIs.

### Modular agents

Each agent has a clearly defined responsibility.

### Structured operations

Agents do not directly generate image pixels. They manipulate a typed canvas through tools.

### Explicit orchestration

[LangGraph](https://github.com/langchain-ai/langgraph) controls the workflow and iteration between agents.

### Tool isolation

[MCP](https://modelcontextprotocol.io/) provides the boundary between agents and painting capabilities.

### Strong domain model

[Pydantic](https://docs.pydantic.dev/) provides typed contracts for plans, shapes, canvas state, and agent results.

### Observable execution

[OpenTelemetry](https://opentelemetry.io/) provides traces, LLM telemetry, tool telemetry, and execution timing.

### Incremental architecture

The system starts as a local application and can evolve toward persistence, multiple artists, vision models, and distributed execution without coupling those concerns into the core domain.

---

# Architecture

The current architecture is divided into several layers.

```text
┌──────────────────────────────────────────────────────────────┐
│                         Application                          │
│                  CLI / create_painting()                     │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                         LangGraph                            │
│                                                              │
│       Director → Artist → Render → Critic                    │
│                              ▲           │                    │
│                              └───────────┘                    │
└───────────────┬───────────────────────┬──────────────────────┘
                │                       │
                ▼                       ▼
        ┌──────────────┐        ┌──────────────┐
        │   LangChain  │        │    MCP       │
        │              │        │              │
        │ LLM agents   │        │ Drawing tools│
        │ Middleware   │        │ Canvas API   │
        └──────┬───────┘        └──────┬───────┘
               │                       │
               ▼                       ▼
        ┌──────────────┐        ┌──────────────┐
        │    Ollama    │        │    Domain    │
        │              │        │              │
        │ Local Qwen   │        │ Canvas       │
        │ model        │        │ Shapes       │
        └──────────────┘        │ Painting     │
                                └──────┬───────┘
                                       │
                                       ▼
                                ┌──────────────┐
                                │ SVG / PNG    │
                                │ Rendering    │
                                └──────────────┘

                    ┌──────────────────────┐
                    │   OpenTelemetry     │
                    │                      │
                    │ LLMs / Agents / MCP │
                    │ Rendering / Runs    │
                    └──────────────────────┘
```

---

# Technology Stack

| Technology | Responsibility |
|---|---|
| **Python 3.12** | Main programming language |
| **uv** | Dependency and project management |
| **LangChain** | LLM and agent abstraction |
| **LangGraph** | Agent workflow/orchestration |
| **MCP** | Tool/capability boundary |
| **langchain-mcp-adapters** | MCP ↔ LangChain integration |
| **Ollama** | Local LLM runtime |
| **Qwen 3 0.6B** | Current local model |
| **Pydantic** | Domain and agent contracts |
| **SVG** | Canonical rendering representation |
| **CairoSVG** | SVG → PNG conversion |
| **OpenTelemetry** | Distributed tracing and telemetry |
| **Jaeger** | Local trace visualization |
| **pytest** | Testing |
| **Ruff** | Linting |
| **Pyright** | Static type checking |

---

# How It Works

## 1. User submits a request

For example:

```text
A colorful sunset over mountains with a large yellow sun.
```

The application creates a new `request_id`.

The request is then passed to the LangGraph workflow.

---

## 2. Director creates a plan

The Director is responsible for translating the natural-language request into a structured `PaintingPlan`.

Example:

```json
{
  "title": "Mountain Sunset",
  "description": "A colorful geometric sunset behind mountain silhouettes.",
  "style": "simple geometric",
  "primary_subjects": [
    "sun",
    "mountains",
    "sky"
  ],
  "composition": "Large sun in the upper center with mountains across the lower portion."
}
```

The Director does **not** modify the canvas.

---

## 3. Artist executes the plan

The Artist receives the `PaintingPlan`.

It is implemented using LangChain's agent framework and has access to MCP drawing tools.

For example, it may decide to call:

```text
add_circle(
    shape_id="sun",
    x=700,
    y=180,
    radius=100,
    fill="#FFD700"
)
```

followed by:

```text
add_rectangle(
    shape_id="sky",
    x=0,
    y=0,
    width=1024,
    height=768,
    fill="#F28C28"
)
```

and additional shapes.

The important distinction is that the Artist generates **operations**, not pixels.

---

## 4. MCP executes the drawing operation

The Artist's tool call crosses the MCP boundary.

The MCP server translates the tool call into an operation on the domain model.

The domain layer validates and stores the shape.

The canvas might then contain:

```text
Canvas
├── sky
├── sun
├── mountain-1
├── mountain-2
└── foreground
```

---

## 5. Render

After the Artist finishes, the graph renders the current canvas.

The rendering pipeline is:

```text
Canvas
  │
  ▼
SVG
  │
  ▼
CairoSVG
  │
  ▼
PNG
```

SVG is currently the canonical rendering representation because it maps naturally to the geometric shape model.

Each iteration can produce a PNG checkpoint.

---

## 6. Critic evaluates the painting

The Critic receives:

- the original `PaintingPlan`
- the current canvas representation

It evaluates:

- required subjects
- composition
- style
- completeness

The Critic returns a structured `Critique`:

```json
{
  "approved": false,
  "assessment": "The main composition is present but the foreground is incomplete.",
  "issues": [
    "Foreground lacks sufficient visual separation."
  ],
  "recommendations": [
    "Add a darker foreground layer."
  ]
}
```

---

## 7. LangGraph decides what happens next

If the painting is approved:

```text
Critic → END
```

Otherwise:

```text
Critic
   │
   ▼
Artist
   │
   ▼
Render
   │
   ▼
Critic
```

The graph stops when either:

- the Critic approves the painting, or
- `max_iterations` is reached.

---

# Project Structure

```text
painting-agents/
├── pyproject.toml
├── uv.lock
├── README.md
├── .env.example
├── .gitignore
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── src/
│   └── painting_agents/
│       ├── __init__.py
│       ├── config.py
│       │
│       ├── domain/
│       │   ├── canvas.py
│       │   ├── painting.py
│       │   ├── shapes.py
│       │   ├── commands.py
│       │   ├── events.py
│       │   ├── session.py
│       │   └── factory.py
│       │
│       ├── agents/
│       │   ├── base.py
│       │   ├── contracts.py
│       │   ├── director.py
│       │   ├── artist.py
│       │   └── critic.py
│       │
│       ├── graph/
│       │   ├── state.py
│       │   ├── nodes.py
│       │   └── workflow.py
│       │
│       ├── mcp/
│       │   ├── server.py
│       │   ├── client.py
│       │   ├── results.py
│       │   └── tools/
│       │       └── canvas.py
│       │
│       ├── models/
│       │   └── ollama.py
│       │
│       ├── rendering/
│       │   ├── svg.py
│       │   └── png.py
│       │
│       ├── observability/
│       │   ├── tracing.py
│       │   ├── metrics.py
│       │   ├── llm.py
│       │   └── mcp.py
│       │
│       └── storage/
│
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   ├── agents/
│   │   ├── graph/
│   │   └── mcp/
│   │
│   └── integration/
│       ├── test_mcp.py
│       ├── test_mcp_client.py
│       ├── test_artist_integration.py
│       ├── test_director_integration.py
│       ├── test_ollama_integration.py
│       └── test_structured_output_integration.py
│
└── scripts/
    ├── run_mcp_server.py
    └── run_painting.py
```

---

# Core Components

## Domain

The domain layer contains the actual painting model.

Important objects include:

### `Canvas`

Represents the drawing surface.

```python
Canvas(
    width=1024,
    height=768,
)
```

### `Shape`

The current supported shapes are:

- Circle
- Rectangle
- Line

### `Painting`

Contains the canvas and painting metadata.

### `PaintingSession`

Represents the lifecycle of a painting and records operations performed during the session.

The domain layer deliberately has no dependency on LangChain, LangGraph, Ollama, or MCP.

This keeps the core painting model independent of the AI infrastructure.

---

# Agent Responsibilities

## Director

Input:

```text
Natural-language user request
```

Output:

```text
PaintingPlan
```

Responsibilities:

- understand the request
- identify subjects
- define composition
- define style
- provide a concrete plan

The Director does not draw.

---

## Artist

Input:

```text
PaintingPlan
+
optional previous Critique
```

Output:

```text
Canvas operations
```

Responsibilities:

- translate the plan into drawing operations
- call MCP tools
- create and modify shapes
- respond to Critic feedback

The Artist is currently the only drawing agent.

---

## Critic

Input:

```text
PaintingPlan
+
current Canvas
```

Output:

```text
Critique
```

Responsibilities:

- evaluate the current painting
- identify missing elements
- provide concrete recommendations
- approve or reject the current result

The Critic does not modify the canvas.

---

# LangChain

LangChain provides the abstraction layer between the agents and the local LLM.

The project uses:

- `ChatOllama`
- structured model output
- LangChain agents
- LangChain tools
- agent middleware

The local model is configured through:

```python
ChatOllama(
    model="qwen3:0.6b",
    base_url="http://localhost:11434",
    temperature=0.2,
)
```

The model implementation is isolated in:

```text
src/painting_agents/models/ollama.py
```

This allows the rest of the application to remain independent of the specific model runtime.

---

# LangGraph

LangGraph owns the application workflow.

The current graph is:

```text
START
  │
  ▼
Director
  │
  ▼
Artist
  │
  ▼
Render
  │
  ▼
Critic
  │
  ├── approved ──► END
  │
  ├── max iterations ──► END
  │
  └── continue ──► Artist
```

LangGraph is used for orchestration rather than embedding workflow logic inside individual agents.

This makes the iteration loop explicit and testable.

---

# MCP

The Model Context Protocol provides a standardized boundary between the Artist and painting capabilities.

Current MCP tools:

```text
add_circle
add_rectangle
add_line
remove_shape
get_canvas
```

Conceptually:

```text
Artist
  │
  │ MCP tool call
  ▼
MCP Client
  │
  ▼
MCP Server
  │
  ▼
CanvasTools
  │
  ▼
PaintingSession
  │
  ▼
Canvas
```

The MCP layer is intentionally thin.

Business rules belong in the domain/application layer rather than inside MCP transport code.

---

# Pydantic

Pydantic is used for explicit contracts between components.

Examples include:

```text
PaintingPlan
ArtistResult
Critique
Canvas
Circle
Rectangle
Line
Painting
PaintingSession
```

This is particularly important for LLM output.

Instead of relying on free-form text such as:

```text
"The painting should have a big yellow sun..."
```

the Director produces a typed `PaintingPlan`.

This makes agent-to-agent communication predictable and testable.

---

# Rendering

The project uses SVG as the intermediate representation.

For example:

```xml
<svg width="1024" height="768">
    <circle
        id="sun"
        cx="700"
        cy="180"
        r="100"
        fill="#FFD700"
    />
</svg>
```

SVG is then converted to PNG using CairoSVG.

This provides a clean separation:

```text
Domain Canvas
      ↓
SVG Renderer
      ↓
PNG Renderer
```

The same canvas can therefore be rendered into different formats later.

---

# Observability

OpenTelemetry is used as the observability foundation.

The application creates a root painting span:

```text
painting.run
```

and agent operations create child spans:

```text
painting.run
├── agent.director
│   └── llm.call
│
├── agent.artist
│   ├── llm.call
│   ├── agent.tool.add_circle
│   └── agent.tool.add_rectangle
│
├── rendering.painting
│
└── agent.critic
    └── llm.call
```

The exact parent/child relationship of server-side MCP spans may differ because the MCP server runs as a separate process.

---

## LLM Telemetry

LLM spans record useful information such as:

- model
- provider
- input token count
- output token count
- total token count
- finish reason
- model execution duration
- model loading duration
- prompt evaluation duration
- generation duration

Prompts and responses are recorded as span events:

```text
llm.prompt
llm.response
```

rather than as large span attributes.

The project uses LangChain's `usage_metadata` for token counts when available.

---

## Agent Middleware

The Artist uses LangChain agent middleware to instrument model and tool calls.

This provides visibility into:

```text
Agent
 ├── model call
 ├── tool call
 ├── model call
 ├── tool call
 └── final response
```

This is preferable to relying only on the high-level Agent span because it exposes the individual actions taken by the agent.

---

# Request IDs and Traces

The application distinguishes between several identifiers.

### `request_id`

A UUID representing a user painting request.

### `session_id`

The identifier of the `PaintingSession`.

### `trace_id`

Generated automatically by OpenTelemetry for an execution trace.

### `span_id`

Identifies an individual operation inside a trace.

Conceptually:

```text
User request
     │
     ├── request_id
     │
     ▼
PaintingSession
     │
     ├── session_id
     │
     ▼
painting.run
     │
     └── trace_id
          │
          ├── Director
          ├── Artist
          ├── Render
          └── Critic
```

---

# Configuration

Current configuration is defined in:

```text
src/painting_agents/config.py
```

Default values include:

```text
Ollama:
  http://localhost:11434

Model:
  qwen3:0.6b

Temperature:
  0.2

OpenTelemetry:
  http://localhost:4317

Service name:
  painting-agents
```

The configuration is currently represented by a Pydantic `Settings` model.

> Note: environment-variable loading is not yet wired through `pydantic-settings`. The current configuration therefore uses the values defined by the application defaults unless configuration loading is explicitly added.

---

# Getting Started

## Requirements

You need:

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/)
- Docker Desktop if you want to run Jaeger locally

---

## Clone the repository

```bash
git clone <repository-url>
cd painting-agents
```

---

## Install dependencies

```bash
uv sync
```

---

## Start Ollama

Make sure Ollama is running.

Then download the configured model:

```bash
ollama pull qwen3:0.6b
```

Verify that the model is available:

```bash
ollama list
```

You can also test the model directly:

```bash
ollama run qwen3:0.6b
```

---

# Running the Application

The main entry point is:

```text
scripts/run_painting.py
```

Example:

```bash
uv run python scripts/run_painting.py \
  "A colorful sunset over mountains" \
  --output output/sunset.png \
  --max-iterations 2
```

On Windows PowerShell:

```powershell
uv run python scripts/run_painting.py `
  "A colorful sunset over mountains" `
  --output output/sunset.png `
  --max-iterations 2
```

The final image will be written to:

```text
output/sunset.png
```

Intermediate rendering checkpoints are stored in the corresponding output directory.

For example:

```text
output/
├── sunset.png
└── sunset/
    ├── iteration-001.png
    └── iteration-002.png
```

---

# Running the MCP Server Separately

The MCP server can be started with:

```bash
uv run python scripts/run_mcp_server.py
```

Normally the application starts the MCP server through the MCP stdio transport automatically, so you do not need to run it manually for a normal painting request.

---

# Running Tests

Run the complete test suite:

```bash
uv run pytest
```

Run only unit tests:

```bash
uv run pytest tests/unit
```

Run integration tests:

```bash
uv run pytest tests/integration
```

Run a specific test:

```bash
uv run pytest tests/unit/domain/test_canvas.py
```

---

# Code Quality

## Ruff

Check the code:

```bash
uv run ruff check .
```

Automatically fix supported issues:

```bash
uv run ruff check . --fix
```

Format the project:

```bash
uv run ruff format .
```

---

## Pyright

Run static type checking:

```bash
uv run pyright
```

---

# Running Jaeger

Jaeger is used as the local OpenTelemetry trace backend/UI.

The project includes Docker configuration for Jaeger.

Start it with:

```bash
docker compose up -d jaeger
```

Check that it is running:

```bash
docker ps
```

The Jaeger UI is available at:

```text
http://localhost:16686
```

The application sends OTLP traces to:

```text
localhost:4317
```

---

# OpenTelemetry Smoke Test

Before debugging application telemetry, it is useful to verify the Jaeger/OTLP pipeline independently.

Run:

```bash
uv run python scripts/otel_smoke.py
```

The smoke test creates a simple span and exports it through OTLP.

Then open the Jaeger UI and look for the service:

```text
painting-agents-smoke
```

If the smoke trace is not visible, the problem is in the OpenTelemetry/Jaeger infrastructure rather than the painting application.

---

# Troubleshooting

## Jaeger shows no traces

First verify Docker:

```bash
docker info
docker ps
```

Verify that the OTLP gRPC port is reachable.

PowerShell:

```powershell
Test-NetConnection localhost -Port 4317
```

If Docker Desktop is being used on Windows, also check:

```powershell
docker context ls
```

The Docker Linux engine must be running.

---

## Application runs but telemetry does not appear

The application must configure OpenTelemetry **before creating the root span**:

```python
configure_tracing()

with tracer.start_as_current_span("painting.run"):
    ...
```

Before the application exits, spans should be flushed:

```python
flush_tracing()
```

This is particularly important for the CLI because OpenTelemetry's batch processor may otherwise still have spans waiting in memory when the process terminates.

---

# Current Canvas Model

The current canvas supports three primitives:

```text
Circle
Rectangle
Line
```

Each shape has an identifier.

For example:

```json
{
  "id": "sun",
  "type": "circle",
  "center": {
    "x": 700,
    "y": 180
  },
  "radius": 100,
  "fill": {
    "value": "#FFD700"
  }
}
```

Shapes are stored in their creation order.

The domain prevents duplicate shape IDs.

---

# Current Agent Context

The current V0.1 Artist receives:

```text
PaintingPlan
+
previous Critique (when iterating)
```

It has access to the MCP tools and can query the canvas.

The Critic receives:

```text
PaintingPlan
+
structured Canvas
```

The Critic does **not** currently receive the rendered PNG.

Likewise, the Artist is not currently a vision model and does not directly inspect the rendered PNG.

This means the current system is fundamentally **structured-data driven**, rather than vision-driven.

---

# Design Principles

## Separate domain from AI infrastructure

The canvas should not know about LangChain or Ollama.

```text
Domain
  ↑
Application
  ↑
Agents / Graph / MCP
  ↑
Infrastructure
```

This makes the core model easier to test and evolve.

---

## Agents produce decisions, not infrastructure

Agents decide:

```text
What should be drawn?
```

Tools decide:

```text
How is it actually changed?
```

The domain decides:

```text
Is that operation valid?
```

---

## LangGraph owns workflow

Agents should not manually orchestrate other agents.

The graph defines:

```text
who runs
when they run
what state they receive
where execution goes next
when execution stops
```

---

## MCP owns capabilities

MCP exposes capabilities such as:

```text
add_circle
add_rectangle
add_line
remove_shape
get_canvas
```

The Artist does not need to know how those operations are implemented.

---

## Pydantic owns contracts

Agent communication should use explicit models rather than loosely structured dictionaries wherever practical.

This provides:

- validation
- type safety
- predictable LLM output
- easier testing
- easier evolution

---

## OpenTelemetry owns observability

Observability should remain independent of the orchestration framework.

The goal is to be able to answer questions such as:

```text
What did the user request?

Which plan did the Director produce?

Which model was used?

What did the Artist ask the model?

Which tools did the Artist call?

How many tokens were consumed?

How long did each model call take?

What did the Critic decide?

How many iterations were required?

Where did an error occur?
```

without putting observability logic into the domain itself.

---

# Development Philosophy

The project intentionally avoids introducing infrastructure before it is needed.

The current development path is:

```text
Domain
  ↓
Rendering
  ↓
MCP
  ↓
LLM
  ↓
Agents
  ↓
LangGraph
  ↓
Observability
  ↓
CLI
  ↓
Persistence / Vision / Multi-Agent Scaling
```

This keeps the V0.1 system understandable while leaving clear extension points for future versions.

---

# License

```text
MIT License
```