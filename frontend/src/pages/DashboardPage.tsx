"use client"

import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  FolderIcon,
  CubeIcon,
  DocumentTextIcon,
  BeakerIcon,
  ClipboardDocumentListIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import { dashboardApi } from '@/services/api';
import { StatusBadge } from '@/components/ui/Badge';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const COLORS = ['#0c8ce9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export default function DashboardPage() {
  const { data: stats } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await dashboardApi.getStats();
      return response.data.data;
    },
  });

  const { data: activity } = useQuery({
    queryKey: ['dashboard-activity'],
    queryFn: async () => {
      const response = await dashboardApi.getRecentActivity(5);
      return response.data.data;
    },
  });

  const statCards = [
    {
      name: 'Agrupadores',
      value: stats?.overview?.totalGroups || 0,
      icon: FolderIcon,
      href: '/groups',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      name: 'Aplicaciones',
      value: stats?.overview?.totalApplications || 0,
      icon: CubeIcon,
      href: '/applications',
      color: 'from-purple-500 to-pink-500',
    },
    {
      name: 'Features',
      value: stats?.overview?.totalFeatures || 0,
      icon: DocumentTextIcon,
      href: '/features',
      color: 'from-green-500 to-emerald-500',
    },
    {
      name: 'Casos de Prueba',
      value: stats?.overview?.totalTestCases || 0,
      icon: BeakerIcon,
      href: '/test-cases',
      color: 'from-orange-500 to-amber-500',
    },
    {
      name: 'Solicitudes Pendientes',
      value: stats?.overview?.pendingRequests || 0,
      icon: ClipboardDocumentListIcon,
      href: '/requests',
      color: 'from-red-500 to-rose-500',
    },
    {
      name: 'Pipelines (7 días)',
      value: stats?.overview?.recentPipelines || 0,
      icon: ClockIcon,
      href: '/pipelines',
      color: 'from-teal-500 to-cyan-500',
    },
  ];

  const testCaseChartData = stats?.testCasesByStatus?.map((item: any) => ({
    name: item.status === 'PLANNED' ? 'Planificado' :
          item.status === 'IN_DEVELOPMENT' ? 'En Desarrollo' :
          item.status === 'PRODUCTIVE' ? 'Productivo' :
          item.status === 'OBSOLETE' ? 'Obsoleto' : item.status,
    value: item.count,
  })) || [];

  const requestsChartData = stats?.requestsByStatus?.map((item: any) => ({
    name: item.status === 'NEW' ? 'Nuevas' :
          item.status === 'IN_ANALYSIS' ? 'En Análisis' :
          item.status === 'APPROVED' ? 'Aprobadas' :
          item.status === 'REJECTED' ? 'Rechazadas' :
          item.status === 'IMPLEMENTED' ? 'Implementadas' : item.status,
    value: item.count,
  })) || [];

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Page header */}
      <motion.div variants={itemVariants}>
        <h1 className="text-2xl font-display font-bold text-surface-100">
          Dashboard
        </h1>
        <p className="text-surface-400 mt-1">
          📊 Resumen general del sistema de gestión de casos de prueba
        </p>
      </motion.div>

      {/* Stats grid */}
      <motion.div
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        {statCards.map((stat) => (
          <Link key={stat.name} to={stat.href}>
            <div className="stat-card group hover:border-surface-600 transition-all duration-300">
              <div className="relative z-10 flex items-center justify-between">
                <div>
                  <p className="text-sm text-surface-400">{stat.name}</p>
                  <p className="text-3xl font-display font-bold text-surface-100 mt-1">
                    {stat.value}
                  </p>
                </div>
                <div
                  className={`w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}
                >
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          </Link>
        ))}
      </motion.div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Test Cases by Status */}
        <motion.div variants={itemVariants} className="card">
          <h2 className="text-lg font-display font-semibold text-surface-100 mb-4">
            Casos de Prueba por Estado
          </h2>
          {testCaseChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={testCaseChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="value" fill="#0c8ce9" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-surface-500">
              📊 No hay datos disponibles
            </div>
          )}
        </motion.div>

        {/* Requests by Status */}
        <motion.div variants={itemVariants} className="card">
          <h2 className="text-lg font-display font-semibold text-surface-100 mb-4">
            Solicitudes por Estado
          </h2>
          {requestsChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={requestsChartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                  labelLine={{ stroke: '#64748b' }}
                >
                  {requestsChartData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-surface-500">
              📊 No hay datos disponibles
            </div>
          )}
        </motion.div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Test Cases */}
        <motion.div variants={itemVariants} className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-display font-semibold text-surface-100">
              Casos de Prueba Recientes
            </h2>
            <Link to="/test-cases" className="text-sm text-primary-400 hover:text-primary-300">
              Ver todos
            </Link>
          </div>
          <div className="space-y-3">
            {activity?.testCases?.map((tc: any) => (
              <Link
                key={tc.id}
                to={`/test-cases/${tc.id}`}
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-surface-800/50 transition-colors group"
              >
                <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
                  <BeakerIcon className="w-5 h-5 text-primary-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-surface-200 truncate group-hover:text-primary-300">
                    {tc.name}
                  </p>
                  <p className="text-xs text-surface-500 truncate">
                    {tc.feature?.application?.name} / {tc.feature?.name}
                  </p>
                </div>
                <StatusBadge status={tc.status} />
              </Link>
            ))}
            {!activity?.testCases?.length && (
              <p className="text-center text-surface-500 py-4">
                🔬 No hay actividad reciente
              </p>
            )}
          </div>
        </motion.div>

        {/* Recent Requests */}
        <motion.div variants={itemVariants} className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-display font-semibold text-surface-100">
              Solicitudes Recientes
            </h2>
            <Link to="/requests" className="text-sm text-primary-400 hover:text-primary-300">
              Ver todas
            </Link>
          </div>
          <div className="space-y-3">
            {activity?.requests?.map((req: any) => (
              <Link
                key={req.id}
                to={`/requests/${req.id}`}
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-surface-800/50 transition-colors group"
              >
                <div className="w-10 h-10 rounded-lg bg-accent-500/20 flex items-center justify-center">
                  <ClipboardDocumentListIcon className="w-5 h-5 text-accent-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-surface-200 truncate group-hover:text-accent-300">
                    {req.title}
                  </p>
                  <p className="text-xs text-surface-500">
                    {req.requester?.firstName} {req.requester?.lastName} ·{' '}
                    {formatDistanceToNow(new Date(req.updatedAt), {
                      addSuffix: true,
                      locale: es,
                    })}
                  </p>
                </div>
                <StatusBadge status={req.status} />
              </Link>
            ))}
            {!activity?.requests?.length && (
              <p className="text-center text-surface-500 py-4">
                📋 No hay solicitudes recientes
              </p>
            )}
          </div>
        </motion.div>
      </div>

      {/* Recent Pipelines */}
      <motion.div variants={itemVariants} className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-display font-semibold text-surface-100">
            Últimos Pipelines
          </h2>
          <Link to="/pipelines" className="text-sm text-primary-400 hover:text-primary-300">
            Ver todos
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Pipeline ID</th>
                <th>Branch</th>
                <th>Estado</th>
                <th>Fecha</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {activity?.pipelines?.map((pipeline: any) => (
                <tr key={pipeline.id}>
                  <td className="font-mono text-primary-400">
                    #{pipeline.gitlabPipelineId}
                  </td>
                  <td>
                    <span className="px-2 py-1 bg-surface-700 rounded text-xs font-mono">
                      {pipeline.branch}
                    </span>
                  </td>
                  <td>
                    <StatusBadge status={pipeline.status} />
                  </td>
                  <td className="text-surface-400">
                    {formatDistanceToNow(new Date(pipeline.executedAt), {
                      addSuffix: true,
                      locale: es,
                    })}
                  </td>
                  <td>
                    {pipeline.webUrl && (
                      <a
                        href={pipeline.webUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-primary-400 hover:text-primary-300"
                      >
                        Ver en GitLab
                      </a>
                    )}
                  </td>
                </tr>
              ))}
              {!activity?.pipelines?.length && (
                <tr>
                  <td colSpan={5} className="text-center text-surface-500 py-8">
                    ⚙️ No hay pipelines recientes
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </motion.div>
    </motion.div>
  );
}

