# Google ADK Code Examples

This document contains various examples of how to use the Google Agent Development Kit (ADK).

---

### Example 1: Creating a Workflow Agent

Workflows are used to orchestrate multiple agents in a sequence. You define nodes (agents) and edges (transitions). This is ideal for multi-step processes.

```python
from google.adk import agents, llms, workflow

# Define agents for each step
step1_agent = agents.Agent(instructions="Get the user's city.")
step2_agent = agents.Agent(instructions="Find a popular landmark in that city.")

# Define the workflow
root_agent = workflow.Workflow(
    nodes={
        "get_city": step1_agent,
        "find_landmark": step2_agent,
    },
    edges={
        ("get_city", "find_landmark"): workflow.ALWAYS,
    },
    entrypoint="get_city"
)
```

### Example 2: Agent with Memory

To create a stateful agent that remembers previous turns in a conversation, add an instance of memory.InMemoryMemory to its constructor.

```python
from google.adk import agents, llms, memory

# This agent will remember things you tell it across multiple messages.
root_agent = agents.Agent(
    llm=llms.Llm(model="gemini-2.0-flash"),
    memory=memory.InMemoryMemory(),
    instructions="You are a helpful assistant. Remember the user's name if they tell you."
)
```

### Example 3: Agent-to-Agent (A2A) Communication

You can create a hierarchy of agents by passing one agent as a tool to another. This is useful for creating a "manager" agent that delegates specialized tasks.

```python
from google.adk import agents, llms

# Define the specialized "worker" agent
math_expert_agent = agents.Agent(
    llm=llms.Llm(model="gemini-2.0-flash"),
    instructions="You are a math expert. You only solve math problems.",
    name="MathExpert",
    description="A tool that can solve complex mathematical equations."
)

# Define the "manager" agent that uses the worker
root_agent = agents.Agent(
    llm=llms.Llm(model="gemini-2.0-flash"),
    instructions="You are a general assistant. If you get a math question, delegate it to the MathExpert tool.",
    tools=[math_expert_agent]
)
```