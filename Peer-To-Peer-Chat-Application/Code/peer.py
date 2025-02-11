'''
    ##  Implementation of peer
    ##  Each peer has a client and a server side that runs on different threads
    ##  150114822 - Eren Ulaş
'''

from socket import *
import threading
import time
import select
import logging
from hashing import Hashing
import colorama

hashing = Hashing()

# Server side of peer
class PeerServer(threading.Thread):


    # Peer server initialization
    def __init__(self, username,color, peerServerPort,ChatRoomName):
        threading.Thread.__init__(self)
        # keeps the username of the peer
        self.username = username
        #color of peer
        self.color = color
        # tcp socket for peer server
        self.tcpServerSocket = socket(AF_INET, SOCK_STREAM)
        # port number of the peer server
        self.peerServerPort = peerServerPort
        # if 1, then user is already chatting with someone
        # if 0, then user is not chatting with anyone
        self.isChatRequested = 0
        # keeps the socket for the peer that is connected to this peer
        self.connectedPeerSocket = None
        # keeps the ip of the peer that is connected to this peer's server
        self.connectedPeerIP = None
        # keeps the port number of the peer that is connected to this peer's server
        self.connectedPeerPort = None
        # online status of the peer
        self.isOnline = True
        # keeps the username of the peer that this peer is chatting with
        self.chattingClientName = None
        # Check whether the user is in a class room or not
        if ChatRoomName == None:
            self.inChatRoom = False
        else:
            self.inChatRoom = True

        #return color back to white
        colorama.init(autoreset=True)
    

    # main method of the peer server thread
    def run(self):

        print("Peer server started...")    

        # gets the ip address of this peer
        # first checks to get it for windows devices
        # if the device that runs this application is not windows
        # it checks to get it for macos devices
        hostname=gethostname()
        try:
            self.peerServerHostname=gethostbyname(hostname)
        except gaierror:
            import netifaces as ni
            self.peerServerHostname = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']

        # ip address of this peer
        #self.peerServerHostname = 'localhost'
        # socket initializations for the server of the peer
        self.tcpServerSocket.bind((self.peerServerHostname, self.peerServerPort))
        self.tcpServerSocket.listen(4)
        # inputs sockets that should be listened
        inputs = [self.tcpServerSocket]
        # server listens as long as there is a socket to listen in the inputs list and the user is online
        while inputs and self.isOnline:
            # monitors for the incoming connections
            try:
                readable, writable, exceptional = select.select(inputs, [], [])
                # If a server waits to be connected enters here
                for s in readable:
                    # if the socket that is receiving the connection is 
                    # the tcp socket of the peer's server, enters here
                    if s is self.tcpServerSocket:
                        # accepts the connection, and adds its connection socket to the inputs list
                        # so that we can monitor that socket as well
                        connected, addr = s.accept()
                        connected.setblocking(0)
                        inputs.append(connected)
                        # if the user is not chatting, then the ip and the socket of
                        # this peer is assigned to server variables
                        if self.isChatRequested == 0:
                            if self.inChatRoom == False:
                                print(self.username + " is connected from " + str(addr))
                            self.connectedPeerSocket = connected
                            self.connectedPeerIP = addr[0]
                    # if the socket that receives the data is the one that
                    # is used to communicate with a connected peer, then enters here
                    else:
                        # message is received from connected peer
                        messageReceived = s.recv(1024).decode()
                        FindIndication = messageReceived.find("ChatRoom ")
                        if (FindIndication != -1):
                            if (len(messageReceived) != 0):
                                messageReceived = messageReceived.replace("ChatRoom ", "")
                                messageReceived = messageReceived.replace(":", "->")
                                messageReceived = messageReceived.split()
                                WordReceived =""
                                for i in range(len(messageReceived)-1):
                                    WordReceived = WordReceived + " " + messageReceived[i]
                                print('\n' + messageReceived[-1] + WordReceived)
                                continue
                        # logs the received message
                        logging.info("Received from " + str(self.connectedPeerIP) + " -> " + str(messageReceived))
                        # if message is a request message it means that this is the receiver side peer server
                        # so evaluate the chat request
                        if len(messageReceived) > 11 and messageReceived[:12] == "CHAT-REQUEST":
                            # text for proper input choices is printed however OK or REJECT is taken as input in main process of the peer
                            # if the socket that we received the data belongs to the peer that we are chatting with,
                            # enters here
                            if s is self.connectedPeerSocket:
                                # parses the message
                                messageReceived = messageReceived.split()
                                # gets the port of the peer that sends the chat request message
                                self.connectedPeerPort = int(messageReceived[1])
                                # gets the username of the peer sends the chat request message
                                self.chattingClientName = messageReceived[2]
                                # prints prompt for the incoming chat request
                                print("Incoming chat request from " + self.chattingClientName + " >> ")
                                print("Enter OK to accept or REJECT to reject:  ")
                                # makes isChatRequested = 1 which means that peer is chatting with someone
                                self.isChatRequested = 1
                            # if the socket that we received the data does not belong to the peer that we are chatting with
                            # and if the user is already chatting with someone else(isChatRequested = 1), then enters here
                            elif s is not self.connectedPeerSocket and self.isChatRequested == 1:
                                # sends a busy message to the peer that sends a chat request when this peer is 
                                # already chatting with someone else
                                message = "BUSY"
                                s.send(message.encode())
                                # remove the peer from the inputs list so that it will not monitor this socket
                                inputs.remove(s)
                        # if an OK message is received then ischatrequested is made 1 and then next messages will be shown to the peer of this server
                        elif messageReceived == "OK":
                            self.isChatRequested = 1
                        # if an REJECT message is received then ischatrequested is made 0 so that it can receive any other chat requests
                        elif messageReceived == "REJECT":
                            self.isChatRequested = 0
                            inputs.remove(s)
                        # if a message is received, and if this is not a quit message ':q' and 
                        # if it is not an empty message, show this message to the user
                        elif messageReceived[:2] != ":q" and len(messageReceived)!= 0:
                            print(self.color + self.chattingClientName + " -> " + messageReceived)
                        # if the message received is a quit message ':q',
                        # makes ischatrequested 1 to receive new incoming request messages
                        # removes the socket of the connected peer from the inputs list
                        elif messageReceived[:2] == ":q" and self.inChatRoom == False:
                            self.isChatRequested = 0
                            inputs.clear()
                            inputs.append(self.tcpServerSocket)
                            # connected peer ended the chat
                            if len(messageReceived) == 2:
                                if self.inChatRoom == False:
                                    print(f"{colorama.Fore.RED}User you're chatting with started the chat")
                                    print(f"{colorama.Fore.RED}Press enter to quit the chat: ")

                        # if the message is an empty one, then it means that the
                        # connected user suddenly ended the chat(an error occurred)
                        elif len(messageReceived) == 0 and self.inChatRoom == False:
                            self.isChatRequested = 0
                            inputs.clear()
                            inputs.append(self.tcpServerSocket)
                            print(f"{colorama.Fore.RED}User you're chatting with suddenly ended the chat")
                            print(f"{colorama.Fore.RED}Press enter if you want to exit the chat: ")

            # handles the exceptions, and logs them
            except OSError as oErr:
                logging.error("OSError: {0}".format(oErr))
            except ValueError as vErr:
                logging.error("ValueError: {0}".format(vErr))
            

