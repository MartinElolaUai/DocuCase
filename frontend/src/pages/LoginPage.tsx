"use client"

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { BeakerIcon, EnvelopeIcon, LockClosedIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import { authApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

interface LoginForm {
  email: string;
  password: string;
}

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>();

  const onSubmit = async (data: LoginForm) => {
    try {
      setLoading(true);
      const response = await authApi.login(data.email, data.password);
      const { token, user } = response.data.data;
      setAuth(token, user);
      toast.success(`¡Bienvenido, ${user.firstName}!`);
      navigate('/');
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      {/* Background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-500/20 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-accent-500/20 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-r from-primary-500/5 to-accent-500/5 rounded-full blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative w-full max-w-md"
      >
        <div className="glass rounded-2xl p-8 shadow-2xl">
          {/* Logo */}
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
              className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 shadow-glow mb-4"
            >
              <BeakerIcon className="w-8 h-8 text-white" />
            </motion.div>
            <h1 className="text-3xl font-display font-bold text-gradient mb-2">
              DashCase
            </h1>
            <p className="text-surface-400">
              Sistema de Gestión de Casos de Prueba
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <Input
              label="Email"
              type="email"
              placeholder="tu@email.com"
              leftIcon={<EnvelopeIcon className="w-5 h-5" />}
              error={errors.email?.message}
              {...register('email', {
                required: 'El email es requerido',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Email inválido',
                },
              })}
            />

            <div className="relative">
              <Input
                label="Contraseña"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                leftIcon={<LockClosedIcon className="w-5 h-5" />}
                error={errors.password?.message}
                {...register('password', {
                  required: 'La contraseña es requerida',
                  minLength: {
                    value: 6,
                    message: 'Mínimo 6 caracteres',
                  },
                })}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-9 text-surface-400 hover:text-surface-300 transition-colors"
              >
                {showPassword ? (
                  <EyeSlashIcon className="w-5 h-5" />
                ) : (
                  <EyeIcon className="w-5 h-5" />
                )}
              </button>
            </div>

            <Button
              type="submit"
              loading={loading}
              className="w-full"
            >
              Iniciar Sesión
            </Button>
          </form>

          {/* Demo credentials */}
          <div className="mt-8 p-4 rounded-lg bg-surface-800/50 border border-surface-700/50">
            <p className="text-xs text-surface-400 text-center mb-3">
              Credenciales de prueba:
            </p>
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="text-center">
                <p className="text-surface-300 font-medium">Admin</p>
                <p className="text-surface-500">admin@docudash.com</p>
                <p className="text-surface-500">admin123</p>
              </div>
              <div className="text-center">
                <p className="text-surface-300 font-medium">Usuario</p>
                <p className="text-surface-500">usuario@docudash.com</p>
                <p className="text-surface-500">user123</p>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

