class Message:
    def __init__(self, text, color=(200, 200, 200)):
        self.text = text
        self.color = color


class MessageLog:
    def __init__(self, height):
        self.messages = []
        self.height = height
    
    def add_message(self, message, color=(200, 200, 200)):
        # wordwrap later
        if len(self.messages) >= self.height:
            del self.messages[0]
        
        self.messages.append(Message(message, color))
