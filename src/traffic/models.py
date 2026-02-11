from __future__ import annotations
import math
import random
from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.traffic.simulation import Simulation

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
    length: float               # In Koordinaten-Einheiten (1.0 = 100m)

    #Statistik-Vars
    current_vehicle_sum: int = 0
    total_vehicle_sum: int = 0     # Summe über alle Zeitschritte
    max_vehicle_sum: int = 0       # Höchstwert jemals gleichzeitig

@dataclass
class Vehicle:
    id: int
    speed: float
    position: Point
    current_road: Edge
    target_node: Node

    def move(self, sim: Simulation):
        # Umrechnung von km/h in Meter pro Sekunde (v / 3.6)
        # Wenn ein Takt 1 Sekunde ist:
        meters_this_step = self.speed / 360
        remaining_distance = meters_this_step
        while remaining_distance > 0:
            target_pos = self.current_road.end_point.position
            # Distanz zum Ende der Straße
            dx = target_pos.x - self.position.x
            dy = target_pos.y - self.position.y
            dist_to_node = math.sqrt(dx**2 + dy**2)
            if remaining_distance >= dist_to_node:
                # FALL: Wir erreichen/überholen den Knoten in diesem Takt
                remaining_distance -= dist_to_node
                self.position = Point(target_pos.x, target_pos.y) # Exakt auf Knoten setzen

                # Nächste Straße über die Intersection bestimmen
                current_node = self.target_node
                if hasattr(current_node, 'choose_next_node_name'):
                    next_road = self.get_next_road(sim)
                    if next_road:
                        self.current_road = next_road
                        self.target_node = self.current_road.end_point
                        continue
                else:
                    sim.vehicles.remove(self)
                    break
            else:
                # FALL: Die Reststrecke reicht nicht bis zum nächsten Knoten
                if dist_to_node > 0:
                    ratio = remaining_distance / dist_to_node
                    self.position.x += dx * ratio
                    self.position.y += dy * ratio

                remaining_distance = 0 # Strecke für diesen Takt komplett verfahren


    def get_next_road(self, sim: Simulation) -> Edge:
        new_target_node_name = self.target_node.choose_next_node_name(self.current_road.start_point.name)
        for road in sim.roads:
            if road.start_point is self.target_node and road.end_point.name == new_target_node_name:
                return road
        return None


@dataclass
class EntryPoint(Node):
    target_intersection: str
    tact: int

    def spawn_vehicle(self, sim: Simulation) -> Vehicle:
        road = next((road for road in sim.roads if road.start_point == self), None)
        # Normalverteilung: mu (Erwartungswert) = 45, sigma (Standardabweichung) = 10
        rng_speed = random.gauss(45, 10)
        target_node = next((node for node in sim.intersections if node.name == self.target_intersection), None)
        if target_node is None:
            raise ValueError(f"Fehler beim Spawnen an {self.name}: "
                             f"Die Ziel-Kreuzung '{self.target_intersection}' existiert nicht in der Simulation!")

        return Vehicle(
            id=sim.max_vehicle_id,
            speed=rng_speed,
            position=Point(x=self.position.x, y=self.position.y),
            current_road=road,
            target_node=target_node
        )

@dataclass
class Intersection(Node):
    connections: dict[str, int]

    def choose_next_node_name(self, last_node_name: str) -> str:
        # 1. Filtere die Verbindung aus, von der wir gerade kommen
        filtered_connections = {
            node: weight
            for node, weight in self.connections.items()
            if node != last_node_name
        }
        if not filtered_connections:
            raise ValueError(f"Keine Ausweichmöglichkeiten von {self.name} außer zurück nach {last_node_name}.")

        # 2. Extrahiere Namen und Gewichte für die Auswahl
        destinations = list(filtered_connections.keys())
        weights = list(filtered_connections.values())

        # 3. Zufällige Wahl basierend auf den relativen Gewichten
        # random.choices berechnet die Wahrscheinlichkeiten intern (weight / sum(weights))
        next_node_name = random.choices(destinations, weights=weights, k=1)[0]

        return next_node_name