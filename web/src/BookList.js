import React, { useState, useEffect } from 'react';
import axios from 'axios';

function BookList({ category }) {
  const [books, setBooks] = useState([]);

  useEffect(() => {
    fetchBooks(category);
  }, [category]);

  const fetchBooks = (category) => {
    axios.get(`/guest/books/${category}`)
      .then(response => {
        setBooks(response.data);
      })
      .catch(error => {
        console.error('There was an error fetching the books!', error);
      });
  };

  const toggleFavorite = (bookIndex) => {
    const updatedBooks = [...books];
    updatedBooks[bookIndex].is_favorite = !updatedBooks[bookIndex].is_favorite;
    setBooks(updatedBooks);
  };

  return (
    <div style={{ width: '100%'}}>
      <h2>{category.toUpperCase()}</h2>
      <section className="book-list">
        {books.map((book, index) => (
          <div className="book-item" key={index} style={{ position: 'relative', display: 'inline-block' }}>
            <img src={book.thumb} alt={book.title} />
            <img
              src={book.is_favorite ? '/images/HeartRed.png' : '/images/UnHeartRed.png'}
              alt="Favorite"
              style={{ position: 'absolute', width: '20%', height: '12%', top: '10px', right: '10px', cursor: 'pointer' }}
              onClick={() => toggleFavorite(index)}
            />
            <h3>{book.title}</h3>
          </div>
        ))}
      </section>
    </div>
  );
}

export default BookList;
