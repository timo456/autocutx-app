# utils/label_map.py

def load_label_map(path='utils/kinetics400_label_map.txt'):
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f]
