import pytest
from models.core import MLMTree, CommissionCalculator


class TestDuplicateIds:
    """Тести обробки дублікатів ID партнерів"""

    def test_duplicate_ids_last_wins(self):
        """Тест що при дублікатах ID залишається останній партнер"""
        # Створюємо дані з дублікатом ID=2
        # Перший партнер 2 має дохід 2000, другий (дублікат) - 5000
        data = [
            {"id": 1, "parent_id": None, "monthly_revenue": 3000},
            {"id": 2, "parent_id": 1, "monthly_revenue": 2000},     # Перший з ID=2
            {"id": 2, "parent_id": 1, "monthly_revenue": 5000},     # Дублікат ID=2
            {"id": 3, "parent_id": 2, "monthly_revenue": 1500}
        ]

        tree = MLMTree(data)

        # Через dictionary comprehension Python зберігає тільки останній ключ
        # Тому маємо 3 унікальних партнери, не 4
        assert len(tree.partners) == 3
        assert 1 in tree.partners
        assert 2 in tree.partners
        assert 3 in tree.partners

        # Партнер 2 має дохід 5000 (останній), а не 2000 (перший)
        # Це тестує поведінку Python, {1: 'a', 1: 'b'} → {1: 'b'}
        assert tree.partners[2].monthly_revenue == 5000

    def test_duplicate_ids_tree_structure(self):
        """Тест що дублікати не ламають структуру дерева"""
        # Перевіряємо що навіть при дублікатах зв'язки батько-дитина працюють правильно
        data = [
            {"id": 1, "parent_id": None, "monthly_revenue": 3000},
            {"id": 2, "parent_id": 1, "monthly_revenue": 2000},     # Перший партнер 2
            {"id": 2, "parent_id": 1, "monthly_revenue": 4000},     # Дублікат перезаписує
            {"id": 3, "parent_id": 2, "monthly_revenue": 1500}      # Посилається на ID=2
        ]

        tree = MLMTree(data)

        # Перевіряємо що ієрархія побудована правильно навіть після дублікатів
        # Партнер 1 (root) має одну дитину - партнера 2
        assert len(tree.partners[1].children) == 1
        assert tree.partners[1].children[0].id == 2

        # Партнер 2 (останній з дублікатів) має одну дитину - партнера 3
        assert len(tree.partners[2].children) == 1
        assert tree.partners[2].children[0].id == 3

        # Партнер 3 - листок дерева
        assert len(tree.partners[3].children) == 0

    def test_multiple_duplicates(self):
        """Тест кількох дублікатів різних ID"""
        # Тестуємо складніший сценарій, дублікати для кількох різних ID
        # ID=1 має 3 дублікати, ID=2 має 2 дублікати
        data = [
            {"id": 1, "parent_id": None, "monthly_revenue": 1000},  # Перший ID=1
            {"id": 1, "parent_id": None, "monthly_revenue": 2000},  # Дублікат 1 для ID=1
            {"id": 1, "parent_id": None, "monthly_revenue": 3000},  # Дублікат 2 для ID=1
            {"id": 2, "parent_id": 1, "monthly_revenue": 500},      # Перший ID=2
            {"id": 2, "parent_id": 1, "monthly_revenue": 1500},     # Дублікат для ID=2
            {"id": 3, "parent_id": 2, "monthly_revenue": 800}       # Унікальний ID=3
        ]

        tree = MLMTree(data)

        # З 6 записів залишається тільки 3 уніальних партнери
        assert len(tree.partners) == 3

        # Для кожного ID зберігається останнє значення з масиву даних
        assert tree.partners[1].monthly_revenue == 3000  # Останній з трьох для ID=1
        assert tree.partners[2].monthly_revenue == 1500  # Останній з двох для ID=2
        assert tree.partners[3].monthly_revenue == 800   # Унікальний, без дублікатів

    def test_duplicate_ids_commission_calculation(self):
        """Тест що комісії розраховуються правильно при дублікатах"""
        # Перевіряємо що розрахунок комісій використовує правильні (останні) дані
        data = [
            {"id": 1, "parent_id": None, "monthly_revenue": 3000},
            {"id": 2, "parent_id": 1, "monthly_revenue": 1500},     # Перший партнер 2: 1500
            {"id": 2, "parent_id": 1, "monthly_revenue": 4500},     # Дублікат перезаписує: 4500
        ]

        tree = MLMTree(data)
        calculator = CommissionCalculator(tree)
        commissions = calculator.calculate_commissions()

        # Комісія розраховується для останнього партнера 2 з доходом 4500, не 1500
        # Денний дохід дитини 4500/30 = 150
        # Комісія партнера 1 150 * 0.05 = 7.5
        assert commissions["1"] == 7.5
        assert commissions["2"] == 0.0  # Листок - немає дітей

    def test_duplicate_parent_references(self):
        """Тест коли дублікат змінює parent_id"""
        # Дублікат не тільки змінює дохід, але й змінює батька!
        # Це може кардинально змінити структуру дерева
        data = [
            {"id": 1, "parent_id": None, "monthly_revenue": 3000},
            {"id": 2, "parent_id": None, "monthly_revenue": 2000},  # Партнер 2 спочатку root
            {"id": 3, "parent_id": 1, "monthly_revenue": 1500},     # Партнер 3 - дитина партнера 1
            {"id": 3, "parent_id": 2, "monthly_revenue": 1800},     # Дублікат: тепер дитина партнера 2!
        ]

        tree = MLMTree(data)

        # Через дублікат партнер 3 "переїхав" від батька 1 до батька 2
        assert len(tree.partners[1].children) == 0  # Партнер 1 втратив дитину
        assert len(tree.partners[2].children) == 1  # Партнер 2 отримав дитину
        assert tree.partners[2].children[0].id == 3

        # Дохід також змінився на значення з дублікату
        assert tree.partners[3].monthly_revenue == 1800

    def test_no_duplicates_baseline(self):
        """Базовий тест без дублікатів для порівняння"""
        # Перевіряємо нормальну поведінку без дублікатів
        # Це "золотий стандарт" для порівняння з попередніми тестами
        data = [
            {"id": 1, "parent_id": None, "monthly_revenue": 3000},
            {"id": 2, "parent_id": 1, "monthly_revenue": 2000},
            {"id": 3, "parent_id": 1, "monthly_revenue": 1500}
        ]

        tree = MLMTree(data)

        # При відсутності дублікатів все працює як очікується
        assert len(tree.partners) == 3  # Кількість партнерів = кількість записів
        assert tree.partners[1].monthly_revenue == 3000
        assert tree.partners[2].monthly_revenue == 2000
        assert tree.partners[3].monthly_revenue == 1500