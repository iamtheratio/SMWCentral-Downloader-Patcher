import json

data = json.load(open('processed.json'))

missing_current_diff = []
for hack_id, hack in data.items():
    if 'current_difficulty' not in hack:
        missing_current_diff.append((hack_id, hack.get('title', 'No title')))

print(f"Total hacks: {len(data)}")
print(f"Hacks missing current_difficulty: {len(missing_current_diff)}")
if missing_current_diff:
    print("\nFirst 5 hacks missing current_difficulty:")
    for hack_id, title in missing_current_diff[:5]:
        print(f"  {hack_id}: {title}")
