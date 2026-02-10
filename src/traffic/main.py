from src.traffic.io.parser import InputParser

if __name__ == "__main__":
    ip = InputParser("Beispielhausen.txt")
    sim = ip.load_input()
    print("##############")
    for road in sim.roads:
        print(f'{road.start_point.position.x} {road.start_point.position.y} {road.end_point.position.x} {road.end_point.position.y}')
    print("##############")
    sim.run()