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


@given(u'the docker registry already has the tag for the build')
def step_impl(context):
    # TODO - refactor this so there's a class /methods encapsulating more of this logic
    from features.helpers.docker import client
    tag = context.build.tag
    image_name = context.build.name
    registry = context.registry.local_address
    img = client.images.pull(f"hello-world")
    img.tag(f"{registry}/{image_name}:{tag}")
    client.images.push(f"{registry}/{image_name}:{tag}")


@then(u'lazy-kaniko logs that it skipped the build')
def step_impl(context):
    assert context.log_parser.skipped_build()
