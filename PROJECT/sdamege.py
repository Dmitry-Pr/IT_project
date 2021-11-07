import requests
from bs4 import BeautifulSoup


def get_problem_by_id(id):
    """Getting information about the task by its id.
    The method does almost the same as the so called
    method from sdamgia lib, but fixes some bugs in it
    and works only for history subject.
    """
    base_url = 'https://hist-ege.sdamgia.ru'
    doujin_page = requests.get(
        f'https://hist-ege.sdamgia.ru/problem?id={id}')
    soup = BeautifulSoup(doujin_page.content, 'html.parser')

    probBlock = soup.find('div', {'class': 'prob_maindiv'})
    if probBlock is None:
        return None
    for i in probBlock.find_all('img'):
        if not 'sdamgia.ru' in i['src']:
            i['src'] = base_url + i['src']

    URL = f'{base_url}/problem?id={id}'
    TOPIC_ID = ' '.join(probBlock.find(
        'span', {'class': 'prob_nums'}).text.split()[1:][:-2])
    ID = id

    CONDITION, SOLUTION = {}, {}

    try:
        images = [i['src'] for i in probBlock.find_all('div', {'class': 'pbody'})[0].find_all('img')]
        if probBlock.find_all('div', {'class': 'probtext'}):
            images += [i['src'] for i in probBlock.find_all('div', {'class': 'probtext'})[0].find_all('img')]
        CONDITION = {'text': probBlock.find_all('div', {'class': 'pbody'})[0].text,
                     'images': images
                     }
    except IndexError:
        pass

    try:
        SOLUTION = {'text': probBlock.find_all('div', {'id': 'sol' + str(id)})[0].text}
    except IndexError:
        pass
    except AttributeError:
        pass
    return {'id': ID, 'topic': TOPIC_ID, 'condition': CONDITION, 'solution': SOLUTION, 'url': URL}
