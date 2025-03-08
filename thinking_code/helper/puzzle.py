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