class Message:
    def __init__(self, text, color=(200, 200, 200)):
        self.text = text
        self.color = color


class MessageLog:
    def __init__(self, height, panel_size):
        self.messages = []
        self.height = height
        self.view_pointer = 0
        self.message_panel_size = panel_size
    
    def add_message(self, message, color=(200, 200, 200)):
        # wordwrap later
        self.messages.append(Message(message, color))
        if len(self.messages) > self.height:
            del self.messages[0]
        if self.message_panel_size < len(self.messages) <= self.height:
            self.adjust_view(1)
        
        print('added message({} total), pointer now: {}'.format(len(self.messages), self.view_pointer))

    def adjust_view(self, amount):
        self.view_pointer += amount
        if self.view_pointer > self.height - self.message_panel_size:
            self.view_pointer = self.height - self.message_panel_size
        if self.view_pointer < 0:
            self.view_pointer = 0
