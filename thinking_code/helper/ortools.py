from collections.abc import Mapping, Sequence
from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpModel, CpSolver, CpSolverSolutionCallback, BoundedLinearExpression


def process_nested_struct(data, func):
    if isinstance(data, Mapping):  # If it's a dictionary, process values recursively
        return {key: process_nested_struct(value, func) for key, value in data.items()}
    elif isinstance(data, Sequence) and not isinstance(data, (str, bytes)):  # If it's a list or tuple
        return type(data)(process_nested_struct(item, func) for item in data)
    else:  # Base case: apply function to individual elements
        return func(data)


class AllSolutions(CpSolverSolutionCallback):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.solutions = []

    def OnSolutionCallback(self):
        if isinstance(self.model, CpModel):
            solution = {var.name: self.SolutionIntegerValue(i) for i, var in enumerate(self.model.proto.variables)}
        else:
            solution = process_nested_struct(self.model, self.Value)
        self.solutions.append(solution)


def get_all_solutions(model, variables=None):
    solver = CpSolver()
    solver.parameters.enumerate_all_solutions = True
    if variables is None:
        variables = model
    solutions = AllSolutions(variables)
    solver.solve(model, solutions)
    return solutions.solutions


def get_circuit(solution):
    solution = {s:e for (s, e), v in solution.items() if v and s != e}
    start = next(iter(solution.keys()))
    path = [start]
    while True:
        start = solution[start]
        if start in path:
            break
        path.append(start)
    return path

def equals(b, expr, model):
    if not isinstance(expr, cp_model.BoundedLinearExpression):
        raise TypeError("expr must be a BoundedLinearExpression.")
    
    expr_var = cp_model.LinearExpr.weighted_sum(expr.vars, expr.coeffs) + expr.offset
    bounds = expr.bounds.complement()
    negated_expr = cp_model.BoundedLinearExpression(expr_var, bounds)
    model.Add(expr).only_enforce_if(b)
    model.Add(negated_expr).only_enforce_if(~b)       

def is_between(expr, lb, ub):
    domain = cp_model.Domain.from_flat_intervals([lb, ub])
    return cp_model.BoundedLinearExpression(expr, domain)

def is_not_between(expr, lb, ub):
    domain = cp_model.Domain.from_flat_intervals([cp_model.INT_MIN, lb - 1, ub + 1, cp_model.INT_MAX])
    return cp_model.BoundedLinearExpression(expr, domain)

def create_circuit_model(edges, include_edges=[]):
    edges = set(edges)
    model = cp_model.CpModel()
    if include_edges:
        for edge in include_edges:
            if edge not in edges:
                edges.add(edge)
    variables = {key:model.new_bool_var(str(key)) for key in edges}
    if include_edges:
        model.add_bool_and([variables[edge] for edge in include_edges])
    model.add_circuit([(s, e, v) for (s, e), v in variables.items()])
    return model, variables

def get_circuit(solution, start=None):
    # 回路の形成に使われる辺のうち、回路に含まれるものを選択し、自己ループは除外
    solution = {s: e for (s, e), v in solution.items() if v and s != e}
    if start is None:
        start = next(iter(solution.keys()))  # 開始頂点を設定（デフォルトでは最初の頂点）
    path = [start]
    while True:
        if start not in solution:
            break  # 回路が完成したので終了
        start = solution[start]
        if start in path:
            break  # 回路が閉じたので終了
        path.append(start)
    return path

def find_all_circuits(edges, include_edges=[], start=None):
    model, variables = create_circuit_model(edges, include_edges)
    solutions = get_all_solutions(model, variables)  # 解のリストを取得
    return [get_circuit(sol, start) for sol in solutions]  # 各解に対して回路を求める

def find_one_circuit(edges, include_edges=[], start=None):
    model, variables = create_circuit_model(edges, include_edges)
    solver = cp_model.CpSolver()
    solver.solve(model)  # 最適解を求める
    sol = {key: solver.value(v) for key, v in variables.items()}  # 解を取得
    return get_circuit(sol, start)  # 回路を取得    