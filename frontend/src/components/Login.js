import React, { useState } from 'react';
import config from '../config';
import './Login.css';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = isRegister ? `${config.API_BASE_URL}/api/v1/auth/register` : `${config.API_BASE_URL}/api/v1/auth/login`;
      
      let body, headers;
      if (isRegister) {
        body = JSON.stringify({ username, password });
        headers = { 'Content-Type': 'application/json' };
      } else {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        body = formData;
        headers = {};
      }

      console.log('Request:', { endpoint, headers, body: isRegister ? JSON.parse(body) : 'FormData' });
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers,
        body
      });

      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);

      if (response.ok) {
        onLogin(data.access_token);
      } else {
        if (data.detail && Array.isArray(data.detail)) {
          const errors = data.detail.map(err => err.msg).join(', ');
          setError(errors);
        } else {
          setError(data.detail || data.message || 'Giriş başarısız');
        }
      }
    } catch (error) {
      setError('Bağlantı hatası');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-form">
        <h2>{isRegister ? 'Kayıt Ol' : 'Giriş Yap'}</h2>
        
        {error && <div className="error">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder={isRegister ? "Kullanıcı adı (en az 3 karakter)" : "Kullanıcı adı"}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          
          <input
            type="password"
            placeholder={isRegister ? "Şifre (en az 6 karakter)" : "Şifre"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          
          <button type="submit" disabled={loading}>
            {loading ? 'Yükleniyor...' : (isRegister ? 'Kayıt Ol' : 'Giriş Yap')}
          </button>
        </form>
        
        <p>
          {isRegister ? 'Hesabın var mı?' : 'Hesabın yok mu?'}
          <button 
            type="button" 
            className="link-btn"
            onClick={() => setIsRegister(!isRegister)}
          >
            {isRegister ? 'Giriş Yap' : 'Kayıt Ol'}
          </button>
        </p>
      </div>
    </div>
  );
}

export default Login;
