class Message:
    def __init__(self, text, color=(200, 200, 200)):
        """
        Holds a message, and that message's color
        :param text: str text of the message
        :param color: tuple color value of the text
        """
        self.text = text
        self.color = color
    
    def to_json(self):
        """
        Serialize Message object to json
        :return: Serialized json of Message object
        """
        return {
            'text': self.text,
            'color': self.color
        }
    
    @staticmethod
    def from_json(json_data):
        """
        Convert serialized json back to message object
        :param json_data: Serialized json of Message object
        :return: Message object
        """
        text = json_data.get('text')
        color = json_data.get('color')
        
        return text, color


class MessageLog:
    def __init__(self, height, panel_size):
        """
        Holds the message log, max log size, current view pointer (top to display),
        and the number that can be displayed in the message panel
        :param height: maximum number of messages in the log
        :param panel_size: how many messages can be viewed in the display
        """
        self.messages = []
        self.height = height
        self.view_pointer = 0
        self.message_panel_size = panel_size
    
    def to_json(self):
        """
        Serialize MessageLog to json
        :return: Serialized json of MessageLog
        """
        return {
            'height': self.height,
            'panel_size': self.message_panel_size,
            'messages': [message.to_json() for message in self.messages]
        }
    
    @staticmethod
    def from_json(json_data):
        """
        Convert serialized json to MessageLog object with messages
        :param json_data: Serialized json of MessageLog
        :return: MessageLog object with messages
        """
        height = json_data.get('height')
        panel_size = json_data.get('panel_size')
        messages_json = json_data.get('messages')
        
        message_log = MessageLog(height=height, panel_size=panel_size)
        
        for message in messages_json:
            text, color = Message.from_json(json_data=message)
            message_log.add_message(message=text, color=color)
        
        return message_log
    
    def add_message(self, message, color=(200, 200, 200)):
        """
        Add a message to the message log
        :param message: message string
        :param color: color tuple, default to text color values
        :return: None
        """
        # wordwrap later if needed
        self.messages.append(Message(message, color))
        if len(self.messages) > self.height:
            del self.messages[0]
        if self.message_panel_size < len(self.messages) <= self.height:
            self.adjust_view(1)
    
    def adjust_view(self, amount):
        """
        Change view of the message log as per scroll of mouse
        :param amount: int amount of scroll
        :return: None
        """
        self.view_pointer += amount
        if self.view_pointer > self.height - self.message_panel_size:
            self.view_pointer = self.height - self.message_panel_size
        if self.view_pointer < 0:
            self.view_pointer = 0
    
    def reset_view(self):
        """
        Reset the view to the last message
        :return: None
        """
        self.view_pointer = len(self.messages) - self.message_panel_size
        if self.view_pointer < 0:
            self.view_pointer = 0
    
    def unpack(self, details: list, color: tuple = (200, 200, 200)):
        """
        add a list of messages all at once, all the same color
        :param details: list of messages
        :param color: color of messages
        :return: None
        """
        if details:
            for detail in details:
                self.add_message(detail, color)
