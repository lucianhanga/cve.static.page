# cve.static.page
generate a static webpage with the CVEs for a specified software version

build the docker image:

```bash
docker image build -t cve.static.page .
```

run the docker image:

```bash
docker container run -d -p 80:80 cve.static.page
```

run check:

```bash
curl http://localhost:80
```

list all the softwares configured using the REST API.

```bash
curl -X GET http://localhost:80/api/v1/registered
```

add a new software to the list using the REST API POST.

```bash
curl -X POST http://localhost:80/api/v1/register -H \
"Content-Type: application/json" \
-d '{"product":"jira_server","version":"9.1.0"}'
```

run it in the development environment not in docker:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```
