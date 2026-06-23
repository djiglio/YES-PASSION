import os, json
d = 'data/seasons'
outliers = set()
sum_values = 0
count_values = 0

for f in os.listdir(d):
    if f.endswith('.json'):
        with open(os.path.join(d,f), encoding='utf-8') as file:
            data = json.load(file)
            for t in data.get('teams', []):
                for p in t.get('players', []):
                    age = p.get('Age', 25)
                    val = p.get('ValueNum', 0)
                    sum_values += val
                    count_values += 1
                    if age < 18 or age > 39:
                        outliers.add(f"{p['Nome']} ({t['name']}) - Age {age}")

print("Outliers:")
for o in outliers:
    print(o)

print(f"\nTotal Players Processed: {count_values}")
if count_values > 0:
    print(f"Average Value: €{sum_values/count_values:,.2f}")
