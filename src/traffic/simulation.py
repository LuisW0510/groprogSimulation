import math
from dataclasses import field, dataclass

from src.traffic.io.printer import OutputPrinter
from src.traffic.models import EntryPoint, Intersection, Edge, Vehicle, Node, Point
from src.traffic.util.validator import Validator


@dataclass
class Simulation:
    end_time: int
    dt: int
    entry_points: list[EntryPoint]
    intersections: list[Intersection]
    time: int = 0
    max_vehicle_id: int = 0
    roads: list[Edge] = field(init=False)
    vehicles: list[Vehicle] = field(default_factory=list)

    def __post_init__(self):
        self.roads = self.load_roads()

    def load_roads(self) -> list[Edge]:
        edges = []
        all_nodes = self.entry_points + self.intersections
        for node in all_nodes:
            connections = getattr(node, 'connections', {})
            if isinstance(node, EntryPoint):
                target_node = next((n for n in self.intersections if n.name == node.target_intersection), None)
                if target_node:
                    edges.append(self._create_edge(node, target_node))
            for target_name, _ in connections.items():
                target_node = next((n for n in all_nodes if n.name == target_name), None)
                if target_node:
                    edges.append(self._create_edge(node, target_node))
        return edges

    @staticmethod
    def _create_edge(start: Node, end: Node) -> Edge:
        # Euklidische Distanz berechnen: sqrt((x2-x1)^2 + (y2-y1)^2)
        dist = math.sqrt(
            (end.position.x - start.position.x)**2 +
            (end.position.y - start.position.y)**2
        )
        return Edge(
            name=f"{start.name}->{end.name}",
            start_point=start,
            end_point=end,
            length=round(dist, 2)
        )

    def run(self):
        v = Validator(self)
        v.run_validations()
        op = OutputPrinter("out")
        op.print_plan(self.roads)
        while self.time <= self.end_time:
            if self.time:
                self.update_vehicles()
                self.spawn_vehicles()
                self.update_statistics()
            if self.time % self.dt == 0:
                op.print_vehicles(self.time, self.vehicles)
            self.time += 1
        op.print_statistics(self.roads)

    def update_vehicles(self):
        for vehicle in self.vehicles[:]:
            vehicle.move(self)

    def spawn_vehicles(self):
        for ep in self.entry_points:
            if self.time % ep.tact == 0:
                self.vehicles.append(ep.spawn_vehicle(self))
                self.max_vehicle_id += 1

    def update_statistics(self):
        for road in self.roads:
            # Zähle Fahrzeuge, die aktuell auf der Straße sind
            cnt = sum(1 for v in self.vehicles if v.current_road == road)
            road.current_vehicle_sum = cnt

            # Kumuliere für Gesamtsumme
            road.total_vehicle_sum += cnt

            # Prüfe auf neuen Maximalwert
            if cnt > road.max_vehicle_sum:
                road.max_vehicle_sum = cnt