.PHONY: start

start:
	podman-compose --verbose --podman-run-args='--health-on-failure=restart' up -d

stop:
	podman-compose --verbose down -v
