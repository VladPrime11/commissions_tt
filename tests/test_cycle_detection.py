import pytest
from models.core import MLMTree


class TestCycleDetection:
    """Тести виявлення циклів у дереві партнерів"""

    def test_simple_cycle_two_partners(self):
        """Тест простого циклу A->B->A"""
        # Створюємо найпростіший цикл: партнер 1 → партнер 2 → партнер 1
        # Партнер 1 має батька 2, а партнер 2 має батька 1
        cyclic_data = [
            {"id": 1, "parent_id": 2, "monthly_revenue": 3000},  # 1 → 2
            {"id": 2, "parent_id": 1, "monthly_revenue": 2000}   # 2 → 1 (цикл!)
        ]

        # Очікуємо що MLMTree викине ValueError з повідомленням "Cycle detected"
        with pytest.raises(ValueError, match="Cycle detected"):
            MLMTree(cyclic_data)

    def test_triangle_cycle(self):
        """Тест трикутного циклу A->B->C->A"""
        # Створюємо трикутний цикл: 1 → 3 → 2 → 1
        # Більш складний випадок з трьома партнерами
        cyclic_data = [
            {"id": 1, "parent_id": 3, "monthly_revenue": 3000},  # 1 → 3
            {"id": 2, "parent_id": 1, "monthly_revenue": 2000},  # 2 → 1
            {"id": 3, "parent_id": 2, "monthly_revenue": 1000}   # 3 → 2 (замикає цикл)
        ]

        # Система повинна виявити цикл і викинути помилку
        with pytest.raises(ValueError, match="Cycle detected"):
            MLMTree(cyclic_data)

    def test_self_cycle(self):
        """Тест самозацикленості A->A"""
        # Партнер є батьком самого себе - найпростіший випадок циклу
        # В реальному MLM такого не може бути
        cyclic_data = [
            {"id": 1, "parent_id": 1, "monthly_revenue": 3000}   # 1 → 1 (сам себе)
        ]

        # Повинна виявлятися помилка навіть для такого тривіального циклу
        with pytest.raises(ValueError, match="Cycle detected"):
            MLMTree(cyclic_data)

    def test_valid_tree_no_cycle(self):
        """Тест що правильне дерево не викидає помилку"""
        # Створюємо правильну ієрархічну структуру без циклів:
        # 1 (root) має дітей 2 і 3
        valid_data = [
            {"id": 1, "parent_id": None, "monthly_revenue": 3000},  # Корінь дерева
            {"id": 2, "parent_id": 1, "monthly_revenue": 2000},     # Дитина кореня
            {"id": 3, "parent_id": 1, "monthly_revenue": 1000}      # Друга дитина кореня
        ]

        # Правильне дерево не повинно викидати жодних помилок
        tree = MLMTree(valid_data)
        # Перевіряємо що всі партнери успішно створені
        assert len(tree.partners) == 3

    def test_longer_cycle(self):
        """Тест довшого циклу A->B->C->D->A"""
        # Створюємо цикл з 4 партнерів: 1 → 4 → 3 → 2 → 1
        # Тестуємо що алгоритм виявляє циклі не тільки короткі
        cyclic_data = [
            {"id": 1, "parent_id": 4, "monthly_revenue": 4000},  # 1 → 4
            {"id": 2, "parent_id": 1, "monthly_revenue": 3000},  # 2 → 1
            {"id": 3, "parent_id": 2, "monthly_revenue": 2000},  # 3 → 2
            {"id": 4, "parent_id": 3, "monthly_revenue": 1000}   # 4 → 3 (замикає довгий цикл)
        ]

        # Алгоритм повинен виявити цикл навіть якщо він проходить через багато вузлів
        with pytest.raises(ValueError, match="Cycle detected"):
            MLMTree(cyclic_data)