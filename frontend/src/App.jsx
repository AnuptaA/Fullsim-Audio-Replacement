import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import TestPage from './pages/TestPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav style={{ padding: '20px', backgroundColor: '#333', color: 'white' }}>
          <Link to="/" style={{ color: 'white', textDecoration: 'none', fontSize: '18px' }}>
            Language Learning App - Test
          </Link>
        </nav>
        <Routes>
          <Route path="/" element={<TestPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;