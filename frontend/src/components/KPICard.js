import { LucideIcon } from 'lucide-react';

const KPICard = ({ icon: Icon, title, value, subtitle, trend }) => {
  return (
    <div className="kpi-card" data-testid="kpi-card">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            {Icon && <Icon className="w-5 h-5 text-primary" />}
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
          </div>
          <p className="text-3xl font-heading font-bold text-foreground mb-1">{value}</p>
          {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
        </div>
        {trend && (
          <div className={`text-sm font-medium ${
            trend.direction === 'up' ? 'text-success' : 'text-error'
          }`}>
            {trend.value}
          </div>
        )}
      </div>
    </div>
  );
};

export default KPICard;