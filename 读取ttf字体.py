from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
import ddddocr

font_path = r'./tempfont.ttf'

# render_and_recognize_glyphs(font_path)    


font = TTFont(font_path)
glyph_set = font.getGlyphSet()
glyphs = glyph_set.keys()
char_set = {}
# print("List of glyphs:")
for glyph in glyphs:
#     print(glyph)
    if glyph.startswith('uni'):
        char_set.update({glyph[3:]:''})
font.close()

try:
    font_size = 64
    canvas_size = 100
    font = ImageFont.truetype(font_path, font_size)
    character = ''
    ocr = ddddocr.DdddOcr(show_ad=False) # OCR识别验证码
    for glyph in char_set.keys():
        character = chr(int(glyph, 16))
        if character == '':
            print(f'{glyph}: 空白字符')
            continue
        image = Image.new("RGB", (canvas_size, canvas_size), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.text((16, 0), character, font=font, fill=(0, 0, 0))
        # images.append(image)
        # image.show()

        # text = pytesseract.image_to_string(image)
        text = ocr.classification(image)
        if text:
            print(f'{glyph}: {text}')
            char_set.update({glyph: text})
        else:
            print(f'{glyph}：识别不了')
    
    # print("Recognized characters:", recognized_characters)

except Exception as e:
    print("Error:", e)

