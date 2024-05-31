import docker


def deploy_container(
    image_name, container_name, ports=None, volumes=None, environment=None
):
    # Create a Docker client
    client = docker.from_env()

    # Pull the specified image
    # client.images.pull(image_name)

    # Run a container
    container = client.containers.run(
        image_name,
        name=container_name,
        ports=ports,
        volumes=volumes,
        environment=environment,
        detach=True,
        network_mode="host",
    )
    return container
