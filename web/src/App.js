import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import BookList from './BookList';

function App() {
  const [searchKeyword, setSearchKeyword] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [message, setMessage] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoginFormVisible, setIsLoginFormVisible] = useState(false);

  const handleSearch = (event) => {
    const keyword = event.target.value;
    setSearchKeyword(keyword);
    if (keyword.length >= 3) {
      fetchSearchResults(keyword);
    } else {
      setSearchResults([]);
    }
  };

  const fetchSearchResults = (keyword) => {
    axios.get(`/search/${keyword}`)
      .then(response => {
        setSearchResults(response.data);
      })
      .catch(error => {
        console.error('There was an error fetching the search results!', error);
      });
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setLoginForm({ ...loginForm, [name]: value });
  };

  const handleLogin = () => {
    axios.post('/login', loginForm)
      .then(response => {
        setMessage(response.data.message);
        localStorage.setItem('accessToken', response.data.access_token);
        setIsLoggedIn(true);
        setIsLoginFormVisible(false);
      })
      .catch(error => {
        setMessage(error.response.data.message);
      });
  };

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    setIsLoggedIn(false);
  };

  const toggleLoginForm = () => {
    setIsLoginFormVisible(!isLoginFormVisible);
  };

  const handleOverlayClick = () => {
    setIsLoginFormVisible(false);
  };

  const handleFormClick = (event) => {
    event.stopPropagation();
  };

  return (
    <div className="App">
      <header className="header">
        <div className="left-header">
          <h1>Waka</h1>
        </div>
        <div className="center-header">
          <input
            type="text"
            placeholder="Search book..."
            value={searchKeyword}
            onChange={handleSearch}
          />
          <div className="search-results">
            {searchResults.slice(0, 5).map((result, index) => (
              <div key={index}>{result.title} ({result.author_name})</div>
            ))}
          </div>
        </div>
        <div className="right-header">
          {!isLoggedIn ? (
            <div>
              <button onClick={toggleLoginForm}>Login</button>
              <button>Register</button>
            </div>
          ) : (
            <button onClick={handleLogout}>Logout</button>
          )}
        </div>
      </header>
      <div className="book-container">
        <div className="category">
          <BookList category="free" />
        </div>
        <div className="category">
          <BookList category="new" />
        </div>
        <div className="category">
          <BookList category="recommended" />
        </div>
      </div>
      {isLoginFormVisible && (
        <div className="overlay" onClick={handleOverlayClick}>
          <div className="login-form" onClick={handleFormClick}>
            <input
              type="text"
              name="username"
              placeholder="Username"
              value={loginForm.username}
              onChange={handleInputChange}
            />
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={loginForm.password}
              onChange={handleInputChange}
            />
            {message && <div className="message">{message}</div>}
            <button onClick={handleLogin}>Login</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
