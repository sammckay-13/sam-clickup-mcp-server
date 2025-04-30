import logging
import requests
from typing import Any, Dict, List, Optional

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
        data = {"name": name, **kwargs}
        return self._make_request("POST", f"/list/{list_id}/task", data=data)
    
    def get_task(self, task_id: str) -> Dict:
        """Get a task by ID"""
        return self._make_request("GET", f"/task/{task_id}")
    
    def update_task(self, task_id: str, **kwargs) -> Dict:
        """Update a task"""
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