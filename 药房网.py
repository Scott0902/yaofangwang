from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
import ddddocr
import requests
import re

se=requests.Session()
se.headers.update({'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',})
ocr = ddddocr.DdddOcr(show_ad=False) # OCR识别验证码


def get_font_and_regonize(font_path, font_file_path):
    with open(font_file_path, 'wb') as f:
        font_data=se.get('https://www.yaofangwang.com' + font_path).content
        f.write(font_data)
    
    font = TTFont(font_file_path)
    glyph_set = font.getGlyphSet()
    glyphs = glyph_set.keys()
    char_set = {}
    for glyph in glyphs:
        if glyph.startswith('uni'):
            char_set.update({glyph[3:]:''})
    font.close()

    try:
        font_size = 64
        canvas_size = 100
        font = ImageFont.truetype(font_file_path, font_size)
        character = ''
        for glyph in char_set.keys():
            character = chr(int(glyph, 16))
            if character == '':
                print(f'{glyph}: 空白字符')
                continue
            image = Image.new("RGB", (canvas_size, canvas_size), (255, 255, 255))
            draw = ImageDraw.Draw(image)
            draw.text((16, 0), character, font=font, fill=(0, 0, 0))
            text = ocr.classification(image)
            if text:
                # print(f'{glyph}: {text}')
                char_set.update({glyph: text})
            else:
                print(f'{glyph}：识别不了')
    except Exception as e:
        print("Error:", e)
    return char_set


if __name__ == '__main__':
    url = "https://www.yaofangwang.com/yaodian/398470/Drugs.html"
    total_page=7
    current_page=1
    font_file_path='./tempfont.ttf'
    font_path=''

    for page in range(1,8):
        response = se.get(url + "?page=" + str(page)).text
        if current_page>1:
            font_path2=re.search('@font-face.*?url\(\'(.*?)\'', response, re.DOTALL)[1]
            if font_path2 != font_path:
                print('ttf字体网址不一样，要重新下载字体文件')
                font_path=font_path2
                char_set = get_font_and_regonize(font_path, font_file_path)
        else:
            font_path = re.search('@font-face.*?url\(\'(.*?)\'', response, re.DOTALL)[1]
            char_set = get_font_and_regonize(font_path, font_file_path)

        print(f'======== Page: {page} =========')
        drug_names=re.findall('<i class=\"icon_.*?<\/i>(.*?)<\/a>', response, re.DOTALL)
        drug_specs=re.findall('<p class=\"st\">(.*?)<\/p>', response)
        drug_price=re.findall('>¥(.*?)<\/label>', response, re.DOTALL)
        for n in range(len(drug_names)):
            for j in re.findall('&#x(.*?);', drug_price[n]):
                drug_price[n]=drug_price[n].replace('&#x'+j+';', char_set[j])
            drug_names[n]=drug_names[n].strip().replace('&nbsp;','')
            print(drug_names[n], drug_specs[n], drug_price[n], sep='\t')
        print('\n\n')

