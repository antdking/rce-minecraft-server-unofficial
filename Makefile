.PHONY: start

start:
	podman-compose --verbose --podman-run-args='--health-on-failure=restart' up --pull --build -d

stop:
	podman-compose --verbose down -v

logs:
	podman-compose logs -f --tail 150 mc playit
