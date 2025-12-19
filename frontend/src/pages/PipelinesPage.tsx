"use client"

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import {
  MagnifyingGlassIcon,
  CogIcon,
  ArrowTopRightOnSquareIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import { pipelinesApi } from '@/services/api';
import { GitlabPipeline } from '@/types';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import { StatusBadge } from '@/components/ui/Badge';

export default function PipelinesPage() {
  const [branch, setBranch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const { data: pipelinesData, isLoading } = useQuery({
    queryKey: ['pipelines', branch, statusFilter],
    queryFn: async () => {
      const params: Record<string, string> = { limit: '100' };
      if (branch) params.branch = branch;
      if (statusFilter) params.status = statusFilter;
      const response = await pipelinesApi.getAll(params);
      return response.data;
    },
  });

  const pipelines = pipelinesData?.data || [];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'PASSED':
        return <CheckCircleIcon className="w-5 h-5 text-emerald-400" />;
      case 'FAILED':
        return <XCircleIcon className="w-5 h-5 text-red-400" />;
      case 'RUNNING':
        return <ClockIcon className="w-5 h-5 text-amber-400 animate-spin" />;
      default:
        return <div className="w-5 h-5 rounded-full bg-surface-600" />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div>
        <h1 className="text-2xl font-display font-bold text-surface-100">
          Pipelines GitLab
        </h1>
        <p className="text-surface-400 mt-1">
          ⚙️ Resultados de ejecución de pipelines CI/CD
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div className="w-full sm:w-64">
          <Input
            placeholder="Filtrar por branch..."
            value={branch}
            onChange={(e) => setBranch(e.target.value)}
            leftIcon={<MagnifyingGlassIcon className="w-5 h-5" />}
          />
        </div>
        <div className="w-full sm:w-48">
          <Select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            options={[
              { value: '', label: 'Todos los estados' },
              { value: 'PASSED', label: 'Exitoso' },
              { value: 'FAILED', label: 'Fallido' },
              { value: 'RUNNING', label: 'Ejecutando' },
              { value: 'PENDING', label: 'Pendiente' },
              { value: 'CANCELED', label: 'Cancelado' },
            ]}
          />
        </div>
      </div>

      {/* Pipelines Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="animate-pulse space-y-4 p-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-16 bg-surface-700 rounded" />
            ))}
          </div>
        ) : pipelines.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-3">⚙️</div>
            <h3 className="text-lg font-medium text-surface-300 mb-2">
              No hay pipelines
            </h3>
            <p className="text-surface-500">
              {branch ? 'No se encontraron resultados' : 'No hay pipelines registrados'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Pipeline</th>
                  <th>Branch</th>
                  <th>Estado</th>
                  <th>Casos de Prueba</th>
                  <th>Fecha</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {pipelines.map((pipeline: GitlabPipeline) => (
                  <tr key={pipeline.id}>
                    <td>
                      <div className="flex items-center gap-3">
                        {getStatusIcon(pipeline.status)}
                        <span className="font-mono text-primary-400">
                          #{pipeline.gitlabPipelineId}
                        </span>
                      </div>
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
                      {pipeline._count?.testCaseResults || 0} casos
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
                          className="inline-flex items-center gap-1 text-sm text-primary-400 hover:text-primary-300"
                        >
                          Ver en GitLab
                          <ArrowTopRightOnSquareIcon className="w-4 h-4" />
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </motion.div>
  );
}

