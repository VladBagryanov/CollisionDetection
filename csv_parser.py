import csv

with open('wiki.csv', newline='') as csvfile:

    reader = csv.DictReader(csvfile)
    i = 0
    for row in reader:
        i += 1
        with open(f"input_data/text{i}.txt", "w") as file:
            file.write(row['text'])
        if (i == 5):
            break