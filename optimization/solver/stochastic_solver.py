from optimization.domain.instance import Instance
from optimization.model.base_model import BaseModel
from optimization.model.model_expander import ModelExpander
from optimization.solver.model_parameters import ModelParametersBuilder
from optimization.solver.solver import Solver


class StochasticSolver(Solver):
    def __init__(
        self,
        scenario_generator,
        scenario_generation_strategy,
        model_parameters_builder: ModelParametersBuilder,
        model_expander: ModelExpander,
    ):
        self.scenario_generator = scenario_generator
        self.scenario_generation_strategy = scenario_generation_strategy
        self.model_parameters_builder = model_parameters_builder
        self.model_expander = model_expander

    def solve(self, instance: Instance):
        scenarios = self.scenario_generation_strategy.generate_scenarios(
            self.scenario_generator, instance
        )

        model_parameters = self.model_parameters_builder.build(instance)
        base_model = BaseModel(model_parameters)
        for scenario in scenarios:
            self.model_expander.expand(base_model, scenario)
        base_model.solve()
