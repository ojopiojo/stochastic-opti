from abc import ABC


class ModelExpander(ABC):
    def expand(self, model, scenario):
        raise NotImplementedError

    @staticmethod
    def add_sub_model(model, sub_model):
        model.sub_models[sub_model.name] = sub_model
