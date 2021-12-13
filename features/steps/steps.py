from features.helpers.docker import DockerBuild, Registry, LazyKanikoRun
from features.helpers.output import LogParser


@given(u'an empty docker registry')
def step_impl(context):
    context.registry = Registry()
    context.network.connect(context.registry.id)


@given(u'the Dockerfile and build context "{build_name}"')
def step_impl(context, build_name):
    context.build = DockerBuild(build_name)


@when(u'Dockerfile and build context are passed to lazy-kaniko')
def step_impl(context):
    context.lazy_kaniko = LazyKanikoRun(registry=context.registry, build=context.build)
    context.network.connect(context.lazy_kaniko.id)
    context.lazy_kaniko.execute()
    context.log_parser = LogParser(context.lazy_kaniko.logs())


@then(u'the new image exists in the docker registry')
def step_impl(context):
    from features.helpers.docker import client
    tag = context.log_parser.tag()
    image = context.build.name
    registry = context.registry.local_address
    client.images.get_registry_data(f"{registry}/{image}:{tag}")
