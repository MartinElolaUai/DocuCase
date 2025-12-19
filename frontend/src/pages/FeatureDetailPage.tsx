"use client"

import { motion } from 'framer-motion';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  ArrowLeftIcon,
  DocumentTextIcon,
  BeakerIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
import { featuresApi } from '@/services/api';
import { StatusBadge, PriorityBadge, TypeBadge } from '@/components/ui/Badge';
import Button from '@/components/ui/Button';

export default function FeatureDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: feature, isLoading } = useQuery({
    queryKey: ['feature', id],
    queryFn: async () => {
      const response = await featuresApi.getById(id!);
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

  if (!feature) {
    return (
      <div className="card text-center py-12">
        <div className="text-4xl mb-3">📄</div>
        <p className="text-surface-400">Feature no encontrada</p>
        <Link to="/features">
          <Button variant="secondary" className="mt-4">
            Volver a features
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
      <Link to="/features" className="inline-flex items-center gap-2 text-surface-400 hover:text-surface-100 transition-colors">
        <ArrowLeftIcon className="w-4 h-4" />
        Volver a features
      </Link>

      {/* Header */}
      <div className="card">
        <div className="flex items-start gap-4">
          <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-green-500/20 to-emerald-500/20 flex items-center justify-center">
            <DocumentTextIcon className="w-8 h-8 text-green-400" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-display font-bold text-surface-100">
                {feature.name}
              </h1>
              <StatusBadge status={feature.status} />
            </div>
            <p className="text-surface-400 mt-1">{feature.description || 'Sin descripción'}</p>
            <div className="flex items-center gap-4 mt-4">
              <Link to={`/applications/${feature.applicationId}`}>
                <span className="px-3 py-1 bg-surface-800 rounded-lg text-sm text-surface-300 hover:bg-surface-700 transition-colors">
                  {feature.application?.name}
                </span>
              </Link>
              {feature.featureFilePath && (
                <span className="text-sm font-mono text-surface-500">
                  {feature.featureFilePath}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Test Cases */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-display font-semibold text-surface-100">
            Casos de Prueba ({feature.testCases?.length || 0})
          </h2>
          <Link to="/test-cases">
            <Button variant="secondary" size="sm">
              Ver todos los casos
            </Button>
          </Link>
        </div>

        {feature.testCases?.length === 0 ? (
          <div className="text-center py-8 text-surface-500">
            <BeakerIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No hay casos de prueba para esta feature</p>
          </div>
        ) : (
          <div className="space-y-3">
            {feature.testCases?.map((tc: any) => (
              <Link
                key={tc.id}
                to={`/test-cases/${tc.id}`}
                className="flex items-center gap-4 p-4 rounded-lg bg-surface-800/50 border border-surface-700/50 hover:border-surface-600 transition-colors group"
              >
                <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center">
                  <BeakerIcon className="w-5 h-5 text-orange-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-surface-100 truncate group-hover:text-primary-300">
                    {tc.name}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <TypeBadge type={tc.type} />
                    <PriorityBadge priority={tc.priority} />
                    <StatusBadge status={tc.status} />
                  </div>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-surface-500">{tc._count?.steps || 0} steps</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

