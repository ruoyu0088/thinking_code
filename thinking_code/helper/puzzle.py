import json
import re
from bs4 import BeautifulSoup
import polars as pl
import numpy as np
import pyperclip 


def extract_slither_link(html=""):
    """
    extract puzzle from https://ja.puzzle-loop.com
    """
    if not html:
        html = pyperclip.paste()
    soup = BeautifulSoup(html, "html.parser")
    cells = []
    
    for div in soup.find_all("div", class_="loop-task-cell"):
        style = div.get("style", "")
        text = div.get_text(strip=True)
        
        top_match = re.search(r"top:\s*(\d+)px", style)
        left_match = re.search(r"left:\s*(\d+)px", style)
        
        top = int(top_match.group(1)) if top_match else None
        left = int(left_match.group(1)) if left_match else None
        
        cells.append({"text": text, "top": int(top), "left": int(left)})

    df = pl.DataFrame(cells)
    board = np.array(
        df.with_columns(
            pl.col('text').replace('', '-1').cast(pl.Int8)
        )
        .sort(by=['top', 'left'])
        .group_by('top', maintain_order=True)
        .agg(pl.col('text'))
        .sort(by='top')
        .get_column('text').to_list()
    )
    return board

def extract_number_link(json_str=""):
    """
    extract puzzle from https://puzzlemadness.co.uk/numberlink/medium
    """
    if not json_str:
        json_str = pyperclip.paste()
    data = json.loads(json_str)
    pdata = data['puzzleData']
    width = pdata['gridWidth']
    height = pdata['gridHeight']
    numbers = pdata['data']['startingGrid']
    return np.array(numbers).reshape(height, width)

def extract_nonogram(html=""):
    def read_table_content(table):
        data = []
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols]) 
        return data

    if not html:
        html = pyperclip.paste()
        
    soup = BeautifulSoup(html, 'html.parser')
    table_top = soup.find(class_='nmtt')
    table_left = soup.find(class_='nmtl')
    cols = [[int(v) for v in line if v] for line in zip(*read_table_content(table_top))]
    rows = [[int(v) for v in line if v] for line in read_table_content(table_left)]

    return {"rows":rows, "cols":cols}

def extract_shikaku(html=""):
    if not html:
        html = pyperclip.paste()
    
    soup = BeautifulSoup(html, 'html.parser')
    cells = soup.find_all('div', class_='cell')
    board = []
    last_top = ''
    for cell in cells:
        style = dict([[s.strip() for s in item.split(':')] for item in cell.attrs['style'].split(';') if item])
        top = style['top']
        if last_top != top:
            board.append([])
            last_top = top
        number = cell.text
        if not number:
            number = 0
        else:
            number = int(number)
        board[-1].append(number)
    return board       

def extract_masyu(html=""):
    if not html:
        html = pyperclip.paste()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    divs = soup.find_all('div', class_='loop-dot')
    
    results = []
    for div in divs:
        class_attr = div.get('class', [])
        style = div.get('style', '')
    
        # Extract top and left from style
        top = left = None
        for rule in style.split(';'):
            rule = rule.strip()
            if rule.startswith('top:'):
                top = rule.split(':')[1].strip()
            elif rule.startswith('left:'):
                left = rule.split(':')[1].strip()
    
        dot = 0
        if 'dot-white' in class_attr:
            dot = 1
        elif 'dot-black' in class_attr:
            dot = 2
        top = int(top.replace('px', ''))
        left = int(left.replace('px', ''))
        results.append({'dot': dot, 'top': top, 'left': left})
    return (
        pl.DataFrame(results)
        .sort('top', 'left')
        .pivot('left', index='top')
        .drop('top')
        .to_numpy()
    )    