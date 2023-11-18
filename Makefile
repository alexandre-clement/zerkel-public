.PHONY: $(MAKECMDGOALS)

IMAGE_NAME="zerkel"
CONTAINER_NAME="zerkel"

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Build and Run the container
	docker-compose up -d --build

start: ## Run the container
	docker-compose up -d

stop: ## Stop the container
	docker-compose stop

down: ## Stop and delete the container
	docker-compose down

remove: ## Remove the image
	docker rmi $(IMAGE_NAME)

test: ## Execute tests
	python -m unittest discover -s src

clean: clean-build clean-pyc clean-hooks clean-backend clean-gv ## Remove compiled files

clean-build:
	rm -fr **/build/
	rm -fr **/dist/
	rm -fr **/.eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-hooks:
	find . -name '*.coverage' -exec rm -f {} +

clean-backend:
	rm -fr backendservices/**/target/

clean-gv:
	find . -name '*.gv' -exec rm -f {} +
	find . -name '*.gv.*' -exec rm -f {} +


# Alias

docs: doc
documentation: doc
documentations: doc
build: up
run: start
uninstall: remove
tests: test
