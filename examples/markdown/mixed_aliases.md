# Pactfix Markdown - Alias language blocks

Ten plik testuje aliasy języków w fenced code blocks (`sh`, `py`, `js`, `tf`, `k8s`).

```sh
#!/bin/sh
cd /tmp
echo "ok"
```

```py
def process_data(items=[]):
    if items == None:
        print "items is None"
    try:
        return items
    except:
        return []
```

```js
var x = 1
if (x == 1) {
  console.log(x)
}
```

```tf
provider "aws" {
  region     = "eu-west-1"
  access_key = "AKIAEXAMPLE"
  secret_key = "SECRETEXAMPLE"
}

resource "aws_s3_bucket" "b" {
  bucket = "my-bucket"
  acl    = "public-read"
}
```

```k8s
apiVersion: v1
kind: Pod
metadata:
  name: demo
  namespace: default
spec:
  containers:
  - name: app
    image: nginx:latest
    securityContext:
      privileged: true
```
