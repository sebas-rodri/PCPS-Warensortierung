import threading

class Session:
    def __init__(self):
        self.active = True
        self.box1 = 0
        self.box2 = 0
        self.lock = threading.Lock()
    
    def start_pause(self):
        self.active = not self.active
        print(f'Active: {self.active}')
    
    def update_box1(self, value):
        with self.lock:
            self.box1 = value
            print(f'Box1: {self.box1}')
    
    def update_box2(self, value):
        self.box2 = value
        print(f'Box2: {self.box2}')
    
    def increment_box1(self):
        with self.lock:
            self.box1 += 1
            print(f'Box1: {self.box1}')
        
    def increment_box2(self):
        with self.lock:
            self.box2 += 1
            print(f'Box2: {self.box2}')
    
    def decrement_box1(self):
        if self.box1 > 0:
            self.box1 -= 1
        print(f'Box1: {self.box1}')
    
    def decrement_box2(self):
        if self.box2 > 0:
            self.box2 -= 1
        print(f'Box2: {self.box2}')