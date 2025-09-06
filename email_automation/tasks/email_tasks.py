from typing import Dict, Any, List
from crewai import Task
from agents.email_processor import EmailProcessorAgent
from agents.categorizer import EmailCategorizerAgent
from agents.knowledge_retriever import KnowledgeRetrieverAgent
from agents.response_generator import ResponseGeneratorAgent
from agents.quality_controller import QualityControllerAgent
from utils.logger import logger

class EmailTasks:
    def __init__(self):
        self.email_processor = EmailProcessorAgent()
        self.categorizer = EmailCategorizerAgent()
        self.knowledge_retriever = KnowledgeRetrieverAgent()
        self.response_generator = ResponseGeneratorAgent()
        self.quality_controller = QualityControllerAgent()
    
    def create_process_emails_task(self, max_emails: int = 10) -> Task:
        """Create task for processing incoming emails"""
        return Task(
            description=f"Process up to {max_emails} incoming emails and extract relevant information",
            agent=self.email_processor,
            expected_output="List of processed emails with extracted information",
            context={"max_emails": max_emails}
        )
    
    def create_categorize_email_task(self, email_data: Dict[str, Any]) -> Task:
        """Create task for categorizing a specific email"""
        return Task(
            description="Categorize email into Sales, Customer Service, or Other and determine importance",
            agent=self.categorizer,
            expected_output="Email categorization with category, importance, and reasoning",
            context={"email_data": email_data}
        )
    
    def create_retrieve_knowledge_task(self, email_data: Dict[str, Any], categorization: Dict[str, Any]) -> Task:
        """Create task for retrieving relevant knowledge"""
        return Task(
            description="Search knowledge base for information relevant to the email",
            agent=self.knowledge_retriever,
            expected_output="Relevant knowledge items with relevance scores",
            context={"email_data": email_data, "categorization": categorization}
        )
    
    def create_generate_response_task(self, email_data: Dict[str, Any], categorization: Dict[str, Any], knowledge: Dict[str, Any]) -> Task:
        """Create task for generating email response"""
        return Task(
            description="Generate appropriate response to the email",
            agent=self.response_generator,
            expected_output="Draft email response with appropriate tone and content",
            context={"email_data": email_data, "categorization": categorization, "knowledge": knowledge}
        )
    
    def create_quality_review_task(self, email_data: Dict[str, Any], response_data: Dict[str, Any]) -> Task:
        """Create task for reviewing response quality"""
        return Task(
            description="Review and improve generated response for quality",
            agent=self.quality_controller,
            expected_output="Quality-reviewed response with score and improvement notes",
            context={"email_data": email_data, "response_data": response_data}
        )
    
    def create_email_processing_workflow(self, max_emails: int = 10) -> List[Task]:
        """Create complete email processing workflow"""
        tasks = []
        
        # Step 1: Process incoming emails
        process_task = self.create_process_emails_task(max_emails)
        tasks.append(process_task)
        
        # For each processed email, create subsequent tasks
        # This is a simplified version - in production, you'd handle this differently
        for i in range(max_emails):
            # Step 2: Categorize email
            categorize_task = self.create_categorize_email_task({"id": f"email_{i}"})
            tasks.append(categorize_task)
            
            # Step 3: Retrieve knowledge
            knowledge_task = self.create_retrieve_knowledge_task(
                {"id": f"email_{i}"}, 
                {"category": "Sales"}  # This would come from categorization
            )
            tasks.append(knowledge_task)
            
            # Step 4: Generate response
            response_task = self.create_generate_response_task(
                {"id": f"email_{i}"},
                {"category": "Sales"},
                {"knowledge_items": []}
            )
            tasks.append(response_task)
            
            # Step 5: Quality review
            quality_task = self.create_quality_review_task(
                {"id": f"email_{i}"},
                {"response_content": "Draft response"}
            )
            tasks.append(quality_task)
        
        return tasks