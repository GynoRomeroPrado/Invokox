import { useState } from 'react';
import { Users, UserPlus, Edit, Trash2, Shield, Key, X } from 'lucide-react';
import { UserRole } from '../App';

interface UserData {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  status: 'active' | 'inactive';
  lastLogin: string;
  created: string;
}

export function UsersRoles() {
  const [users, setUsers] = useState<UserData[]>([
    {
      id: '1',
      email: 'admin@example.com',
      name: 'Administrador',
      role: 'admin',
      status: 'active',
      lastLogin: '2024-11-18 10:30',
      created: '2024-01-15'
    },
    {
      id: '2',
      email: 'operator@example.com',
      name: 'Operador Principal',
      role: 'operator',
      status: 'active',
      lastLogin: '2024-11-18 09:15',
      created: '2024-02-20'
    },
    {
      id: '3',
      email: 'viewer@example.com',
      name: 'Consultor Externo',
      role: 'viewer',
      status: 'active',
      lastLogin: '2024-11-17 16:45',
      created: '2024-03-10'
    }
  ]);

  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState<UserData | null>(null);

  const handleEdit = (user: UserData) => {
    setEditingUser(user);
    setShowModal(true);
  };

  const handleNew = () => {
    setEditingUser(null);
    setShowModal(true);
  };

  const handleResetPassword = (user: UserData) => {
    alert(`Restablecer contraseña para ${user.email}`);
  };

  const handleToggleStatus = (userId: string) => {
    setUsers(users.map(u =>
      u.id === userId
        ? { ...u, status: u.status === 'active' ? 'inactive' as const : 'active' as const }
        : u
    ));
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-gray-900 mb-2">Usuarios y Roles</h1>
            <p className="text-gray-600">Administración de cuentas y permisos</p>
          </div>
          <button
            onClick={handleNew}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <UserPlus className="w-4 h-4" />
            Nuevo Usuario
          </button>
        </div>

        {/* Roles Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
            <div className="flex items-center gap-3 mb-2">
              <Shield className="w-5 h-5 text-purple-600" />
              <h3 className="text-purple-900">Admin</h3>
            </div>
            <p className="text-purple-800 text-sm">
              Acceso completo: configuración, usuarios, aprobación y administración
            </p>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <div className="flex items-center gap-3 mb-2">
              <Users className="w-5 h-5 text-blue-600" />
              <h3 className="text-blue-900">Operator</h3>
            </div>
            <p className="text-blue-800 text-sm">
              Puede cargar, validar y aprobar/rechazar facturas
            </p>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <div className="flex items-center gap-3 mb-2">
              <Users className="w-5 h-5 text-gray-600" />
              <h3 className="text-gray-900">Viewer</h3>
            </div>
            <p className="text-gray-700 text-sm">
              Solo lectura: puede ver facturas y reportes
            </p>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-gray-700">Usuario</th>
              <th className="px-6 py-3 text-left text-gray-700">Rol</th>
              <th className="px-6 py-3 text-left text-gray-700">Estado</th>
              <th className="px-6 py-3 text-left text-gray-700">Último Acceso</th>
              <th className="px-6 py-3 text-left text-gray-700">Creado</th>
              <th className="px-6 py-3 text-left text-gray-700">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {users.map((user) => (
              <tr key={user.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div>
                    <p className="text-gray-900">{user.name}</p>
                    <p className="text-gray-600 text-sm">{user.email}</p>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded text-sm ${
                    user.role === 'admin' ? 'bg-purple-100 text-purple-800' :
                    user.role === 'operator' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {user.role === 'admin' && 'Admin'}
                    {user.role === 'operator' && 'Operator'}
                    {user.role === 'viewer' && 'Viewer'}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <button
                    onClick={() => handleToggleStatus(user.id)}
                    className={`px-3 py-1 rounded text-sm ${
                      user.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {user.status === 'active' ? 'Activo' : 'Inactivo'}
                  </button>
                </td>
                <td className="px-6 py-4 text-gray-700 text-sm">
                  {new Date(user.lastLogin).toLocaleString('es-ES')}
                </td>
                <td className="px-6 py-4 text-gray-700 text-sm">
                  {new Date(user.created).toLocaleDateString('es-ES')}
                </td>
                <td className="px-6 py-4">
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(user)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                      title="Editar"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleResetPassword(user)}
                      className="p-2 text-yellow-600 hover:bg-yellow-50 rounded"
                      title="Restablecer contraseña"
                    >
                      <Key className="w-4 h-4" />
                    </button>
                    <button
                      className="p-2 text-red-600 hover:bg-red-50 rounded"
                      title="Eliminar"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Audit Trail */}
      <div className="mt-8 bg-white p-6 rounded-lg border border-gray-200">
        <h2 className="text-gray-900 mb-4">Auditoría de Accesos Recientes</h2>
        <div className="space-y-2">
          {[
            { user: 'admin@example.com', action: 'Inicio de sesión', time: '2024-11-18 10:30', ip: '192.168.1.100' },
            { user: 'operator@example.com', action: 'Aprobó factura F001-00123', time: '2024-11-18 09:15', ip: '192.168.1.101' },
            { user: 'viewer@example.com', action: 'Exportó reporte', time: '2024-11-17 16:45', ip: '192.168.1.102' },
            { user: 'admin@example.com', action: 'Creó usuario nuevo', time: '2024-11-17 14:20', ip: '192.168.1.100' }
          ].map((log, index) => (
            <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-gray-50 text-sm">
              <div className="flex-1">
                <span className="text-gray-900">{log.user}</span>
                <span className="text-gray-600 mx-2">•</span>
                <span className="text-gray-700">{log.action}</span>
              </div>
              <div className="flex items-center gap-4 text-gray-600">
                <span>{log.ip}</span>
                <span>{new Date(log.time).toLocaleString('es-ES')}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <UserModal
          user={editingUser}
          onClose={() => setShowModal(false)}
          onSave={(data) => {
            setShowModal(false);
            alert('Usuario guardado');
          }}
        />
      )}
    </div>
  );
}

interface UserModalProps {
  user: UserData | null;
  onClose: () => void;
  onSave: (user: Partial<UserData>) => void;
}

function UserModal({ user, onClose, onSave }: UserModalProps) {
  const [formData, setFormData] = useState({
    email: user?.email || '',
    name: user?.name || '',
    role: user?.role || 'viewer' as UserRole,
    password: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full">
        <div className="p-6 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-gray-900">
            {user ? 'Editar Usuario' : 'Nuevo Usuario'}
          </h2>
          <button onClick={onClose} className="p-2 text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-gray-700 mb-2">Nombre Completo *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 mb-2">Email *</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 mb-2">Rol *</label>
            <select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value as UserRole })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="viewer">Viewer - Solo lectura</option>
              <option value="operator">Operator - Gestión de facturas</option>
              <option value="admin">Admin - Acceso completo</option>
            </select>
          </div>

          {!user && (
            <div>
              <label className="block text-gray-700 mb-2">Contraseña *</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required={!user}
                minLength={8}
              />
              <p className="text-gray-600 text-sm mt-1">Mínimo 8 caracteres</p>
            </div>
          )}

          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Guardar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
