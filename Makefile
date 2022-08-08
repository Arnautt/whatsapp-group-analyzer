venv_name = .venv

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build-env: ## Build virtual environment and install required packages
	virtualenv -p python3 $(venv_name)
	$(venv_name)/bin/pip3 install -Ur requirements.txt

app: ## Run the application
	. $(venv_name)/bin/activate; \
	streamlit run app.py

format-code:  ## Sort import statements in the right format ; Reformat code to be PEP8-aligned
	isort .; autopep8 --in-place -r src; autopep8 --in-place app.py

update-reqs: ## Update requirements file
	$(venv_name)/bin/pip3 freeze > requirements.txt
