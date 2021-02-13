import argparse

if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("config", action="store")  # configuration file
    parser.add_argument("-b", "--benchmark", action="store_true")  # benchmark
    parser.add_argument("-p", "--plot", action="store_true")  # plot
    args = parser.parse_args()