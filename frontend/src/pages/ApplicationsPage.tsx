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
  CubeIcon,
  DocumentTextIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline';
import { applicationsApi, groupsApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import { Application, Group } from '@/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Modal from '@/components/ui/Modal';
import { StatusBadge } from '@/components/ui/Badge';

interface ApplicationForm {
  name: string;
  description: string;
  groupId: string;
  gitlabProjectId: string;
  gitlabProjectUrl: string;
}

export default function ApplicationsPage() {
  const [search, setSearch] = useState('');
  const [groupFilter, setGroupFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingApp, setEditingApp] = useState<Application | null>(null);
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const isAdmin = user?.role === 'ADMIN';

  const { register, handleSubmit, reset, formState: { errors } } = useForm<ApplicationForm>();

  const { data: appsData, isLoading } = useQuery({
    queryKey: ['applications', search, groupFilter, statusFilter],
    queryFn: async () => {
      const params: Record<string, string> = { limit: '100' };
      if (search) params.search = search;
      if (groupFilter) params.groupId = groupFilter;
      if (statusFilter) params.status = statusFilter;
      const response = await applicationsApi.getAll(params);
      return response.data;
    },
  });

  const { data: groupsData } = useQuery({
    queryKey: ['groups-list'],
    queryFn: async () => {
      const response = await groupsApi.getAll({ limit: '100' });
      return response.data.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: ApplicationForm) => applicationsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      toast.success('Aplicación creada exitosamente');
      handleCloseModal();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al crear aplicación');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ApplicationForm> }) =>
      applicationsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      toast.success('Aplicación actualizada exitosamente');
      handleCloseModal();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al actualizar');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => applicationsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      toast.success('Aplicación eliminada exitosamente');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al eliminar');
    },
  });

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingApp(null);
    reset();
  };

  const handleEdit = (app: Application) => {
    setEditingApp(app);
    reset({
      name: app.name,
      description: app.description || '',
      groupId: app.groupId,
      gitlabProjectId: app.gitlabProjectId || '',
      gitlabProjectUrl: app.gitlabProjectUrl || '',
    });
    setIsModalOpen(true);
  };

  const onSubmit = (data: ApplicationForm) => {
    if (editingApp) {
      updateMutation.mutate({ id: editingApp.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleDelete = (app: Application) => {
    if (confirm(`¿Estás seguro de eliminar la aplicación "${app.name}"?`)) {
      deleteMutation.mutate(app.id);
    }
  };

  const applications = appsData?.data || [];
  const groups = groupsData || [];

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
            Aplicaciones
          </h1>
          <p className="text-surface-400 mt-1">
            📱 Gestiona las aplicaciones del sistema
          </p>
        </div>
        {isAdmin && (
          <Button
            onClick={() => setIsModalOpen(true)}
            leftIcon={<PlusIcon className="w-5 h-5" />}
          >
            Nueva Aplicación
          </Button>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div className="w-full sm:w-64">
          <Input
            placeholder="Buscar aplicaciones..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            leftIcon={<MagnifyingGlassIcon className="w-5 h-5" />}
          />
        </div>
        <div className="w-full sm:w-48">
          <Select
            value={groupFilter}
            onChange={(e) => setGroupFilter(e.target.value)}
            options={[
              { value: '', label: 'Todos los agrupadores' },
              ...groups.map((g: Group) => ({ value: g.id, label: g.name })),
            ]}
          />
        </div>
        <div className="w-full sm:w-40">
          <Select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            options={[
              { value: '', label: 'Todos los estados' },
              { value: 'ACTIVE', label: 'Activas' },
              { value: 'DISCONTINUED', label: 'Descontinuadas' },
            ]}
          />
        </div>
      </div>

      {/* Applications Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-6 bg-surface-700 rounded w-3/4 mb-4" />
              <div className="h-4 bg-surface-700 rounded w-full mb-2" />
              <div className="h-4 bg-surface-700 rounded w-2/3" />
            </div>
          ))}
        </div>
      ) : applications.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-4xl mb-3">📱</div>
          <h3 className="text-lg font-medium text-surface-300 mb-2">
            No hay aplicaciones
          </h3>
          <p className="text-surface-500">
            {search ? 'No se encontraron resultados' : 'Crea la primera aplicación'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {applications.map((app: Application) => (
            <motion.div
              key={app.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card-hover relative group"
            >
              <Link to={`/applications/${app.id}`} className="block">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center flex-shrink-0">
                    <CubeIcon className="w-6 h-6 text-purple-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-semibold text-surface-100 truncate">
                        {app.name}
                      </h3>
                      <StatusBadge status={app.status} />
                    </div>
                    <p className="text-sm text-surface-400 line-clamp-2 mt-1">
                      {app.description || 'Sin descripción'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-4 mt-4 text-sm text-surface-500">
                  <span className="px-2 py-1 bg-surface-800 rounded text-xs">
                    {app.group?.name}
                  </span>
                  <div className="flex items-center gap-1">
                    <DocumentTextIcon className="w-4 h-4" />
                    <span>{app._count?.features || 0} features</span>
                  </div>
                </div>

                <div className="flex items-center justify-between mt-4 pt-4 border-t border-surface-700/50">
                  <span className="text-sm text-primary-400 flex items-center gap-1 group-hover:gap-2 transition-all">
                    Ver detalles
                    <ArrowRightIcon className="w-4 h-4" />
                  </span>
                  {app.gitlabProjectUrl && (
                    <a
                      href={app.gitlabProjectUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="p-1.5 rounded-lg text-surface-400 hover:text-primary-400 hover:bg-surface-700 transition-colors"
                      title="Ver en GitLab"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="6" x2="6" y1="3" y2="15"></line>
                        <circle cx="18" cy="6" r="3"></circle>
                        <circle cx="6" cy="18" r="3"></circle>
                        <path d="M18 9a9 9 0 0 1-9 9"></path>
                      </svg>
                    </a>
                  )}
                </div>
              </Link>

              {isAdmin && (
                <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                  <button
                    onClick={(e) => { e.preventDefault(); handleEdit(app); }}
                    className="p-1.5 rounded-lg text-surface-400 hover:text-surface-100 hover:bg-surface-700"
                  >
                    <PencilIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => { e.preventDefault(); handleDelete(app); }}
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
        title={editingApp ? 'Editar Aplicación' : 'Nueva Aplicación'}
        size="lg"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Nombre"
            placeholder="Nombre de la aplicación"
            error={errors.name?.message}
            {...register('name', { required: 'El nombre es requerido' })}
          />
          
          <Select
            label="Agrupador"
            error={errors.groupId?.message}
            options={[
              { value: '', label: 'Seleccionar agrupador' },
              ...groups.map((g: Group) => ({ value: g.id, label: g.name })),
            ]}
            {...register('groupId', { required: 'El agrupador es requerido' })}
          />

          <div>
            <label className="label">Descripción</label>
            <textarea
              className="input min-h-[100px] resize-none"
              placeholder="Descripción de la aplicación"
              {...register('description')}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="GitLab Project ID"
              placeholder="12345"
              {...register('gitlabProjectId')}
            />
            <Input
              label="GitLab Project URL"
              placeholder="https://gitlab.com/..."
              {...register('gitlabProjectUrl')}
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
              {editingApp ? 'Guardar cambios' : 'Crear aplicación'}
            </Button>
          </div>
        </form>
      </Modal>
    </motion.div>
  );
}

