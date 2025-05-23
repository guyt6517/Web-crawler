from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        start_url = request.form.get("url")
        max_depth = int(request.form.get("depth", 2))
        visited = set()

        def crawl(url, depth):
            if depth > max_depth or url in visited:
                return
            visited.add(url)
            try:
                response = requests.get(url, timeout=5)
                if 'text/html' not in response.headers.get('Content-Type', ''):
                    return
            except requests.RequestException:
                return

            soup = BeautifulSoup(response.text, 'html.parser')
            results.append(f"{'  '*depth}{url}")
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                crawl(full_url, depth + 1)
                time.sleep(0.2)

        crawl(start_url, 0)

    return render_template_string("""
        <h1>Web Spider</h1>
        <form method="post">
            URL: <input name="url" required><br>
            Max Depth: <input name="depth" type="number" value="2"><br>
            <input type="submit" value="Crawl">
        </form>
        {% if results %}
        <h2>Results</h2>
        <pre>{{ results|join('\\n') }}</pre>
        {% endif %}
    """, results=results)

if __name__ == "__main__":
    app.run(debug=True)
