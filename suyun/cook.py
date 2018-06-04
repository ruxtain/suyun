# export data to a human-readable form

from openpyxl import Workbook
import pymongo
from openpyxl.drawing.image import Image
import os
import settings

def get_cursor():
    client = pymongo.MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DATABASE]
    collection = db[settings.MONGO_COLLECTION]
    return collection.find()

def make_xlsx(cursor):
    '''
    '''
    def get_data(item, field):
        print(settings.IMAGES_STORE)
        if field == 'images':
            try:
                full_path = item['images'][0]['path']
                image_name = os.path.basename(full_path)
                thumb_path = os.path.join(settings.IMAGES_STORE, 'thumbs/big', image_name)
            except IndexError and KeyError:
                 thumb_path = os.path.join(settings.IMAGES_STORE, 'default.jpg')
            img = Image(thumb_path)
            return img
        elif field == 'date':
            d = item.get(field, [' '])[0]
            if d:
                return d
            else:
                return ' '
        else:
            return item.get(field, [' '])[0]


    wb = Workbook()
    ws = wb.active
    ws.title = "Competitor ASIN Data - Michael Tan"
    ws.append(['Image', 'ASIN', 'URL', 'Price','Title', 'Date', 'Big Category', 'Big Rank', 'Small Category 1', 'Small Rank 1', 'Small Category 2', 'Small Rank 2', 'Small Category 3', 'Small Rank 3', 'Review', 'Star', 'FBA'])
    i = 2
    for item in cursor:
        ws.append([
            get_data(item, ''), # will be overrided
            get_data(item, 'asin'),
            get_data(item, 'link'),
            get_data(item, 'price'),
            get_data(item, 'title'),
            get_data(item, 'date'),
            get_data(item, 'big_category'),
            get_data(item, 'big_rank'),
            get_data(item, 'small_category_1'),
            get_data(item, 'small_rank_1'),
            get_data(item, 'small_category_2'),
            get_data(item, 'small_rank_2'),
            get_data(item, 'small_category_3'),
            get_data(item, 'small_rank_3'),
            get_data(item, 'review'),
            get_data(item, 'star'),
            get_data(item, 'fba'),
        ])
        ws.add_image(get_data(item, 'images'), 'A' + str(i))
        ws.row_dimensions[i].height = 77
        i += 1
    brand = item.get('title', ['Competitor'])[0].split()[0].upper()
    ws.column_dimensions["A"].width = 13
    ws.column_dimensions["E"].width = 15
    ws.column_dimensions["G"].width = 15
    ws.column_dimensions["I"].width = 15
    ws.column_dimensions["K"].width = 15
    ws.column_dimensions["M"].width = 15
    filename = '{} Store Data.xlsx'.format(brand)
    wb.save(filename=filename)
    os.startfile(filename)

make_xlsx(get_cursor())
