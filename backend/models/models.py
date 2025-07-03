from flask_login import UserMixin

class EmployeeUser(UserMixin):
    def __init__(self, row):
        self.id = row.EmployeeID
        self.username = row.Username
        self.name = row.Name
        self.type = row.Type
