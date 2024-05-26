.PHONY: start

start:
	podman-compose --verbose --podman-run-args='--health-on-failure=restart' up --build -d

stop:
	podman-compose --verbose down -v
