import { useState } from 'react';
import { User, UserRole } from '../App';
import { Lock, Mail, Globe } from 'lucide-react';

interface LoginProps {
  onLogin: (user: User) => void;
}

type Language = 'es' | 'en';

export function Login({ onLogin }: LoginProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);
  const [language, setLanguage] = useState<Language>('es');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Simulate API call
    setTimeout(() => {
      if (email && password) {
        const role: UserRole = email.includes('admin') ? 'admin' : email.includes('operator') ? 'operator' : 'viewer';
        onLogin({
          id: 'user-1',
          email,
          name: email.split('@')[0],
          role
        });
      } else {
        setError(language === 'es' ? 'Credenciales inválidas' : 'Invalid credentials');
      }
      setLoading(false);
    }, 800);
  };

  const texts = {
    es: {
      title: 'Sistema de Facturas OCR',
      subtitle: 'Inicia sesión para continuar',
      email: 'Correo electrónico',
      password: 'Contraseña',
      remember: 'Recordarme',
      login: 'Iniciar Sesión',
      forgot: '¿Olvidaste tu contraseña?',
      demo: 'Demo: admin@example.com, operator@example.com o viewer@example.com'
    },
    en: {
      title: 'OCR Invoice System',
      subtitle: 'Sign in to continue',
      email: 'Email',
      password: 'Password',
      remember: 'Remember me',
      login: 'Sign In',
      forgot: 'Forgot your password?',
      demo: 'Demo: admin@example.com, operator@example.com or viewer@example.com'
    }
  };

  const t = texts[language];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
              <span className="text-3xl">📄</span>
            </div>
            <h1 className="text-blue-600 mb-2">{t.title}</h1>
            <p className="text-gray-600">{t.subtitle}</p>
          </div>

          {/* Language Selector */}
          <div className="flex justify-end mb-4">
            <button
              onClick={() => setLanguage(language === 'es' ? 'en' : 'es')}
              className="flex items-center gap-2 text-gray-600 hover:text-blue-600 text-sm"
            >
              <Globe className="w-4 h-4" />
              <span>{language === 'es' ? 'English' : 'Español'}</span>
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div>
              <label className="block text-gray-700 mb-2">{t.email}</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="usuario@ejemplo.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-gray-700 mb-2">{t.password}</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-gray-700 text-sm">{t.remember}</span>
              </label>
              <a href="#" className="text-blue-600 hover:text-blue-700 text-sm">
                {t.forgot}
              </a>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (language === 'es' ? 'Cargando...' : 'Loading...') : t.login}
            </button>
          </form>

          {/* Demo Info */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-blue-800 text-sm">{t.demo}</p>
          </div>
        </div>

        <p className="text-center mt-6 text-gray-600 text-sm">
          © 2025 Sistema de Facturas OCR
        </p>
      </div>
    </div>
  );
}
