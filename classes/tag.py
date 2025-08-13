#   Name: Kayden Ye
#   Date: 30/06/2025
#   File: classes/tag.py

class Tag:
    def __init__(self, 
                 name: str):
        self.name = name

    def __str__(self):
        return f"Name: {self.name}"
    
    def __repr__(self):
        return f"'{self.name}'"

    def get_name(self):
        return self.name
    
    def set_name(self, new_name):
        self.name = new_name