from features.helpers.docker import DockerBuild, Registry, LazyKanikoRun


@given(u'an empty docker registry')
def step_impl(context):
    context.registry = Registry()


@given(u'the Dockerfile and build context "{build_name}"')
def step_impl(context, build_name):
    context.build = DockerBuild(build_name)


@when(u'Dockerfile and build context are passed to lazy-kaniko')
def step_impl(context):
    context.lazy_kaniko = LazyKanikoRun(registry=context.registry, build=context.build)


@then(u'the new image exists in the docker registry')
def step_impl(context):
    from features.helpers.docker import client
    client.images.get("localhost:5000/simple")
