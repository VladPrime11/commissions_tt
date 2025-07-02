import json
import sys
from models.core import MLMTree, CommissionCalculator


def load_partners(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_commissions(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    try:
        input_file = sys.argv[sys.argv.index("--input") + 1]
        output_file = sys.argv[sys.argv.index("--output") + 1]
    except (ValueError, IndexError):
        print("Usage: python main.py --input partners.json --output commissions.json")
        sys.exit(1)

    partners_data = load_partners(input_file)
    tree = MLMTree(partners_data)
    calculator = CommissionCalculator(tree)
    commissions = calculator.calculate_commissions()
    save_commissions(commissions, output_file)
