from behave.model_core import Status
from features.helpers.docker import setup_networking


def before_all(context):
    context.network = setup_networking()


def after_all(context):
    context.network.remove()


def after_scenario(context, scenario):
    if scenario.status == Status.failed and hasattr(context, "lazy_kaniko"):
        print(context.lazy_kaniko.debug())
