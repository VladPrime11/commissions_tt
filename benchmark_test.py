import time
import os
import random
import json
import argparse
from models.core import MLMTree, CommissionCalculator
from utils.benchmark import benchmark


TEMP_DIR = "temp"
PARTNERS_PATH = os.path.join(TEMP_DIR, "partners.json")
COMMISSIONS_PATH = os.path.join(TEMP_DIR, "commissions.json")


def generate_fake_partners(n: int) -> list[dict]:
    partners = []
    for i in range(1, n + 1):
        parent_id = None if i == 1 else random.randint(1, i - 1)
        partners.append({
            "id": i,
            "parent_id": parent_id,
            "monthly_revenue": random.randint(1000, 10000)
        })
    return partners


def benchmark_large_run(n: int):
    os.makedirs(TEMP_DIR, exist_ok=True)

    partners_data = generate_fake_partners(n)

    with open(PARTNERS_PATH, "w", encoding="utf-8") as f:
        json.dump(partners_data, f, indent=2)

    tree = MLMTree(partners_data)
    calculator = CommissionCalculator(tree)
    commissions = calculator.calculate_commissions()

    with open(COMMISSIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(commissions, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=50000, help="default: 50000")
    args = parser.parse_args()

    benchmark_large_run(args.n)
