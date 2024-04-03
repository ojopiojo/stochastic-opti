from optimization.scenarios.scenario_generator_strategy import ScenarioGeneratorStrategy


class ExhaustiveScenarioGeneratorStrategy(ScenarioGeneratorStrategy):
    @staticmethod
    def generate_scenarios(scenario_generator, instance):
        scenarios = []
        for index in scenario_generator.index_iterator():
            scenarios.append(scenario_generator.generate_by_index(index))

        return scenarios
