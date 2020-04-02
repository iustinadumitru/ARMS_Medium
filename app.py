import os
from urllib.parse import quote, unquote
from werkzeug.datastructures import ImmutableMultiDict
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, redirect, url_for, json
from get_info import get_topics, get_stories, get_people, get_publications, get_tags, make_gephi_graph


def make_statistics():
    stats = dict()
    topics = get_topics()
    for topic in topics:
        stats[topic] = {
            'stories': get_stories(topic)[:10],
            'people': get_people(topic)[:10],
            'publications': get_publications(topic)[:10],
            'tags': get_tags(topic)[:10]
        }
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    statistics_location = os.path.join(SITE_ROOT, "static/data/medium_statistics.json")
    with open(statistics_location, 'w+') as fh:
        json.dump(stats, fh, indent=4)
    make_gephi_graph(stats)


def job_function():
    make_statistics()


app = Flask(__name__)

scheduler = BackgroundScheduler(daemon=True)

scheduler.start()

scheduler.add_job(job_function, "interval", minutes=10)


def get_medium_info():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data/medium_statistics.json")
    data = json.load(open(json_url))
    return data


@app.route('/')
@app.route('/topics/')
def index():
    topics = get_topics()
    return render_template("index.html", topics=topics)


@app.route('/topics/<string:topic>/', methods=['GET', 'POST'])
def showTopic(topic):
    topic = unquote(topic)
    data = get_medium_info()
    if request.method == 'POST':
        return redirect(url_for('index'))
    else:
        # print(data.get(topic))
        return render_template('index.html', topic_info=data.get(topic))


@app.route('/search')
def search():
    imd = ImmutableMultiDict(request.args)
    imd = imd.to_dict(flat=False)
    q = imd.get('q')[0]
    if q:
        return redirect('https://medium.com/search?q={}'.format(quote(q)))
    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.debug = True
    app.run(port=4900)
