from termcolor import cprint


class Road:

    def __init__(self, start, end, distance):
        self.start = start
        self.end = end
        self.distance = distance


class Warehouse:

    def __init__(self, name, content=0):
        self.name = name
        self.content = content
        self.road_out = None
        self.queue_in = []
        self.queue_out = []

    def __str__(self):
        return f'In stock {self.name} {self.content} cargo.'

    def set_road_out(self, road):
        self.road_out = road

    def truck_arrived(self, truck):
        self.queue_in.append(truck)
        truck.place = self
        print(f'The {truck} truck has arrived at the {self.name} warehouse.')

    def get_next_truck(self):
        if self.queue_in:
            truck = self.queue_in.pop()
            return truck

    def truck_ready(self, truck):
        self.queue_out.append(truck)
        print(f'The {truck} truck in the {self.name} warehouse is ready for departure.')

    def act(self):
        while self.queue_out:
            truck = self.queue_out.pop()
            truck.go_to(road=self.road_out)


class Vehicle:
    fuel_rate = 0
    total_fuel = 0

    def __init__(self, model):
        self.model = model
        self.fuel = 0

    def __str__(self):
        return f'{self.model}. Fuel - {self.fuel}. '

    def tank_up(self):
        self.fuel += 1000
        Vehicle.total_fuel += 1000
        print(f'{self.model} fueled up.')

    def act(self):
        if self.fuel <= 10:
            self.tank_up()
            return False
        return True


class Truck(Vehicle):
    fuel_rate = 50
    dead_time = 0

    def __init__(self, model, body_space=1000):
        super().__init__(model=model)
        self.body_space = body_space
        self.cargo = 0
        self.velocity = 100
        self.place = None
        self.distance_to_target = 0

    def __str__(self):
        res = super().__str__()
        return res + f'Cargo - {self.cargo}.'

    def ride(self):
        self.fuel -= self.fuel_rate
        if self.distance_to_target > self.velocity:
            self.distance_to_target -= self.velocity
            print(f'{self.model} is driving on the road. {self.distance_to_target} km left.')
        else:
            self.place.end.truck_arrived(self)

    def go_to(self, road):
        self.place = road
        self.distance_to_target = road.distance
        print(f'{self.model} has hit the road.')

    def act(self):
        if super().act():
            if isinstance(self.place, Road):
                self.ride()
            else:
                Truck.dead_time += 1


class AutoLoader(Vehicle):
    fuel_rate = 30
    dead_time = 0

    def __init__(self, model, bucket_capacity=100, warehouse=None, role='loader'):
        super().__init__(model=model)
        self.bucket_capacity = bucket_capacity
        self.warehouse = warehouse
        self.role = role
        self.truck = None

    def __str__(self):
        res = super().__str__()
        return res + f' loads {self.truck}'

    def act(self):
        if super().act():
            if self.truck is None:
                self.truck = self.warehouse.get_next_truck()
                if self.truck is None:
                    print(f'{self.model} has no trucks to work with.')
                    AutoLoader.dead_time += 1
                else:
                    print(f'{self.model} took {self.truck} into operation.')
            elif self.role == 'loader':
                self.load()
            else:
                self.unload()

    def load(self):
        if self.warehouse.content == 0:
            print(f'There is nothing in the {self.model} warehouse')
            if self.truck:
                self.warehouse.truck_ready(truck=self.truck)
                self.truck = None
            return
        self.fuel -= self.fuel_rate
        truck_cargo_rest = self.truck.body_space - self.truck.cargo
        if truck_cargo_rest >= self.bucket_capacity:
            cargo = self.bucket_capacity
        else:
            cargo = truck_cargo_rest
        if self.warehouse.content < cargo:
            cargo = self.warehouse.content
        self.warehouse.content -= cargo
        self.truck.cargo += cargo
        print(f'{self.model} was loading the {self.truck}.')
        if self.truck.cargo == self.truck.body_space:
            self.warehouse.truck_ready(truck=self.truck)
            self.truck = None

    def unload(self):
        self.fuel -= self.fuel_rate
        if self.truck.cargo >= self.bucket_capacity:
            self.truck.cargo -= self.bucket_capacity
            self.warehouse.content += self.bucket_capacity
        else:
            self.truck.cargo -= self.truck.cargo
            self.warehouse.content += self.truck.cargo
        if self.truck.cargo == 0:
            self.warehouse.truck_ready(truck=self.truck)
            self.truck = None
        print(f'{self.model} was unloading the {self.truck}.')


TOTAL_CARGO = 100000

moscow = Warehouse(name='Moscow', content=TOTAL_CARGO)
helsinki = Warehouse(name='Helsinki', content=0)

moscow_helsinki = Road(start=moscow, end=helsinki, distance=1080)
helsinki_moscow = Road(start=helsinki, end=moscow, distance=1090)

moscow.set_road_out(road=moscow_helsinki)
helsinki.set_road_out(road=helsinki_moscow)

loader_1 = AutoLoader(model='Bobcat', bucket_capacity=1000, warehouse=moscow, role='loader')
loader_2 = AutoLoader(model='Lonking', bucket_capacity=500, warehouse=helsinki, role='unloader')

trucks = []
for number in range(5):
    truck = Truck(model=f'Scania #{number + 1}', body_space=5000)
    moscow.truck_arrived(truck)
    trucks.append(truck)
for number in range(2):
    truck = Truck(model=f'Suzuki #{number + 1}', body_space=1000)
    moscow.truck_arrived(truck)
    trucks.append(truck)

hour = 0
while helsinki.content < TOTAL_CARGO:
    hour += 1
    cprint(f'================== HOUR {hour} ==================', color='red')
    for truck in trucks:
        truck.act()
    loader_1.act()
    loader_2.act()
    moscow.act()
    helsinki.act()
    for truck in trucks:
        cprint(truck, color='cyan')
    cprint(loader_1, color='cyan')
    cprint(loader_2, color='cyan')
    cprint(moscow, color='cyan')
    cprint(helsinki, color='cyan')

cprint(f'A total of {Vehicle.total_fuel} fuel was spent.', color='yellow')
cprint(f'Total idle time of trucks - {Truck.dead_time}', color='yellow')
cprint(f'Total idle time of loaders - {AutoLoader.dead_time}', color='yellow')
