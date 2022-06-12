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

# Inheritance

class Sedan(Car):
        
    def __init__(self, color, type, seats):
        super().__init__(color, type)
        self.seats = seats
        
class ElectricSedan(Sedan):

    def __init__(self, color, type, seats, range_km):
        super().__init__(color, type, seats)
        self.range_km = range_km
        
my_car = Sedan('blue', 'automatic', 5)
print(my_car.color)
print(my_car.seats)
my_car.start()


my_future_car = ElectricSedan('red', 'automatic', 5, 500)
print(my_future_car.color)
print(my_future_car.seats)
print(my_future_car.range_km)
my_future_car.start()
