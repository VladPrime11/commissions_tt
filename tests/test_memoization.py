import pytest
from models.core import MLMTree, CommissionCalculator


class TestMemoization:
    """Тести мемоізації - кожен вузол обробляється рівно 1 раз"""

    def test_memoization_simple_tree(self):
        """Тест що кожен партнер обробляється 1 раз в простому дереві"""
        data = [
            {"id": 1, "parent_id": None, "monthly_revenue": 3000},
            {"id": 2, "parent_id": 1, "monthly_revenue": 2000},
            {"id": 3, "parent_id": 1, "monthly_revenue": 1500},
            {"id": 4, "parent_id": 2, "monthly_revenue": 1000}
        ]

        tree = MLMTree(data)
        calculator = CommissionCalculator(tree)

        # Спочатку memo порожнє
        assert len(calculator.memo) == 0

        # Виконуємо розрахунок
        commissions = calculator.calculate_commissions()

        # Після розрахунку всі партнери повинні бути в memo
        assert len(calculator.memo) == 4
        assert set(calculator.memo.keys()) == {1, 2, 3, 4}

        # Перевіряємо що результати збережені
        for partner_id in [1, 2, 3, 4]:
            assert partner_id in calculator.memo
            assert isinstance(calculator.memo[partner_id], (int, float))

    def test_memoization_with_manual_dfs_calls(self):
        """Тест що повторні виклики _dfs() використовують кеш"""
        data = [
            {"id": 1, "parent_id": None, "monthly_revenue": 3000},
            {"id": 2, "parent_id": 1, "monthly_revenue": 2000}
        ]

        tree = MLMTree(data)
        calculator = CommissionCalculator(tree)

        # Перший виклик _dfs для партнера 2
        result1 = calculator._dfs(tree.partners[2])

        # Партнер 2 повинен бути в memo
        assert 2 in calculator.memo
        assert calculator.memo[2] == result1

        # Повторний виклик для того ж партнера
        result2 = calculator._dfs(tree.partners[2])

        # Результат має бути однаковим
        assert result1 == result2

        # Memo не змінилося (не було нових обчислень)
        assert calculator.memo[2] == result1

    def test_memoization_counter(self):
        """Тест підрахунку кількості реальних обчислень через patching"""
        from unittest.mock import patch

        data = [
            {"id": 1, "parent_id": None, "monthly_revenue": 3000},
            {"id": 2, "parent_id": 1, "monthly_revenue": 2000},
            {"id": 3, "parent_id": 2, "monthly_revenue": 1500}
        ]

        tree = MLMTree(data)
        calculator = CommissionCalculator(tree)

        # Лічильник викликів обчислень (не з кешу)
        computation_count = 0
        original_dfs = calculator._dfs

        def counting_dfs(partner):
            nonlocal computation_count
            # Якщо партнер не в кеші - це нове обчислення
            if partner.id not in calculator.memo:
                computation_count += 1
            return original_dfs(partner)

        # Підміняємо метод
        calculator._dfs = counting_dfs

        # Виконуємо розрахунок
        commissions = calculator.calculate_commissions()

        # Кількість обчислень = кількість партнерів
        assert computation_count == 3
        assert len(calculator.memo) == 3

    def test_memoization_deep_tree(self):
        """Тест мемоізації на глибокому дереві"""
        # Створюємо лінійне дерево: 1->2->3->4->5
        data = []
        for i in range(1, 6):
            parent_id = None if i == 1 else i - 1
            data.append({
                "id": i,
                "parent_id": parent_id,
                "monthly_revenue": 1000 * i
            })

        tree = MLMTree(data)
        calculator = CommissionCalculator(tree)

        # Розрахунок комісій
        commissions = calculator.calculate_commissions()

        # Всі 5 партнерів повинні бути в memo
        assert len(calculator.memo) == 5
        assert set(calculator.memo.keys()) == {1, 2, 3, 4, 5}

        # Листок (партнер 5) має результат 0
        assert calculator.memo[5] == 0

        # Кожен наступний включає суму попередніх
        assert calculator.memo[4] > 0  # включає дохід партнера 5
        assert calculator.memo[3] > calculator.memo[4]  # включає 4 і 5
        assert calculator.memo[2] > calculator.memo[3]  # включає 3, 4, 5
        assert calculator.memo[1] > calculator.memo[2]  # включає всіх

    def test_memoization_independence(self):
        """Тест що різні калькулятори мають незалежні memo"""
        data = [
            {"id": 1, "parent_id": None, "monthly_revenue": 3000},
            {"id": 2, "parent_id": 1, "monthly_revenue": 2000}
        ]

        tree = MLMTree(data)

        # Два різні калькулятори
        calc1 = CommissionCalculator(tree)
        calc2 = CommissionCalculator(tree)

        # Виконуємо розрахунки
        commissions1 = calc1.calculate_commissions()
        commissions2 = calc2.calculate_commissions()

        # Результати однакові
        assert commissions1 == commissions2

        # Але memo різні об'єкти
        assert calc1.memo is not calc2.memo
        assert calc1.memo == calc2.memo  # але з однаковим вмістом