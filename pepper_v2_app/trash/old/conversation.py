def conversation(user_text: str, assistant_text: str, history):
    
    user_msg = {'role': 'user', 'content': user_text}
    assistant_msg = {'role': 'assistant', 'content': assistant_text}
    history.append(user_msg)
    history.append(assistant_msg)
    
    return history
