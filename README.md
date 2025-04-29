# clickup-mcp-server: A ClickUp MCP Server

## Overview

A Model Context Protocol server for ClickUp API interaction and automation. This server provides tools for AI systems to read, create, and update tasks, lists, and spaces in ClickUp.

This MCP server enables AI tools like Claude to interact with your ClickUp workspace, helping automate task management, project planning, and other workflows.

## Tools

The server provides the following tools for interacting with ClickUp:

### Workspace/Team Tools

1. `get_workspaces`
   - Gets all workspaces/teams
   - Input: None
   - Returns: List of workspaces with IDs and names

### Space Tools

2. `get_spaces`
   - Gets all spaces in a workspace
   - Input:
     - `workspace_id` (string): ID of the workspace/team
   - Returns: List of spaces with IDs and names

3. `create_space`
   - Creates a new space in a workspace
   - Inputs:
     - `workspace_id` (string): ID of the workspace/team
     - `name` (string): Name of the new space
   - Returns: Details of the created space

### List/Board Tools

4. `get_lists`
   - Gets all lists/boards in a space
   - Input:
     - `space_id` (string): ID of the space
   - Returns: List of lists/boards with IDs and names

5. `create_list`
   - Creates a new list/board in a space
   - Inputs:
     - `space_id` (string): ID of the space
     - `name` (string): Name of the new list/board
   - Returns: Details of the created list/board

### Task Tools

6. `get_tasks`
   - Gets all tasks in a list/board
   - Input:
     - `list_id` (string): ID of the list/board
   - Returns: List of tasks with IDs, names, and other details

7. `get_tasks_by_status`
   - Gets tasks with a specific status in a list/board
   - Inputs:
     - `list_id` (string): ID of the list/board
     - `status` (string): Status to filter tasks by
   - Returns: List of tasks with the specified status

8. `create_task`
   - Creates a new task in a list/board
   - Inputs:
     - `list_id` (string): ID of the list/board
     - `name` (string): Name of the task
     - `description` (string, optional): Task description
     - `priority` (number, optional): Task priority (1-4)
     - `due_date` (number, optional): Task due date in milliseconds
     - `tags` (string[], optional): List of tag names to add to task
   - Returns: Details of the created task

9. `get_task`
   - Gets details of a specific task
   - Input:
     - `task_id` (string): ID of the task
   - Returns: Full details of the task including description, status, etc.

10. `update_task`
    - Updates a task's properties
    - Inputs:
      - `task_id` (string): ID of the task
      - `name` (string, optional): New task name
      - `description` (string, optional): New task description
      - `priority` (number, optional): New task priority (1-4)
      - `due_date` (number, optional): New due date in milliseconds
      - `tags` (string[], optional): New list of tag names
    - Returns: Updated task details

11. `update_task_status`
    - Updates a task's status
    - Inputs:
      - `task_id` (string): ID of the task
      - `status` (string): New status for the task
    - Returns: Updated task details

12. `assign_task`
    - Assigns users to a task
    - Inputs:
      - `task_id` (string): ID of the task
      - `assignee_ids` (string[]): List of user IDs to assign to the task
    - Returns: Confirmation of assignment

13. `get_task_subtasks`
    - Gets subtasks for a task
    - Input:
      - `task_id` (string): ID of the task
    - Returns: List of subtasks with their details

## Installation

### Prerequisites

- Python 3.10 or higher
- A ClickUp account with an API key

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *clickup-mcp-server*.

```
uv --directory "/path/to/clickup-mcp-server" run clickup-mcp-server --api-key YOUR_API_KEY
```

Or use a .env file (see Configuration section).

### Using PIP

Alternatively, you can install `clickup-mcp-server` via pip:

```
pip install clickup-mcp-server
```

After installation, you can run it as a script using:

```
python -m clickup_mcp_server --api-key YOUR_API_KEY
```

## Configuration

### API Key

