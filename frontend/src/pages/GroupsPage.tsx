"use client"

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  FolderIcon,
  CubeIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';
import { groupsApi, usersApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import { Group } from '@/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Modal from '@/components/ui/Modal';
import { Link } from 'react-router-dom';

interface GroupForm {
  name: string;
  description: string;
}

export default function GroupsPage() {
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingGroup, setEditingGroup] = useState<Group | null>(null);
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const isAdmin = user?.role === 'ADMIN';

  const { register, handleSubmit, reset, formState: { errors } } = useForm<GroupForm>();

  const { data: groupsData, isLoading } = useQuery({
    queryKey: ['groups', search],
    queryFn: async () => {
      const response = await groupsApi.getAll({ search, limit: '100' });
      return response.data;
    },
  });

  const { data: subscriptions } = useQuery({
    queryKey: ['user-subscriptions'],
    queryFn: async () => {
      const response = await usersApi.getSubscriptions();
      return response.data.data;
    },
  });

  const subscribedGroupIds = new Set(subscriptions?.map((s: any) => s.groupId) || []);

  const createMutation = useMutation({
    mutationFn: (data: GroupForm) => groupsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] });
      toast.success('Agrupador creado exitosamente');
      handleCloseModal();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al crear agrupador');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: GroupForm }) =>
      groupsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] });
      toast.success('Agrupador actualizado exitosamente');
      handleCloseModal();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al actualizar agrupador');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => groupsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] });
      toast.success('Agrupador eliminado exitosamente');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al eliminar agrupador');
    },
  });

  const subscribeMutation = useMutation({
    mutationFn: (groupId: string) => usersApi.subscribe(groupId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-subscriptions'] });
      toast.success('Suscrito al agrupador');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al suscribirse');
    },
  });

  const unsubscribeMutation = useMutation({
    mutationFn: (groupId: string) => usersApi.unsubscribe(groupId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-subscriptions'] });
      toast.success('Suscripción cancelada');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al cancelar suscripción');
    },
  });

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingGroup(null);
    reset();
  };

  const handleEdit = (group: Group) => {
    setEditingGroup(group);
    reset({ name: group.name, description: group.description || '' });
    setIsModalOpen(true);
  };

  const onSubmit = (data: GroupForm) => {
    if (editingGroup) {
      updateMutation.mutate({ id: editingGroup.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleDelete = (group: Group) => {
    if (confirm(`¿Estás seguro de eliminar el agrupador "${group.name}"?`)) {
      deleteMutation.mutate(group.id);
    }
  };

  const groups = groupsData?.data || [];

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
            Agrupadores
          </h1>
          <p className="text-surface-400 mt-1">
            📁 Gestiona los agrupadores de aplicaciones
          </p>
        </div>
        {isAdmin && (
          <Button
            onClick={() => setIsModalOpen(true)}
            leftIcon={<PlusIcon className="w-5 h-5" />}
          >
            Nuevo Agrupador
          </Button>
        )}
      </div>

      {/* Search */}
      <div className="max-w-md">
        <Input
          placeholder="Buscar agrupadores..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          leftIcon={<MagnifyingGlassIcon className="w-5 h-5" />}
        />
      </div>

      {/* Groups Grid */}
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
      ) : groups.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-4xl mb-3">📁</div>
          <h3 className="text-lg font-medium text-surface-300 mb-2">
            No hay agrupadores
          </h3>
          <p className="text-surface-500">
            {search ? 'No se encontraron resultados' : 'Crea el primer agrupador'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {groups.map((group: Group) => (
            <motion.div
              key={group.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card-hover relative group"
            >
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center flex-shrink-0">
                  <FolderIcon className="w-6 h-6 text-primary-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold text-surface-100 truncate">
                    {group.name}
                  </h3>
                  <p className="text-sm text-surface-400 line-clamp-2 mt-1">
                    {group.description || 'Sin descripción'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-4 mt-4 text-sm text-surface-500">
                <div className="flex items-center gap-1">
                  <CubeIcon className="w-4 h-4" />
                  <span>{group._count?.applications || 0} apps</span>
                </div>
                <div className="flex items-center gap-1">
                  <UserGroupIcon className="w-4 h-4" />
                  <span>{group._count?.subscriptions || 0} suscriptores</span>
                </div>
              </div>

              <div className="flex items-center gap-2 mt-4">
                {subscribedGroupIds.has(group.id) ? (
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => unsubscribeMutation.mutate(group.id)}
                    loading={unsubscribeMutation.isPending}
                  >
                    Cancelar suscripción
                  </Button>
                ) : (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => subscribeMutation.mutate(group.id)}
                    loading={subscribeMutation.isPending}
                  >
                    Suscribirse
                  </Button>
                )}
              </div>

              {isAdmin && (
                <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                  <button
                    onClick={() => handleEdit(group)}
                    className="p-1.5 rounded-lg text-surface-400 hover:text-surface-100 hover:bg-surface-700"
                  >
                    <PencilIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(group)}
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
        title={editingGroup ? 'Editar Agrupador' : 'Nuevo Agrupador'}
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Nombre"
            placeholder="Nombre del agrupador"
            error={errors.name?.message}
            {...register('name', { required: 'El nombre es requerido' })}
          />
          <div>
            <label className="label">Descripción</label>
            <textarea
              className="input min-h-[100px] resize-none"
              placeholder="Descripción del agrupador"
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
              {editingGroup ? 'Guardar cambios' : 'Crear agrupador'}
            </Button>
          </div>
        </form>
      </Modal>
    </motion.div>
  );
}

