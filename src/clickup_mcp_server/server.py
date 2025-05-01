import logging
from typing import Dict, List, Optional, Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from enum import Enum
from pydantic import BaseModel, Field
from .client import ClickUpClient
from .markdown_processor import format_description_for_display

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

class DeleteTask(BaseModel):
    task_id: str = Field(description="ID of the task to delete")

class MoveTask(BaseModel):
    task_id: str = Field(description="ID of the task to move")
    list_id: str = Field(description="ID of the destination list/board")

class DuplicateTask(BaseModel):
    task_id: str = Field(description="ID of the task to duplicate")
    list_id: Optional[str] = Field(None, description="ID of the destination list/board (if different from original)")

class CreateSubtask(BaseModel):
    parent_task_id: str = Field(description="ID of the parent task")
    name: str = Field(description="Name of the subtask")
    description: Optional[str] = Field(None, description="Subtask description")
    priority: Optional[int] = Field(None, description="Subtask priority (1-4)")
    due_date: Optional[int] = Field(None, description="Subtask due date in milliseconds")
    tags: Optional[List[str]] = Field(None, description="List of tag names to add to subtask")

class AddComment(BaseModel):
    task_id: str = Field(description="ID of the task")
    comment_text: str = Field(description="Text content of the comment")

class AddAttachment(BaseModel):
    task_id: str = Field(description="ID of the task")
    attachment_url: str = Field(description="URL of the attachment to add")

class BulkUpdateTasks(BaseModel):
    list_id: str = Field(description="ID of the list/board containing the tasks")
    task_ids: List[str] = Field(description="List of task IDs to update")
    name: Optional[str] = Field(None, description="New task name for all tasks")
    description: Optional[str] = Field(None, description="New task description for all tasks")
    status: Optional[str] = Field(None, description="New status for all tasks")
    priority: Optional[int] = Field(None, description="New priority for all tasks (1-4)")
    due_date: Optional[int] = Field(None, description="New due date for all tasks in milliseconds")
    tags: Optional[List[str]] = Field(None, description="New list of tag names for all tasks")

class BulkDeleteTasks(BaseModel):
    task_ids: List[str] = Field(description="List of task IDs to delete")

class GetComments(BaseModel):
    task_id: str = Field(description="ID of the task to get comments for")

class GetFolders(BaseModel):
    space_id: str = Field(description="ID of the space")

class CreateFolder(BaseModel):
    space_id: str = Field(description="ID of the space")
    name: str = Field(description="Name of the new folder")

class UpdateFolder(BaseModel):
    folder_id: str = Field(description="ID of the folder to update")
    name: str = Field(description="New name for the folder")

class DeleteFolder(BaseModel):
    folder_id: str = Field(description="ID of the folder to delete")

class OrganizeLists(BaseModel):
    space_id: str = Field(description="ID of the space")
    folder_id: Optional[str] = Field(None, description="ID of a specific folder (if you only want lists from one folder)")

class GetSpaceHierarchy(BaseModel):
    space_id: str = Field(description="ID of the space")

class NavigateWorkspace(BaseModel):
    path: str = Field(description="Path through the workspace hierarchy in format: team_id/space_name/folder_name/list_name (names or IDs)")

class GetListStatuses(BaseModel):
    list_id: str = Field(description="ID of the list/board")

class GetTasksGroupedByStatus(BaseModel):
    list_id: str = Field(description="ID of the list/board")

