import logging
from typing import Dict, List, Optional, Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from enum import Enum
from pydantic import BaseModel, Field
from .client import ClickUpClient

# Input Models for ClickUp API Operations

class GetWorkspaces(BaseModel):
    pass

class GetSpaces(BaseModel):
    workspace_id: str = Field(description="ID of the workspace/team")

class CreateSpace(BaseModel):
    workspace_id: str = Field(description="ID of the workspace/team")
    name: str = Field(description="Name of the new space")

class GetLists(BaseModel):
    space_id: str = Field(description="ID of the space")

class CreateList(BaseModel):
    space_id: str = Field(description="ID of the space")
    name: str = Field(description="Name of the new list")
    folder_id: Optional[str] = Field(None, description="ID of the folder (if creating list in a folder)")

class GetTasks(BaseModel):
    list_id: str = Field(description="ID of the list/board")

class GetTasksByStatus(BaseModel):
    list_id: str = Field(description="ID of the list/board")
    status: str = Field(description="Status to filter tasks by")

class CreateTask(BaseModel):
    list_id: str = Field(description="ID of the list/board")
    name: str = Field(description="Name of the task")
    description: Optional[str] = Field(None, description="Task description")
    priority: Optional[int] = Field(None, description="Task priority (1-4)")
    due_date: Optional[int] = Field(None, description="Task due date in milliseconds")
    tags: Optional[List[str]] = Field(None, description="List of tag names to add to task")

class GetTask(BaseModel):
    task_id: str = Field(description="ID of the task")

class UpdateTask(BaseModel):
    task_id: str = Field(description="ID of the task")
    name: Optional[str] = Field(None, description="New task name")
    description: Optional[str] = Field(None, description="New task description")
    priority: Optional[int] = Field(None, description="New task priority (1-4)")
    due_date: Optional[int] = Field(None, description="New due date in milliseconds")
    tags: Optional[List[str]] = Field(None, description="New list of tag names")

class UpdateTaskStatus(BaseModel):
    task_id: str = Field(description="ID of the task")
    status: str = Field(description="New status for the task")

class AssignTask(BaseModel):
    task_id: str = Field(description="ID of the task")
    assignee_ids: List[str] = Field(description="List of user IDs to assign to the task")

class GetTaskSubtasks(BaseModel):
    task_id: str = Field(description="ID of the task")

class GetFolders(BaseModel):
    space_id: str = Field(description="ID of the space")

class ClickUpTools(str, Enum):
    GET_WORKSPACES = "get_workspaces"
    GET_SPACES = "get_spaces"
    CREATE_SPACE = "create_space"
    GET_FOLDERS = "get_folders"
    GET_LISTS = "get_lists"
    CREATE_LIST = "create_list"
    GET_TASKS = "get_tasks"
    GET_TASKS_BY_STATUS = "get_tasks_by_status"
    CREATE_TASK = "create_task"
    GET_TASK = "get_task"
    UPDATE_TASK = "update_task"
    UPDATE_TASK_STATUS = "update_task_status"
    ASSIGN_TASK = "assign_task"
    GET_TASK_SUBTASKS = "get_task_subtasks"

