from src.traffic.io.parser import InputParser

if __name__ == "__main__":
    #ip = InputParser("Beispielhausen.txt")
    ip = InputParser("Ringstadt.txt")
    sim = ip.load_input()
    sim.run()