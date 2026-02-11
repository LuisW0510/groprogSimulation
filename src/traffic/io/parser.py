from enum import IntEnum
from pathlib import Path

from src.traffic.models import EntryPoint, Point, Intersection
from src.traffic.simulation import Simulation

class Modes(IntEnum):
    NONE = 0
    ZEITRAUM = 1
    EINFALLSPUNKTE = 2
    KREUZUNGEN = 3

class InputParser:
    def __init__(self, example_path):
        current_file = Path(__file__).resolve()
        project_root = current_file.parents[3]
        input_path = project_root / "examples" / example_path
        self.input_path = input_path

    @staticmethod
    def _validate_data(entry_points: list[EntryPoint], intersections: list[Intersection]):
        # Alle existierenden Kreuzungsnamen in ein Set für schnellen Zugriff
        existing_intersection_names = {it.name for it in intersections}

        # 1. Validiere Einfallspunkte -> Zielkreuzung
        for ep in entry_points:
            if ep.target_intersection not in existing_intersection_names:
                raise ValueError(
                    f"Validierungsfehler in Einfallspunkt '{ep.name}': "
                    f"Die Zielkreuzung '{ep.target_intersection}' existiert nicht im Abschnitt 'Kreuzungen:'."
                )

    def load_input(self) -> Simulation:
        with open(self.input_path) as f:
            lines = f.readlines()

        end_time: int
        dt: int
        entry_points = []
        intersections = []
        current_block = Modes.NONE

        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                continue
            if current_block == 0:
                match line:
                    case "Zeitraum:":
                        current_block = Modes.ZEITRAUM
                    case "Einfallspunkte:":
                        current_block = Modes.EINFALLSPUNKTE
                    case "Kreuzungen:":
                        current_block = Modes.KREUZUNGEN
                    case _:
                        current_block = Modes.NONE
            else:
                if not line:
                    current_block = Modes.NONE
                else:
                    parts = line.split()
                    match current_block:
                        case 1:
                            end_time = int(parts[0])
                            dt = int(parts[1])
                        case 2:
                            pos = Point(float(parts[1]), float(parts[2]))
                            ep = EntryPoint(name=parts[0], position=pos, target_intersection=parts[3], tact=int(parts[4]))
                            entry_points.append(ep)
                        case 3:
                            conn = {}
                            for i in range(3, len(parts), 2):
                                key = parts[i]
                                if i + 1 < len(parts):
                                    value = int(parts[i+1])
                                    conn[key] = value
                            pos = Point(float(parts[1]), float(parts[2]))
                            it = Intersection(name=parts[0], position=pos, connections=conn)
                            intersections.append(it)

        try:
            self._validate_data(entry_points, intersections)
        except ValueError as e:
            # Beendet das Programm mit einer klaren Fehlermeldung statt eines Absturzes
            print(f"FEHLER BEIM EINLESEN: {e}")
            exit(1)

        return Simulation(end_time=end_time, dt=dt, entry_points=entry_points, intersections=intersections)