from dataclasses import dataclass

from optimization.model.base_model import BaseModel
from optimization.model.model_expander import ModelExpander
from optimization.model.sub_model import SubModel
from optimization.scenarios.changed_task_duration_scenario import (
    ChangedTaskDurationScenario,
)
from optimization.scenarios.scenario import Scenario


class ChangedTaskDurationsub_model(SubModel):
    s_advance: dict
    s_delay: dict
    s_t: dict

    def __init__(
        self,
        scenario: ChangedTaskDurationScenario,
        s_advance,
        s_delay,
        s_t,
        advance_costs,
        delay_costs,
    ):
        self.scenario = scenario
        self.task_duration = scenario.task_duration
        self.weight = scenario.weight
        self.name = f"Sub Model {scenario.name}"
        self.s_advance = s_advance
        self.s_delay = s_delay
        self.s_t = s_t
        self.advance_costs = advance_costs
        self.delay_costs = delay_costs

    def extract_variables(self):
        print(f"In scenario {self.name} with weight {self.weight}")
        for s in self.task_duration.keys():
            print(f"Task {s} ends at {self.s_t[s].solution_value() + self.task_duration[s]}")
            print(f"Task {s} is delayed by {self.s_delay[s].solution_value()}")
            print(f"Task {s} is advanced by {self.s_advance[s].solution_value()}")
            print(
                f"Sub objective Value: "
                f"advance: {self.s_advance[s].solution_value() * self.advance_costs[s]} \n"
                f"delay: {self.s_delay[s].solution_value() * self.delay_costs[s]} \n"
            )


class ChangedTaskDurationSubModelExpander(ModelExpander):
    def expand(self, base_model: BaseModel, scenario: ChangedTaskDurationScenario):
        sub_model = self.create_sub_model(base_model, scenario)
        self.add_sub_model(base_model, sub_model)
        self.add_sub_model_constraints(base_model, sub_model)
        self.add_sub_model_wighted_cost_objective(base_model, sub_model)

    @staticmethod
    def create_sub_model(model: BaseModel, scenario: ChangedTaskDurationScenario):
        s_advance = {}
        s_delay = {}
        s_t = {}
        for s in model.model_parameters.S:
            s_advance[s] = model.model.IntVar(
                0, model.end_date, f"{scenario.name}_s+_{s}"
            )
            s_delay[s] = model.model.IntVar(
                0, model.end_date, f"{scenario.name}_s-_{s}"
            )
            s_t[s] = model.model.IntVar(0, model.end_date, f"{scenario.name}_s_{s}")

        return ChangedTaskDurationsub_model(
            scenario,
            s_advance,
            s_delay,
            s_t,
            model.model_parameters.advance_costs,
            model.model_parameters.delay_costs,
        )

    def add_sub_model_constraints(
        self, model: BaseModel, sub_model: ChangedTaskDurationsub_model
    ):
        self.add_sub_model_overlap_constraints(model, sub_model)
        self._create_advance_constraints(model, sub_model)
        self._create_delay_constraints(model, sub_model)

    @staticmethod
    def add_sub_model_overlap_constraints(
        model: BaseModel, sub_model: ChangedTaskDurationsub_model
    ):
        for (s, r), j_sr in model.j.items():
            constraint_name = (
                f"{sub_model.name}_overlap_{s}_{r}_duration_"
                f"{model.model_parameters.task_duration[s]}"
            )

            model.model.Add(
                sub_model.s_t[s] + sub_model.task_duration[s]
                <= sub_model.s_t[r] + model.end_date * (1 - j_sr),
                constraint_name,
            )

    @staticmethod
    def _create_advance_constraints(
            model: BaseModel, sub_model: ChangedTaskDurationsub_model
    ):
        for s in model.model_parameters.S:
            model.model.Add(
                model.model_parameters.target_execution_times[s] - sub_model.s_t[s]
                <= sub_model.s_advance[s],
                f"advance_{s}",
            )

    @staticmethod
    def _create_delay_constraints(
            model: BaseModel, sub_model: ChangedTaskDurationsub_model
    ):
        for s in model.model_parameters.S:
            model.model.Add(
                sub_model.s_t[s] - model.model_parameters.target_execution_times[s]
                <= sub_model.s_delay[s],
                f"delay_{s}",
            )

    @staticmethod
    def add_sub_model_wighted_cost_objective(
        model: BaseModel, sub_model: ChangedTaskDurationsub_model
    ):
        for s in model.model_parameters.S:
            model.objective.SetCoefficient(
                sub_model.s_delay[s], model.model_parameters.delay_costs[s]
            )

            model.objective.SetCoefficient(
                sub_model.s_advance[s], model.model_parameters.advance_costs[s]
            )
