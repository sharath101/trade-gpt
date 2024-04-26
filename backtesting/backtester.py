import csv


class BackTester:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path

    def backtest(self):
        with open(self.csv_file_path, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                print(row)

                # Pass data to strategy class
                # strategy.handle_data(
                #     date, open_price, high_price, low_price, close_price, volume
                # )
