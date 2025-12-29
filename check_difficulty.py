import json

data = json.load(open('processed.json'))
sample = next(iter(data.values()))

print("Sample hack keys:", list(sample.keys()))
print("Has difficulty:", "difficulty" in sample)
print("Has current_difficulty:", "current_difficulty" in sample)
print("difficulty value:", sample.get("difficulty", "NOT FOUND"))
print("current_difficulty value:", sample.get("current_difficulty", "NOT FOUND"))
