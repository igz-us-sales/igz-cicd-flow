import importlib

import mlrun

IMAGE_REQUIREMENTS = ["PyGithub==1.59.0", "deepchecks==0.17.4"]


def assert_build():
    for module_name in IMAGE_REQUIREMENTS:
        name, version = module_name.split("==")
        module = importlib.import_module(name)
        print(module.__version__)
        assert module.__version__ == version


def create_and_set_project(
    name: str,
    source: str,
    default_image: str = None,
    default_base_image: str = "mlrun/mlrun:1.4.1",
    user_project: bool = False,
    env_file: str = None,
    force_build: bool = False,
):
    """
    Creating the project for this demo.
    :param source:                  the source of the project.
    :param name:                    project name
    :param default_image:           the default image of the project
    :param user_project:            whether to add username to the project name

    :returns: a fully prepared project for this demo.
    """

    # Set MLRun DB endpoint
    if env_file:
        mlrun.set_env_from_file(env_file=env_file)

    # Get / Create a project from the MLRun DB:
    project = mlrun.get_or_create_project(
        name=name, context="./", user_project=user_project
    )

    # Set or build the default image:
    if force_build or project.default_image is None:
        if default_image is None:
            print("Building default project image...")
            image_builder = project.set_function(
                func="src/project_setup.py",
                name="image-builder",
                handler="assert_build",
                kind="job",
                image=default_base_image,
            )
            build_status = project.build_function(
                function=image_builder,
                base_image=default_base_image,
                requirements=IMAGE_REQUIREMENTS,
            )
            default_image = build_status.outputs["image"]
        project.set_default_image(default_image)

    # Export project to zip if relevant
    if ".zip" in source:
        print(f"Exporting project as zip archive to {source}...")
        project.export(source)

    # Set the project source
    project.set_source(source, pull_at_runtime=True)

    # Set MLRun functions
    project.set_function(
        name="data",
        func="src/functions/data.py",
        kind="job",
        with_repo=True
    )
    project.set_function(
        name="describe",
        func="hub://describe",
        kind="job",
        handler="analyze",
    )
    project.set_function(
        name="train",
        func="src/functions/train.py",
        kind="job",
        handler="train_model",
        image=default_base_image,
    )
    project.set_function(
        name="validate",
        func="src/functions/validate.py",
        kind="job",
    )
    project.set_function(
        name="test",
        func="src/functions/test_classifier.py",
        kind="job",
        handler="test_classifier",
    )
    project.set_function(
        name="serving",
        func="hub://v2_model_server",
        kind="serving",
        image=default_base_image,
        requirements=IMAGE_REQUIREMENTS,
    )
    project.set_function(
        name="model-server-tester",
        func="hub://v2_model_tester",
        kind="job",
        handler="model_server_tester",
    )


    # Set MLRun workflows
    project.set_workflow(
        name="train", workflow_path="src/workflows/train_workflow.py"
    )
    project.set_workflow(
        name="deploy", workflow_path="src/workflows/deploy_workflow.py"
    )

    # Save and return the project:
    project.save()
    return project
