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
  UsersIcon,
} from '@heroicons/react/24/outline';
import { usersApi } from '@/services/api';
import { User } from '@/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Modal from '@/components/ui/Modal';
import { StatusBadge, RoleBadge } from '@/components/ui/Badge';

interface UserForm {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role: string;
  status: string;
}

export default function UsersPage() {
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const queryClient = useQueryClient();

  const { register, handleSubmit, reset, formState: { errors } } = useForm<UserForm>();

  const { data: usersData, isLoading } = useQuery({
    queryKey: ['users', search, roleFilter],
    queryFn: async () => {
      const params: Record<string, string> = { limit: '100' };
      if (search) params.search = search;
      if (roleFilter) params.role = roleFilter;
      const response = await usersApi.getAll(params);
      return response.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: UserForm) => usersApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('Usuario creado exitosamente');
      handleCloseModal();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al crear usuario');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<UserForm> }) =>
      usersApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('Usuario actualizado exitosamente');
      handleCloseModal();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al actualizar');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => usersApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('Usuario eliminado exitosamente');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al eliminar');
    },
  });

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingUser(null);
    reset();
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    reset({
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
      role: user.role,
      status: user.status,
      password: '',
    });
    setIsModalOpen(true);
  };

  const onSubmit = (data: UserForm) => {
    if (editingUser) {
      const updateData: Partial<UserForm> = { ...data };
      if (!updateData.password) delete updateData.password;
      updateMutation.mutate({ id: editingUser.id, data: updateData });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleDelete = (user: User) => {
    if (confirm(`¿Estás seguro de eliminar al usuario "${user.firstName} ${user.lastName}"?`)) {
      deleteMutation.mutate(user.id);
    }
  };

  const users = usersData?.data || [];

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
            Usuarios
          </h1>
          <p className="text-surface-400 mt-1">
            👥 Gestiona los usuarios del sistema
          </p>
        </div>
        <Button
          onClick={() => setIsModalOpen(true)}
          leftIcon={<PlusIcon className="w-5 h-5" />}
        >
          Nuevo Usuario
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div className="w-full sm:w-64">
          <Input
            placeholder="Buscar usuarios..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            leftIcon={<MagnifyingGlassIcon className="w-5 h-5" />}
          />
        </div>
        <div className="w-full sm:w-40">
          <Select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            options={[
              { value: '', label: 'Todos los roles' },
              { value: 'ADMIN', label: 'Administrador' },
              { value: 'USER', label: 'Usuario' },
            ]}
          />
        </div>
      </div>

      {/* Users Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="animate-pulse space-y-4 p-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-12 bg-surface-700 rounded" />
            ))}
          </div>
        ) : users.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-3">👥</div>
            <h3 className="text-lg font-medium text-surface-300 mb-2">
              No hay usuarios
            </h3>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Email</th>
                  <th>Rol</th>
                  <th>Estado</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {users.map((user: User) => (
                  <tr key={user.id}>
                    <td>
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white font-semibold">
                          {user.firstName?.[0]}{user.lastName?.[0]}
                        </div>
                        <div>
                          <p className="font-medium text-surface-100">
                            {user.firstName} {user.lastName}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="text-surface-400">{user.email}</td>
                    <td><RoleBadge role={user.role} /></td>
                    <td><StatusBadge status={user.status} /></td>
                    <td>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleEdit(user)}
                          className="p-1.5 rounded-lg text-surface-400 hover:text-surface-100 hover:bg-surface-700"
                        >
                          <PencilIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(user)}
                          className="p-1.5 rounded-lg text-surface-400 hover:text-red-400 hover:bg-surface-700"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingUser ? 'Editar Usuario' : 'Nuevo Usuario'}
        size="lg"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Nombre"
              placeholder="Nombre"
              error={errors.firstName?.message}
              {...register('firstName', { required: 'El nombre es requerido' })}
            />
            <Input
              label="Apellido"
              placeholder="Apellido"
              error={errors.lastName?.message}
              {...register('lastName', { required: 'El apellido es requerido' })}
            />
          </div>

          <Input
            label="Email"
            type="email"
            placeholder="email@ejemplo.com"
            error={errors.email?.message}
            {...register('email', { required: 'El email es requerido' })}
          />

          <Input
            label={editingUser ? 'Nueva Contraseña (dejar vacío para mantener)' : 'Contraseña'}
            type="password"
            placeholder="••••••••"
            error={errors.password?.message}
            {...register('password', {
              required: editingUser ? false : 'La contraseña es requerida',
              minLength: {
                value: 6,
                message: 'Mínimo 6 caracteres',
              },
            })}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Select
              label="Rol"
              options={[
                { value: 'USER', label: 'Usuario' },
                { value: 'ADMIN', label: 'Administrador' },
              ]}
              {...register('role')}
            />
            <Select
              label="Estado"
              options={[
                { value: 'ACTIVE', label: 'Activo' },
                { value: 'INACTIVE', label: 'Inactivo' },
              ]}
              {...register('status')}
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
              {editingUser ? 'Guardar cambios' : 'Crear usuario'}
            </Button>
          </div>
        </form>
      </Modal>
    </motion.div>
  );
}

