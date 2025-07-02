from decimal import Decimal, ROUND_HALF_UP
from utils.benchmark import benchmark


class Partner:
    def __init__(self, id, parent_id, monthly_revenue):
        self.id = id
        self.parent_id = parent_id
        self.monthly_revenue = monthly_revenue
        self.children = []

    def daily_revenue(self):
        return self.monthly_revenue / 30


class MLMTree:
    def __init__(self, partners_data):
        self.partners = self._build_partners(partners_data)
        self._build_tree()
        self._check_for_cycles()

    def _build_partners(self, data):
        return {p["id"]: Partner(p["id"], p["parent_id"], p["monthly_revenue"]) for p in data}

    def _build_tree(self):
        for partner in self.partners.values():
            if partner.parent_id is not None:
                parent = self.partners.get(partner.parent_id)
                if parent:
                    parent.children.append(partner)

    def _check_for_cycles(self):
        visited = set()
        rec_stack = set()

        def dfs(partner_id):
            visited.add(partner_id)
            rec_stack.add(partner_id)
            for child in self.partners[partner_id].children:
                if child.id not in visited:
                    dfs(child.id)
                elif child.id in rec_stack:
                    raise ValueError(f"Cycle detected at partner {child.id}")
            rec_stack.remove(partner_id)

        for pid in self.partners:
            if pid not in visited:
                dfs(pid)


class CommissionCalculator:
    def __init__(self, tree: MLMTree):
        self.tree = tree
        self.memo = {}

    @benchmark()
    def calculate_commissions(self):
        result = {}
        for pid, partner in self.tree.partners.items():
            commission = Decimal(str(0.05 * self._dfs(partner))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            result[str(pid)] = float(commission)
        return result

    def _dfs(self, partner: Partner):
        if partner.id in self.memo:
            return self.memo[partner.id]

        total = 0
        for child in partner.children:
            total += child.daily_revenue()
            total += self._dfs(child)

        self.memo[partner.id] = total
        return total
