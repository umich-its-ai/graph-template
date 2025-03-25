# Go Blue Graph Template

This repository is maintained by the GenAI team at ITS (Information and Technology Services), University of Michigan. It provides a streamlined version of the core AI orchestration layer used in platforms like *MiMaizey* and *GoBlue AI*.

The goal of this repository is to enable University of Michigan developers to build and integrate compatible tools with the AI system in a modular and maintainable manner which can then be used in the actual production environment.

## 🧠 Overview

This orchestration layer manages interactions between AI models and university-specific tools and services. While much of the internal logic is abstracted, this template offers the necessary structure to:

- Develop custom tools.
- Test them via a basic frontend interface.
- Integrate seamlessly with the core AI backend used in production environments.

## 🚀 Getting Started

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)

    Follow the official installation guide to install **uv**, a fast and modern Python package manager.

    **On macOS and Linux**
    `curl -LsSf https://astral.sh/uv/install.sh | sh`

    **On Windows**
    `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

    Alternatively, install via `pipx`:

    `pipx install uv`

    Other alternative methods, such as HomeBrew, can be found in the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/).

2. Create a Virtual Environment

    `uv venv`

    This command creates a `.venv` directory with an isolated Python environment.

3. Activate the Virtual Environment

    **On macOS and Linux**
    `source .venv/bin/activate`

    **On Windows**
    `.venv\Scripts\activate`

4. Sync Dependencies

    Run the following to install all required dependencies as specified in the `pyproject.toml` and `uv.lock` files:

    `uv sync`

    **Note**: Ensure that both `pyproject.toml` and `uv.lock` are present in the repository. If `uv.lock` is missing, `uv` will generate one based on `pyproject.toml`.

5. Run the Frontend [Streamlit](https://streamlit.io)

    Launch the demo client:

    `streamlit run src/client/streamlit_app.py`

## 🛠️ Development

To add new dependencies:

`uv add <package-name>`

To remove existing dependencies:

`uv remove <package-name>`

Important: Avoid using `uv pip install` for managing packages, as it does not update the lock file. Always use uv add and uv remove to ensure that `uv.lock` remains accurate and consistent.

After adding or removing packages, synchronize the environment:

`uv sync`

## 📁 Project Structure

```plaintext
graph-template
├─ .python-version
├─ README.md
├─ pyproject.toml
├─ src
│  ├─ __init__.py
│  ├─ client
│  │  ├─ __init__.py
│  │  └─ streamlit_app.py
│  ├─ graph
│  │  ├─ __init__.py
│  │  ├─ agent_graph.py
│  │  ├─ create_graph.py
│  │  ├─ prompts.py
│  │  ├─ states.py
│  │  └─ utils.py
│  └─ tools
│     ├─ __init__.py
│     ├─ base.py
│     ├─ schemas.py
│     └─ tool_directory
│        ├─ __init__.py
│        └─ math_tool.py
└─ uv.lock
```

🧩 We recommend only modifying src/tools/tool_directory/. Altering other parts of the orchestration layer may lead to compatibility issues with production services.

## 🙌 Contributing

University of Michigan developers interested in contributing should contact the GenAI team for access and design guidelines.

## 📬 Support

For questions or assistance with integrating your tool with GoBlue or MiMaizey, please reach out to the GenAI team at ITS.
