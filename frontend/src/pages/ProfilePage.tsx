"use client"

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import {
  UserIcon,
  KeyIcon,
  BellIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';
import { authApi, usersApi, groupsApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { RoleBadge } from '@/components/ui/Badge';

interface PasswordForm {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState<'profile' | 'password' | 'subscriptions'>('profile');
  const { user, updateUser } = useAuthStore();
  const queryClient = useQueryClient();

  const { register, handleSubmit, reset, formState: { errors }, watch } = useForm<PasswordForm>();
  const newPassword = watch('newPassword');

  const { data: profileData } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const response = await authApi.me();
      return response.data.data;
    },
  });

  const { data: subscriptions } = useQuery({
    queryKey: ['user-subscriptions'],
    queryFn: async () => {
      const response = await usersApi.getSubscriptions();
      return response.data.data;
    },
  });

  const { data: groups } = useQuery({
    queryKey: ['groups-list'],
    queryFn: async () => {
      const response = await groupsApi.getAll({ limit: '100' });
      return response.data.data;
    },
  });

  const subscribedGroupIds = new Set(subscriptions?.map((s: any) => s.groupId) || []);

  const changePasswordMutation = useMutation({
    mutationFn: (data: PasswordForm) =>
      authApi.changePassword(data.currentPassword, data.newPassword),
    onSuccess: () => {
      toast.success('Contraseña actualizada exitosamente');
      reset();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al cambiar contraseña');
    },
  });

  const subscribeMutation = useMutation({
    mutationFn: (groupId: string) => usersApi.subscribe(groupId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-subscriptions'] });
      toast.success('Suscrito al agrupador');
    },
  });

  const unsubscribeMutation = useMutation({
    mutationFn: (groupId: string) => usersApi.unsubscribe(groupId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-subscriptions'] });
      toast.success('Suscripción cancelada');
    },
  });

  const onPasswordSubmit = (data: PasswordForm) => {
    changePasswordMutation.mutate(data);
  };

  const tabs = [
    { id: 'profile', label: 'Perfil', icon: UserIcon },
    { id: 'password', label: 'Contraseña', icon: KeyIcon },
    { id: 'subscriptions', label: 'Suscripciones', icon: BellIcon },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto space-y-6"
    >
      {/* Header */}
      <div className="card">
        <div className="flex items-center gap-4">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-2xl font-bold">
            {user?.firstName?.[0]}{user?.lastName?.[0]}
          </div>
          <div>
            <h1 className="text-2xl font-display font-bold text-surface-100">
              {user?.firstName} {user?.lastName}
            </h1>
            <p className="text-surface-400">{user?.email}</p>
            <RoleBadge role={user?.role || 'USER'} />
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-surface-700/50">
        <nav className="flex gap-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-400'
                  : 'border-transparent text-surface-400 hover:text-surface-200'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'profile' && (
        <div className="card">
          <h2 className="text-lg font-display font-semibold text-surface-100 mb-6">
            Información del Perfil
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="label">Nombre</p>
              <p className="text-surface-100">{profileData?.firstName}</p>
            </div>
            <div>
              <p className="label">Apellido</p>
              <p className="text-surface-100">{profileData?.lastName}</p>
            </div>
            <div>
              <p className="label">Email</p>
              <p className="text-surface-100">{profileData?.email}</p>
            </div>
            <div>
              <p className="label">Rol</p>
              <RoleBadge role={profileData?.role || 'USER'} />
            </div>
          </div>
        </div>
      )}

      {activeTab === 'password' && (
        <div className="card">
          <h2 className="text-lg font-display font-semibold text-surface-100 mb-6">
            Cambiar Contraseña
          </h2>
          <form onSubmit={handleSubmit(onPasswordSubmit)} className="space-y-4 max-w-md">
            <Input
              label="Contraseña actual"
              type="password"
              placeholder="••••••••"
              error={errors.currentPassword?.message}
              {...register('currentPassword', { required: 'La contraseña actual es requerida' })}
            />
            <Input
              label="Nueva contraseña"
              type="password"
              placeholder="••••••••"
              error={errors.newPassword?.message}
              {...register('newPassword', {
                required: 'La nueva contraseña es requerida',
                minLength: { value: 6, message: 'Mínimo 6 caracteres' },
              })}
            />
            <Input
              label="Confirmar nueva contraseña"
              type="password"
              placeholder="••••••••"
              error={errors.confirmPassword?.message}
              {...register('confirmPassword', {
                required: 'Confirma la nueva contraseña',
                validate: (value) =>
                  value === newPassword || 'Las contraseñas no coinciden',
              })}
            />
            <Button type="submit" loading={changePasswordMutation.isPending}>
              Cambiar contraseña
            </Button>
          </form>
        </div>
      )}

      {activeTab === 'subscriptions' && (
        <div className="card">
          <h2 className="text-lg font-display font-semibold text-surface-100 mb-6">
            Suscripciones a Agrupadores
          </h2>
          <p className="text-surface-400 mb-6">
            Recibe notificaciones por email sobre novedades en los agrupadores a los que te suscribas.
          </p>
          <div className="space-y-3">
            {groups?.map((group: any) => (
              <div
                key={group.id}
                className="flex items-center justify-between p-4 rounded-lg bg-surface-800/50 border border-surface-700/50"
              >
                <div>
                  <p className="font-medium text-surface-100">{group.name}</p>
                  <p className="text-sm text-surface-500">{group.description}</p>
                </div>
                {subscribedGroupIds.has(group.id) ? (
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => unsubscribeMutation.mutate(group.id)}
                    loading={unsubscribeMutation.isPending}
                    leftIcon={<CheckCircleIcon className="w-4 h-4" />}
                  >
                    Suscrito
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
            ))}
            {(!groups || groups.length === 0) && (
              <p className="text-center text-surface-500 py-8">
                No hay agrupadores disponibles
              </p>
            )}
          </div>
        </div>
      )}
    </motion.div>
  );
}

