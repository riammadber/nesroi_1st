import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from crewai import Crew, Process
from tasks.email_tasks import EmailTasks
from tasks.response_tasks import ResponseTasks
from tools.supabase_tool import SupabaseTool
from utils.logger import logger
from utils.error_handlers import handle_error, EmailAutomationError
from config.settings import settings

class EmailAutomationSystem:
    def __init__(self):
        self.email_tasks = EmailTasks()
        self.response_tasks = ResponseTasks()
        self.supabase_tool = SupabaseTool()
        self.running = False
    
    async def start(self):
        """Start the email automation system"""
        logger.info("Starting Email Automation System")
        self.running = True
        
        try:
            while self.running:
                # Process incoming emails
                await self.process_incoming_emails()
                
                # Send pending responses
                await self.send_pending_responses()
                
                # Wait before next cycle
                await asyncio.sleep(settings.processing_timeout)
                
        except KeyboardInterrupt:
            logger.info("Shutting down Email Automation System")
            self.running = False
        except Exception as e:
            logger.error("Fatal error in Email Automation System", error=str(e))
            self.running = False
            raise
    
    async def process_incoming_emails(self):
        """Process incoming emails"""
        try:
            logger.info("Processing incoming emails")
            
            # Create email processing workflow
            tasks = self.email_tasks.create_email_processing_workflow(settings.batch_size)
            
            # Create crew for email processing
            email_crew = Crew(
                agents=[
                    self.email_tasks.email_processor,
                    self.email_tasks.categorizer,
                    self.email_tasks.knowledge_retriever,
                    self.email_tasks.response_generator,
                    self.email_tasks.quality_controller
                ],
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            
            # Execute the workflow
            result = email_crew.kickoff()
            
            logger.info("Email processing completed", result=result)
            
        except Exception as e:
            error_result = handle_error(e, {"operation": "process_incoming_emails"})
            logger.error("Failed to process incoming emails", error=error_result)
    
    async def send_pending_responses(self):
        """Send pending email responses"""
        try:
            logger.info("Sending pending responses")
            
            # Get unsent emails
            unsent_emails = self.supabase_tool._run("get_unsent_emails", limit=settings.batch_size)
            
            if not unsent_emails:
                logger.info("No pending responses to send")
                return
            
            # Create response sending workflow
            tasks = self.response_tasks.create_send_responses_workflow(unsent_emails)
            
            # Create crew for response sending
            response_crew = Crew(
                agents=[
                    self.response_tasks.response_generator,
                    self.response_tasks.quality_controller
                ],
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            
            # Execute the workflow
            result = response_crew.kickoff()
            
            logger.info("Response sending completed", result=result)
            
        except Exception as e:
            error_result = handle_error(e, {"operation": "send_pending_responses"})
            logger.error("Failed to send pending responses", error=error_result)
    
    def stop(self):
        """Stop the email automation system"""
        logger.info("Stopping Email Automation System")
        self.running = False

async def main():
    """Main entry point"""
    # Initialize the system
    system = EmailAutomationSystem()
    
    try:
        # Start the system
        await system.start()
    except Exception as e:
        logger.error("System failed to start", error=str(e))
        raise

if __name__ == "__main__":
    # Run the main application
    asyncio.run(main())