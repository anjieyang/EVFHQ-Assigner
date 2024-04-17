# EVFHQ-Assigner

EVFHQ-Assigner distributes video download tasks across multiple servers to optimize load and efficiency by RabbitMQ.

## DockerHub Repository

You can find the [Docker image](https://hub.docker.com/repository/docker/anjieyang/evfhq-assigner/general) for EVFHQ-Assigner on DockerHub.

## Deployment Configurations

### Local Build Deployment with Docker Compose

For deploying EVFHQ-Assigner using Docker Compose and building the Docker image locally, you can use the provided `docker-compose.yml` file.

### DockerHub Deployment

If you prefer a quick and straightforward deployment using the Docker image from DockerHub.

1. Download [dockerhub_deploy.yml](https://drive.google.com/uc?export=download&id=1-dV7tm9kfEqW2XNfFHhx8ha6SCWr78wo).

2. Replace the placeholder values (`your_db_host`, `your_db_name`, `your_db_user`, `your_db_password`, `your_db_port`, `your_rabbitmq_host`, `your_rabbitmq_port`) with your actual configurations.

3. Run the following command to start the EVFHQ-Fetcher service:

```bash
docker-compose -f dockerhub_deploy.yml up -d
```
