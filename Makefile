SERVICE_NAME=journey-booking
PORT=7444

.PHONY: build run stop logs

build:
	docker build -t $(SERVICE_NAME) .

run:
	docker run -d -p $(PORT):7444 --name $(SERVICE_NAME) $(SERVICE_NAME)

stop:
	docker stop $(SERVICE_NAME) && docker rm $(SERVICE_NAME)

logs:
	docker logs -f $(SERVICE_NAME)
