import clsx from 'clsx';

interface BadgeProps {
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'accent' | 'default';
  size?: 'sm' | 'md';
  children: React.ReactNode;
  className?: string;
}

const variantClasses = {
  primary: 'badge-primary',
  success: 'badge-success',
  warning: 'badge-warning',
  danger: 'badge-danger',
  info: 'badge-info',
  accent: 'badge-accent',
  default: 'bg-surface-700 text-surface-300 border border-surface-600',
};

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
};

export default function Badge({
  variant = 'default',
  size = 'sm',
  children,
  className,
}: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium rounded-full',
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
    >
      {children}
    </span>
  );
}

// Status badge helpers
export function StatusBadge({ status }: { status: string }) {
  const statusConfig: Record<string, { variant: BadgeProps['variant']; label: string }> = {
    // Feature / Test Case status
    PLANNED: { variant: 'info', label: 'Planificado' },
    IN_DEVELOPMENT: { variant: 'warning', label: 'En Desarrollo' },
    PRODUCTIVE: { variant: 'success', label: 'Productivo' },
    OBSOLETE: { variant: 'danger', label: 'Obsoleto' },
    // Request status
    NEW: { variant: 'primary', label: 'Nueva' },
    IN_ANALYSIS: { variant: 'warning', label: 'En Análisis' },
    APPROVED: { variant: 'success', label: 'Aprobada' },
    REJECTED: { variant: 'danger', label: 'Rechazada' },
    IMPLEMENTED: { variant: 'accent', label: 'Implementada' },
    // Pipeline status
    PENDING: { variant: 'info', label: 'Pendiente' },
    RUNNING: { variant: 'warning', label: 'Ejecutando' },
    PASSED: { variant: 'success', label: 'Exitoso' },
    FAILED: { variant: 'danger', label: 'Fallido' },
    CANCELED: { variant: 'default', label: 'Cancelado' },
    SKIPPED: { variant: 'default', label: 'Omitido' },
    // Test result status
    NOT_EXECUTED: { variant: 'default', label: 'No Ejecutado' },
    // Application status
    ACTIVE: { variant: 'success', label: 'Activa' },
    DISCONTINUED: { variant: 'danger', label: 'Descontinuada' },
    // User status
    INACTIVE: { variant: 'danger', label: 'Inactivo' },
  };

  const config = statusConfig[status] || { variant: 'default', label: status };

  return <Badge variant={config.variant}>{config.label}</Badge>;
}

export function PriorityBadge({ priority }: { priority: string }) {
  const priorityConfig: Record<string, { variant: BadgeProps['variant']; label: string }> = {
    HIGH: { variant: 'danger', label: 'Alta' },
    MEDIUM: { variant: 'warning', label: 'Media' },
    LOW: { variant: 'info', label: 'Baja' },
  };

  const config = priorityConfig[priority] || { variant: 'default', label: priority };

  return <Badge variant={config.variant}>{config.label}</Badge>;
}

export function TypeBadge({ type }: { type: string }) {
  const typeConfig: Record<string, { variant: BadgeProps['variant']; label: string }> = {
    AUTOMATED: { variant: 'accent', label: 'Automatizado' },
    MANUAL: { variant: 'info', label: 'Manual' },
  };

  const config = typeConfig[type] || { variant: 'default', label: type };

  return <Badge variant={config.variant}>{config.label}</Badge>;
}

export function RoleBadge({ role }: { role: string }) {
  const roleConfig: Record<string, { variant: BadgeProps['variant']; label: string }> = {
    ADMIN: { variant: 'accent', label: 'Administrador' },
    USER: { variant: 'primary', label: 'Usuario' },
  };

  const config = roleConfig[role] || { variant: 'default', label: role };

  return <Badge variant={config.variant}>{config.label}</Badge>;
}

