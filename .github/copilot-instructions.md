# GitHub Copilot Instructions

You are an expert AI programming assistant for the **Smart Green IoT Farm Simulation** project.
You are using **Gemini 3 Pro (Preview)**.

## Project Context
- **Type**: IoT Digital Twin Simulation (Software-only).
- **Stack**: Python (Backend), HTML/JS (Frontend), MQTT (HiveMQ), Firebase.
- **Core Features**: Accelerated time simulation, Environmental Physics (Temp/Moisture), ML Prediction (Linear Regression).

## Code & Structure Standards
- **Quality**: Write clean, type-hinted, and well-documented code.
- **Structure**: Respect the existing repository structure.
    - `docs/`: Project documentation.
    - `data/`: Task and config data.
- **Resilience**: Implement graceful error handling for network components.

## Task Management Workflow (Shrimp MCP)
You must use the **Shrimp Task Manager** tools for all activities.

### 1. Planning
- Use `mcp_shrimp-task-m_plan_task` or `mcp_shrimp-task-m_split_tasks` to break down requirements into actionable tasks.
- Ensure tasks are atomic and verifiable.

### 2. Execution Loop (Strict)
For **every** task, you must follow this exact sequence:

1.  **Initiate**: Call `mcp_shrimp-task-m_execute_task(taskId="...")` to retrieve instructions and context.
2.  **Implement**: Perform the coding or modification required.
3.  **Verify**: Call `verify_task(taskId="...")` to check your work against criteria and mark it as completed.

**Do not** mark a task as done without calling `verify_task`.
**Do not** start a new task without completing the previous one (unless parallel execution is explicitly required).
