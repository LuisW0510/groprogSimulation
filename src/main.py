import sys
from src.traffic.io.parser import InputParser

if __name__ == "__main__":
    file_name = sys.argv[1] if len(sys.argv) > 1 else "Beispielhausen.txt"
    ip = InputParser(file_name)
    sim = ip.load_input()
    sim.run()