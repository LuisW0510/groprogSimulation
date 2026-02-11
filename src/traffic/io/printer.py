import shutil
from pathlib import Path

from src.traffic.models import Vehicle, Edge

class OutputPrinter:
    def __init__(self, output_path):
        self.out_dir = Path(__file__).parent.parent.parent.parent / "out"
        if self.out_dir.exists():
            shutil.rmtree(self.out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def print_plan(self, roads: list[Edge]):
        file_path = self.out_dir / "Plan.txt"
        with open(file_path, "w") as f:
            for road in roads:
                f.write(f'{road.start_point.position.x} {road.start_point.position.y} '
                        f'{road.end_point.position.x} {road.end_point.position.y}\n')

    def print_statistics(self, roads: list[Edge]):
        file_path = self.out_dir / "Statistik.txt"
        with open(file_path, "w") as f:
            f.write("Gesamtanzahl Fahrzeuge pro 100m:\n")
            for road in roads:
                norm_total = road.total_vehicle_sum / road.length
                f.write(f"{road.name}: {norm_total:.2f}\n")
            f.write("Maximale Anzahl Fahrzeuge pro 100m:\n")
            for road in roads:
                norm_max = road.max_vehicle_sum / road.length
                f.write(f"{road.name}: {norm_max:.2f}\n")


    def print_vehicles(self, t: int, vehicles: list[Vehicle]):
        file_path = self.out_dir / "Fahrzeuge.txt"
        # 'a' steht für append (anhängen)
        with open(file_path, "a") as f:
            f.write(f'*** t = {t}\n')
            for v in vehicles:
                f.write(f'{v.position.x} {v.position.y} '
                        f'{v.target_node.position.x} {v.target_node.position.y} '
                        f'{v.id}\n')
