<div align="center">
<img src="static/img/logo.png" width="100">
</div>

# VirusScan Web

This is a web application to scan files for viruses using ClamAV.

## Quick Start

### Running the Application

1. Clone the repository:

```bash
git clone https://github.com/security-dev/virusscan-web.git
```

2. Navigate to the project directory:

```bash
cd virusscan-web
```

3. Run the following command to run the application:

```bash
make run
```

### Settings

The application settings are stored in the `.env` file. You can copy the `.env.example` file and modify the settings as
needed.

## Tech stack

- Python 3.12
- Django
- django-ninja
- ClamAV
- Celery
- Redis
- Docker

## Development

To start the development environment, run the following commands:

```bash
make build
make start
```

This will build the development environment and start the containers.

To generate the correct styles for the frontend, run the following command:

```bash
npx @tailwindcss/cli -i ./frontend/input.css -o ./static/css/styles.css --watch
```

To stop the containers, run the following command:

```bash
make stop
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes and commit them.
4. Push your changes to your fork.
5. Create a pull request.

## License

This project is licensed under the Apache-2.0 License.