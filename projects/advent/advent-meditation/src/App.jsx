import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import WeekPage from './pages/WeekPage';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/week/:id" element={<WeekPage />} />
      </Routes>
    </Layout>
  );
}

export default App;
