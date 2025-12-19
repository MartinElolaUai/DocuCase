"use client"

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  BeakerIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
import { testCasesApi, applicationsApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import { TestCase, Application } from '@/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import { StatusBadge, PriorityBadge, TypeBadge } from '@/components/ui/Badge';

export default function TestCasesPage() {
  const [search, setSearch] = useState('');
  const [appFilter, setAppFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const { user } = useAuthStore();
  const isAdmin = user?.role === 'ADMIN';

  const { data: testCasesData, isLoading } = useQuery({
    queryKey: ['test-cases', search, appFilter, statusFilter, typeFilter],
    queryFn: async () => {
      const params: Record<string, string> = { limit: '100' };
      if (search) params.search = search;
      if (appFilter) params.applicationId = appFilter;
      if (statusFilter) params.status = statusFilter;
      if (typeFilter) params.type = typeFilter;
      const response = await testCasesApi.getAll(params);
      return response.data;
    },
  });

  const { data: appsData } = useQuery({
    queryKey: ['applications-list'],
    queryFn: async () => {
      const response = await applicationsApi.getAll({ limit: '100' });
      return response.data.data;
    },
  });

  const testCases = testCasesData?.data || [];
  const applications = appsData || [];

  const getLastResult = (tc: TestCase) => {
    if (!tc.pipelineResults?.length) return null;
    return tc.pipelineResults[0];
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-surface-100">
            Casos de Prueba
          </h1>
          <p className="text-surface-400 mt-1">
            🔬 Gestiona los casos de prueba automatizados
          </p>
        </div>
        {isAdmin && (
          <Link to="/test-cases/new">
            <Button leftIcon={<PlusIcon className="w-5 h-5" />}>
              Nuevo Caso de Prueba
            </Button>
          </Link>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div className="w-full sm:w-64">
          <Input
            placeholder="Buscar casos de prueba..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            leftIcon={<MagnifyingGlassIcon className="w-5 h-5" />}
          />
        </div>
        <div className="w-full sm:w-48">
          <Select
            value={appFilter}
            onChange={(e) => setAppFilter(e.target.value)}
            options={[
              { value: '', label: 'Todas las aplicaciones' },
              ...applications.map((a: Application) => ({ value: a.id, label: a.name })),
            ]}
          />
        </div>
        <div className="w-full sm:w-40">
          <Select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            options={[
              { value: '', label: 'Todos los estados' },
              { value: 'PLANNED', label: 'Planificado' },
              { value: 'IN_DEVELOPMENT', label: 'En Desarrollo' },
              { value: 'PRODUCTIVE', label: 'Productivo' },
              { value: 'OBSOLETE', label: 'Obsoleto' },
            ]}
          />
        </div>
        <div className="w-full sm:w-40">
          <Select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            options={[
              { value: '', label: 'Todos los tipos' },
              { value: 'AUTOMATED', label: 'Automatizado' },
              { value: 'MANUAL', label: 'Manual' },
            ]}
          />
        </div>
      </div>

      {/* Test Cases Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="animate-pulse space-y-4 p-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-surface-700 rounded" />
            ))}
          </div>
        ) : testCases.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-3">🔬</div>
            <h3 className="text-lg font-medium text-surface-300 mb-2">
              No hay casos de prueba
            </h3>
            <p className="text-surface-500">
              {search ? 'No se encontraron resultados' : 'Crea el primer caso de prueba'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Feature / App</th>
                  <th>Tipo</th>
                  <th>Prioridad</th>
                  <th>Estado</th>
                  <th>Último Resultado</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {testCases.map((tc: TestCase) => {
                  const lastResult = getLastResult(tc);
                  return (
                    <tr key={tc.id}>
                      <td>
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-orange-500/20 flex items-center justify-center">
                            <BeakerIcon className="w-4 h-4 text-orange-400" />
                          </div>
                          <div>
                            <p className="font-medium text-surface-100">{tc.name}</p>
                            {tc.scenarioName && (
                              <p className="text-xs text-surface-500 font-mono">{tc.scenarioName}</p>
                            )}
                          </div>
                        </div>
                      </td>
                      <td>
                        <div>
                          <p className="text-sm">{tc.feature?.name}</p>
                          <p className="text-xs text-surface-500">{tc.feature?.application?.name}</p>
                        </div>
                      </td>
                      <td><TypeBadge type={tc.type} /></td>
                      <td><PriorityBadge priority={tc.priority} /></td>
                      <td><StatusBadge status={tc.status} /></td>
                      <td>
                        {lastResult ? (
                          <div className="flex items-center gap-2">
                            {lastResult.status === 'PASSED' ? (
                              <CheckCircleIcon className="w-5 h-5 text-emerald-400" />
                            ) : lastResult.status === 'FAILED' ? (
                              <XCircleIcon className="w-5 h-5 text-red-400" />
                            ) : (
                              <span className="w-5 h-5 rounded-full bg-surface-600" />
                            )}
                            <StatusBadge status={lastResult.status} />
                          </div>
                        ) : (
                          <span className="text-surface-500 text-sm">Sin ejecución</span>
                        )}
                      </td>
                      <td>
                        <Link
                          to={`/test-cases/${tc.id}`}
                          className="text-primary-400 hover:text-primary-300 flex items-center gap-1"
                        >
                          Ver
                          <ArrowRightIcon className="w-4 h-4" />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </motion.div>
  );
}