You need a ClickUp API key to use this server. You can get one from [ClickUp API Settings](https://app.clickup.com/settings/apps).

The API key can be provided in two ways:

1. Command-line argument: `--api-key YOUR_API_KEY`
2. Environment variable in a `.env` file:
   ```
   CLICKUP_API_KEY=your_api_key_here
   ```

### Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

<details>
<summary>Using uvx</summary>

```json
"mcpServers": {
  "clickup": {
    "command": "uvx",
    "args": ["clickup-mcp-server", "--api-key", "YOUR_API_KEY"]
  }
}
```
</details>

<details>
<summary>Using docker</summary>

```json
"mcpServers": {
  "clickup": {
    "command": "docker",
    "args": ["run", "--rm", "-i", "-e", "CLICKUP_API_KEY=YOUR_API_KEY", "mcp/clickup"]
  }
}
```
</details>

<details>
<summary>Using pip installation</summary>

```json
"mcpServers": {
  "clickup": {
    "command": "python",
    "args": ["-m", "clickup_mcp_server", "--api-key", "YOUR_API_KEY"]
  }
}
```
</details>

### Usage with VS Code

For manual installation, add the following JSON block to your User Settings (JSON) file in VS Code. You can do this by pressing `Ctrl + Shift + P` and typing `Preferences: Open Settings (JSON)`.

Optionally, you can add it to a file called `.vscode/mcp.json` in your workspace. This will allow you to share the configuration with others. 

> Note that the `mcp` key is not needed in the `.vscode/mcp.json` file.

```json
{
  "mcp": {
    "servers": {
      "clickup": {
        "command": "uvx",
        "args": ["clickup-mcp-server"],
        "env": {
          "CLICKUP_API_KEY": "YOUR_API_KEY"
        }
      }
    }
  }
}
```

For Docker installation:

```json
{
  "mcp": {
    "servers": {
      "clickup": {
        "command": "docker",
        "args": [
          "run",
          "--rm",
          "-i",
          "-e", "CLICKUP_API_KEY=YOUR_API_KEY",
          "mcp/clickup"
        ]
      }
    }
  }
}
```

### Usage with [Zed](https://github.com/zed-industries/zed)

Add to your Zed settings.json:

<details>
<summary>Using uvx</summary>

```json
"context_servers": [
  "mcp-server-clickup": {
    "command": {
      "path": "uvx",
      "args": ["clickup-mcp-server"]
    },
    "env": {
      "CLICKUP_API_KEY": "YOUR_API_KEY"
    }
  }
],
```
</details>

<details>
<summary>Using pip installation</summary>

```json
"context_servers": {
  "mcp-server-clickup": {
    "command": {
      "path": "python",
      "args": ["-m", "clickup_mcp_server"]
    },
    "env": {
      "CLICKUP_API_KEY": "YOUR_API_KEY"
    }
  }
},
```
</details>

## Example Usage Scenarios

### Task Management with Claude

Claude can help you manage your ClickUp tasks:

1. **Creating a Task Plan**:
   Ask Claude to create a plan based on a specific task in ClickUp. Claude will:
   - Find the task by name or ID
   - Analyze its description and subtasks
   - Generate a structured plan for completing the task

2. **Task Automation**:
   For a task containing code-related instructions, Claude can:
   - Get the task details from ClickUp
   - Update the task status to "In Progress"
   - Implement the code according to the task requirements
   - Check off subtasks as they're completed
   - Update the status to "Ready for Review" when finished

3. **Task Reporting**:
   Ask Claude to generate summaries of tasks with specific statuses:
   - Get all tasks marked "In Progress"
   - Compile a status report with completion estimates
   - Create new tasks for blockers or dependencies

## Debugging

Run your server with the `-v` or `-vv` flag for increased verbosity:

```
uvx clickup-mcp-server -vv
```

You can use the MCP inspector to debug the server:

```
npx @modelcontextprotocol/inspector uvx clickup-mcp-server
```

## Development

### Setting Up Development Environment

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/clickup-mcp-server.git
   cd clickup-mcp-server
   ```

2. Install development dependencies:
   ```
   uv pip install -e ".[dev]"
   ```

3. Run tests:
   ```
   pytest
   ```

### Docker Build

Build the Docker image:

```bash
docker build -t mcp/clickup .
```

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
EOF < /dev/null