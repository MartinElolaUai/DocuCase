"use client"

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  DocumentTextIcon,
  BeakerIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline';
import { featuresApi, applicationsApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import { Feature, Application } from '@/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Modal from '@/components/ui/Modal';
import { StatusBadge } from '@/components/ui/Badge';

interface FeatureForm {
  name: string;
  description: string;
  applicationId: string;
  featureFilePath: string;
  status: string;
}

export default function FeaturesPage() {
  const [search, setSearch] = useState('');
  const [appFilter, setAppFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingFeature, setEditingFeature] = useState<Feature | null>(null);
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const isAdmin = user?.role === 'ADMIN';

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FeatureForm>();

  const { data: featuresData, isLoading } = useQuery({
    queryKey: ['features', search, appFilter, statusFilter],
    queryFn: async () => {
      const params: Record<string, string> = { limit: '100' };
      if (search) params.search = search;
      if (appFilter) params.applicationId = appFilter;
      if (statusFilter) params.status = statusFilter;
      const response = await featuresApi.getAll(params);
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

  const createMutation = useMutation({
    mutationFn: (data: FeatureForm) => featuresApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['features'] });
      toast.success('Feature creada exitosamente');
      handleCloseModal();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al crear feature');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<FeatureForm> }) =>
      featuresApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['features'] });
      toast.success('Feature actualizada exitosamente');
      handleCloseModal();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al actualizar');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => featuresApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['features'] });
      toast.success('Feature eliminada exitosamente');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al eliminar');
    },
  });

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingFeature(null);
    reset();
  };

  const handleEdit = (feature: Feature) => {
    setEditingFeature(feature);
    reset({
      name: feature.name,
      description: feature.description || '',
      applicationId: feature.applicationId,
      featureFilePath: feature.featureFilePath || '',
      status: feature.status,
    });
    setIsModalOpen(true);
  };

  const onSubmit = (data: FeatureForm) => {
    if (editingFeature) {
      updateMutation.mutate({ id: editingFeature.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleDelete = (feature: Feature) => {
    if (confirm(`¿Estás seguro de eliminar la feature "${feature.name}"?`)) {
      deleteMutation.mutate(feature.id);
    }
  };

  const features = featuresData?.data || [];
  const applications = appsData || [];

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
            Features
          </h1>
          <p className="text-surface-400 mt-1">
            📄 Gestiona las features de Cucumber
          </p>
        </div>
        {isAdmin && (
          <Button
            onClick={() => setIsModalOpen(true)}
            leftIcon={<PlusIcon className="w-5 h-5" />}
          >
            Nueva Feature
          </Button>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div className="w-full sm:w-64">
          <Input
            placeholder="Buscar features..."
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
            ]}
          />
        </div>
      </div>

      {/* Features Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-6 bg-surface-700 rounded w-3/4 mb-4" />
              <div className="h-4 bg-surface-700 rounded w-full mb-2" />
            </div>
          ))}
        </div>
      ) : features.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-4xl mb-3">📄</div>
          <h3 className="text-lg font-medium text-surface-300 mb-2">
            No hay features
          </h3>
          <p className="text-surface-500">
            {search ? 'No se encontraron resultados' : 'Crea la primera feature'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((feature: Feature) => (
            <motion.div
              key={feature.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card-hover relative group"
            >
              <Link to={`/features/${feature.id}`} className="block">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500/20 to-emerald-500/20 flex items-center justify-center flex-shrink-0">
                    <DocumentTextIcon className="w-6 h-6 text-green-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-semibold text-surface-100 truncate">
                        {feature.name}
                      </h3>
                    </div>
                    <StatusBadge status={feature.status} />
                    <p className="text-sm text-surface-400 line-clamp-2 mt-2">
                      {feature.description || 'Sin descripción'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-4 mt-4 text-sm text-surface-500">
                  <span className="px-2 py-1 bg-surface-800 rounded text-xs truncate max-w-[150px]">
                    {feature.application?.name}
                  </span>
                  <div className="flex items-center gap-1">
                    <BeakerIcon className="w-4 h-4" />
                    <span>{feature._count?.testCases || 0} casos</span>
                  </div>
                </div>

                {feature.featureFilePath && (
                  <p className="mt-3 text-xs font-mono text-surface-500 truncate">
                    {feature.featureFilePath}
                  </p>
                )}

                <div className="flex items-center justify-between mt-4 pt-4 border-t border-surface-700/50">
                  <span className="text-sm text-primary-400 flex items-center gap-1 group-hover:gap-2 transition-all">
                    Ver detalles
                    <ArrowRightIcon className="w-4 h-4" />
                  </span>
                </div>
              </Link>

              {isAdmin && (
                <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                  <button
                    onClick={(e) => { e.preventDefault(); handleEdit(feature); }}
                    className="p-1.5 rounded-lg text-surface-400 hover:text-surface-100 hover:bg-surface-700"
                  >
                    <PencilIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => { e.preventDefault(); handleDelete(feature); }}
                    className="p-1.5 rounded-lg text-surface-400 hover:text-red-400 hover:bg-surface-700"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingFeature ? 'Editar Feature' : 'Nueva Feature'}
        size="lg"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Nombre"
            placeholder="Nombre de la feature"
            error={errors.name?.message}
            {...register('name', { required: 'El nombre es requerido' })}
          />
          
          <Select
            label="Aplicación"
            error={errors.applicationId?.message}
            options={[
              { value: '', label: 'Seleccionar aplicación' },
              ...applications.map((a: Application) => ({ value: a.id, label: a.name })),
            ]}
            {...register('applicationId', { required: 'La aplicación es requerida' })}
          />

          <Select
            label="Estado"
            options={[
              { value: 'PLANNED', label: 'Planificado' },
              { value: 'IN_DEVELOPMENT', label: 'En Desarrollo' },
              { value: 'PRODUCTIVE', label: 'Productivo' },
            ]}
            {...register('status')}
          />

          <Input
            label="Ruta del archivo .feature"
            placeholder="features/mi_feature.feature"
            {...register('featureFilePath')}
          />

          <div>
            <label className="label">Descripción</label>
            <textarea
              className="input min-h-[100px] resize-none"
              placeholder="Descripción de la feature"
              {...register('description')}
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button variant="secondary" type="button" onClick={handleCloseModal}>
              Cancelar
            </Button>
            <Button
              type="submit"
              loading={createMutation.isPending || updateMutation.isPending}
            >
              {editingFeature ? 'Guardar cambios' : 'Crear feature'}
            </Button>
          </div>
        </form>
      </Modal>
    </motion.div>
  );
}