# Client side of peer
class PeerClient(threading.Thread):
    # variable initializations for the client side of the peer
    def __init__(self, ipToConnect, portToConnect, username, peerServer, responseReceived,message =None,receiver=None,color ='None'):
        threading.Thread.__init__(self)
        # keeps the ip address of the peer that this will connect
        self.ipToConnect = ipToConnect
        # keeps the username of the peer
        self.username = username
        # keeps the port number that this client should connect
        self.portToConnect = portToConnect
        # client side tcp socket initialization
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        # keeps the server of this client
        self.peerServer = peerServer
        # keeps the phrase that is used when creating the client
        # if the client is created with a phrase, it means this one received the request
        # this phrase should be none if this is the client of the requester peer
        self.responseReceived = responseReceived
        # keeps if this client is ending the chat or not
        self.isEndingChat = False
        self.message = message
        self.receiver = receiver
        self.color =color

    # main method of the peer client thread
    def run(self):
        if self.message == None:
            print("Peer client started...")
        # connects to the server of other peer
        self.tcpClientSocket.connect((self.ipToConnect, self.portToConnect))
        # if the server of this peer is not connected by someone else and if this is the requester side peer client then enters here
        if self.message != None:
            #self.peerServer.isChatRequested = 1
            RequestMessage = "ChatRoom " + self.username + " : " + self.message + " " + self.color
            self.tcpClientSocket.send(RequestMessage.encode())
        elif self.peerServer.isChatRequested == 0 and self.responseReceived == None:
            # composes a request message and this is sent to server and then this waits a response message from the server this client connects
            requestMessage = "CHAT-REQUEST " + str(self.peerServer.peerServerPort)+ " " + self.username
            # logs the chat request sent to other peer
            logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + requestMessage)
            # sends the chat request
            self.tcpClientSocket.send(requestMessage.encode())
            print("Request message " + requestMessage + " is sent...")
            # received a response from the peer which the request message is sent to
            self.responseReceived = self.tcpClientSocket.recv(1024).decode()
            # logs the received message
            logging.info("Received from " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + self.responseReceived)
            print("Response is " + self.responseReceived)
            # parses the response for the chat request
            self.responseReceived = self.responseReceived.split()
            # if response is ok then incoming messages will be evaluated as client messages and will be sent to the connected server
            if self.responseReceived[0] == "OK":
                # changes the status of this client's server to chatting
                self.peerServer.isChatRequested = 1
                # sets the server variable with the username of the peer that this one is chatting
                self.peerServer.chattingClientName = self.responseReceived[1]
                # as long as the server status is chatting, this client can send messages
                while self.peerServer.isChatRequested == 1:
                    # message input prompt
                    messageSent = input()
                    # sends the message to the connected peer, and logs it
                    self.tcpClientSocket.send(messageSent.encode())
                    logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + messageSent)
                    # if the quit message is sent, then the server status is changed to not chatting
                    # and this is the side that is ending the chat
                    if messageSent == ":q":
                        self.peerServer.isChatRequested = 0
                        self.isEndingChat = True
                        break
                # if peer is not chatting, checks if this is not the ending side
                if self.peerServer.isChatRequested == 0:
                    if not self.isEndingChat:
                        # tries to send a quit message to the connected peer
                        # logs the message and handles the exception
                        try:
                            self.tcpClientSocket.send(":q ending-side".encode())
                            logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> :q")
                        except BrokenPipeError as bpErr:
                            logging.error("BrokenPipeError: {0}".format(bpErr))
                    # closes the socket
                    self.responseReceived = None
                    self.tcpClientSocket.close()
            # if the request is rejected, then changes the server status, sends a reject message to the connected peer's server
            # logs the message and then the socket is closed       
            elif self.responseReceived[0] == "REJECT":
                self.peerServer.isChatRequested = 0
                print("client of requester is closing...")
                self.tcpClientSocket.send("REJECT".encode())
                logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> REJECT")
                self.tcpClientSocket.close()
            # if a busy response is received, closes the socket
            elif self.responseReceived[0] == "BUSY":
                print("Receiver peer is busy")
                self.tcpClientSocket.close()
        # if the client is created with OK message it means that this is the client of receiver side peer
        # so it sends an OK message to the requesting side peer server that it connects and then waits for the user inputs.
        elif self.responseReceived == "OK":
            # server status is changed
            self.peerServer.isChatRequested = 1
            # ok response is sent to the requester side
            okMessage = "OK"
            self.tcpClientSocket.send(okMessage.encode())
            logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + okMessage)
            print("Client with OK message is created... and sending messages")
            # client can send messsages as long as the server status is chatting
            while self.peerServer.isChatRequested == 1:
                # input prompt for user to enter message
                messageSent = input()
                self.tcpClientSocket.send(messageSent.encode())
                logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + messageSent)
                # if a quit message is sent, server status is changed
                if messageSent == ":q":
                    self.peerServer.isChatRequested = 0
                    self.isEndingChat = True
                    break
            # if server is not chatting, and if this is not the ending side
            # sends a quitting message to the server of the other peer
            # then closes the socket
            if self.peerServer.isChatRequested == 0:
                if not self.isEndingChat:
                    self.tcpClientSocket.send(":q ending-side".encode())
                    logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> :q")
                self.responseReceived = None
                self.tcpClientSocket.close()
                

