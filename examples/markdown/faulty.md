# Pactfix Markdown Example

Ten plik zawiera wiele codeblocków w różnych językach.

```bash
#!/bin/bash
cd /tmp
echo $VAR
```

```python
print "Hello from Python 2 style"
try:
    x = 1
except:
    pass
```

```javascript
var x = 1
if (x == 1) {
  console.log(x)
}
```

```dockerfile
FROM ubuntu
RUN apt-get install -y python3
ADD app.py /app/
WORKDIR app
ENV API_KEY=secret
CMD python3 app.py
```
