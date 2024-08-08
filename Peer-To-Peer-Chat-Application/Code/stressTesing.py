from pymongo import MongoClient
import db
import time 
import csv

class TestDBFunctions():

    def setUp(self):
        # Set up the database connection and create a test instance
        self.client = MongoClient('mongodb://localhost:27017/')
        #self.test_db = self.client['test_p2p-chat']
        self.db = db.DB()
        self.registeryTime = []

    def add_1000_users(self):
        # Add 1000 users to the database for testing
        f = open('dataRegister.csv' , 'w')

        # create the csv writer
        writer = csv.writer(f)

        # write a row to the csv file
        

        
        startTime = time.time()
        
        for i in range(1000):
            username = f'test_user_{i}'
            password = f'test_password_{i}'
            self.db.register(username, password)
            if i % 100 == 0 :
                self.registeryTime.append(time.time() - startTime)
           
        writer.writerow(self.registeryTime)
        totalTime = time.time() - startTime
        #Time taken to register users in database
        print("Total time to register 1000 users: " + str(totalTime))

        # close the file
        f.close()




    def logIN_1000_users(self):
        self.registeryTime = []
        # Add 1000 users to the database for testing
        f = open('dataLogin.csv' , 'w')

        # create the csv writer
        writer = csv.writer(f)

        # write a row to the csv file
        

        
        startTime = time.time()
        
        for i in range(1000):
            username = f'test_user_{i}'
            ip = '127.0.0.1'
            port = 12340 + i
            self.db.user_login(username, ip, port)
            if i % 100 == 0 :
                self.registeryTime.append(time.time() - startTime)
           
        writer.writerow(self.registeryTime)
        totalTime = time.time() - startTime
        #Time taken to register users in database
        print("Total time to login 1000 users: " + str(totalTime))

        # close the file
        f.close()




    def create_ChatRoom_1000_users(self):
        self.registeryTime = []
        # Add 1000 users to the database for testing
        f = open('dataCreateChatRoom.csv' , 'w')

        # create the csv writer
        writer = csv.writer(f)

        # write a row to the csv file
        

        
        startTime = time.time()
        
        for i in range(1000):
            chat_room_name = f'test_chat_room_{i}'
            self.db.create_ChatRoom(chat_room_name)
            if i % 100 == 0 :
                self.registeryTime.append(time.time() - startTime)
           
        writer.writerow(self.registeryTime)

        totalTime = time.time() - startTime
        #Time taken to register users in database
        print("Total time to create 1000 : " + str(totalTime))

        # close the file
        f.close()


    def Join_ChatRoom_1000_users(self):
        self.registeryTime = []
        # Add 1000 users to the database for testing
        f = open('dataJoinChatRoom.csv' , 'w')

        # create the csv writer
        writer = csv.writer(f)
        
        startTime = time.time()
        
        for i in range(1000):
            username = f'test_user_{i}'
            chat_room_name = f'test_chat_room_{i}'
            self.db.join_ChatRoom(chat_room_name, username)
            if i % 100 == 0 :
                self.registeryTime.append(time.time() - startTime)

        # write a row to the csv file   
        writer.writerow(self.registeryTime)

        totalTime = time.time() - startTime
        #Time taken to register users in database
        print("Total time for 1000 users to join 1000 chatroom: " + str(totalTime))

        # close the file
        f.close()




if __name__ == '__main__':
    tests = TestDBFunctions()
    tests.setUp()
    tests.add_1000_users()
    tests.logIN_1000_users()
    tests.create_ChatRoom_1000_users()
    tests.Join_ChatRoom_1000_users()





