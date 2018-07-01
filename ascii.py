from flask import Flask, request, Response, send_file, redirect
import random, os
app = Flask(__name__)

from pyfiglet import figlet_format as pf
from pyfiglet import Figlet
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

fig = Figlet()

discord_ua1 = 'Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)'
discord_ua2 = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:38.0) Gecko/20100101 Firefox/38.0'
discord_ua = [discord_ua1, discord_ua2]

site_name = 'DMTools'
description = 'Инструменты в виде REST API'
info = '''Создатель сайта: DanilMirov
API endpoints:
    /render?text=Hello!&font=banner - Отрендерить текст
    /render?text=Hello!&font=random - Отрендерить текст с рандомным шрифтом
    /render?text=Привет!&font=randomru - Отрендерить текст в рандомным шрифтом, который поддерживает русский язык
    /fonts - Все шрифты
    /fonts?m=2 - Показать шрифты, которые работают с русским языком
    /imagerender?text=abc - Превратить текст в изображение
ChangeLog 1.2.0:
    Добавлена возможность быстрого просмотра отрендереного текста в дискорде
    Добавлены новые пути - /imagerender
ChangeLog 1.2.0.1
    Всё что возможно - сделано читаемым из дискорда'''

def imageBuilder(host, text):
    return f'http://{host}/imagerender?text={text}'.replace(' ', '+').replace('<', '%3C').replace('>', '%3E')

ru = ['banner', 'georgia11', 'graceful', 'mnemonic']
fonts = fig.getFonts()
wrfonts = [x for x in fonts if x not in ru]
stats = {'rendered': {'success': 0, 'fail': 0}}

def imageRender(text: str):
    b = BytesIO()
    font = ImageFont.truetype('Roboto-Thin.ttf', 30)
    img = Image.new('RGB', (2000, 1000))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, fill=(0, 0, 0), font=font)
    W, H = font.getsize(text)
    W = 0
    for line in text.splitlines():
        tmp = font.getsize(line)
        if tmp[0] > W:
            W = tmp[0]
    imgs = Image.new('RGB', (W, H*len(text.splitlines())), (255, 255, 255))
    draw = ImageDraw.Draw(imgs)
    draw.text((0, 0), text, fill=(0, 0, 0), font=font)
    W, H = font.getsize(text)
    imgs.save(b, 'png')
    b.seek(0)
    return b

@app.route('/imagerender')
def ir():
    text = request.args.get('text', 'null')
    return send_file(imageRender(text.replace(r'\n', '\n').replace('<br>', '\n')), attachment_filename='rendered.png', mimetype='image/png')

@app.route('/')
def main():
    h = 'http://'+request.headers.get('Host')+'/help'
    if request.headers.get('User-Agent') in discord_ua or request.args.get('discord'):
        return send_file(imageRender(info), attachment_filename='rendered.png', mimetype='image/png')
    return f'<meta property="og:description" content="{description}"><meta property="og:site_name" content="{site_name}" />\nВсю важную информацию можно увидеть <a href="{h}">тут</a>'

@app.route('/help')
def help():
    rs = stats['rendered']['success']
    rf = stats['rendered']['fail']
    text = f'{info}\n\nСтатистика за последний запуск\nОтрендерено:\n    Всего: {rs+rf}\n    Получилось: {rs}\n    Не получилось {rf}'
    if request.headers.get('User-Agent') in discord_ua:
        return send_file(imageRender(info), attachment_filename='rendered.png', mimetype='image/png')
    return Response(text, mimetype='text/plain')

@app.route('/render')
def render():
    print(request.headers.get('User-Agent'))
    text = request.args.get('text', 'null')
    font = request.args.get('font', 'banner')
    bru = bool(int(request.args.get('ru', 0)))
    if font == 'randomru':
        font = random.choice(ru)
    if font == 'random':
        font = random.choice(fonts)
    try: rendered = pf(text, font=font)
    except: rendered = False
    if rendered: stats['rendered']['success'] += 1
    else: stats['rendered']['fail'] += 1
    rendered = rendered or pf('Не отрендерено', 'banner')
    if request.headers.get('User-Agent') in discord_ua:
        return send_file(imageRender(rendered), attachment_filename='rendered.png', mimetype='image/png')
    return Response(rendered, mimetype='text/plain')

@app.route('/fonts')
@app.route('/list')
def _fonts():
    m = int(request.args.get('m', 0))
    if m == 2: res = ', '.join(ru)
    elif m == 1: res = ', '.join(wrfonts)
    else: res = ', '.join(fonts)
    if request.headers.get('User-Agent') in discord_ua:
        a = []
        fin = ''
        for i in res.split(', '):
            if len(a) >= len(res.split(', '))//36:
                fin += ', '.join(a)+'\n'
                a = []
            a.append(i)
        if a:
            fin += ', '.join(a)
        return send_file(imageRender(fin.strip('\n')), attachment_filename='rendered.png', mimetype='image/png')
    return res

app.run(host='0.0.0.0', port=os.getenv('PORT', 5000))