import logging
import requests
from typing import Any, Dict, List, Optional
from .markdown_processor import process_markdown

class ClickUpClient:
    """Client for interacting with the ClickUp API"""
    
    BASE_URL = "https://api.clickup.com/api/v2"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """Make a request to the ClickUp API"""
        url = f"{self.BASE_URL}{endpoint}"
        
        self.logger.debug(f"Making {method} request to {url}")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data
            )
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making request to ClickUp API: {e}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"Response: {e.response.text}")
            raise
    
    # Workspace/Team methods
    
    def get_workspaces(self) -> List[Dict]:
        """Get all workspaces/teams"""
        response = self._make_request("GET", "/team")
        return response.get("teams", [])
    
    # Space methods
    
    def get_spaces(self, workspace_id: str) -> List[Dict]:
        """Get all spaces in a workspace"""
        response = self._make_request("GET", f"/team/{workspace_id}/space")
        return response.get("spaces", [])
    
    def create_space(self, workspace_id: str, name: str) -> Dict:
        """Create a new space in a workspace"""
        data = {"name": name}
        return self._make_request("POST", f"/team/{workspace_id}/space", data=data)
    
    # Folder methods
    
    def get_folders(self, space_id: str) -> List[Dict]:
        """Get all folders in a space"""
        response = self._make_request("GET", f"/space/{space_id}/folder")
        return response.get("folders", [])
        
    def create_folder(self, space_id: str, name: str) -> Dict:
        """Create a new folder in a space"""
        data = {"name": name}
        return self._make_request("POST", f"/space/{space_id}/folder", data=data)
    
    def update_folder(self, folder_id: str, name: str) -> Dict:
        """Update a folder's name"""
        data = {"name": name}
        return self._make_request("PUT", f"/folder/{folder_id}", data=data)
    
    def delete_folder(self, folder_id: str) -> Dict:
        """Delete a folder"""
        return self._make_request("DELETE", f"/folder/{folder_id}")
        
    def organize_lists(self, space_id: str, folder_id: Optional[str] = None) -> Dict[str, List[Dict]]:
        """Organize lists by their location (in space or in folders)"""
        # Get lists directly in the space
        direct_lists = []
        if not folder_id:
            response = self._make_request("GET", f"/space/{space_id}/list")
            direct_lists = response.get("lists", [])
        
        # Get folders and their lists
        folder_lists = {}
        if folder_id:
            # If a specific folder is requested
            folders = [self._make_request("GET", f"/folder/{folder_id}")]
        else:
            # Get all folders in the space
            folders = self.get_folders(space_id)
            
        for folder in folders:
            folder_id = folder.get("id")
            folder_name = folder.get("name")
            folder_response = self._make_request("GET", f"/folder/{folder_id}/list")
            folder_lists[f"{folder_name} ({folder_id})"] = folder_response.get("lists", [])
        
        result = {}
        if direct_lists:
            result["Space (direct)"] = direct_lists
        result.update(folder_lists)
        
        return result
    
    def get_space_hierarchy(self, space_id: str) -> Dict:
        """Get the full hierarchy of a space including folders and lists"""
        # Get space details
        space = self._make_request("GET", f"/space/{space_id}")
        
        # Get folders
        folders = self.get_folders(space_id)
        folder_data = []
        
        for folder in folders:
            folder_id = folder.get("id")
            folder_lists_response = self._make_request("GET", f"/folder/{folder_id}/list")
            folder_lists = folder_lists_response.get("lists", [])
            
            # Add lists to folder
            folder["lists"] = folder_lists
            folder_data.append(folder)
        
        # Get lists directly in space
        direct_lists_response = self._make_request("GET", f"/space/{space_id}/list")
        direct_lists = direct_lists_response.get("lists", [])
        
        # Build hierarchy
        hierarchy = {
            "id": space.get("id"),
            "name": space.get("name"),
            "folders": folder_data,
            "lists": direct_lists
        }
        
        return hierarchy
    
    # List/Board methods
    
    def get_lists(self, space_id: str) -> List[Dict]:
        """Get all lists in a space, including lists inside folders"""
        # First get lists directly in the space
        response = self._make_request("GET", f"/space/{space_id}/list")
        lists = response.get("lists", [])
        
        # Then get folders and their lists
        folders = self.get_folders(space_id)
        for folder in folders:
            folder_id = folder.get("id")
            folder_response = self._make_request("GET", f"/folder/{folder_id}/list")
            folder_lists = folder_response.get("lists", [])
            
            # Add folder information to each list for context
            for list_item in folder_lists:
                list_item["folder_id"] = folder_id
                list_item["folder_name"] = folder.get("name")
            
            lists.extend(folder_lists)
            
        return lists
    
    def create_list(self, space_id: str, name: str, folder_id: Optional[str] = None) -> Dict:
        """Create a new list in a space or folder"""
        data = {"name": name}
        
        if folder_id:
            # Create list in a folder
            return self._make_request("POST", f"/folder/{folder_id}/list", data=data)
        else:
            # Create list directly in a space
            return self._make_request("POST", f"/space/{space_id}/list", data=data)
    
    # Task methods
    
    def get_tasks(self, list_id: str, params: Optional[Dict] = None) -> List[Dict]:
        """Get tasks in a list with optional filtering"""
        response = self._make_request("GET", f"/list/{list_id}/task", params=params)
        return response.get("tasks", [])
    
    def get_tasks_by_status(self, list_id: str, status: str) -> List[Dict]:
        """Get tasks in a list with a specific status"""
        params = {"statuses[]": status}
        return self.get_tasks(list_id, params)
        
    def get_list_statuses(self, list_id: str) -> List[Dict]:
        """Get all statuses available in a list"""
        response = self._make_request("GET", f"/list/{list_id}")
        return response.get("statuses", [])
        
    def get_tasks_grouped_by_status(self, list_id: str) -> Dict[str, List[Dict]]:
        """Get all tasks in a list grouped by status, including empty statuses"""
        # Get all tasks in the list
        all_tasks = self.get_tasks(list_id)
        
        # Get all statuses in the list
        statuses = self.get_list_statuses(list_id)
        
        # Initialize result dictionary with empty lists for each status
        result = {status["status"]: [] for status in statuses}
        
        # Group tasks by status
        for task in all_tasks:
            status = task.get("status", {})
            if isinstance(status, dict):
                status_name = status.get("status")
            else:
                status_name = status
            
            if status_name in result:
                result[status_name].append(task)
        
        return result
    
    def create_task(self, list_id: str, name: str, **kwargs) -> Dict:
        """Create a new task in a list"""
        # Process markdown in description if present, ensuring HTML compatibility
        if "markdown_description" in kwargs:
            kwargs["description"] = process_markdown("/Markdown " + kwargs["markdown_description"], convert_to_html=False)
            del kwargs["markdown_description"]
            
        data = {"name": name, **kwargs}
        return self._make_request("POST", f"/list/{list_id}/task", data=data)
    
    def get_task(self, task_id: str) -> Dict:
        """Get a task by ID"""
        return self._make_request("GET", f"/task/{task_id}")
    
    def update_task(self, task_id: str, **kwargs) -> Dict:
        """Update a task"""
        # Process markdown in description if present, ensuring HTML compatibility
        if "markdown_description" in kwargs:
            kwargs["description"] = process_markdown("/Markdown " + kwargs["markdown_description"], convert_to_html=False)
            del kwargs["markdown_description"]
            
        return self._make_request("PUT", f"/task/{task_id}", data=kwargs)
    
    def update_task_status(self, task_id: str, status: str) -> Dict:
        """Update a task's status"""
        return self.update_task(task_id, status=status)
    
    def assign_task(self, task_id: str, assignee_ids: List[str]) -> Dict:
        """Assign users to a task"""
        data = {"assignees": assignee_ids}
        return self._make_request("POST", f"/task/{task_id}/assignee", data=data)
    
    def get_task_subtasks(self, task_id: str) -> List[Dict]:
        """Get subtasks for a task"""
        params = {"subtasks": True}
        response = self._make_request("GET", f"/task/{task_id}", params=params)
        return response.get("subtasks", [])
        
    def delete_task(self, task_id: str) -> Dict:
        """Delete a task by ID"""
        return self._make_request("DELETE", f"/task/{task_id}")
        
    def move_task(self, task_id: str, list_id: str) -> Dict:
        """Move a task to a different list"""
        data = {"list_id": list_id}
        return self._make_request("POST", f"/task/{task_id}", data=data)
        
    def duplicate_task(self, task_id: str, list_id: str = None) -> Dict:
        """Duplicate a task, optionally to a different list"""
        data = {}
        if list_id:
            data["list_id"] = list_id
        return self._make_request("POST", f"/task/{task_id}/duplicate", data=data)
        
    def create_subtask(self, parent_task_id: str, name: str, **kwargs) -> Dict:
        """Create a subtask for a parent task"""
        # Process markdown in description if present, ensuring HTML compatibility
        if "markdown_description" in kwargs:
            kwargs["description"] = process_markdown("/Markdown " + kwargs["markdown_description"], convert_to_html=False)
            del kwargs["markdown_description"]
            
        data = {"name": name, **kwargs}
        return self._make_request("POST", f"/task/{parent_task_id}/subtask", data=data)
        
    def add_comment(self, task_id: str, comment_text: str) -> Dict:
        """Add a comment to a task"""
        # Process markdown in comment text, ensuring HTML compatibility
        # Set convert_to_html=True to ensure we get HTML output for ClickUp
        processed_comment = process_markdown(comment_text, convert_to_html=False)
        data = {"comment_text": processed_comment}
        return self._make_request("POST", f"/task/{task_id}/comment", data=data)
    
    def get_comments(self, task_id: str) -> List[Dict]:
        """Get all comments for a task"""
        response = self._make_request("GET", f"/task/{task_id}/comment")
        return response.get("comments", [])
        
    def add_attachment(self, task_id: str, attachment_url: str) -> Dict:
        """Add an attachment to a task by URL"""
        data = {"attachment": attachment_url}
        return self._make_request("POST", f"/task/{task_id}/attachment", data=data)
        
    def bulk_update_tasks(self, list_id: str, task_ids: List[str], **kwargs) -> Dict:
        """Update multiple tasks in a list at once"""
        # Process markdown in description if present, ensuring HTML compatibility
        if "markdown_description" in kwargs:
            kwargs["description"] = process_markdown("/Markdown " + kwargs["markdown_description"], convert_to_html=False)
            del kwargs["markdown_description"]
            
        data = {"ids": task_ids, **kwargs}
        return self._make_request("PUT", f"/list/{list_id}/task/bulk", data=data)
        
    def bulk_delete_tasks(self, task_ids: List[str]) -> Dict:
        """Delete multiple tasks at once"""
        data = {"tasks": task_ids}
        return self._make_request("DELETE", "/task/bulk", data=data)
        
    def navigate_workspace(self, path: str) -> Dict:
        """
        Navigate through workspace hierarchy using path notation
        
        Path format: team_id/space_name/folder_name/list_name
        or using IDs: team_id/space_id/folder_id/list_id
        
        Returns the details of the target entity and its full path
        """
        parts = path.strip('/').split('/')
        if len(parts) < 1:
            raise ValueError("Path must include at least a team/workspace ID")
            
        # Start with team/workspace
        team_id = parts[0]
        current_entity = {"id": team_id, "name": "Workspace", "type": "team"}
        path_info = [current_entity]
        
        if len(parts) >= 2:
            # Find space by name or ID
            space_identifier = parts[1]
            spaces = self.get_spaces(team_id)
            
            found_space = None
            for space in spaces:
                if space.get("id") == space_identifier or space.get("name") == space_identifier:
                    found_space = space
                    found_space["type"] = "space"
                    break
                    
            if not found_space:
                raise ValueError(f"Space '{space_identifier}' not found in workspace {team_id}")
                
            current_entity = found_space
            path_info.append(current_entity)
            
            if len(parts) >= 3:
                # Find folder by name or ID
                folder_identifier = parts[2]
                folders = self.get_folders(current_entity.get("id"))
                
                found_folder = None
                for folder in folders:
                    if folder.get("id") == folder_identifier or folder.get("name") == folder_identifier:
                        found_folder = folder
                        found_folder["type"] = "folder"
                        break
                        
                if not found_folder:
                    raise ValueError(f"Folder '{folder_identifier}' not found in space {current_entity.get('name')}")
                    
                current_entity = found_folder
                path_info.append(current_entity)
                
                if len(parts) >= 4:
                    # Find list by name or ID
                    list_identifier = parts[3]
                    lists = self._make_request("GET", f"/folder/{current_entity.get('id')}/list").get("lists", [])
                    
                    found_list = None
                    for list_item in lists:
                        if list_item.get("id") == list_identifier or list_item.get("name") == list_identifier:
                            found_list = list_item
                            found_list["type"] = "list"
                            break
                            
                    if not found_list:
                        raise ValueError(f"List '{list_identifier}' not found in folder {current_entity.get('name')}")
                        
                    current_entity = found_list
                    path_info.append(current_entity)
        
        # Build result with the entity and path information
        result = {
            "entity": current_entity,
            "path": "/".join([item.get("name", item.get("id")) for item in path_info]),
            "path_details": path_info
        }
        
        return result