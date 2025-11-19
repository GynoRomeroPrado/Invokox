import { useState } from 'react';
import { Login } from './components/Login';
import { Dashboard } from './components/Dashboard';
import { InvoicePanel } from './components/InvoicePanel';
import { UploadInvoices } from './components/UploadInvoices';
import { ValidateInvoice } from './components/ValidateInvoice';
import { ViewInvoice } from './components/ViewInvoice';
import { Companies } from './components/Companies';
import { Analytics } from './components/Analytics';
import { Export } from './components/Export';
import { GeneralSettings } from './components/GeneralSettings';
import { OcrSettings } from './components/OcrSettings';
import { ServerSync } from './components/ServerSync';
import { UsersRoles } from './components/UsersRoles';
import { Help } from './components/Help';

export type UserRole = 'admin' | 'operator' | 'viewer';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
}

export type View = 
  | 'login' 
  | 'dashboard' 
  | 'invoices' 
  | 'upload' 
  | 'validate' 
  | 'view' 
  | 'companies' 
  | 'analytics' 
  | 'export' 
  | 'settings' 
  | 'ocr-settings' 
  | 'server' 
  | 'users' 
  | 'help';

export default function App() {
  const [currentView, setCurrentView] = useState<View>('login');
  const [user, setUser] = useState<User | null>(null);
  const [selectedInvoiceId, setSelectedInvoiceId] = useState<string | null>(null);

  const handleLogin = (userData: User) => {
    setUser(userData);
    setCurrentView('dashboard');
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentView('login');
  };

  const navigateTo = (view: View, invoiceId?: string) => {
    setCurrentView(view);
    if (invoiceId) {
      setSelectedInvoiceId(invoiceId);
    }
  };

  if (currentView === 'login' || !user) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-white border-r border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-blue-600">Sistema de Facturas OCR</h1>
          <p className="text-gray-600 text-sm mt-1">{user.name}</p>
          <p className="text-gray-500 text-xs capitalize">{user.role}</p>
        </div>
        
        <nav className="p-4 space-y-1">
          <NavItem 
            icon="LayoutDashboard" 
            label="Panel Principal" 
            active={currentView === 'dashboard'}
            onClick={() => navigateTo('dashboard')}
          />
          <NavItem 
            icon="FileText" 
            label="Facturas" 
            active={currentView === 'invoices'}
            onClick={() => navigateTo('invoices')}
          />
          <NavItem 
            icon="Upload" 
            label="Cargar Facturas" 
            active={currentView === 'upload'}
            onClick={() => navigateTo('upload')}
          />
          <NavItem 
            icon="Building2" 
            label="Empresas" 
            active={currentView === 'companies'}
            onClick={() => navigateTo('companies')}
          />
          <NavItem 
            icon="BarChart3" 
            label="Analytics" 
            active={currentView === 'analytics'}
            onClick={() => navigateTo('analytics')}
          />
          <NavItem 
            icon="Download" 
            label="Exportación" 
            active={currentView === 'export'}
            onClick={() => navigateTo('export')}
          />
          
          <div className="pt-4 mt-4 border-t border-gray-200">
            <p className="text-gray-500 text-xs px-3 mb-2">CONFIGURACIÓN</p>
            <NavItem 
              icon="Settings" 
              label="General" 
              active={currentView === 'settings'}
              onClick={() => navigateTo('settings')}
            />
            <NavItem 
              icon="ScanLine" 
              label="OCR Avanzado" 
              active={currentView === 'ocr-settings'}
              onClick={() => navigateTo('ocr-settings')}
            />
            <NavItem 
              icon="Server" 
              label="Servidor" 
              active={currentView === 'server'}
              onClick={() => navigateTo('server')}
            />
            {user.role === 'admin' && (
              <NavItem 
                icon="Users" 
                label="Usuarios y Roles" 
                active={currentView === 'users'}
                onClick={() => navigateTo('users')}
              />
            )}
          </div>
          
          <div className="pt-4 mt-4 border-t border-gray-200">
            <NavItem 
              icon="HelpCircle" 
              label="Ayuda y Soporte" 
              active={currentView === 'help'}
              onClick={() => navigateTo('help')}
            />
            <NavItem 
              icon="LogOut" 
              label="Cerrar Sesión" 
              onClick={handleLogout}
            />
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {currentView === 'dashboard' && <Dashboard navigateTo={navigateTo} />}
        {currentView === 'invoices' && <InvoicePanel navigateTo={navigateTo} userRole={user.role} />}
        {currentView === 'upload' && <UploadInvoices navigateTo={navigateTo} />}
        {currentView === 'validate' && selectedInvoiceId && (
          <ValidateInvoice invoiceId={selectedInvoiceId} navigateTo={navigateTo} userRole={user.role} />
        )}
        {currentView === 'view' && selectedInvoiceId && (
          <ViewInvoice invoiceId={selectedInvoiceId} navigateTo={navigateTo} />
        )}
        {currentView === 'companies' && <Companies />}
        {currentView === 'analytics' && <Analytics />}
        {currentView === 'export' && <Export />}
        {currentView === 'settings' && <GeneralSettings />}
        {currentView === 'ocr-settings' && <OcrSettings />}
        {currentView === 'server' && <ServerSync />}
        {currentView === 'users' && <UsersRoles />}
        {currentView === 'help' && <Help />}
      </main>
    </div>
  );
}

interface NavItemProps {
  icon: string;
  label: string;
  active?: boolean;
  onClick: () => void;
}

function NavItem({ icon, label, active, onClick }: NavItemProps) {
  const icons: Record<string, any> = {
    LayoutDashboard: '📊',
    FileText: '📄',
    Upload: '⬆️',
    Building2: '🏢',
    BarChart3: '📈',
    Download: '⬇️',
    Settings: '⚙️',
    ScanLine: '🔍',
    Server: '🖥️',
    Users: '👥',
    HelpCircle: '❓',
    LogOut: '🚪'
  };

  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
        active 
          ? 'bg-blue-50 text-blue-600' 
          : 'text-gray-700 hover:bg-gray-50'
      }`}
    >
      <span className="text-lg">{icons[icon]}</span>
      <span className="text-sm">{label}</span>
    </button>
  );
}
