# django-ecommerce
Welcome to the E-Commerce REST API Dockerized project! This repository contains a RESTful API for an e-commerce application, packaged with Docker for easy deployment and management. This README will guide you through the process of cloning and setting up the project.

### Prerequisites
Before you begin, ensure you have the following installed on your system:
- Docker:[Installation Guide] (https://www.docker.com/get-started/)
- Git: [Installation Guide] (https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### Clone the Repository
To clone the repository, open your terminal and run the following command:

`git clone https://github.com/fathimaNasmin/django-ecommerce.git`

### Setup
Once you have cloned the repository, navigate into the project directory:

`cd django-ecommerce`

### Docker Compose
This project utilizes Docker Compose to manage multi-container Docker applications. To build and start the Docker containers, run the following command:

`docker-compose up --build`

### Accessing the API
Once the Docker containers are up and running, you can access the API endpoints by navigating to http://localhost:8000 in your web browser or using an API testing tool such as Postman or curl.

### API Documentation
For detailed documentation on the API endpoints and usage, refer to the API documentation provided in the docs directory or visit http://localhost:8000/docs after starting the containers.

### Shutting Down
To stop and remove the Docker containers, use the following command:

`docker-compose down`

This command will stop the containers and remove the associated volumes.

### Contributions
Contributions to this project are welcome! If you find any issues or have suggestions for improvements, please feel free to open an issue or create a pull request.

***
Thank you for using the E-Commerce REST API Dockerized project! If you have any questions or need further assistance, feel free to reach out. Happy coding! 🚀
