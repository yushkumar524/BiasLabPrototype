import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="logo">
          🔍 The Bias Lab
        </Link>
        <div className="tagline">
          AI-powered media bias analysis
        </div>
      </div>
    </header>
  );
};

export default Header;