async def serve(api_key: str) -> None:
    """Run the ClickUp MCP server"""
    logger = logging.getLogger(__name__)
    client = ClickUpClient(api_key)
    
    server = Server("mcp-clickup")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        return [
            Tool(
                name=ClickUpTools.GET_WORKSPACES,
                description="Get all workspaces/teams",
                inputSchema=GetWorkspaces.schema(),
            ),
            Tool(
                name=ClickUpTools.GET_SPACES,
                description="Get all spaces in a workspace",
                inputSchema=GetSpaces.schema(),
            ),
            Tool(
                name=ClickUpTools.CREATE_SPACE,
                description="Create a new space in a workspace",
                inputSchema=CreateSpace.schema(),
            ),
            Tool(
                name=ClickUpTools.GET_FOLDERS,
                description="Get all folders in a space",
                inputSchema=GetFolders.schema(),
            ),
            Tool(
                name=ClickUpTools.GET_LISTS,
                description="Get all lists/boards in a space (including lists in folders)",
                inputSchema=GetLists.schema(),
            ),
            Tool(
                name=ClickUpTools.CREATE_LIST,
                description="Create a new list/board in a space or folder",
                inputSchema=CreateList.schema(),
            ),
            Tool(
                name=ClickUpTools.GET_TASKS,
                description="Get all tasks in a list/board",
                inputSchema=GetTasks.schema(),
            ),
            Tool(
                name=ClickUpTools.GET_TASKS_BY_STATUS,
                description="Get tasks with a specific status in a list/board",
                inputSchema=GetTasksByStatus.schema(),
            ),
            Tool(
                name=ClickUpTools.CREATE_TASK,
                description="Create a new task in a list/board",
                inputSchema=CreateTask.schema(),
            ),
            Tool(
                name=ClickUpTools.GET_TASK,
                description="Get details of a specific task",
                inputSchema=GetTask.schema(),
            ),
            Tool(
                name=ClickUpTools.UPDATE_TASK,
                description="Update a task's properties",
                inputSchema=UpdateTask.schema(),
            ),
            Tool(
                name=ClickUpTools.UPDATE_TASK_STATUS,
                description="Update a task's status",
                inputSchema=UpdateTaskStatus.schema(),
            ),
            Tool(
                name=ClickUpTools.ASSIGN_TASK,
                description="Assign users to a task",
                inputSchema=AssignTask.schema(),
            ),
            Tool(
                name=ClickUpTools.GET_TASK_SUBTASKS,
                description="Get subtasks for a task",
                inputSchema=GetTaskSubtasks.schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        logger.debug(f"Calling tool: {name} with arguments: {arguments}")
        
        try:
            match name:
                case ClickUpTools.GET_WORKSPACES:
                    workspaces = client.get_workspaces()
                    return [TextContent(
                        type="text",
                        text=f"Workspaces:\n{format_json_list(workspaces)}"
                    )]
                
                case ClickUpTools.GET_SPACES:
                    spaces = client.get_spaces(arguments["workspace_id"])
                    return [TextContent(
                        type="text",
                        text=f"Spaces in workspace {arguments['workspace_id']}:\n{format_json_list(spaces)}"
                    )]
                
                case ClickUpTools.CREATE_SPACE:
                    space = client.create_space(arguments["workspace_id"], arguments["name"])
                    return [TextContent(
                        type="text",
                        text=f"Created space:\n{format_json(space)}"
                    )]
                
                case ClickUpTools.GET_FOLDERS:
                    folders = client.get_folders(arguments["space_id"])
                    return [TextContent(
                        type="text",
                        text=f"Folders in space {arguments['space_id']}:\n{format_json_list(folders)}"
                    )]
                
                case ClickUpTools.GET_LISTS:
                    lists = client.get_lists(arguments["space_id"])
                    return [TextContent(
                        type="text",
                        text=f"Lists in space {arguments['space_id']} (including lists in folders):\n{format_json_list(lists)}"
                    )]
                
                case ClickUpTools.CREATE_LIST:
                    space_id = arguments["space_id"]
                    name = arguments["name"]
                    folder_id = arguments.get("folder_id")
                    list_obj = client.create_list(space_id, name, folder_id)
                    
                    location_info = f"space {space_id}"
                    if folder_id:
                        location_info = f"folder {folder_id} in space {space_id}"
                        
                    return [TextContent(
                        type="text",
                        text=f"Created list in {location_info}:\n{format_json(list_obj)}"
                    )]
                
                case ClickUpTools.GET_TASKS:
                    tasks = client.get_tasks(arguments["list_id"])
                    return [TextContent(
                        type="text",
                        text=f"Tasks in list {arguments['list_id']}:\n{format_json_list(tasks)}"
                    )]
                
                case ClickUpTools.GET_TASKS_BY_STATUS:
                    tasks = client.get_tasks_by_status(arguments["list_id"], arguments["status"])
                    return [TextContent(
                        type="text",
                        text=f"Tasks with status '{arguments['status']}' in list {arguments['list_id']}:\n{format_json_list(tasks)}"
                    )]
                
                case ClickUpTools.CREATE_TASK:
                    # Extract optional parameters
                    list_id = arguments.pop("list_id")
                    name = arguments.pop("name")
                    task = client.create_task(list_id, name, **arguments)
                    return [TextContent(
                        type="text",
                        text=f"Created task:\n{format_json(task)}"
                    )]
                
                case ClickUpTools.GET_TASK:
                    task = client.get_task(arguments["task_id"])
                    return [TextContent(
                        type="text",
                        text=f"Task details:\n{format_json(task)}"
                    )]
                
                case ClickUpTools.UPDATE_TASK:
                    # Extract task_id and pass the rest as keyword arguments
                    task_id = arguments.pop("task_id")
                    task = client.update_task(task_id, **arguments)
                    return [TextContent(
                        type="text",
                        text=f"Updated task:\n{format_json(task)}"
                    )]
                
                case ClickUpTools.UPDATE_TASK_STATUS:
                    task = client.update_task_status(arguments["task_id"], arguments["status"])
                    return [TextContent(
                        type="text",
                        text=f"Updated task status to '{arguments['status']}':\n{format_json(task)}"
                    )]
                
                case ClickUpTools.ASSIGN_TASK:
                    result = client.assign_task(arguments["task_id"], arguments["assignee_ids"])
                    return [TextContent(
                        type="text",
                        text=f"Assigned users to task:\n{format_json(result)}"
                    )]
                
                case ClickUpTools.GET_TASK_SUBTASKS:
                    subtasks = client.get_task_subtasks(arguments["task_id"])
                    return [TextContent(
                        type="text",
                        text=f"Subtasks for task {arguments['task_id']}:\n{format_json_list(subtasks)}"
                    )]
                
                case _:
                    raise ValueError(f"Unknown tool: {name}")
        
        except Exception as e:
            logger.error(f"Error calling tool {name}: {str(e)}")
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)

def format_json(obj: Dict) -> str:
    """Format a dictionary in a friendly way for display"""
    if not obj:
        return "No data"
    
    lines = []
    for key, value in obj.items():
        if isinstance(value, dict):
            value_str = "{...}" # Simplified display for nested objects
        elif isinstance(value, list):
            value_str = f"[{len(value)} items]"
        else:
            value_str = str(value)
        lines.append(f"  {key}: {value_str}")
    
    return "\n".join(lines)

def format_json_list(items: List[Dict]) -> str:
    """Format a list of dictionaries in a friendly way for display"""
    if not items:
        return "No items found"
    
    result = []
    for i, item in enumerate(items, 1):
        name = item.get("name", f"Item {i}")
        id_value = item.get("id", "unknown")
        
        # For lists that are in folders, show folder information
        if "folder_name" in item and "folder_id" in item:
            result.append(f"{i}. {name} (ID: {id_value}) - in folder: {item['folder_name']} (ID: {item['folder_id']})")
        else:
            result.append(f"{i}. {name} (ID: {id_value})")
    
    return "\n".join(result)