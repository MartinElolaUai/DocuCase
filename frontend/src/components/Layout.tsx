import { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  HomeIcon,
  FolderIcon,
  CubeIcon,
  DocumentTextIcon,
  BeakerIcon,
  ClipboardDocumentListIcon,
  UsersIcon,
  CogIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  ChevronDownIcon,
  BellIcon,
} from '@heroicons/react/24/outline';
import { useAuthStore } from '@/store/authStore';
import clsx from 'clsx';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Agrupadores', href: '/groups', icon: FolderIcon },
  { name: 'Aplicaciones', href: '/applications', icon: CubeIcon },
  { name: 'Features', href: '/features', icon: DocumentTextIcon },
  { name: 'Casos de Prueba', href: '/test-cases', icon: BeakerIcon },
  { name: 'Solicitudes', href: '/requests', icon: ClipboardDocumentListIcon },
  { name: 'Pipelines', href: '/pipelines', icon: CogIcon },
];

const adminNavigation = [
  { name: 'Usuarios', href: '/users', icon: UsersIcon },
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isAdmin = user?.role === 'ADMIN';

  return (
    <div className="min-h-screen flex">
      {/* Mobile sidebar backdrop */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-surface-950/80 backdrop-blur-sm z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed inset-y-0 left-0 z-50 w-72 bg-surface-900/95 backdrop-blur-xl border-r border-surface-700/50 transform transition-transform duration-300 lg:translate-x-0 lg:static lg:flex lg:flex-col',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 h-16 px-6 border-b border-surface-700/50">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
            <BeakerIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-display font-bold text-gradient">DashCase</h1>
            <p className="text-xs text-surface-500">Test Management</p>
          </div>
          <button
            className="ml-auto lg:hidden text-surface-400 hover:text-surface-100"
            onClick={() => setSidebarOpen(false)}
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                clsx(
                  isActive ? 'nav-link-active' : 'nav-link'
                )
              }
              onClick={() => setSidebarOpen(false)}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.name}</span>
            </NavLink>
          ))}

          {isAdmin && (
            <>
              <div className="pt-4 mt-4 border-t border-surface-700/50">
                <p className="px-4 mb-2 text-xs font-semibold text-surface-500 uppercase tracking-wider">
                  Administración
                </p>
              </div>
              {adminNavigation.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    clsx(
                      isActive ? 'nav-link-active' : 'nav-link'
                    )
                  }
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className="w-5 h-5" />
                  <span>{item.name}</span>
                </NavLink>
              ))}
            </>
          )}
        </nav>

        {/* User info */}
        <div className="p-4 border-t border-surface-700/50">
          <div className="flex items-center gap-3 p-2 rounded-lg bg-surface-800/50">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white font-semibold">
              {user?.firstName?.[0]}{user?.lastName?.[0]}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-surface-100 truncate">
                {user?.firstName} {user?.lastName}
              </p>
              <p className="text-xs text-surface-500 truncate">{user?.email}</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="sticky top-0 z-30 h-16 glass border-b border-surface-700/50 flex items-center justify-between px-4 lg:px-6">
          <button
            className="lg:hidden text-surface-400 hover:text-surface-100"
            onClick={() => setSidebarOpen(true)}
          >
            <Bars3Icon className="w-6 h-6" />
          </button>

          <div className="flex-1" />

          <div className="flex items-center gap-4">
            <button className="relative p-2 text-surface-400 hover:text-surface-100 transition-colors">
              <BellIcon className="w-6 h-6" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-accent-500 rounded-full" />
            </button>

            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-2 p-2 rounded-lg hover:bg-surface-800/50 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-sm font-semibold">
                  {user?.firstName?.[0]}{user?.lastName?.[0]}
                </div>
                <ChevronDownIcon className="w-4 h-4 text-surface-400" />
              </button>

              <AnimatePresence>
                {userMenuOpen && (
                  <>
                    <div
                      className="fixed inset-0"
                      onClick={() => setUserMenuOpen(false)}
                    />
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="absolute right-0 mt-2 w-56 rounded-xl glass border border-surface-700/50 shadow-xl py-2"
                    >
                      <div className="px-4 py-2 border-b border-surface-700/50">
                        <p className="text-sm font-medium text-surface-100">
                          {user?.firstName} {user?.lastName}
                        </p>
                        <p className="text-xs text-surface-500">{user?.email}</p>
                        <span className="inline-block mt-1 px-2 py-0.5 text-xs font-medium bg-primary-500/20 text-primary-300 rounded-full">
                          {user?.role === 'ADMIN' ? 'Administrador' : 'Usuario'}
                        </span>
                      </div>
                      <NavLink
                        to="/profile"
                        className="flex items-center gap-2 px-4 py-2 text-sm text-surface-300 hover:text-surface-100 hover:bg-surface-800/50"
                        onClick={() => setUserMenuOpen(false)}
                      >
                        <CogIcon className="w-4 h-4" />
                        Mi Perfil
                      </NavLink>
                      <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-surface-800/50"
                      >
                        <ArrowRightOnRectangleIcon className="w-4 h-4" />
                        Cerrar Sesión
                      </button>
                    </motion.div>
                  </>
                )}
              </AnimatePresence>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 lg:p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

