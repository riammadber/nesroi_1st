from typing import Dict, Any, List
from crewai import Agent
from tools.gmail_tool import GmailTool
from tools.hubspot_tool import HubSpotTool
from tools.supabase_tool import SupabaseTool
from utils.logger import logger
from utils.security import SecurityManager

class QualityControllerAgent(Agent):
    def __init__(self):
        super().__init__(
            role='Quality Control Specialist',
            goal='Review and improve generated responses for accuracy, tone, and completeness',
            backstory='You ensure all outgoing responses meet quality standards and maintain brand voice.',
            tools=[GmailTool(), HubSpotTool(), SupabaseTool()],
            verbose=True
        )
    
    def review_response(self, email_data: Dict[str, Any], response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Review and improve generated response"""
        try:
            logger.info("Reviewing response quality", email_id=email_data['id'])
            
            # Perform quality checks
            quality_checks = self._perform_quality_checks(email_data, response_data)
            
            # Calculate overall quality score
            quality_score = self._calculate_quality_score(quality_checks)
            
            # Improve response if needed
            improved_response = response_data['response_content']
            if quality_score < 0.8:  # 80% threshold
                improved_response = self._improve_response(
                    email_data, response_data, quality_checks
                )
            
            # Determine if escalation is needed
            escalation_needed = self._determine_escalation_need(
                email_data, response_data, quality_score
            )
            
            quality_result = {
                'email_id': email_data['id'],
                'original_response': response_data['response_content'],
                'improved_response': improved_response,
                'quality_score': quality_score,
                'quality_checks': quality_checks,
                'escalation_needed': escalation_needed,
                'reviewed_at': datetime.utcnow().isoformat()
            }
            
            # Update database with quality review results
            supabase_tool = SupabaseTool()
            supabase_tool._run("update_email",
                              email_id=email_data['id'],
                              update_data={
                                  'final_response': improved_response,
                                  'quality_score': quality_score,
                                  'quality_checks': quality_checks,
                                  'escalation_needed': escalation_needed
                              })
            
            logger.info("Quality review completed",
                       email_id=email_data['id'],
                       quality_score=quality_score,
                       escalation_needed=escalation_needed)
            
            return quality_result
            
        except Exception as e:
            logger.error("Failed to review response quality",
                        email_id=email_data['id'],
                        error=str(e))
            raise EmailProcessingError(f"Failed to review response quality: {e}")
    
    def _perform_quality_checks(self, email_data: Dict[str, Any], response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform various quality checks on the response"""
        response_content = response_data['response_content']
        email_content = email_data['body']
        
        checks = {
            'grammar_spelling': self._check_grammar_spelling(response_content),
            'tone_appropriateness': self._check_tone_appropriateness(response_content, email_data),
            'content_completeness': self._check_content_completeness(response_content, email_content),
            'brand_voice': self._check_brand_voice(response_content),
            'accuracy': self._check_accuracy(response_content, email_data),
            'professionalism': self._check_professionalism(response_content),
            'action_clarity': self._check_action_clarity(response_content)
        }
        
        return checks
    
    def _check_grammar_spelling(self, response_content: str) -> Dict[str, Any]:
        """Check for grammar and spelling errors"""
        # This is a simplified check
        # In production, use a proper grammar checking service
        
        error_indicators = ['teh', 'recieve', 'occured', 'seperate', 'definately']
        error_count = sum(1 for indicator in error_indicators if indicator in response_content.lower())
        
        return {
            'passed': error_count == 0,
            'score': max(0, 1 - (error_count * 0.2)),
            'issues': [] if error_count == 0 else [f"Potential spelling error: {indicator}" for indicator in error_indicators if indicator in response_content.lower()]
        }
    
    def _check_tone_appropriateness(self, response_content: str, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if tone is appropriate for the email context"""
        # Analyze email sentiment
        email_sentiment = self._analyze_sentiment(email_data['body'])
        
        # Check response tone matches email sentiment
        response_sentiment = self._analyze_sentiment(response_content)
        
        # Simple tone matching logic
        if email_sentiment == 'negative' and response_sentiment == 'positive':
            return {
                'passed': True,
                'score': 0.9,
                'issues': []
            }
        elif email_sentiment == 'positive' and response_sentiment == 'negative':
            return {
                'passed': False,
                'score': 0.3,
                'issues': ['Response tone does not match email sentiment']
            }
        else:
            return {
                'passed': True,
                'score': 0.8,
                'issues': []
            }
    
    def _check_content_completeness(self, response_content: str, email_content: str) -> Dict[str, Any]:
        """Check if response addresses all points in the email"""
        # Extract questions from email
        email_questions = self._extract_questions(email_content)
        
        # Check if response addresses each question
        addressed_questions = 0
        for question in email_questions:
            if self._is_question_addressed(question, response_content):
                addressed_questions += 1
        
        completeness_score = addressed_questions / len(email_questions) if email_questions else 1.0
        
        return {
            'passed': completeness_score >= 0.8,
            'score': completeness_score,
            'issues': [] if completeness_score >= 0.8 else ['Not all questions addressed']
        }
    
    def _check_brand_voice(self, response_content: str) -> Dict[str, Any]:
        """Check if response maintains brand voice"""
        brand_keywords = ['professional', 'helpful', 'clear', 'concise']
        brand_violations = ['robotic', 'overly formal', 'casual slang']
        
        # Simple check for brand voice
        violations = []
        for violation in brand_violations:
            if violation in response_content.lower():
                violations.append(f"Brand voice violation: {violation}")
        
        return {
            'passed': len(violations) == 0,
            'score': max(0, 1 - (len(violations) * 0.3)),
            'issues': violations
        }
    
    def _check_accuracy(self, response_content: str, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for factual accuracy"""
        # This is a simplified check
        # In production, use fact-checking services
        
        # Check for common inaccuracies
        inaccuracies = []
        
        # Check if response makes promises it shouldn't
        if "guarantee" in response_content.lower() and "service" in response_content.lower():
            inaccuracies.append("Making service guarantees without authority")
        
        # Check for incorrect information
        if "24/7 support" in response_content.lower():
            inaccuracies.append("Incorrect information about support hours")
        
        return {
            'passed': len(inaccuracies) == 0,
            'score': max(0, 1 - (len(inaccuracies) * 0.5)),
            'issues': inaccuracies
        }
    
    def _check_professionalism(self, response_content: str) -> Dict[str, Any]:
        """Check for professionalism"""
        unprofessional_phrases = ['lol', 'omg', 'hey guys', 'what\'s up']
        
        violations = []
        for phrase in unprofessional_phrases:
            if phrase in response_content.lower():
                violations.append(f"Unprofessional phrase: {phrase}")
        
        return {
            'passed': len(violations) == 0,
            'score': max(0, 1 - (len(violations) * 0.3)),
            'issues': violations
        }
    
    def _check_action_clarity(self, response_content: str) -> Dict[str, Any]:
        """Check if response has clear action items"""
        action_indicators = ['please', 'you should', 'next steps', 'we will', 'i will']
        
        has_action_items = any(indicator in response_content.lower() for indicator in action_indicators)
        
        return {
            'passed': has_action_items,
            'score': 0.9 if has_action_items else 0.5,
            'issues': [] if has_action_items else ['No clear action items']
        }
    
    def _calculate_quality_score(self, quality_checks: Dict[str, Any]) -> float:
        """Calculate overall quality score"""
        scores = [check['score'] for check in quality_checks.values()]
        return sum(scores) / len(scores) if scores else 0.0
    
    def _improve_response(self, email_data: Dict[str, Any], response_data: Dict[str, Any], quality_checks: Dict[str, Any]) -> str:
        """Improve response based on quality checks"""
        improved_response = response_data['response_content']
        
        # Fix grammar issues
        if not quality_checks['grammar_spelling']['passed']:
            improved_response = self._fix_grammar_issues(improved_response)
        
        # Improve tone
        if not quality_checks['tone_appropriateness']['passed']:
            improved_response = self._adjust_tone(improved_response, email_data)
        
        # Add missing content
        if not quality_checks['content_completeness']['passed']:
            improved_response = self._add_missing_content(improved_response, email_data)
        
        # Ensure professionalism
        if not quality_checks['professionalism']['passed']:
            improved_response = self._ensure_professionalism(improved_response)
        
        # Add clear action items
        if not quality_checks['action_clarity']['passed']:
            improved_response = self._add_action_items(improved_response)
        
        return improved_response
    
    def _determine_escalation_need(self, email_data: Dict[str, Any], response_data: Dict[str, Any], quality_score: float) -> bool:
        """Determine if human escalation is needed"""
        # Escalate if quality score is too low
        if quality_score < 0.6:
            return True
        
        # Escalate for sensitive topics
        sensitive_keywords = ['legal', 'lawsuit', 'complaint', 'refund', 'cancel']
        email_content = email_data['body'].lower()
        
        if any(keyword in email_content for keyword in sensitive_keywords):
            return True
        
        # Escalate for executive communications
        if 'ceo' in email_data['from'].lower() or 'executive' in email_data['from'].lower():
            return True
        
        return False
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'happy', 'pleased', 'thank you']
        negative_words = ['bad', 'terrible', 'awful', 'unhappy', 'disappointed', 'angry']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _extract_questions(self, text: str) -> List[str]:
        """Extract questions from text"""
        import re
        
        # Simple question extraction
        questions = re.findall(r'[^.!?]*\?', text)
        return [q.strip() for q in questions if q.strip()]
    
    def _is_question_addressed(self, question: str, response: str) -> bool:
        """Check if a question is addressed in the response"""
        # Simple keyword matching
        question_words = question.lower().split()
        response_lower = response.lower()
        
        # Check if key question words appear in response
        return any(word in response_lower for word in question_words if len(word) > 3)
    
    def _fix_grammar_issues(self, text: str) -> str:
        """Fix basic grammar issues"""
        # This is a simplified implementation
        # In production, use a proper grammar correction service
        
        # Fix common errors
        text = text.replace('teh ', 'the ')
        text = text.replace(' recieve ', ' receive ')
        text = text.replace(' occured ', ' occurred ')
        text = text.replace(' seperate ', ' separate ')
        text = text.replace(' definately ', ' definitely ')
        
        return text
    
    def _adjust_tone(self, text: str, email_data: Dict[str, Any]) -> str:
        """Adjust tone to match email context"""
        # This is a simplified implementation
        # In production, use more sophisticated tone adjustment
        
        email_sentiment = self._analyze_sentiment(email_data['body'])
        
        if email_sentiment == 'negative':
            # Add empathetic phrases
            if not any(phrase in text.lower() for phrase in ['sorry', 'understand', 'apologize']):
                text = "I'm sorry to hear about your experience. " + text
        
        return text
    
    def _add_missing_content(self, text: str, email_data: Dict[str, Any]) -> str:
        """Add missing content to address all email points"""
        # This is a simplified implementation
        # In production, use more sophisticated content analysis
        
        email_questions = self._extract_questions(email_data['body'])
        
        for question in email_questions:
            if not self._is_question_addressed(question, text):
                text += f"\n\nRegarding your question about \"{question}\", I'd like to add that..."
        
        return text
    
    def _ensure_professionalism(self, text: str) -> str:
        """Ensure professional language"""
        # Replace unprofessional phrases
        replacements = {
            'lol': '',
            'omg': '',
            'hey guys': 'Hello',
            'what\'s up': 'How are you'
        }
        
        for unprofessional, professional in replacements.items():
            text = text.replace(unprofessional, professional)
        
        return text
    
    def _add_action_items(self, text: str) -> str:
        """Add clear action items"""
        if not any(phrase in text.lower() for phrase in ['please', 'next steps', 'will']):
            text += "\n\nNext steps: I will follow up with you within 24 hours."
        
        return text