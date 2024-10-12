import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader

def parse_farmer_daily():
    url = 'https://www.farmer.com.cn/farmer/xw/sntt/list.shtml'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_list = []

    news_elements = soup.select('div.list_con_c > ul > li')
    for news in news_elements:
        title_element = news.select_one('div.list_con_c_tit > a')
        title = title_element.text.strip()
        link = 'https://www.farmer.com.cn' + title_element['href']

        summary_element = news.select_one('div.list_con_c_zy')
        summary = summary_element.text.strip()

        pub_date_element = news.select_one('div.list_con_c_ly > span:first-child')
        pub_date = datetime.strptime(pub_date_element.text.strip(), '%Y-%m-%d %H:%M:%S')

        news_list.append({
            'title': title,
            'link': link,
            'summary': summary,
            'pub_date': pub_date
        })

    return news_list

def parse_fao_news():
    url = 'https://www.fao.org/newsroom/zh/news/rss.xml'
    feed = feedparser.parse(url)
    news_list = []

    for entry in feed.entries:
        news_list.append({
            'title': entry.title,
            'link': entry.link,
            'summary': entry.summary,
            'pub_date': datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
        })

    return news_list

def filter_news(news_list):
    news_list.sort(key=lambda x: x['pub_date'], reverse=True)
    return news_list[:12]

def render_template(news_list):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('news_template.html')
    return template.render(news_list=news_list)

def main():
    farmer_daily_news = parse_farmer_daily()
    fao_news = parse_fao_news()
    all_news = farmer_daily_news + fao_news
    filtered_news = filter_news(all_news)
    html_content = render_template(filtered_news)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == '__main__':
    main()
