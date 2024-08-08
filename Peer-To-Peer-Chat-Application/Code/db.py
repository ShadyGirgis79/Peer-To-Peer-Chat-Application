from pymongo import MongoClient
from hashing import Hashing
import random
import colorama

hashing = Hashing()

# Includes database operations
class DB:


    # db initializations
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['p2p-chat']


    # checks if an account with the username exists
    def is_account_exist(self, username):
        if len(list(self.db.accounts.find({'username': username})))> 0:
            return True
        else:
            return False
    

    # registers a user
    # Adds hashing to the password
    def register(self, username, password):
        account = {
            "username": username,
            "password": hashing.encodePassword(password)
        }
        self.db.accounts.insert_one(account)


    # retrieves the password for a given username
    def get_password(self, username):
        return self.db.accounts.find_one({"username": username})["password"]


    # checks if an account with the username online
    def is_account_online(self, username):
        if len(list(self.db.online_peers.find({"username": username}))) > 0:
            return True
        else:
            return False

    
    # logs in the user
    def user_login(self, username, ip, port):
        x= [colorama.Fore.RED,
            colorama.Fore.GREEN, 
            colorama.Fore.YELLOW,
            colorama.Fore.BLUE,
            colorama.Fore.MAGENTA,
            colorama.Fore.CYAN,
        
            (colorama.Fore.RED + colorama.Style.BRIGHT),
            (colorama.Fore.GREEN + colorama.Style.BRIGHT),
            (colorama.Fore.YELLOW + colorama.Style.BRIGHT),
            (colorama.Fore.BLUE + colorama.Style.BRIGHT),
            (colorama.Fore.MAGENTA + colorama.Style.BRIGHT),
            (colorama.Fore.CYAN + colorama.Style.BRIGHT),
        
            ]
        online_peer = {
            "username": username,
            "ip": ip,
            "port": port,
            "color" : x[random.randint(0,len(x)-1)]
        }
        self.db.online_peers.insert_one(online_peer)
    

    # logs out the user 
    def user_logout(self, username):
        self.db.online_peers.delete_one({"username": username})
    

    # retrieves the ip address and the port number of the username
    def get_peer_ip_port(self, username):
        res = self.db.online_peers.find_one({"username": username})
        return (res["ip"], res["port"])
    
     #return list of online usernames
    def get_online_users (self):
        x = self.db.online_peers.find({},{"username": 1 ,"_id" :0})
        x = list(x)
        nameList = []
        for i in range(len(x)):
            nameList.append(x[i]["username"])
        return nameList

    #get color
    def get_color(self,username):
        color = self.db.online_peers.find_one({"username" : username})["color"]
        return color

    #Create a Chat Room
    def create_ChatRoom(self, ChatRoom_Name):
        ChatRoom = {
            "ChatRoom_Name": ChatRoom_Name,
            "Participants": []
        }
        self.db.ChatRooms.insert_one(ChatRoom)

    #Join a Chat Room
    def join_ChatRoom(self , ChatRoom_Name , username):
        self.db.ChatRooms.update_one(
            {"ChatRoom_Name": ChatRoom_Name},
            {"$addToSet": {"Participants": username}}
        )

    #Checks if the Chat Room exists or not
    def does_ChatRoom_Exists(self , ChatRoom_Name):
        ChatRoom_Exists = self.db.ChatRooms.find_one({"ChatRoom_Name": ChatRoom_Name})
        if ChatRoom_Exists != None:
            return True
        else:
            return False

    #Get the participants in the Chat Room
    def get_ChatRoom_Participants(self, ChatRoom_Name):
        Participants = ''
        ChatRoom_Participants = self.db.ChatRooms.find_one({"ChatRoom_Name": ChatRoom_Name})["Participants"]
        Participants = " ".join(ChatRoom_Participants)
        return Participants

        # Remove user from chat room list

    #To remove user frmo the chat room database list
    def remove_ChatRoom_user(self, ChatRoom_Name, username):
        self.db.ChatRooms.update_one(
            {"ChatRoom_Name": ChatRoom_Name},
            {"$pull": {"Participants": username}}
        )