from behave.model_core import Status


def after_scenario(context, scenario):
    if scenario.status == Status.failed and hasattr(context, "lazy_kaniko"):
        print(context.lazy_kaniko.debug())
