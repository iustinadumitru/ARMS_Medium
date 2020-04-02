import re
import json
import requests
from urllib.parse import quote

# get_stories_url = r'https://medium.com/search?q=atificial%20intelligence'
# get_people_url = r'https://medium.com/search/users?q=atificial%20intelligence'
# get_publications_url = r'https://medium.com/search/publications?q=atificial%20intelligence'
# get_tags_url = r'https://medium.com/search/tags?q=atificial%20intelligence'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
}


def get_uniqe(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def get_stories(info):
    get_stories_url = r'https://medium.com/search?q={}'.format(quote(info))
    r = requests.get(get_stories_url, headers=HEADERS)
    text = r.text
    stories = [_ for _ in re.findall('href="([^"]+\?source=search_post-*\d+)"', text) if
               not re.search('https://medium.com/@[^/]+\?source=search_post-*\d+', _)]
    stories = get_uniqe(stories)
    # print(stories)
    return stories


def get_people(info):
    get_people_url = 'https://medium.com/search/users?q={}'.format(quote(info))
    r = requests.get(get_people_url, headers=HEADERS)
    text = r.text
    usernames = get_uniqe(re.findall('href="https://medium.com/(@[^"]+)" property="cc:attributionName"', text))
    profile_pictures = get_uniqe(re.findall('img\s*src="([^"]+)"\s*class="avatar-image avatar-image--small"', text))
    user_info = zip(usernames, profile_pictures)
    # print(*user_info)
    return list(user_info)


def get_publications(info):
    get_publications_url = r'https://medium.com/search/publications?q={}'.format(quote(info))
    r = requests.get(get_publications_url, headers=HEADERS)
    text = r.text
    publications = get_uniqe(re.findall('href="([^"]+\?source=search_collection)"', text))
    # print(*publication_info)
    return publications


def get_tags(info):
    get_tags_url = r'https://medium.com/search/tags?q={}'.format(quote(info))
    r = requests.get(get_tags_url, headers=HEADERS)
    text = r.text
    if 'We couldn’t find any tags' in text:
        return list()
    tags = get_uniqe(re.findall('href="https://medium.com/tag/([^"]+)\?source=search"', text))
    # print(tags)
    return tags


def get_topics():
    topics_url = r'https://cdn-client.medium.com/lite/static/js/screen.home.3fbabd04.chunk.js'
    r = requests.get(topics_url, headers=HEADERS)
    text = r.text
    topics = re.findall('label:"([^"]+)"\s*,\s*type:"[^"]+"', text)
    topics = [t.strip().lower() for t in topics]
    # if not topics:
    #     with open(r'.\medium_info\medium_topics.json', 'r') as fh:
    #         topics = json.load(fh)
    # print(topics)
    return topics


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
    with open(r'.\medium_info\medium_statistics.json', 'w+') as fh:
        json.dump(stats, fh, indent=4)


def convert_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text]).strip()


def make_gephi_graph(stats):
    gephi_graph = dict()
    for topic, topic_info in stats.items():
        gephi_graph[topic] = list()
        stories_list = topic_info['stories']
        print("TOPIC IS {}".format(topic))
        for story in stories_list:
            title = None
            try:
                page_content = requests.get(story, headers=HEADERS).text
                r1 = re.search(r'<h1[^>]*>\s*([^<]+)\s*</h1>', page_content)
                r2 = re.search(r'collectionDescription"[^>]*>\s*([^<]+)<\s*', page_content)
                r3 = re.search(r'title"\s*content="([^"]+)"', page_content)
                if r1:
                    title = r1.group(1)
                elif r2:
                    title = r2.group(1)
                elif r3:
                    title = r3.group(1)
            except Exception as e:
                continue
            if not title: continue
            gephi_graph[topic].append(title)

    with open(r'.\medium_info\gephi_graph.csv', 'w+') as fh:
        for topic, topic_info in gephi_graph.items():
            try:
                text = '"{}";'.format(topic)
                for t in topic_info:
                    t = convert_ascii(t)
                    text += '"{}";'.format(t)
                text = text[:-1]
                fh.write(text + '\n')
            except Exception as e:
                print(topic, topic_info, repr(e))


if __name__ == '__main__':
    pass
    info = 'artificial intelligence'
    # get_stories(info)
    # get_people(info)
    # get_publications(info)
    # get_tags(info)
    # get_topics()
    # make_statistics()
    # make_gephi_graph()
