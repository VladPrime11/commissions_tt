"""
Основний файл для розрахунку комісій в MLM системі.

Завантажує дані партнерів, будує дерево, рахує комісії і зберігає результат.
Запускається з командного рядка.

Запуск - python main.py --input partners.json --output commissions.json
"""

import json
import sys
from models.core import MLMTree, CommissionCalculator


def load_partners(filepath):
    """
    Читає дані партнерів з JSON файлу.

    Args:
        filepath (str): Шлях до файлу з партнерами

    Returns:
        list: Список партнерів
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_commissions(data, filepath):
    """
    Зберігає комісії в JSON файл.

    Args:
        data (dict): Розраховані комісії 
        filepath (str): Куди зберігати
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    # Парсимо аргументи командного рядка
    # Шукаємо --input і --output
    try:
        input_file = sys.argv[sys.argv.index("--input") + 1]
        output_file = sys.argv[sys.argv.index("--output") + 1]
    except (ValueError, IndexError):
        # Якщо щось не так з аргументами - показуємо як користуватися
        print("Usage: python main.py --input partners.json --output commissions.json")
        sys.exit(1)

    # Основна робота
    partners_data = load_partners(input_file)

    # Будуємо дерево MLM
    tree = MLMTree(partners_data)

    # Рахуємо комісії
    calculator = CommissionCalculator(tree)
    commissions = calculator.calculate_commissions()

    # Зберігаємо результат
    save_commissions(commissions, output_file)