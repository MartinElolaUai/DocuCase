"use client"

import { motion } from 'framer-motion';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  ArrowLeftIcon,
  CubeIcon,
  DocumentTextIcon,
  BeakerIcon,
  LinkIcon,
} from '@heroicons/react/24/outline';
import { applicationsApi } from '@/services/api';
import { StatusBadge } from '@/components/ui/Badge';
import Button from '@/components/ui/Button';

export default function ApplicationDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: app, isLoading } = useQuery({
    queryKey: ['application', id],
    queryFn: async () => {
      const response = await applicationsApi.getById(id!);
      return response.data.data;
    },
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 bg-surface-700 rounded w-1/4" />
        <div className="card">
          <div className="h-6 bg-surface-700 rounded w-1/2 mb-4" />
          <div className="h-4 bg-surface-700 rounded w-3/4" />
        </div>
      </div>
    );
  }

  if (!app) {
    return (
      <div className="card text-center py-12">
        <div className="text-4xl mb-3">📱</div>
        <p className="text-surface-400">Aplicación no encontrada</p>
        <Link to="/applications">
          <Button variant="secondary" className="mt-4">
            Volver a aplicaciones
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Back button */}
      <Link to="/applications" className="inline-flex items-center gap-2 text-surface-400 hover:text-surface-100 transition-colors">
        <ArrowLeftIcon className="w-4 h-4" />
        Volver a aplicaciones
      </Link>

      {/* Header */}
      <div className="card">
        <div className="flex items-start gap-4">
          <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center">
            <CubeIcon className="w-8 h-8 text-purple-400" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-display font-bold text-surface-100">
                {app.name}
              </h1>
              <StatusBadge status={app.status} />
            </div>
            <p className="text-surface-400 mt-1">{app.description || 'Sin descripción'}</p>
            <div className="flex items-center gap-4 mt-4">
              <span className="px-3 py-1 bg-surface-800 rounded-lg text-sm text-surface-300">
                {app.group?.name}
              </span>
              {app.gitlabProjectUrl && (
                <a
                  href={app.gitlabProjectUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-3 py-1.5 bg-surface-800 hover:bg-surface-700 rounded-lg text-sm text-primary-400 hover:text-primary-300 transition-colors"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="6" x2="6" y1="3" y2="15"></line>
                    <circle cx="18" cy="6" r="3"></circle>
                    <circle cx="6" cy="18" r="3"></circle>
                    <path d="M18 9a9 9 0 0 1-9 9"></path>
                  </svg>
                  <span>Ver en GitLab</span>
                </a>
              )}
              {app.availabilityUrl && (
                <a
                  href={app.availabilityUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-3 py-1.5 bg-surface-800 hover:bg-surface-700 rounded-lg text-sm text-emerald-400 hover:text-emerald-300 transition-colors"
                >
                  <LinkIcon className="w-4 h-4" />
                  <span>Ver en Disponibilidad</span>
                </a>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-display font-semibold text-surface-100">
            Features ({app.features?.length || 0})
          </h2>
          <Link to="/features">
            <Button variant="secondary" size="sm">
              Ver todas las features
            </Button>
          </Link>
        </div>

        {app.features?.length === 0 ? (
          <div className="text-center py-8 text-surface-500">
            <DocumentTextIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No hay features para esta aplicación</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {app.features?.map((feature: any) => (
              <Link
                key={feature.id}
                to={`/features/${feature.id}`}
                className="p-4 rounded-lg bg-surface-800/50 border border-surface-700/50 hover:border-surface-600 transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                    <DocumentTextIcon className="w-5 h-5 text-green-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium text-surface-100 truncate group-hover:text-primary-300">
                        {feature.name}
                      </h3>
                      <StatusBadge status={feature.status} />
                    </div>
                    <p className="text-sm text-surface-500">
                      {feature._count?.testCases || 0} casos de prueba
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

