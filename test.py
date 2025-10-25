import os
import pandas as pd

folder = 'tum_mealler'
files = [f for f in os.listdir(folder) if f.endswith('.csv') and 'arapca' not in f.lower() and 'sozl' not in f.lower() and 'mekki' not in f.lower()]
print('Files:', files)

meal_file = None
for f in files:
    if 'Diyanet' in f:
        meal_file = f
        break
if meal_file:
    print('Meal file:', repr(meal_file))
    path = os.path.join(folder, meal_file)
    print('Path:', repr(path))

    try:
        df = pd.read_csv(path, dtype=str, encoding='utf-8-sig', engine='python', quoting=3, on_bad_lines='skip')
        print('Loaded successfully')
    except Exception as e:
        print('Exception:', e)
else:
    print('Diyanet file not found')