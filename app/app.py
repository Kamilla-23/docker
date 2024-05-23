import time
import redis
from flask import Flask, render_template, send_from_directory
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)
cache = redis.Redis(host='srv-captain--redis', port=6379)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name= "BIPM", count = count)

@app.route('/titanic')
def titanic():
    data = pd.read_csv('static/titanic.csv')
    first_five_rows = data.head(5).to_html(index=False)
    return render_template('titanic.html', tables=first_five_rows)

def create_figure(data):
    fig, ax = plt.subplots()
    survival_counts = data.groupby(['sex', 'survived']).size().unstack()
    survival_counts.plot(kind='bar', stacked=True, ax=ax)
    ax.set_title('Survival Counts by Gender')
    ax.set_xlabel('Sex')
    ax.set_ylabel('Count')
    plt.tight_layout()

    # Save to static directory
    path = os.path.join('static', 'plot.png')
    fig.savefig(path)
    plt.close(fig)  # Close the figure to free up memory
    return path

@app.route('/plot.png')
def plot_png():
    data = pd.read_csv('titanic.csv')
    image_path = create_figure(data)  # This now returns a path
    return send_from_directory('static', 'plot.png', as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)



