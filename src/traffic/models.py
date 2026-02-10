import math
from abc import ABC
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Node(ABC):
    name: str
    position: Point

@dataclass
class Edge:
    name: str
    start_point: Node
    end_point: Node
    length: float
    vehicle_cnt: int = 0
    #TODO? max: int für statistik
    #TODO? aktuelle Autos auf Road für statistik
    # bei änderung von aktuelle autos -> größer als max? ändern oder lassen

@dataclass
class Vehicle:
    id: int
    speed: float
    position: Point
    current_road: Edge
    target_node: Node

    def move(self):
        remaining_distance = self.speed
        while remaining_distance > 0:
            target_pos = self.current_road.end_point.position
            # 2. Distanz zum Ende der Straße
            dx = target_pos.x - self.position.x
            dy = target_pos.y - self.position.y
            dist_to_node = math.sqrt(dx**2 + dy**2)
            if remaining_distance >= dist_to_node:
                # FALL: Wir erreichen/überholen den Knoten in diesem Takt
                remaining_distance -= dist_to_node
                self.position = Point(target_pos.x, target_pos.y) # Exakt auf Knoten setzen

                # Nächste Straße über die Intersection bestimmen
                current_node = self.target_node
                #TODO bei der if abfrage -> wenn nicht dann muss EntryPoint und dann auto entfernen (bei return "finished)
                if hasattr(current_node, 'choose_next_node'):
                    next_road = self.get_next_road()
                    if next_road:
                        #TODO statistik Logik -> straße aktueller vehicle cnt runter und bei neuer hoch
                        self.current_road = next_road
                        continue
                else:
                    # Simulation.removeVehicle (self)
                    pass
            else:
                # FALL: Die Reststrecke reicht nicht bis zum nächsten Knoten
                if dist_to_node > 0:
                    ratio = remaining_distance / dist_to_node
                    self.position.x += dx * ratio
                    self.position.y += dy * ratio

                remaining_distance = 0 # Strecke für diesen Takt komplett verfahren


    def get_next_road(self) -> Edge:
        #TODO ruft intersection.choose_next_node auf und sucht dann die passende straße von der intersection bis zum neuen node
        pass

@dataclass
class EntryPoint(Node):
    target_intersection: str
    tact: int

    def spawn_vehicle(self, v_id, all_roads) -> Vehicle:
        road = next((road for road in all_roads if road.start_point == self), None)
        #TODO rng speed
        return Vehicle(id=v_id, speed=0.0, position=Point(x=self.position.x, y=self.position.y), current_road=road, target_node=self.target_intersection)

@dataclass
class Intersection(Node):
    connections: dict[str, int]

    def choose_next_node(self, car: Vehicle) -> Node:
        ...
