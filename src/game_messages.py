class Message:
    def __init__(self, text, color=(200, 200, 200)):
        """
        Holds a message, and that message's color
        :param text: the text of the message
        :param color: default color value of the text (basic text color)
        """
        self.text = text
        self.color = color


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

    def unpack(self, details: list, color: tuple):
        """
        add a list of messages all at once, all the same color
        :param details: list of messages
        :param color: color of messages
        :return: None
        """
        for detail in details:
            self.add_message(detail, color)
