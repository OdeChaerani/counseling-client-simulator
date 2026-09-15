import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [message, setMessage] = useState('Loading...')

  useEffect(() => {
    // Memanggil API dari backend FastAPI
    fetch('http://127.0.0.1:8000/api/data')
      .then(response => response.json())
      .then(data => setMessage(data.message))
      .catch(error => console.error('Error:', error))
  }, [])
  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <h1>React + FastAPI</h1>
      <p>Respon dari Backend: <strong>{message}</strong></p>
    </div>
  )
}

export default App
