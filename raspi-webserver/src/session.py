import threading
from db.database import DatabaseManager


class Session:
    def __init__(self):
        self.active = True
        self.db_manager = DatabaseManager('raspi-webserver/src/db/database.db')
        ''' uncomment for testing
        additional_data = [
            (100, 1),
            (200, 1),
            (510, 2)
        ]
        for data in additional_data:
            self.db_manager.set(data[0], data[1])
        '''
        self.box1 = self.db_manager.getPacketsInBoxCount(1)
        self.box2 = self.db_manager.getPacketsInBoxCount(2)
        self.lock = threading.Lock()
    
    def start_pause(self):
        self.active = not self.active
        print(f'Active: {self.active}')
    
    def update_box1(self, value):
        with self.lock:
            self.box1 = value
        print(f'Box1: {self.box1}')
    
    def update_box2(self, value):
        with self.lock:
            self.box2 = value
        print(f'Box2: {self.box2}')
    
    def increment_box1(self):
        with self.lock:
            self.box1 += 1
            self.db_manager.set(100,1)  #buffer weight
            print(f'Box1: {self.box1}')
        
    def increment_box2(self):
        with self.lock:
            self.box2 += 1
            self.db_manager.set(300,2)  #buffer weight
            print(f'Box2: {self.box2}')
    
    def decrement_box1(self):
        if self.box1 > 0:
            self.box1 -= 1
            self.db_manager.deleteLast(1)
        print(f'Box1: {self.box1}')
    
    def decrement_box2(self):
        if self.box2 > 0:
            self.box2 -= 1
            self.db_manager.deleteLast(2)
        print(f'Box2: {self.box2}')