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
        return f'Склад {self.name} груза {self.content}'

    def set_road_out(self, road):
        self.road_out = road

    def truck_arrived(self, truck):
        self.queue_in.append(truck)
        truck.place = self
        print(f'На склад {self.name} прибыл грузовик {truck}')

    def get_next_truck(self):
        if self.queue_in:
            truck = self.queue_in.pop()
            return truck

    def truck_ready(self, truck):
        self.queue_out.append(truck)
        print(f'На складе {self.name} грузовик {truck} готов к выезду')

    def act(self):
        while self.queue_out:
            truck = self.queue_out.pop()
            truck.go_to(road=self.road_out)


class Vehicle:
    fuel_rate = 0

    def __init__(self, model):
        self.model = model
        self.fuel = 0

    def __str__(self):
        return f'{self.model}. топлива - {self.fuel}'

    def tank_up(self):
        self.fuel += 1000
        print(f'{self.model} заправился')


class Truck(Vehicle):
    fuel_rate = 50

    def __init__(self, model, body_space=1000):
        super().__init__(model=model)
        self.body_space = body_space
        self.cargo = 0
        self.velocity = 100
        self.place = None
        self.distance_to_target = 0

    def __str__(self):
        res = super().__str__()
        return res + f' груза {self.cargo}'

    def ride(self):
        self.fuel -= self.fuel_rate
        if self.distance_to_target > self.velocity:
            self.distance_to_target -= self.velocity
            print(f'{self.model} едет по дороге. Осталось {self.distance_to_target} км')
        else:
            self.place.end.truck_arrived(self)
            print(f'{self.model} доехал')

    def go_to(self, road):
        self.place = road
        self.distance_to_target = road.distance
        print(f'{self.model} выехал в путь')

    def act(self):
        if self.fuel <= 10:
            self.tank_up()
        elif isinstance(self.place, Road):
            self.ride()


class AutoLoader(Vehicle):
    fuel_rate = 30

    def __init__(self, model, bucket_capacity=100, warehouse=None, role='loader'):
        super().__init__(model=model)
        self.bucket_capacity = bucket_capacity
        self.warehouse = warehouse
        self.role = role
        self.truck = None

    def __str__(self):
        res = super().__str__()
        return res + f' грузим {self.truck}'

    def act(self):
        if self.fuel <= 10:
            self.tank_up()
        elif self.truck is None:
            self.truck = self.warehouse.get_next_truck()
            print(f'{self.model} взял в работу {self.truck}')
        elif self.role == 'loader':
            self.load()
        else:
            self.unload()

    def load(self):
        self.fuel -= self.fuel_rate
        if self.truck.cargo == self.truck.body_space or self.warehouse.content == 0:
            self.warehouse.truck_ready(truck=self.truck)
            self.truck = None
            return
        truck_cargo_rest = self.truck.body_space - self.truck.cargo
        if truck_cargo_rest >= self.bucket_capacity:
            self.warehouse.content -= self.bucket_capacity
            self.truck.cargo += self.bucket_capacity
        else:
            self.warehouse.content -= truck_cargo_rest
            self.truck.cargo += truck_cargo_rest
        print(f'{self.model} грузил {self.truck}')

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
        print(f'{self.model} разгружал {self.truck}')


TOTAL_CARGO = 100000

moscow = Warehouse(name='Moscow', content=TOTAL_CARGO)
helsinki = Warehouse(name='Helsinki', content=0)

moscow_helsinki = Road(start=moscow, end=helsinki, distance=1080)
helsinki_moscow = Road(start=helsinki, end=moscow, distance=1090)

moscow.set_road_out(road=moscow_helsinki)
helsinki.set_road_out(road=helsinki_moscow)

loader_1 = AutoLoader(model='Bobcat', bucket_capacity=1000, warehouse=moscow, role='loader')
loader_2 = AutoLoader(model='Lonking', bucket_capacity=500, warehouse=helsinki, role='unloader')

truck_1 = Truck(model='Scania', body_space=5000)
truck_2 = Truck(model='Suzuki', body_space=1000)

moscow.truck_arrived(truck_1)
moscow.truck_arrived(truck_2)

hour = 0
while helsinki.content < TOTAL_CARGO:
    hour += 1
    cprint(f'================== HOUR {hour} ==================', color='red')
    truck_1.act()
    truck_2.act()
    loader_1.act()
    loader_2.act()
    moscow.act()
    helsinki.act()
    cprint(truck_1, color='cyan')
    cprint(truck_2, color='cyan')
    cprint(loader_1, color='cyan')
    cprint(loader_2, color='cyan')
    cprint(moscow, color='cyan')
    cprint(helsinki, color='cyan')
