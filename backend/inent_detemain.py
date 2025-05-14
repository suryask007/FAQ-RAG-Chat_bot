
def detect_escalation_need(user_message, intent, confidence):
    """
    Determine if a conversation needs to be escalated to a human agent.
    
    Args:
        user_message: Current user message
        conversation_history: Previous messages in the conversation
        intent: Detected intent
        confidence: Confidence score for intent detection
    
    Returns:
        tuple: (needs_escalation, reason)
    """
    # Count number of exchanges
    # num_exchanges = len([m for m in conversation_history if m["role"] == "user"])
    
    # Check confidence threshold
    if confidence < 0.6:
        return True, "I'm not confident about answering this question accurately."
    
    # Check for explicit requests for human agent
    human_keywords = ["speak to human", "real person", "customer service", "agent", "representative"]
    if any(keyword in user_message.lower() for keyword in human_keywords):
        return True, "You've requested to speak with a human agent."
    
    
    
    # Check for complex intents that might need human intervention
    complex_intents = ["payment_issue", "technical_problem", "complaint"]
    if intent in complex_intents:
        return True, f"Your question about {intent.replace('_', ' ')} might need specialized assistance."
    
   
    
    return False, None
