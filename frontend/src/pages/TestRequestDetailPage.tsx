import { motion } from 'framer-motion';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { formatDistanceToNow, format } from 'date-fns';
import { es } from 'date-fns/locale';
import toast from 'react-hot-toast';
import {
  ArrowLeftIcon,
  ClipboardDocumentListIcon,
  LinkIcon,
  UserIcon,
  CalendarIcon,
} from '@heroicons/react/24/outline';
import { testRequestsApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import { StatusBadge } from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';

export default function TestRequestDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const isAdmin = user?.role === 'ADMIN';

  const { data: request, isLoading } = useQuery({
    queryKey: ['test-request', id],
    queryFn: async () => {
      const response = await testRequestsApi.getById(id!);
      return response.data.data;
    },
    enabled: !!id,
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ status, notes }: { status: string; notes?: string }) =>
      testRequestsApi.updateStatus(id!, { status, notes }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['test-request', id] });
      toast.success('Estado actualizado');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al actualizar');
    },
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

  if (!request) {
    return (
      <div className="card text-center py-12">
        <div className="text-4xl mb-3">📋</div>
        <p className="text-surface-400">Solicitud no encontrada</p>
        <Link to="/requests">
          <Button variant="secondary" className="mt-4">
            Volver a solicitudes
          </Button>
        </Link>
      </div>
    );
  }

  const handleStatusChange = (newStatus: string) => {
    updateStatusMutation.mutate({ status: newStatus });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Back button */}
      <Link to="/requests" className="inline-flex items-center gap-2 text-surface-400 hover:text-surface-100 transition-colors">
        <ArrowLeftIcon className="w-4 h-4" />
        Volver a solicitudes
      </Link>

      {/* Header */}
      <div className="card">
        <div className="flex items-start gap-4">
          <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-accent-500/20 to-pink-500/20 flex items-center justify-center">
            <ClipboardDocumentListIcon className="w-8 h-8 text-accent-400" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-2xl font-display font-bold text-surface-100">
                {request.title}
              </h1>
              <StatusBadge status={request.status} />
            </div>
            
            <div className="flex flex-wrap items-center gap-4 mt-4 text-sm text-surface-400">
              <Link to={`/applications/${request.applicationId}`}>
                <span className="px-3 py-1 bg-surface-800 rounded-lg hover:bg-surface-700 transition-colors">
                  {request.application?.name}
                </span>
              </Link>
              <div className="flex items-center gap-1">
                <UserIcon className="w-4 h-4" />
                {request.requester?.firstName} {request.requester?.lastName}
              </div>
              <div className="flex items-center gap-1">
                <CalendarIcon className="w-4 h-4" />
                {format(new Date(request.createdAt), "d 'de' MMMM, yyyy", { locale: es })}
              </div>
            </div>

            {request.azureWorkItemId && (
              <a
                href={request.azureWorkItemUrl || '#'}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 mt-4 text-sm text-primary-400 hover:text-primary-300"
              >
                <LinkIcon className="w-4 h-4" />
                Work Item: {request.azureWorkItemId}
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Admin Actions */}
      {isAdmin && (
        <div className="card">
          <h2 className="text-lg font-display font-semibold text-surface-100 mb-4">
            Gestión de la Solicitud
          </h2>
          <div className="flex flex-wrap gap-4">
            <div className="w-48">
              <Select
                label="Cambiar estado"
                value={request.status}
                onChange={(e) => handleStatusChange(e.target.value)}
                options={[
                  { value: 'NEW', label: 'Nueva' },
                  { value: 'IN_ANALYSIS', label: 'En Análisis' },
                  { value: 'APPROVED', label: 'Aprobada' },
                  { value: 'REJECTED', label: 'Rechazada' },
                  { value: 'IMPLEMENTED', label: 'Implementada' },
                ]}
              />
            </div>
            {request.assignee && (
              <div>
                <p className="label">Asignado a</p>
                <p className="text-surface-200">
                  {request.assignee.firstName} {request.assignee.lastName}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Description */}
      <div className="card">
        <h2 className="text-lg font-display font-semibold text-surface-100 mb-4">
          Descripción
        </h2>
        <div className="prose prose-invert max-w-none">
          <p className="text-surface-300 whitespace-pre-wrap">{request.description}</p>
        </div>
      </div>

      {/* Additional Notes */}
      {request.additionalNotes && (
        <div className="card">
          <h2 className="text-lg font-display font-semibold text-surface-100 mb-4">
            Notas y Comentarios
          </h2>
          <div className="prose prose-invert max-w-none">
            <pre className="text-surface-400 whitespace-pre-wrap text-sm bg-surface-800 p-4 rounded-lg">
              {request.additionalNotes}
            </pre>
          </div>
        </div>
      )}

      {/* Generated Test Case */}
      {request.generatedTestCase && (
        <div className="card">
          <h2 className="text-lg font-display font-semibold text-surface-100 mb-4">
            Caso de Prueba Generado
          </h2>
          <Link
            to={`/test-cases/${request.generatedTestCase.id}`}
            className="flex items-center gap-4 p-4 rounded-lg bg-surface-800/50 border border-surface-700/50 hover:border-primary-500/50 transition-colors"
          >
            <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center">
              <ClipboardDocumentListIcon className="w-5 h-5 text-orange-400" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-surface-100">{request.generatedTestCase.name}</p>
              <StatusBadge status={request.generatedTestCase.status} />
            </div>
          </Link>
        </div>
      )}
    </motion.div>
  );
}

