import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow
from datetime import datetime

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['institutions', 'positions', 'experiences', 'skills','feedback', 'users','wordle', 'scores']
        
        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        ''' FILL ME IN WITH CODE THAT CREATES YOUR DATABASE TABLES.'''

        #should be in order or creation - this matters if you are using forign keys.
         
        if purge:
            for table in self.tables[::-1]:
                self.query(f"""DROP TABLE IF EXISTS {table}""")
            
        # Execute all SQL queries in the /database/create_tables directory.
        for table in self.tables:
            
            #Create each table using the .sql file in /database/create_tables directory.
            with open(data_path + f"create_tables/{table}.sql") as read_file:
                create_statement = read_file.read()
            self.query(create_statement)

            # Import the initial data
            try:
                params = []
                with open(data_path + f"initial_data/{table}.csv") as read_file:
                    scsv = read_file.read()            
                for row in csv.reader(StringIO(scsv), delimiter=','):
                    params.append(row)
            
                # Insert the data
                cols = params[0]; params = params[1:] 
                self.insertRows(table = table,  columns = cols, parameters = params)
            except:
                print('no initial data')

    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        
        # Check if there are multiple rows present in the parameters
        has_multiple_rows = any(isinstance(el, list) for el in parameters)
        keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
        # Construct the query we will execute to insert the row(s)
        query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        if has_multiple_rows:
            for p in parameters:
                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))
        else:
            query += f"""({values}) """                      
        
        insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']         
        return insert_id

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    # Encrypt a string one way
    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string

    #Encrypt a string with option to decrypt
    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message


    
    #If user is not already created then a user is added to the database
    def createUser(self, email='me@email.com', password='password', role='user'):       
        table = self.query()
        userPresentInTable = False
        encryptedPassword = self.onewayEncrypt(password)
        #check if user already present in database
        for row in table:
            if(row['email'] == email):
                userPresentInTable = True

        if(not userPresentInTable):
            self.insertRows('users', ['email', 'password', 'role'], [email,encryptedPassword,role])
            return {'success': 1}
        return {'success': 0}

    #Authentiate log in information 
    #returns true if log in is authenticated (password and email match a value in the db) and false if not
    def authenticate(self, email='me@email.com', password='password'):
        table = self.query()
        userPresentInTable = False
        encryptedPassword = self.onewayEncrypt(password)

        for row in table:
            if(row['email'] == email and row['password'] == encryptedPassword):
                return {'success': 1}
        return {'success': 0}
    
    #saves the word to the database
    def setWord(self,wordOfTheDay):
        table = self.query("SELECT * FROM wordle")  
        wordPresentInTable = False
        for row in table:
            if(row['word'] == wordOfTheDay):
              wordPresentInTable = True
        if(not wordPresentInTable):
          self.insertRows('wordle',['word'],[wordOfTheDay])
          return {'success': 1}
        return {'success': 1}

#https://www.freecodecamp.org/news/how-to-get-the-current-time-in-python-with-datetime/#:~:text=To%20get%20the%20current%20time%20in%20particular%2C%20you%20can%20use,hours%2C%20minutes%2C%20and%20seconds.
#current time
#https://www.atlassian.com/data/sql/how-to-update-a-column-based-on-a-filter-of-another-column#:~:text=To%20do%20a%20conditional%20update,perform%20updates%20on%20those%20rows.
#SQL query
    #Updates the score for a user
    #if the score is a lower one than was previously in the databse
    def updateScore(self, word, email, turns):
        table = self.query("SELECT * FROM scores")
        user_in_leaderboard = False
        time = datetime.now().strftime("%H:%M:%S")
        for row in table:
          #Finds user and word of the day
          if(row['email'] == email and row['word'] == word):
            user_in_leaderboard = True
            if(row['turns'] > turns):
              query_string = "UPDATE scores SET turns = " + str(turns) + " WHERE email = '" + row['email'] + "'"
              x = self.query(query_string)
        if(not user_in_leaderboard):
          self.insertRows('scores',['word','email', 'turns','time'], [word, email, turns, time])


#https://stackoverflow.com/questions/54300715/python-3-list-sorting-with-a-tie-breaker
#sorting tuples
    def getLeaderboard(self, word):
        table = self.query("SELECT * FROM scores")
        scores_from_today = []
        for row in table:
          if(row['word']==word):
            scores_from_today.append((row['email'], row['turns'], row['time']))
        #sort scorer by turns and then time as a tiebreaker
        scores_from_today.sort(key = lambda entry: (entry[1], entry[2]))
        return scores_from_today



    
