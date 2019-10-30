from database import DatabaseConnection


class UserService():

    def __init__(self):

        self.db = DatabaseConnection()

        self.collection = "users"

    def authenticate(self, username, password):

        user = self.db.findOne(self.collection, {"username": username})

        print(user)

        print(type(user))

        if user["password"] == password:

            return True

        else:

            return False

    def authorize(self, sid):

        session = self.db.findOne("sessions", {"sid": sid})

        if session:

            return session["username"]

        else:

            return False

    def getFirstName(self, username):

        user = self.db.findOne(self.collection, {"username": username})

        return user["firstName"]

