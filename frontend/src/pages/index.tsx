import React, { useState } from 'react';
import Link from 'next/link';

export default function Home() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>🚗 UberGo - Ride Booking System</h1>
      
      <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
        <Link href="/admin">
          <button style={buttonStyle}>👨‍💼 Admin Dashboard</button>
        </Link>
        <Link href="/user">
          <button style={buttonStyle}>👤 User Portal</button>
        </Link>
        <Link href="/driver">
          <button style={buttonStyle}>🚕 Driver Portal</button>
        </Link>
      </div>

      <div style={{ marginTop: '3rem', background: '#f0f0f0', padding: '1rem', borderRadius: '8px' }}>
        <h2>API Status</h2>
        <p>Backend API: <code>/api/health</code></p>
        <ApiStatus />
      </div>
    </div>
  );
}

function ApiStatus() {
  const [status, setStatus] = useState('Checking...');

  React.useEffect(() => {
    fetch('/api/health')
      .then(r => r.json())
      .then(data => setStatus('✅ Online'))
      .catch(() => setStatus('❌ Offline'));
  }, []);

  return <p>{status}</p>;
}

const buttonStyle = {
  padding: '12px 24px',
  fontSize: '16px',
  borderRadius: '8px',
  border: 'none',
  background: '#007bff',
  color: 'white',
  cursor: 'pointer',
};
