# How to Access and Use the Chudnelius CLI Agent from WSL

This guide will walk you through accessing your WSL-connected Linux machine from a Windows terminal and running the `agent_cli.py` script.

## Prerequisites

*   **Windows Subsystem for Linux (WSL)**: Ensure you have WSL installed and a Linux distribution (e.g., Ubuntu) set up.
*   **Windows Terminal**: Recommended for a better experience with WSL.
*   **uv**: The `uv` package manager should be installed in your WSL environment, as `agent_cli.py` uses `uv run main.py` internally.

## Steps to Access and Run the Agent

1.  **Open a WSL Terminal**:
    *   Open the Windows Terminal.
    *   You can directly open a new tab or window for your WSL distribution (e.g., "Ubuntu") from the dropdown menu.
    *   Alternatively, you can type `wsl` in a PowerShell or Command Prompt window to enter your default WSL distribution.

2.  **Navigate to the Agent's Directory**:
    Once inside your WSL terminal, you need to navigate to the directory where the `agent_cli.py` script is located. Assuming the agent's files are in a directory like `/path/to/chudnelius2.0/agent_sandbox` (replace with your actual path), you would use the `cd` command:

    ```bash
    cd /path/to/chudnelius2.0/agent_sandbox
    ```
    *(Note: The exact path will depend on where you have cloned or placed the agent's repository within your WSL filesystem.)*

3.  **Run the `agent_cli.py` Script**:

    The `agent_cli.py` script provides a splash screen and allows you to interact with the agent.

    *   **Interactive Mode (without a direct question)**:
        To run the agent and be prompted for a question, simply execute the script:

        ```bash
        python agent_cli.py
        ```
        After the splash screen, you will see a prompt: `What can I help you with today? `

    *   **With a Direct Question**:
        You can also pass your question directly as an argument to the script:

        ```bash
        python agent_cli.py "Your question goes here, e.g., What is the capital of France?"
        ```
        *(Remember to enclose your question in double quotes if it contains spaces.)*

    The `agent_cli.py` script will display a welcome splash screen and then execute the main agent logic using `uv run main.py` with your provided question.

---

By following these steps, you should be able to successfully access your WSL environment and interact with the Chudnelius CLI Agent.