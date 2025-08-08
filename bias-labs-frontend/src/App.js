import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

// Import components
import Header from './components/Header';
import Homepage from './pages/Homepage';
import NarrativeDetail from './pages/NarrativeDetail';
import ArticleDetail from './pages/ArticleDetail';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Homepage />} />
            <Route path="/narrative/:narrativeId" element={<NarrativeDetail />} />
            <Route path="/article/:articleId" element={<ArticleDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;