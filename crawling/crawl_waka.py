import logging
import requests

categories = {
    'free': 'https://beta-api.waka.vn/super/listContentMajor?os=wap&id=15b0307ca39d18d5ecd2834d3e04651e&account=guest&major_id=504&content_type=0&page_no=1&page_size=10&secure_code=oYN9rM0%2FAKWGHQmSHAEXKT1IXcM%3D',
    'new': 'https://beta-api.waka.vn/super/listContentMajor?os=wap&id=15b0307ca39d18d5ecd2834d3e04651e&account=guest&major_id=500&content_type=0&page_no=1&page_size=10&secure_code=05v8Qk6bsFFHyCYAi7ZsheFifSo%3D',
    'recommended': 'https://beta-api.waka.vn/super/listContentMajor?os=wap&id=15b0307ca39d18d5ecd2834d3e04651e&account=guest&major_id=502&content_type=0&page_no=1&page_size=10&secure_code=M2g0gHw%2B4Dg8bY035NLFmryeqIs%3D'
}

def get_books(category):
    api_url = categories.get(category)
    if api_url:
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            logging.error(f"Failed to fetch books from {category} category API")
    else:
        logging.error(f"No API URL found for {category} category")

def insert_books_to_database(category):
    books = get_books(category)
    if books:
        for book in books:
            insert_book_to_database(category, book)

def insert_book_to_database(category, book):
    book_data = {
        'book_id': book.get('id'),
        'title': book.get('title'),
        'thumb': book.get('thumb'),
        'author_id': book.get('authors')[0].get('id'),
        'author_name': book.get('authors')[0].get('name')
    }
    insert_url = f'http://api:5000/insert_book/{category}'
    insert_response = requests.post(insert_url, json=book_data)
    if insert_response.status_code != 200:
        logging.error(f"Failed to insert book {book_data['title']} into category {category}. Error: {insert_response.text}")
    else :
        logging.info(f"Successfully inserted book {book_data['title']} into category {category}")

for category in categories:
    insert_books_to_database(category)

