import { CheckCircle2, XCircle, AlertCircle, Copy } from 'lucide-react';

const StatusBadge = ({ status }) => {
  const configs = {
    match: {
      icon: CheckCircle2,
      label: 'Correto',
      className: 'status-badge match',
    },
    divergence: {
      icon: AlertCircle,
      label: 'Divergência',
      className: 'status-badge divergence',
    },
    not_found: {
      icon: XCircle,
      label: 'Não Encontrado',
      className: 'status-badge error',
    },
    found_both_match: {
      icon: CheckCircle2,
      label: 'Ambas Bases - OK',
      className: 'status-badge match',
    },
    found_both_divergence: {
      icon: AlertCircle,
      label: 'Ambas Bases - Divergência',
      className: 'status-badge divergence',
    },
    duplicate: {
      icon: Copy,
      label: 'ID Duplicado',
      className: 'status-badge',
      style: { backgroundColor: 'rgba(139, 92, 246, 0.1)', color: '#8B5CF6' },
    },
    duplicate_divergence: {
      icon: Copy,
      label: 'Duplicado c/ Divergência',
      className: 'status-badge error',
    },
    processing: {
      icon: AlertCircle,
      label: 'Processando',
      className: 'status-badge',
      style: { backgroundColor: 'rgba(59, 130, 246, 0.1)', color: '#3B82F6' },
    },
    completed: {
      icon: CheckCircle2,
      label: 'Concluído',
      className: 'status-badge match',
    },
    error: {
      icon: XCircle,
      label: 'Erro',
      className: 'status-badge error',
    },
  };

  const config = configs[status] || configs.error;
  const Icon = config.icon;

  return (
    <span className={config.className} style={config.style} data-testid={`status-badge-${status}`}>
      <Icon className="w-3 h-3" />
      {config.label}
    </span>
  );
};

export default StatusBadge;