# main process of the peer
class peerMain:

    # peer initializations
    def __init__(self):
        # ip address of the registry
        self.registryName = input("Enter IP address of registry: ")
        #self.registryName = 'localhost'
        # port number of the registry
        self.registryPort = 15600
        # tcp socket connection to registry
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpClientSocket.connect((self.registryName,self.registryPort))
        # initializes udp socket which is used to send hello messages
        self.udpClientSocket = socket(AF_INET, SOCK_DGRAM)
        # udp port of the registry
        self.registryUDPPort = 15500
        # login info of the peer
        self.loginCredentials = (None, None)
        # online status of the peer
        self.isOnline = False
        # server port number of this peer
        self.peerServerPort = None
        # server of this peer
        self.peerServer = None
        # client of this peer
        self.peerClient = None
        # timer initialization
        self.timer = None
        # Track the users in the Chat Room
        self.ChatRoomUsers = []
        # Track the name of the Chat Room
        self.ChatRoomName = ''
        
        choice = "0"
        initialFlag = True
        # log file initialization
        logging.basicConfig(filename="peer.log", level=logging.INFO)
        # as long as the user is not logged out, asks to select an option in the menu
        while choice != "3":

            if (initialFlag):
                print("*********************************************************************************\n*\t\t\t\t\t\t\t\t\t        *\n*\t\t\t WELCOME TO CHAT ROOMS\t\t\t\t\t*\n*\t\t\t     \t\t\t\t\t\t        *\n*********************************************************************************")
                choice = input(f"{colorama.Fore.MAGENTA}Choose: \nCreate account: 1\nLogin: 2\n")
                if choice == "2":
                    initialFlag = False
            else:
                choice = input(f"{colorama.Fore.MAGENTA}Choose: \nCreate account: 1\nLogin: 2\nLogout: 3\nSearch: 4\nStart a chat: 5\nShow online users: 6\nCreate Group: 7\nJoin Group: 8\n")

            # if choice is 1, creates an account with the username
            # and password entered by the user
            if choice == "1":
                username = input(f"{colorama.Fore.BLUE}username: ")
                password = input(f"{colorama.Fore.BLUE}password: ")

                self.createAccount(username, password)


            # if choice is 2 and user is not logged in, asks for the username
            # and the password to login
            elif choice == "2" and not self.isOnline:
                username = input(f"{colorama.Fore.BLUE}username: ")
                password = input(f"{colorama.Fore.BLUE}password: ")
                # asks for the port number for server's tcp socket
                peerServerPort = int(input(f"{colorama.Fore.BLUE}Enter a port number for peer server: "))
                
                status = self.login(username, password, peerServerPort)
                # is user logs in successfully, peer variables are set
                if status == 1:
                    self.isOnline = True
                    color = self.get_color(username)
                    self.loginCredentials = (username, password,color)
                    self.peerServerPort = peerServerPort
                    # creates the server thread for this peer, and runs it
                    self.peerServer = PeerServer(self.loginCredentials[0],self.loginCredentials[2], self.peerServerPort,self.ChatRoomName)
                    self.peerServer.start()
                    # hello message is sent to registry
                    self.sendHelloMessage()
                else:
                    initialFlag = True

            # if choice is 3 and user is logged in, then user is logged out
            # and peer variables are set, and server and client sockets are closed
            elif choice == "3" and self.isOnline:
                self.logout(1)
                self.isOnline = False
                self.loginCredentials = (None, None)
                self.peerServer.isOnline = False
                self.peerServer.tcpServerSocket.close()
                if self.peerClient is not None:
                    self.peerClient.tcpClientSocket.close()
                print(f"{colorama.Fore.RED}Logged out successfully")
            # is peer is not logged in and exits the program
            elif choice == "3":
                self.logout(2)

            # if choice is 4 and user is online, then user is asked
            # for a username that is wanted to be searched
            elif choice == "4" and self.isOnline:
                username = input(f"{colorama.Fore.GREEN}Username to be searched: ")
                searchStatus = self.searchUser(username)
                # if user is found its ip address is shown to user
                if searchStatus != None and searchStatus != 0:
                    print("IP address of " + username + " is " + searchStatus)

            # if choice is 5 and user is online, then user is asked
            # to enter the username of the user that is wanted to be chatted
            elif choice == "5" and self.isOnline:
                username = input(f"{colorama.Fore.GREEN}Enter the username of user to start chat: ")
                searchStatus = self.searchUser(username)
                # if searched user is found, then its ip address and port number is retrieved
                # and a client thread is created
                # main process waits for the client thread to finish its chat
                if searchStatus != None:
                    searchStatus = searchStatus.split(":")
                    self.peerClient = PeerClient(searchStatus[0], int(searchStatus[1]) , self.loginCredentials[0], self.peerServer, None)
                    self.peerClient.start()
                    self.peerClient.join()

            # choice 6 to display usernames of all online users
            elif choice == "6":
                print("\n********************************************************")
                print("\t\t Online Users\n")
                self.get_users()
                print("********************************************************\n")

            #choice 7 to create a new Chat Room
            elif choice == "7" and self.isOnline:
                ChatRoom_Name = input("Create new Chat Room: ")
                self.createChatRoom(ChatRoom_Name)

            #choice 8 to join an existing Chat Room
            elif choice == "8" and self.isOnline:
                ChatRoom_Name = input("Join Chat Room: ")
                self.joinChatRoom(ChatRoom_Name)
                while self.inChatRoom:
                    message = input()
                    self.ChatRoomUsers = self.updateChatRoomUsersList(ChatRoom_Name)
                    if self.ChatRoomUsers is not None:
                        
                        if message == ":q":
                            self.exitChatRoom(username,ChatRoom_Name)
                            break
                        for user in self.ChatRoomUsers:
                            # Don't send a message to the same user
                            if user != username:
                                self.initiate_ChatRoom(user, message)

            # if this is the receiver side then it will get the prompt to accept an incoming request during the main loop
            # that's why response is evaluated in main process not the server thread even though the prompt is printed by server
            # if the response is ok then a client is created for this peer with the OK message and that's why it will directly
            # sent an OK message to the requesting side peer server and waits for the user input
            # main process waits for the client thread to finish its chat
            elif choice == "OK" and self.isOnline:
                okMessage = "OK " + self.loginCredentials[0]
                logging.info("Send to " + self.peerServer.connectedPeerIP + " -> " + okMessage)
                self.peerServer.connectedPeerSocket.send(okMessage.encode())
                self.peerClient = PeerClient(self.peerServer.connectedPeerIP, self.peerServer.connectedPeerPort , self.loginCredentials[0], self.peerServer, "OK")
                self.peerClient.start()
                self.peerClient.join()
            # if user rejects the chat request then reject message is sent to the requester side
            elif choice == "REJECT" and self.isOnline:
                self.peerServer.connectedPeerSocket.send("REJECT".encode())
                self.peerServer.isChatRequested = 0
                logging.info("Send to " + self.peerServer.connectedPeerIP + " -> REJECT")
            # if choice is cancel timer for hello message is cancelled
            elif choice == "CANCEL":
                self.timer.cancel()
                break


        # if main process is not ended with cancel selection
        # socket of the client is closed
        if choice != "CANCEL":
            self.tcpClientSocket.close()

    # account creation function
    def createAccount(self, username, password):
        # join message to create an account is composed and sent to registry
        # if response is success then informs the user for account creation
        # if response is exist then informs the user for account existence
        message = "JOIN " + username + " " + password
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
        if response == "join-success":
            print(f"{colorama.Fore.RED}Account {username} created...")
        elif response == "join-exist":
            print(f"{colorama.Fore.RED}choose another username or login...")

    # login function
    def login(self, username, password, peerServerPort):
        # a login message is composed and sent to registry
        # an integer is returned according to each response
        # Added encoding to the password
        message = "LOGIN " + username + " " + hashing.encodePassword(password) + " " + str(peerServerPort)
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
        if response == "login-success":
            print(f"{colorama.Fore.RED}Logged in successfully...")
            return 1
        elif response == "login-account-not-exist":
            print(f"{colorama.Fore.RED}Account does not exist...")
            return 0
        elif response == "login-online":
            print(f"{colorama.Fore.RED}Account is already online...")
            return 2
        elif response == "login-wrong-password":
            print(f"{colorama.Fore.RED}Wrong password...")
            return 3
    
    # logout function
    def logout(self, option):
        # a logout message is composed and sent to registry
        # timer is stopped
        if option == 1:
            message = "LOGOUT " + self.loginCredentials[0]
            self.timer.cancel()
        else:
            message = "LOGOUT"
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        

    # function for searching an online user
    def searchUser(self, username):
        # a search message is composed and sent to registry
        # custom value is returned according to each response
        # to this search message
        message = "SEARCH " + username
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        logging.info("Received from " + self.registryName + " -> " + " ".join(response))
        if response[0] == "search-success":
            return response[1]
        elif response[0] == "search-user-not-online":
            print(username + " is not online...")
            return 0
        elif response[0] == "search-user-not-found":
            print(username + " is not found")
            return None
    
    # function for sending hello message
    # a timer thread is used to send hello messages to udp socket of registry
    def sendHelloMessage(self):
        message = "HELLO " + self.loginCredentials[0]
        logging.info("Send to " + self.registryName + ":" + str(self.registryUDPPort) + " -> " + message)
        self.udpClientSocket.sendto(message.encode(), (self.registryName, self.registryUDPPort))
        self.timer = threading.Timer(1, self.sendHelloMessage)
        self.timer.start()

    #print list of online users
    def get_users(self):
        
        if self.isOnline:
            message = "List"
            self.tcpClientSocket.send(message.encode())
            response = self.tcpClientSocket.recv(1024).decode()
            response=response.split()
            for i in range(len(response)):
              print(response[i])
        else:
           print(f"{colorama.Fore.RED}you didn't log in\n")

    # gets color assigned to current online user
    def get_color(self,username):
        message = "Color " + username
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        return response[0]

    #Function for creating a Chat Room
    def createChatRoom(self, ChatRoom_Name):
        message = "Create_ChatRoom " + ChatRoom_Name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        if response[0] == "ChatRoom-Exist":
            print(f"{colorama.Fore.RED}This Chat Room {ChatRoom_Name} already exist ... Choose another name")
            return 0
        elif response[0] == "ChatRoom-Created-Successfully":
            print(f"{colorama.Fore.YELLOW}The Chat Room {ChatRoom_Name} is created Successfully ")
            self.inChatRoom = True

    #Function for Joining a Chat Room
    def joinChatRoom(self, ChatRoom_Name):
        message = "Join-ChatRoom " + ChatRoom_Name + " " + self.loginCredentials[0]
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        if response[0] == "ChatRoom_Not_Found":
            print(f"{colorama.Fore.YELLOW} Chatroom {ChatRoom_Name} is not found")
            return 0
        elif response[0] == "ChatRoom_Found":
            print(f"{colorama.Fore.YELLOW} Joined Chatroom {ChatRoom_Name} successfully\n")
            self.inChatRoom = True
            self.ChatRoomName = ChatRoom_Name
            #This for loop is for showing the users in Chat Room
            print(f"{colorama.Fore.CYAN}The current users in this Chatroom {ChatRoom_Name} are : \n")
            for user in (response[1:]):
                print(f"{colorama.Fore.CYAN}{user}")
                self.ChatRoomUsers.append(user)
            if self.ChatRoomUsers != None:
                for user in self.ChatRoomUsers:
                    self.initiate_ChatRoom(user,"User " + self.loginCredentials[0]  + " has joined " + ChatRoom_Name + " ChatRoom")

    def updateChatRoomUsersList(self,ChatRoom_Name):
        if self.isOnline:
            #Send a request to the registry to get the Chat Room  Users update
            message = "Get_ChatRoom_UsersList " + ChatRoom_Name
            self.tcpClientSocket.send(message.encode())
            response = self.tcpClientSocket.recv(1024).decode().split()
            #Process the received chat room list
        if response[0] == "ChatRoom_Userlist":
            updatedChatRoomUsersList = response[1:]
            return updatedChatRoomUsersList

    def initiate_ChatRoom(self,username,message):
        SearchStatus = self.searchUser(username)
        # if searched user is found, then its ip address and port number is retrieved
        # and a client thread is created
        # main process waits for the client thread to finish its chat
        if SearchStatus is not None:
            SearchStatus = SearchStatus.split(":")
            self.peerClient = PeerClient(SearchStatus[0], int(SearchStatus[1]), self.loginCredentials[0],self.peerServer, None, message,username,self.get_color(self.loginCredentials[0]))
            self.peerClient.start()
            self.peerClient.join()

    #Exiting the chat room
    def exitChatRoom(self, username, ChatRoom_Name):
        if self.ChatRoomUsers != None:
            for user in self.ChatRoomUsers:
                self.initiate_ChatRoom(user, f"{colorama.Fore.RED}User {username} has left the room")
        message = "Exit_CHAT_ROOM " + username + " " + ChatRoom_Name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        if response[0] == "Chat_Room_Exit":
            print(f"{colorama.Fore.RED} You have left the chat room")
            self.inChatroom = False
            return 0

# peer is started
main = peerMain()