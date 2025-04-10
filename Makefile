SERVICE_NAME=journey-booking
PORT=7444

.PHONY: build run stop logs

ensure-network:
	@if ! docker network ls | grep -q shared_network; then \
		echo "Creating shared_network..."; \
		docker network create shared_network; \
	else \
		echo "shared_network already exists."; \
	fi

build:
	docker build -t $(SERVICE_NAME) .

run:
	docker run -d -p $(PORT):7444 --name $(SERVICE_NAME) $(SERVICE_NAME)

stop:
	docker stop $(SERVICE_NAME) && docker rm $(SERVICE_NAME)

logs:
	docker logs -f $(SERVICE_NAME)

compose-up: ensure-nework
	docker-compose up -d --build

compose-down:
	docker-compose down

compose-logs:
	docker-compose logs -f

rebuild:
	$(MAKE) compose-down
	$(MAKE) compose-up