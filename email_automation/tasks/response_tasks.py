from typing import Dict, Any, List
from crewai import Task
from agents.response_generator import ResponseGeneratorAgent
from agents.quality_controller import QualityControllerAgent
from tools.gmail_tool import GmailTool
from tools.supabase_tool import SupabaseTool
from utils.logger import logger

class ResponseTasks:
    def __init__(self):
        self.response_generator = ResponseGeneratorAgent()
        self.quality_controller = QualityControllerAgent()
        self.gmail_tool = GmailTool()
        self.supabase_tool = SupabaseTool()
    
    def create_send_response_task(self, email_data: Dict[str, Any], response_content: str) -> Task:
        """Create task for sending email response"""
        return Task(
            description="Send the email response to the customer",
            agent=self.response_generator,
            expected_output="Confirmation of sent email with message ID",
            context={"email_data": email_data, "response_content": response_content}
        )
    
    def create_update_database_task(self, email_id: str, update_data: Dict[str, Any]) -> Task:
        """Create task for updating database record"""
        return Task(
            description="Update email record in database",
            agent=self.quality_controller,
            expected_output="Confirmation of database update",
            context={"email_id": email_id, "update_data": update_data}
        )
    
    def create_send_responses_workflow(self, unsent_emails: List[Dict[str, Any]]) -> List[Task]:
        """Create workflow for sending unsent responses"""
        tasks = []
        
        for email in unsent_emails:
            # Send response
            send_task = self.create_send_response_task(
                email,
                email.get('final_response', '')
            )
            tasks.append(send_task)
            
            # Update database
            update_task = self.create_update_database_task(
                email['id'],
                {
                    'message_sent': True,
                    'sent_at': datetime.utcnow().isoformat()
                }
            )
            tasks.append(update_task)
        
        return tasks