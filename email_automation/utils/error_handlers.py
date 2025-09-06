import traceback
from typing import Dict, Any
from utils.logger import logger

class EmailAutomationError(Exception):
    """Base exception for email automation system"""
        pass

        class EmailProcessingError(EmailAutomationError):
            """Raised when email processing fails"""
                pass

                class CRMIntegrationError(EmailAutomationError):
                    """Raised when CRM integration fails"""
                        pass

                        class KnowledgeBaseError(EmailAutomationError):
                            """Raised when knowledge base operations fail"""
                                pass

                                def handle_error(error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
                                    """Handle errors with proper logging and context"""
                                        error_details = {
                                                "error_type": type(error).__name__,
                                                        "error_message": str(error),
                                                                "traceback": traceback.format_exc(),
                                                                        "context": context or {}
                                                                            }
                                                                                
                                                                                    logger.error("Error occurred", **error_details)
                                                                                        
                                                                                            return {
                                                                                                    "success": False,
                                                                                                            "error": error_details,
                                                                                                                    "retryable": isinstance(error, (EmailProcessingError, CRMIntegrationError))
                                                                                                                        }