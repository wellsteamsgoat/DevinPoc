```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return {"status": "success", "message": "Application is running"}, 200

if __name__ == '__main__':
    # host='0.0.0.0' is required for Docker and external access
    app.run(host='0.0.0.0', port=5000)
```