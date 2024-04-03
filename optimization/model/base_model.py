from ortools.linear_solver import pywraplp

from optimization.solver.base_model_parameters import BaseModelParameters


class BaseModel:


    def __init__(self, model_parameters: BaseModelParameters):
        self.model_parameters = model_parameters
        self.end_date = self.model_parameters.end_date
        self.model = pywraplp.Solver.CreateSolver("SCIP")
        self.variables = {}
        self.constraints = {}
        self.objective = None
        self._create_variables()
        self._create_constraints()
        self._create_objective()
        self.sub_models = {}

    def _create_variables(self):
        self.y = {}
        self.j = {}
        self.s_advance = {}
        self.s_delay = {}
        self.s_t = {}

        for m, t in self.model_parameters.y:
            self.y[m, t] = self.model.IntVar(0, 1, f"y_{m}_{t}")

        for s, t in self.model_parameters.j:
            self.j[s, t] = self.model.IntVar(0, 1, f"j_{s}_{t}")

        for s in self.model_parameters.S:
            self.s_advance[s] = self.model.IntVar(0, self.end_date, f"s+_{s}")
            self.s_delay[s] = self.model.IntVar(0, self.end_date, f"s-_{s}")
            self.s_t[s] = self.model.IntVar(0, self.end_date, f"s_{s}")

    def _create_constraints(self):
        self._create_overlap_constraints()
        self._create_advance_constraints()
        self._create_delay_constraints()
        self._create_machine_assignment_constraints()
        self._create_asymmetric_task_sequence_constraints()
        self._create_task_sequence_requirement_constraints()

    def _create_overlap_constraints(self):
        for (s, r), j_sr in self.j.items():
            self.model.Add(
                self.s_t[s] + self.model_parameters.task_duration[s]
                <= self.s_t[r] + self.end_date * (1 - j_sr),
                f"overlap_{s}_{r}_duration_{self.model_parameters.task_duration[s]}",
            )

    def _create_advance_constraints(self):
        for s in self.model_parameters.S:
            self.model.Add(
                self.model_parameters.target_execution_times[s] - self.s_t[s]
                <= self.s_advance[s],
                f"advance_{s}",
            )

    def _create_delay_constraints(self):
        for s in self.model_parameters.S:
            self.model.Add(
                self.s_t[s] - self.model_parameters.target_execution_times[s]
                <= self.s_delay[s],
                f"delay_{s}",
            )

    def _create_machine_assignment_constraints(self):
        for s in self.model_parameters.S:
            constraint_expr = []
            for m in self.model_parameters.M:
                if (m, s) in self.y:
                    constraint_expr.append(self.y[m, s])

            self.model.Add(sum(constraint_expr) == 1)

    def _create_asymmetric_task_sequence_constraints(self):
        for s in self.model_parameters.S:
            for t in self.model_parameters.S:
                if s != t and (s, t) in self.j and (t, s) in self.j:
                    self.model.Add(
                        self.j[s, t] + self.j[t, s] <= 1,
                        f"asymmetric_task_sequence_{s}_{t}",
                    )

    def _create_task_sequence_requirement_constraints(self):
        for s in self.model_parameters.S:
            for t in self.model_parameters.S:
                if s != t and (s, t) in self.j and (t, s) in self.j:
                    for m in self.model_parameters.M:
                        if (m, s) in self.y and (m, t) in self.y:
                            self.model.Add(
                                self.y[m, s] + self.y[m, t] - 1
                                <= self.j[s, t] + self.j[t, s],
                                f"task_sequence_requirement_{s}_{t}_{m}",
                            )

    def _create_objective(self):
        self.objective = self.model.Objective()
        for s in self.model_parameters.S:
            self.objective.SetCoefficient(
                self.s_advance[s], self.model_parameters.advance_costs[s]
            )
            self.objective.SetCoefficient(
                self.s_delay[s], self.model_parameters.delay_costs[s]
            )

    def solve(self):

        status = self.model.Solve()

        if status == pywraplp.Solver.OPTIMAL:
            return self._extract_variables()

        else:
            print("The problem does not have an optimal solution.")
            return None

    def _extract_variables(self):
        print("Solution:")
        print("Objective value =", self.model.Objective().Value())
        for s in self.model_parameters.S:
            for m in self.model_parameters.M:
                if self.y[m, s].solution_value() > 0:
                    print(f"Task {s} is assigned to machine {m}")

        for s in self.model_parameters.S:
            for r in self.model_parameters.S:
                if r != s and self.j[s, r].solution_value() > 0:
                    print(f"Task {s} is executed before task {r}")

        for s in self.model_parameters.S:
            print(f"Task {s} starts at {self.s_t[s].solution_value()}")

        for s in self.model_parameters.S:
            print(
                f"Task {s} ends at {self.s_t[s].solution_value() + self.model_parameters.task_duration[s]}"
            )

        for s in self.model_parameters.S:
            print(f"Task {s} is delayed by {self.s_delay[s].solution_value()}")

        for s in self.model_parameters.S:
            print(f"Task {s} is advanced by {self.s_advance[s].solution_value()}")

        for name, sub_model in self.sub_models.items():
            print(f"\n\nSub model {name}: ")
            sub_model.extract_variables()
