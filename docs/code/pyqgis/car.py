class Car:
    
    model = 'Civic'
    
    def __init__(self, color, type):
        self.color = color
        self.type = type
        self.started = False
        self.stopped = False
    
    def start(self):
        print('Car Started')
        self.started = True
        self.stopped = False
        
    def stop(self):
        print('Car Stopped')
        self.stopped = True
        sefl.started = False

# Instantiate the class      
my_car = Car('blue', 'automatic')

print(my_car)

# Call a method
my_car.start()

# Check the value of an instance variable
print('Car Started?', my_car.started)

# Check the value of a class variable
print('Car model', Car.model)
