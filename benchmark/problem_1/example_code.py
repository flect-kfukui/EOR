import pyomo.environ as pyo

# Parameters Section Begin
# Define model parameters
production_lines = ["A", "B"]
tasks = [1, 2, 3]

# Minimum and maximum energy efficiency consumption (kw) for each task
min_energy_consumption = {1: 10, 2: 15, 3: 12}
max_energy_consumption = {1: 20, 2: 25, 3: 22}

# Energy consumption cost per unit (yuan/kw)
energy_cost_per_unit = {1: 5, 2: 4, 3: 6}

# Production cost per unit (yuan/piece)
production_cost_per_unit = {1: 30, 2: 35, 3: 32}

# Production quantity required for each task (pieces)
production_quantity = {1: 300, 2: 200, 3: 250}

# Total production capacity for each production line (pieces)
production_capacity = {"A": 400, "B": 350}
# Parameters Section End


# ORExplainer DATA CODE GOES HERE


# ORExplainer DATA CODE ENDS HERE


# Create a Pyomo model
m: pyo.ConcreteModel = pyo.ConcreteModel()  # type: ignore

# Decision Variables Section Begin
# Create decision variables x[i, j] for production quantity of production line i
# for completing production task j
m.x = pyo.Var(production_lines, tasks, domain=pyo.NonNegativeIntegers)
# Decision Variables Section End


# Objective Function Section Begin
# Set the objective function to minimize total energy consumption and production cost


def objective_rule(model):
    return sum(
        energy_cost_per_unit[j] * min_energy_consumption[j] * model.x[i, j]
        + production_cost_per_unit[j] * model.x[i, j]
        for i in production_lines
        for j in tasks
    )


m.obj = pyo.Objective(rule=objective_rule, sense=pyo.minimize)
# Objective Function Section End


# ORExplainer CONSTRAINTS CODE GOES HERE


# Constraints Section Begin
# Constraint: The production quantity for each task must meet the demand
def production_quantity_rule(model, j):
    return sum(model.x[i, j] for i in production_lines) == production_quantity[j]


m.production_quantity_constraints = pyo.Constraint(tasks, rule=production_quantity_rule)

# Constraint: The task allocation for each production line must not exceed
# its total production capacity


def production_capacity_rule(model, i):
    return sum(model.x[i, j] for j in tasks) <= production_capacity[i]


m.production_capacity_constraints = pyo.Constraint(
    production_lines, rule=production_capacity_rule
)

# Constraint: The energy usage for each production task is within the minimum
# and maximum energy efficiency consumption standards
# Note: The original constraint was redundant as written - removing it since
# min <= max is always true. If you need actual energy consumption constraints,
# they should be like:
# energy_consumed[i,j] >= min_energy_consumption[j] * x[i,j]
# energy_consumed[i,j] <= max_energy_consumption[j] * x[i,j]
# Constraints Section End


# ORExplainer CONSTRAINTS CODE MIDDLE HERE


# ORExplainer CONSTRAINTS CODE ENDS HERE


# Solving the Model Section Begin
# Solve the model
solver = pyo.SolverFactory("cbc")  # Using CBC solver (open source)
result = solver.solve(m)

# Output the results
if result.solver.termination_condition == pyo.TerminationCondition.optimal:
    print(
        "Minimum total energy consumption and production cost: " f"{pyo.value(m.obj)}"
    )
    for i in production_lines:
        for j in tasks:
            print(
                f"Production line {i} completes production task {j} "
                f"with a production quantity of: {pyo.value(m.x[i, j])}"
            )
else:
    print("No optimal solution found.")
# Solving the Model Section End
