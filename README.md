# ai-driven-interview-system
AI-Driven Interview System: 
1-Day Prototype Goal Build a minimal prototype of an AI-Driven Interview System that: 
- Dynamically generates a small set of interview questions.
- Evaluates and scores the candidate’s responses.
- Produces basic feedback.


## SETUP

### Requirements management

 
**uv** is an extremely fast Python package installer and resolver, written in Rust, and designed as a drop-in replacement for pip and pip-tools workflows. To install it you can run 
```{bash}
pip install uv``` or ``` curl -LsSf https://astral.sh/uv/install.sh | sh 
```
To setup a virtual environment with uv run

```{bash}
uv venv .venv
```

The requirements are managed using `uv pip compile`. To add a new package to the requirements:

- First add it to `requirements/core_packages.in`.
- Then regenerate `requirements.txt` using:

  ```{bash}
  uv pip compile requirements/core_packages.in -o requirements.txt
  ```
To install the generated requirements run:
```{bash}
uv pip install -r requirements.txt
```

#### Updating the requirements periodically:

It is important to update the requirements periodically to ensure that the project is using the latest versions of the packages. To do this, run the following command:

```{bash}
pip-compile -U requirements/core_packages.in -o requirements.txt
```

(Note the `-U` flag which updates the packages to the latest versions)


#### Setting the environments variables

Create a new `.env` in the project root directory and copy the content of the `.env_sample` file, set the environment variables values accordingly

#### Runing the project 

When you are ready with the `.env` file execute in the project root directory

```{bash}
docker-compose up --build
```

You should see three service building and running `db`, `backend` and `admin`. The `admin` service is a simple CMS on which you can see the data stored from accessing and consuming the API, it is available on http://localhost:8002/admin/ You can browse and test the available API endpoints on http://localhost:8000/docs you should see two endpoints available there `/interview/start` and `/interview/submit`. 

#### Running unit tests
To run the unit tests attach to the backend container by executing in the project root directory:
```{bash}
docker-compose exec backend bash
``` 

Once you are in the container activate the virtual environment runnig 
```{bash}
source .venv/bin/activate
```
And after that run 
```{bash}
pytest -vv
```
