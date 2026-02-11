from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.traffic.simulation import Simulation


class Validator:
    def __init__(self, sim: Simulation):
        self.sim = sim

    def run_validations(self):
        self._validate_entrypoints_to_intersection()
        self._validate_range_of_values()
        self._validate_distinct_coords()
        self._validate_no_dead_ends()
        self._validate_reachablility()

    def _validate_entrypoints_to_intersection(self):
        # Alle existierenden Kreuzungsnamen in ein Set für schnellen Zugriff
        existing_intersection_names = {it.name for it in self.sim.intersections}

        # 1. Validiere Einfallspunkte -> Zielkreuzung
        for ep in self.sim.entry_points:
            if ep.target_intersection not in existing_intersection_names:
                raise ValueError(
                    f"Validierungsfehler in Einfallspunkt '{ep.name}': "
                    f"Die Zielkreuzung '{ep.target_intersection}' existiert nicht im Abschnitt 'Kreuzungen:'."
                )

    def _validate_range_of_values(self):
        # 1. Zeitraum-Validierung (dt und Endzeit)
        if self.sim.dt <= 0:
            raise ValueError(f"Ungültiger Zeitschritt (dt={self.sim.dt}): Muss größer als 0 sein.")

        if self.sim.end_time <= 0:
            raise ValueError(f"Ungültige Simulationsdauer (Endzeit={self.sim.end_time})")

        # 2. Gewichts-Validierung an Kreuzungen
        for it in self.sim.intersections:
            for target, weight in it.connections.items():
                if weight <= 0:
                    raise ValueError(
                        f"Gewichtsfehler an Kreuzung '{it.name}' -> '{target}':"
                        f"Gewicht muss positiv sein (gegeben: {weight})."
                    )

        # 3. Taktvalidierung der Einfallspunkte
        for ep in self.sim.entry_points:
            if ep.tact <= 0:
                raise ValueError(
                    f"Fahrzeuge können nicht im negativen Takt erzeugt werden: '{ep.tact}'"
                )

    def _validate_distinct_coords(self):
        all_nodes = self.sim.entry_points + self.sim.intersections

        # 1. Prüfe alle Knoten gegen alle anderen (Identische Positionen) generell
        for i, node_a in enumerate(all_nodes):
            for node_b in all_nodes[i + 1:]:
                if node_a.position.x == node_b.position.x and \
                    node_a.position.y == node_b.position.y:
                    raise ValueError(
                        f"Kritischer Positionsfehler: '{node_a.name}' und '{node_b.name}'"
                        f"liegen beide auf ({node_a.position.x}, {node_a.position.y}). "
                        f"Dies würde zu einer Straßenlänge von 0 führen!"
                    )

    def _validate_no_dead_ends(self):
        for it in self.sim.intersections:
            # 1. Überprüfung: Gibt es mindestens 2 Wege?
            if len(it.connections) < 2:
                target = list(it.connections.keys())[0]
                raise ValueError(
                    f"Sackgassen-Fehler: Kreuzung '{it.name}' hat nur eine Verbindung nach '{target}'. "
                    f"Das führt zu einem Stillstand-Szenario, da Fahrzeuge nicht umkehren können."
                )

            # 2. Überprüfung: Selbst-Referenz
            if it.name in it.connections:
                raise ValueError(
                    f"Logik-Fehler: Kreuzung '{it.name}' kann keine Verbindung zu sich selbst haben."
                )

    def _validate_reachablility(self):
        referenced_names = {ep.target_intersection for ep in self.sim.entry_points}
        for it in self.sim.intersections:
            referenced_names.update(it.connections.keys())

        for it in self.sim.intersections:
            if it.name not in referenced_names:
                print(f"WARNUNG: Kreuzung '{it.name}' ist von niergendwo erreichbar.")