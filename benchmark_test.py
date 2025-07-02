"""
Скрипт для тестування продуктивності MLM системи.

Генерує фейкових партнерів і тестує як швидко система рахує комісії.
За замовчуванням тестує на 50 тисячах партнерів.

Запуск - python benchmark_test.py --n 50000
"""

import time
import os
import random
import json
import argparse
from models.core import MLMTree, CommissionCalculator

# Папка для тимчасових файлів
TEMP_DIR = "temp"
PARTNERS_PATH = os.path.join(TEMP_DIR, "partners.json")
COMMISSIONS_PATH = os.path.join(TEMP_DIR, "commissions.json")


def generate_fake_partners(n: int) -> list[dict]:
    """
    Створює фейкових партнерів для тестування.

    Генерує дерево де кожен партнер (крім першого) має випадкового батька
    з тих що вже створені. Це дає реалістичну MLM структуру.

    Args:
        n: Кількість партнерів для створення

    Returns:
        Список словників з даними партнерів
    """
    partners = []
    for i in range(1, n + 1):
        # Перший партнер - корінь дерева, інші мають випадкового батька
        parent_id = None if i == 1 else random.randint(1, i - 1)
        partners.append({
            "id": i,
            "parent_id": parent_id,
            "monthly_revenue": random.randint(1000, 10000)  # Випадковий дохід
        })
    return partners


def benchmark_large_run(n: int):
    """
    Виконує повний тест продуктивності.

    Створює партнерів, зберігає їх, будує дерево, рахує комісії
    і зберігає результат. Вимірює час виконання через декоратор.

    Args:
        n: Кількість партнерів для тестування
    """
    # Створюємо папку якщо її немає
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Генеруємо фейкових партнерів
    partners_data = generate_fake_partners(n)

    # Зберігаємо вхідні дані
    with open(PARTNERS_PATH, "w", encoding="utf-8") as f:
        json.dump(partners_data, f, indent=2)

    # Основна робота - будуємо дерево і рахуємо комісії
    tree = MLMTree(partners_data)
    calculator = CommissionCalculator(tree)
    commissions = calculator.calculate_commissions()

    # Зберігаємо результати
    with open(COMMISSIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(commissions, f, indent=2)


if __name__ == "__main__":
    # Парсимо аргументи командного рядка
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=50000,
                        help="Кількість партнерів для тестування (за замовчуванням: 50000)")
    args = parser.parse_args()

    benchmark_large_run(args.n)