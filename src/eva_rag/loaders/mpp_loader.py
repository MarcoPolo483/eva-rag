"""
Microsoft Project Loader

Loads Microsoft Project files (.xml format).
Note: .mpp files are proprietary binary format and require conversion to XML first.

Extracts:
- Project metadata (title, author, start date, finish date)
- Tasks (name, ID, start, finish, duration, percent complete)
- Resources (name, ID, type, cost)
- Assignments (task-resource mappings)
- Calendar information
- Dependencies and constraints
"""

from typing import BinaryIO
import xml.etree.ElementTree as ET
from datetime import datetime

from eva_rag.loaders.base import DocumentLoader, ExtractedDocument


class MSProjectLoader(DocumentLoader):
    """
    Loader for Microsoft Project XML files.
    
    Supports Microsoft Project 2003+ XML format.
    
    Args:
        include_resources: Whether to extract resource information
        include_assignments: Whether to extract task-resource assignments
        max_tasks: Maximum number of tasks to extract (None for all)
    """
    
    def __init__(
        self,
        include_resources: bool = True,
        include_assignments: bool = True,
        max_tasks: int | None = None,
    ):
        self.include_resources = include_resources
        self.include_assignments = include_assignments
        self.max_tasks = max_tasks
    
    def load(self, file_path: str) -> ExtractedDocument:
        """
        Load Microsoft Project XML from a file path.
        
        Args:
            file_path: Path to MS Project XML file
            
        Returns:
            ExtractedDocument with project data
        """
        with open(file_path, "rb") as f:
            return self.load_from_stream(f)
    
    def load_from_stream(self, stream: BinaryIO) -> ExtractedDocument:
        """
        Load Microsoft Project XML from a binary stream.
        
        Args:
            stream: Binary stream containing MS Project XML data
            
        Returns:
            ExtractedDocument with project data in markdown format
        """
        try:
            content = stream.read()
            root = ET.fromstring(content)
            
            # Remove namespace if present
            if root.tag.startswith("{"):
                # Extract namespace
                ns = root.tag[1:root.tag.index("}")]
                # Strip namespace from all elements
                for elem in root.iter():
                    if elem.tag.startswith("{"):
                        elem.tag = elem.tag[elem.tag.index("}")+1:]
            
            # Extract project metadata
            metadata = self._extract_project_metadata(root)
            
            # Extract tasks
            tasks = self._extract_tasks(root)
            
            # Extract resources
            resources = []
            if self.include_resources:
                resources = self._extract_resources(root)
            
            # Extract assignments
            assignments = []
            if self.include_assignments:
                assignments = self._extract_assignments(root)
            
            # Generate markdown text
            text = self._generate_markdown(metadata, tasks, resources, assignments)
            
            return ExtractedDocument(
                text=text,
                metadata={
                    "source": "microsoft_project",
                    "format": "xml",
                    "project_name": metadata.get("title", "Unknown"),
                    "project_start": metadata.get("start_date"),
                    "project_finish": metadata.get("finish_date"),
                    "task_count": len(tasks),
                    "resource_count": len(resources),
                    "assignment_count": len(assignments),
                    "author": metadata.get("author"),
                    "company": metadata.get("company"),
                },
                page_count=1,
            )
            
        except ET.ParseError as e:
            return ExtractedDocument(
                text=f"Error parsing MS Project XML: {str(e)}",
                metadata={"error": str(e), "source": "microsoft_project"},
                page_count=0,
            )
        except Exception as e:
            return ExtractedDocument(
                text=f"Error loading MS Project file: {str(e)}",
                metadata={"error": str(e), "source": "microsoft_project"},
                page_count=0,
            )
    
    def _extract_project_metadata(self, root: ET.Element) -> dict:
        """Extract project-level metadata."""
        metadata = {}
        
        # Standard fields
        fields = {
            "title": "Title",
            "subject": "Subject",
            "author": "Author",
            "company": "Company",
            "start_date": "StartDate",
            "finish_date": "FinishDate",
            "creation_date": "CreationDate",
            "last_saved": "LastSaved",
            "schedule_from_start": "ScheduleFromStart",
            "current_date": "CurrentDate",
            "calendar_uid": "CalendarUID",
        }
        
        for key, xpath in fields.items():
            elem = root.find(xpath)
            if elem is not None and elem.text:
                metadata[key] = elem.text.strip()
        
        return metadata
    
    def _extract_tasks(self, root: ET.Element) -> list[dict]:
        """Extract all tasks from the project."""
        tasks = []
        tasks_elem = root.find("Tasks")
        
        if tasks_elem is None:
            return tasks
        
        for task_elem in tasks_elem.findall("Task"):
            task = {}
            
            # Basic fields
            fields = {
                "id": "ID",
                "uid": "UID",
                "name": "Name",
                "start": "Start",
                "finish": "Finish",
                "duration": "Duration",
                "percent_complete": "PercentComplete",
                "work": "Work",
                "cost": "Cost",
                "priority": "Priority",
                "outline_level": "OutlineLevel",
                "outline_number": "OutlineNumber",
                "is_milestone": "Milestone",
                "is_critical": "Critical",
                "is_summary": "Summary",
                "wbs": "WBS",
                "notes": "Notes",
                "predecessor_link": "PredecessorLink",
            }
            
            for key, xpath in fields.items():
                elem = task_elem.find(xpath)
                if elem is not None and elem.text:
                    text = elem.text.strip()
                    # Convert boolean strings
                    if text in ("0", "1"):
                        task[key] = text == "1"
                    else:
                        task[key] = text
            
            # Extract predecessor links
            predecessors = []
            pred_links = task_elem.findall(".//PredecessorLink")
            for pred in pred_links:
                pred_uid = pred.find("PredecessorUID")
                link_type = pred.find("Type")
                if pred_uid is not None and pred_uid.text:
                    pred_info = {"uid": pred_uid.text}
                    if link_type is not None and link_type.text:
                        pred_info["type"] = link_type.text
                    predecessors.append(pred_info)
            
            if predecessors:
                task["predecessors"] = predecessors
            
            tasks.append(task)
            
            # Respect max_tasks limit
            if self.max_tasks and len(tasks) >= self.max_tasks:
                break
        
        return tasks
    
    def _extract_resources(self, root: ET.Element) -> list[dict]:
        """Extract all resources from the project."""
        resources = []
        resources_elem = root.find("Resources")
        
        if resources_elem is None:
            return resources
        
        for resource_elem in resources_elem.findall("Resource"):
            resource = {}
            
            fields = {
                "id": "ID",
                "uid": "UID",
                "name": "Name",
                "type": "Type",
                "is_null": "IsNull",
                "initials": "Initials",
                "email": "EmailAddress",
                "standard_rate": "StandardRate",
                "overtime_rate": "OvertimeRate",
                "cost": "Cost",
                "work": "Work",
                "max_units": "MaxUnits",
            }
            
            for key, xpath in fields.items():
                elem = resource_elem.find(xpath)
                if elem is not None and elem.text:
                    resource[key] = elem.text.strip()
            
            resources.append(resource)
        
        return resources
    
    def _extract_assignments(self, root: ET.Element) -> list[dict]:
        """Extract all task-resource assignments."""
        assignments = []
        assignments_elem = root.find("Assignments")
        
        if assignments_elem is None:
            return assignments
        
        for assignment_elem in assignments_elem.findall("Assignment"):
            assignment = {}
            
            fields = {
                "uid": "UID",
                "task_uid": "TaskUID",
                "resource_uid": "ResourceUID",
                "units": "Units",
                "work": "Work",
                "start": "Start",
                "finish": "Finish",
                "cost": "Cost",
            }
            
            for key, xpath in fields.items():
                elem = assignment_elem.find(xpath)
                if elem is not None and elem.text:
                    assignment[key] = elem.text.strip()
            
            assignments.append(assignment)
        
        return assignments
    
    def _generate_markdown(
        self,
        metadata: dict,
        tasks: list[dict],
        resources: list[dict],
        assignments: list[dict],
    ) -> str:
        """Generate markdown representation of the project."""
        lines = []
        
        # Project header
        lines.append(f"# {metadata.get('title', 'Untitled Project')}")
        lines.append("")
        
        # Project metadata
        lines.append("## Project Information")
        lines.append("")
        
        if metadata.get("author"):
            lines.append(f"**Author:** {metadata['author']}")
        if metadata.get("company"):
            lines.append(f"**Company:** {metadata['company']}")
        if metadata.get("start_date"):
            lines.append(f"**Start Date:** {metadata['start_date']}")
        if metadata.get("finish_date"):
            lines.append(f"**Finish Date:** {metadata['finish_date']}")
        if metadata.get("creation_date"):
            lines.append(f"**Created:** {metadata['creation_date']}")
        
        lines.append("")
        lines.append(f"**Total Tasks:** {len(tasks)}")
        lines.append(f"**Total Resources:** {len(resources)}")
        lines.append(f"**Total Assignments:** {len(assignments)}")
        lines.append("")
        
        # Tasks section
        lines.append("## Tasks")
        lines.append("")
        
        if tasks:
            # Group by outline level for hierarchy
            summary_tasks = [t for t in tasks if t.get("is_summary")]
            milestones = [t for t in tasks if t.get("is_milestone")]
            critical_tasks = [t for t in tasks if t.get("is_critical")]
            
            if summary_tasks:
                lines.append(f"**Summary Tasks:** {len(summary_tasks)}")
            if milestones:
                lines.append(f"**Milestones:** {len(milestones)}")
            if critical_tasks:
                lines.append(f"**Critical Path Tasks:** {len(critical_tasks)}")
            lines.append("")
            
            # Task table
            lines.append("| ID | Task Name | Start | Finish | Duration | % Complete | Type |")
            lines.append("| --- | --- | --- | --- | --- | --- | --- |")
            
            for task in tasks[:100]:  # Limit to 100 tasks in table
                task_id = task.get("id", "")
                name = task.get("name", "Unnamed")
                start = task.get("start", "")[:10] if task.get("start") else ""
                finish = task.get("finish", "")[:10] if task.get("finish") else ""
                duration = task.get("duration", "")
                percent = task.get("percent_complete", "0")
                
                # Determine type
                task_type = "Task"
                if task.get("is_summary"):
                    task_type = "Summary"
                elif task.get("is_milestone"):
                    task_type = "Milestone"
                elif task.get("is_critical"):
                    task_type = "Critical"
                
                # Indent name based on outline level
                outline_level = int(task.get("outline_level", "1"))
                indent = "  " * (outline_level - 1)
                
                lines.append(
                    f"| {task_id} | {indent}{name} | {start} | {finish} | "
                    f"{duration} | {percent}% | {task_type} |"
                )
            
            if len(tasks) > 100:
                lines.append("")
                lines.append(f"*({len(tasks) - 100} more tasks not shown)*")
        else:
            lines.append("*No tasks found*")
        
        lines.append("")
        
        # Resources section
        if self.include_resources and resources:
            lines.append("## Resources")
            lines.append("")
            lines.append("| ID | Name | Type | Email | Standard Rate | Work |")
            lines.append("| --- | --- | --- | --- | --- | --- |")
            
            for resource in resources[:50]:  # Limit to 50 resources
                res_id = resource.get("id", "")
                name = resource.get("name", "Unnamed")
                res_type = resource.get("type", "")
                email = resource.get("email", "")
                rate = resource.get("standard_rate", "")
                work = resource.get("work", "")
                
                lines.append(f"| {res_id} | {name} | {res_type} | {email} | {rate} | {work} |")
            
            if len(resources) > 50:
                lines.append("")
                lines.append(f"*({len(resources) - 50} more resources not shown)*")
            
            lines.append("")
        
        # Assignments section
        if self.include_assignments and assignments:
            lines.append("## Assignments")
            lines.append("")
            lines.append(f"**Total Assignments:** {len(assignments)}")
            lines.append("")
            lines.append("| Task UID | Resource UID | Units | Work | Cost |")
            lines.append("| --- | --- | --- | --- | --- |")
            
            for assignment in assignments[:50]:  # Limit to 50 assignments
                task_uid = assignment.get("task_uid", "")
                resource_uid = assignment.get("resource_uid", "")
                units = assignment.get("units", "")
                work = assignment.get("work", "")
                cost = assignment.get("cost", "")
                
                lines.append(f"| {task_uid} | {resource_uid} | {units} | {work} | {cost} |")
            
            if len(assignments) > 50:
                lines.append("")
                lines.append(f"*({len(assignments) - 50} more assignments not shown)*")
            
            lines.append("")
        
        return "\n".join(lines)