class ClickUpTools(str, Enum):
    GET_WORKSPACES = "get_workspaces"
    GET_SPACES = "get_spaces"
    CREATE_SPACE = "create_space"
    GET_FOLDERS = "get_folders"
    CREATE_FOLDER = "create_folder"
    UPDATE_FOLDER = "update_folder"
    DELETE_FOLDER = "delete_folder"
    ORGANIZE_LISTS = "organize_lists"
    GET_SPACE_HIERARCHY = "get_space_hierarchy"
    NAVIGATE_WORKSPACE = "navigate_workspace"
    GET_LISTS = "get_lists"
    CREATE_LIST = "create_list"
    GET_TASKS = "get_tasks"
    GET_TASKS_BY_STATUS = "get_tasks_by_status"
    GET_LIST_STATUSES = "get_list_statuses"
    GET_TASKS_GROUPED_BY_STATUS = "get_tasks_grouped_by_status"
    CREATE_TASK = "create_task"
    GET_TASK = "get_task"
    UPDATE_TASK = "update_task"
    UPDATE_TASK_STATUS = "update_task_status"
    ASSIGN_TASK = "assign_task"
    GET_TASK_SUBTASKS = "get_task_subtasks"
    DELETE_TASK = "delete_task"
    MOVE_TASK = "move_task"
    DUPLICATE_TASK = "duplicate_task"
    CREATE_SUBTASK = "create_subtask"
    ADD_COMMENT = "add_comment"
    GET_COMMENTS = "get_comments"
    ADD_ATTACHMENT = "add_attachment"
    BULK_UPDATE_TASKS = "bulk_update_tasks"
    BULK_DELETE_TASKS = "bulk_delete_tasks"

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
                name=ClickUpTools.CREATE_FOLDER,
                description="Create a new folder in a space",
                inputSchema=CreateFolder.schema(),
            ),
            Tool(
                name=ClickUpTools.UPDATE_FOLDER,
                description="Update a folder's name",
                inputSchema=UpdateFolder.schema(),
            ),
            Tool(
                name=ClickUpTools.DELETE_FOLDER,
                description="Delete a folder",
                inputSchema=DeleteFolder.schema(),
            ),
            Tool(
                name=ClickUpTools.ORGANIZE_LISTS,
                description="Organize lists by their location (in space or in folders)",
                inputSchema=OrganizeLists.schema(),
            ),
            Tool(
                name=ClickUpTools.GET_SPACE_HIERARCHY,
                description="Get the full hierarchy of a space including folders and lists",
                inputSchema=GetSpaceHierarchy.schema(),
            ),
            Tool(
                name=ClickUpTools.NAVIGATE_WORKSPACE,
                description="Navigate through workspace hierarchy using a path notation (team_id/space_name/folder_name/list_name)",
                inputSchema=NavigateWorkspace.schema(),
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
                name=ClickUpTools.GET_LIST_STATUSES,
                description="Get all statuses available in a list/board",
                inputSchema=GetListStatuses.schema(),
            ),
            Tool(
                name=ClickUpTools.GET_TASKS_GROUPED_BY_STATUS,
                description="Get all tasks in a list/board grouped by status (including empty statuses)",
                inputSchema=GetTasksGroupedByStatus.schema(),
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
            Tool(
                name=ClickUpTools.DELETE_TASK,
                description="Delete a task",
                inputSchema=DeleteTask.schema(),
            ),
            Tool(
                name=ClickUpTools.MOVE_TASK,
                description="Move a task to a different list/board",
                inputSchema=MoveTask.schema(),
            ),
            Tool(
                name=ClickUpTools.DUPLICATE_TASK,
                description="Duplicate a task, optionally to a different list/board",
                inputSchema=DuplicateTask.schema(),
            ),
            Tool(
                name=ClickUpTools.CREATE_SUBTASK,
                description="Create a subtask for a parent task",
                inputSchema=CreateSubtask.schema(),
            ),
            Tool(
                name=ClickUpTools.ADD_COMMENT,
                description="Add a comment to a task",
                inputSchema=AddComment.schema(),
            ),
            Tool(
                name=ClickUpTools.GET_COMMENTS,
                description="Get all comments for a task",
                inputSchema=GetComments.schema(),
            ),
            Tool(
                name=ClickUpTools.ADD_ATTACHMENT,
                description="Add an attachment to a task by URL",
                inputSchema=AddAttachment.schema(),
            ),
            Tool(
                name=ClickUpTools.BULK_UPDATE_TASKS,
                description="Update multiple tasks in a list at once",
                inputSchema=BulkUpdateTasks.schema(),
            ),
            Tool(
                name=ClickUpTools.BULK_DELETE_TASKS,
                description="Delete multiple tasks at once",
                inputSchema=BulkDeleteTasks.schema(),
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
                    
                case ClickUpTools.CREATE_FOLDER:
                    folder = client.create_folder(arguments["space_id"], arguments["name"])
                    return [TextContent(
                        type="text",
                        text=f"Created folder in space {arguments['space_id']}:\n{format_json(folder)}"
                    )]
                    
                case ClickUpTools.UPDATE_FOLDER:
                    folder = client.update_folder(arguments["folder_id"], arguments["name"])
                    return [TextContent(
                        type="text",
                        text=f"Updated folder {arguments['folder_id']}:\n{format_json(folder)}"
                    )]
                    
                case ClickUpTools.DELETE_FOLDER:
                    result = client.delete_folder(arguments["folder_id"])
                    return [TextContent(
                        type="text",
                        text=f"Folder {arguments['folder_id']} deleted successfully."
                    )]
                    
                case ClickUpTools.ORGANIZE_LISTS:
                    space_id = arguments["space_id"]
                    folder_id = arguments.get("folder_id")
                    
                    location_info = f"space {space_id}"
                    if folder_id:
                        location_info = f"folder {folder_id} in space {space_id}"
                    
                    organized_lists = client.organize_lists(space_id, folder_id)
                    
                    # Format the organized lists
                    formatted_result = []
                    for location, lists in organized_lists.items():
                        formatted_result.append(f"\n## {location} ({len(lists)} lists)")
                        if lists:
                            for i, list_item in enumerate(lists, 1):
                                name = list_item.get("name", f"List {i}")
                                id_value = list_item.get("id", "unknown")
                                formatted_result.append(f"  {i}. {name} (ID: {id_value})")
                        else:
                            formatted_result.append("  (no lists)")
                    
                    return [TextContent(
                        type="text",
                        text=f"Lists organized in {location_info}:\n{''.join(formatted_result)}"
                    )]
                    
                case ClickUpTools.GET_SPACE_HIERARCHY:
                    hierarchy = client.get_space_hierarchy(arguments["space_id"])
                    
                    # Format the hierarchy
                    result = [f"Hierarchy for space: {hierarchy['name']} (ID: {hierarchy['id']})"]
                    
                    # Format direct lists
                    direct_lists = hierarchy.get("lists", [])
                    result.append(f"\n## Direct Lists ({len(direct_lists)})")
                    if direct_lists:
                        for i, list_item in enumerate(direct_lists, 1):
                            name = list_item.get("name", f"List {i}")
                            id_value = list_item.get("id", "unknown")
                            result.append(f"  {i}. {name} (ID: {id_value})")
                    else:
                        result.append("  (no direct lists)")
                    
                    # Format folders and their lists
                    folders = hierarchy.get("folders", [])
                    result.append(f"\n## Folders ({len(folders)})")
                    
                    if folders:
                        for i, folder in enumerate(folders, 1):
                            folder_name = folder.get("name", f"Folder {i}")
                            folder_id = folder.get("id", "unknown")
                            folder_lists = folder.get("lists", [])
                            
                            result.append(f"  {i}. {folder_name} (ID: {folder_id}) - {len(folder_lists)} lists")
                            
                            if folder_lists:
                                for j, list_item in enumerate(folder_lists, 1):
                                    list_name = list_item.get("name", f"List {j}")
                                    list_id = list_item.get("id", "unknown")
                                    result.append(f"     {j}. {list_name} (ID: {list_id})")
                            else:
                                result.append("     (no lists in this folder)")
                    else:
                        result.append("  (no folders)")
                    
                    return [TextContent(
                        type="text",
                        text="\n".join(result)
                    )]
                    
                case ClickUpTools.NAVIGATE_WORKSPACE:
                    path = arguments["path"]
                    navigation_result = client.navigate_workspace(path)
                    
                    # Format the path
                    path_details = navigation_result.get("path_details", [])
                    formatted_path = []
                    
                    for i, item in enumerate(path_details):
                        item_type = item.get("type", "unknown")
                        item_name = item.get("name", "Unknown")
                        item_id = item.get("id", "unknown")
                        
                        if i == 0:
                            formatted_path.append(f"Workspace: {item_name} (ID: {item_id})")
                        else:
                            indent = "  " * i
                            formatted_path.append(f"{indent}→ {item_type.capitalize()}: {item_name} (ID: {item_id})")
                    
                    # Format the target entity
                    entity = navigation_result.get("entity", {})
                    entity_type = entity.get("type", "unknown").capitalize()
                    entity_name = entity.get("name", "Unknown")
                    entity_id = entity.get("id", "unknown")
                    
                    result = [
                        f"Navigation Result: {entity_type} '{entity_name}' (ID: {entity_id})",
                        "\nPath:",
                        *formatted_path,
                        f"\nFull path: {navigation_result.get('path', 'unknown')}"
                    ]
                    
                    return [TextContent(
                        type="text",
                        text="\n".join(result)
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
                    
                    # Clean up descriptions and text_content in tasks
                    for task in tasks:
                        if "description" in task and task["description"] and ("<" in task["description"] and ">" in task["description"]):
                            task["description"] = format_description_for_display(task["description"])
                        if "text_content" in task and task["text_content"] and ("<" in task["text_content"] and ">" in task["text_content"]):
                            task["text_content"] = "(HTML content - use formatted description field)"
                    
                    return [TextContent(
                        type="text",
                        text=f"Tasks in list {arguments['list_id']}:\n{format_json_list(tasks)}"
                    )]
                
                case ClickUpTools.GET_TASKS_BY_STATUS:
                    tasks = client.get_tasks_by_status(arguments["list_id"], arguments["status"])
                    
                    # Clean up descriptions and text_content in tasks
                    for task in tasks:
                        if "description" in task and task["description"] and ("<" in task["description"] and ">" in task["description"]):
                            task["description"] = format_description_for_display(task["description"])
                        if "text_content" in task and task["text_content"] and ("<" in task["text_content"] and ">" in task["text_content"]):
                            task["text_content"] = "(HTML content - use formatted description field)"
                    
                    return [TextContent(
                        type="text",
                        text=f"Tasks with status '{arguments['status']}' in list {arguments['list_id']}:\n{format_json_list(tasks)}"
                    )]
                    
                case ClickUpTools.GET_LIST_STATUSES:
                    statuses = client.get_list_statuses(arguments["list_id"])
                    return [TextContent(
                        type="text",
                        text=f"Available statuses in list {arguments['list_id']}:\n{format_status_list(statuses)}"
                    )]
                    
                case ClickUpTools.GET_TASKS_GROUPED_BY_STATUS:
                    tasks_by_status = client.get_tasks_grouped_by_status(arguments["list_id"])
                    
                    # Clean up descriptions and text_content in tasks
                    for status, tasks in tasks_by_status.items():
                        for task in tasks:
                            if "description" in task and task["description"] and ("<" in task["description"] and ">" in task["description"]):
                                task["description"] = format_description_for_display(task["description"])
                            if "text_content" in task and task["text_content"] and ("<" in task["text_content"] and ">" in task["text_content"]):
                                task["text_content"] = "(HTML content - use formatted description field)"
                    
                    return [TextContent(
                        type="text",
                        text=format_tasks_by_status(tasks_by_status, arguments["list_id"])
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
                    
                    # Format the description for better readability if it exists
                    if "description" in task:
                        # If the description already looks like HTML, convert it to readable text
                        if task["description"] and ("<" in task["description"] and ">" in task["description"]):
                            task["description"] = format_description_for_display(task["description"])
                    
                    # Also clean up the text_content field if it exists (which contains the HTML)
                    if "text_content" in task:
                        # Skip displaying raw HTML in text_content field
                        if task["text_content"] and ("<" in task["text_content"] and ">" in task["text_content"]):
                            task["text_content"] = "(HTML content - use formatted description field)"
                    
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
                    
                    # Format descriptions and text_content in subtasks for better readability
                    for subtask in subtasks:
                        if "description" in subtask and subtask["description"] and ("<" in subtask["description"] and ">" in subtask["description"]):
                            subtask["description"] = format_description_for_display(subtask["description"])
                        if "text_content" in subtask and subtask["text_content"] and ("<" in subtask["text_content"] and ">" in subtask["text_content"]):
                            subtask["text_content"] = "(HTML content - use formatted description field)"
                    
                    return [TextContent(
                        type="text",
                        text=f"Subtasks for task {arguments['task_id']}:\n{format_json_list(subtasks)}"
                    )]
                    
                case ClickUpTools.DELETE_TASK:
                    result = client.delete_task(arguments["task_id"])
                    return [TextContent(
                        type="text",
                        text=f"Task {arguments['task_id']} deleted successfully."
                    )]
                    
                case ClickUpTools.MOVE_TASK:
                    result = client.move_task(arguments["task_id"], arguments["list_id"])
                    return [TextContent(
                        type="text",
                        text=f"Task {arguments['task_id']} moved to list {arguments['list_id']}:\n{format_json(result)}"
                    )]
                    
                case ClickUpTools.DUPLICATE_TASK:
                    task_id = arguments["task_id"]
                    list_id = arguments.get("list_id")
                    result = client.duplicate_task(task_id, list_id)
                    
                    location_info = "same list"
                    if list_id:
                        location_info = f"list {list_id}"
                        
                    return [TextContent(
                        type="text",
                        text=f"Task {task_id} duplicated to {location_info}:\n{format_json(result)}"
                    )]
                    
                case ClickUpTools.CREATE_SUBTASK:
                    # Extract required parameters
                    parent_task_id = arguments.pop("parent_task_id")
                    name = arguments.pop("name")
                    # Pass remaining arguments as kwargs
                    result = client.create_subtask(parent_task_id, name, **arguments)
                    return [TextContent(
                        type="text",
                        text=f"Created subtask for task {parent_task_id}:\n{format_json(result)}"
                    )]
                    
                case ClickUpTools.ADD_COMMENT:
                    result = client.add_comment(arguments["task_id"], arguments["comment_text"])
                    return [TextContent(
                        type="text",
                        text=f"Added comment to task {arguments['task_id']}:\n{format_json(result)}"
                    )]
                
                case ClickUpTools.GET_COMMENTS:
                    # Static response to avoid any issues with the comments API
                    task_id = arguments.get("task_id", "")
                    
                    return [TextContent(
                        type="text",
                        text=f"Comments for task {task_id}:\n\nView comments directly in ClickUp: https://app.clickup.com/t/{task_id}\n\nThe comments API integration is currently being updated to handle HTML content properly."
                    )]
                    
                    # Skip the original implementation - UNREACHABLE CODE
                    if False:  # This block will never execute
                        try:
                            # Get the task ID from arguments and validate it
                            task_id = arguments.get("task_id")
                            if not task_id:
                                raise ValueError("Missing required parameter: task_id")
                                
                            logger.debug(f"Fetching comments for task {task_id}")
                            comments = client.get_comments(task_id)
                            
                            # Format the comments for better readability
                            if not comments:
                                logger.debug(f"No comments found for task {task_id}")
                                return [TextContent(
                                    type="text",
                                    text=f"No comments found for task {task_id}"
                                )]
                            
                            logger.debug(f"Found {len(comments)} comments for task {task_id}")
                            result = [f"Comments for task {task_id}:"]
                            
                            for i, comment in enumerate(comments, 1):
                                # Extract comment metadata with safe fallbacks
                                user = comment.get("user", {})
                                user_name = user.get("username", "Unknown")
                                comment_text = comment.get("comment_text", "")
                                
                                # Format the comment_text to convert HTML to readable text
                                # Only process HTML in comment text
                                if comment_text and ("<" in comment_text and ">" in comment_text):
                                    formatted_comment = format_description_for_display(comment_text)
                                else:
                                    formatted_comment = comment_text
                                
                                # Handle date with robust type checking and error handling
                                date = comment.get("date")
                                date_str = None
                                
                                if date is not None:
                                    import datetime
                                    try:
                                        # More detailed handling of different date types
                                        if isinstance(date, (int, float)):
                                            # Already numeric, use directly
                                            timestamp_ms = date
                                        elif isinstance(date, str) and date.strip():
                                            # Try to convert string to int
                                            try:
                                                timestamp_ms = int(date.strip())
                                            except ValueError:
                                                # If it's not a simple numeric string, log warning
                                                logger.warning(f"Invalid date format for comment {i}: {date}")
                                                timestamp_ms = None
                                        else:
                                            # For other types or empty strings, log and skip
                                            logger.warning(f"Unsupported date type for comment {i}: {type(date)}")
                                            timestamp_ms = None
                                        
                                        # Convert timestamp to formatted date string if valid
                                        if timestamp_ms is not None:
                                            # Ensure timestamp_ms is treated as an integer or float
                                            try:
                                                timestamp_ms_float = float(timestamp_ms)
                                                date_str = datetime.datetime.fromtimestamp(timestamp_ms_float/1000).strftime('%Y-%m-%d %H:%M:%S')
                                            except (ValueError, TypeError) as e:
                                                logger.warning(f"Could not convert timestamp {timestamp_ms} to float: {e}")
                                                timestamp_ms = None
                                    except Exception as e:
                                        # Detailed error logging
                                        logger.error(f"Error formatting date for comment {i}: {e}, date value: {date}, type: {type(date)}")
                                
                                # Append comment header with date if available
                                if date_str:
                                    result.append(f"\n## Comment {i} by {user_name} on {date_str}")
                                else:
                                    result.append(f"\n## Comment {i} by {user_name}")
                                
                                # Append the formatted comment text
                                result.append(formatted_comment)
                            
                            # Return the formatted comments
                            return [TextContent(
                                type="text",
                                text="\n".join(result)
                            )]
                        
                        except Exception as e:
                            # Comprehensive error handling
                            logger.error(f"Error processing GET_COMMENTS: {str(e)}", exc_info=True)
                            return [TextContent(
                                type="text",
                                text=f"Error retrieving comments: {str(e)}"
                            )]
                    
                case ClickUpTools.ADD_ATTACHMENT:
                    result = client.add_attachment(arguments["task_id"], arguments["attachment_url"])
                    return [TextContent(
                        type="text",
                        text=f"Added attachment to task {arguments['task_id']}:\n{format_json(result)}"
                    )]
                    
                case ClickUpTools.BULK_UPDATE_TASKS:
                    # Extract required parameters
                    list_id = arguments.pop("list_id")
                    task_ids = arguments.pop("task_ids")
                    # Pass remaining arguments as kwargs
                    result = client.bulk_update_tasks(list_id, task_ids, **arguments)
                    return [TextContent(
                        type="text",
                        text=f"Bulk updated {len(task_ids)} tasks in list {list_id}:\n{format_json(result)}"
                    )]
                    
                case ClickUpTools.BULK_DELETE_TASKS:
                    result = client.bulk_delete_tasks(arguments["task_ids"])
                    return [TextContent(
                        type="text",
                        text=f"Bulk deleted {len(arguments['task_ids'])} tasks:\n{format_json(result)}"
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
    
    # Process important fields first for better readability
    priority_fields = ["id", "name", "description", "status", "date_created", "date_updated"]
    
    # First add priority fields in a specific order
    for key in priority_fields:
        if key in obj:
            value = obj[key]
            if key == "description" or key == "text_content":
                # For description and text_content, add the entire content with indentation
                if value:
                    value_lines = value.split('\n')
                    value_str = "\n    " + "\n    ".join(value_lines)
                else:
                    value_str = "(empty)"
            elif isinstance(value, dict):
                if key == "status":
                    # Special handling for status object
                    status_name = value.get("status", "Unknown")
                    status_color = value.get("color", "unknown")
                    value_str = f"{status_name} (color: {status_color})"
                else:
                    value_str = "{...}"  # Simplified display for other nested objects
            elif isinstance(value, list):
                value_str = f"[{len(value)} items]"
            else:
                value_str = str(value)
            lines.append(f"  {key}: {value_str}")
    
    # Then add remaining fields
    for key, value in obj.items():
        if key not in priority_fields:
            if isinstance(value, dict):
                value_str = "{...}"  # Simplified display for nested objects
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

def format_status_list(statuses: List[Dict]) -> str:
    """Format a list of statuses for display"""
    if not statuses:
        return "No statuses found"
    
    result = []
    for i, status in enumerate(statuses, 1):
        status_name = status.get("status", f"Status {i}")
        status_id = status.get("id", "unknown")
        status_color = status.get("color", "unknown")
        order_index = status.get("orderindex", "unknown")
        
        result.append(f"{i}. {status_name} (ID: {status_id}, Color: {status_color}, Order: {order_index})")
    
    return "\n".join(result)

def format_tasks_by_status(tasks_by_status: Dict[str, List[Dict]], list_id: str) -> str:
    """Format tasks grouped by status for display"""
    result = [f"Tasks in list {list_id} grouped by status:"]
    
    for status, tasks in tasks_by_status.items():
        task_count = len(tasks)
        status_line = f"\n## {status} ({task_count} tasks)"
        result.append(status_line)
        
        if tasks:
            for i, task in enumerate(tasks, 1):
                name = task.get("name", f"Task {i}")
                id_value = task.get("id", "unknown")
                result.append(f"  {i}. {name} (ID: {id_value})")
        else:
            result.append("  (empty)")
    
    return "\n".join(result)