import { useEffect, useState } from 'react';
import axios from 'axios';
import { API } from '../App';
import { BarChart3, FileCheck, AlertTriangle, Copy, TrendingUp } from 'lucide-react';
import KPICard from '../components/KPICard';
import StatusBadge from '../components/StatusBadge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Link } from 'react-router-dom';

const DashboardPage = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await axios.get(`${API}/dashboard/stats`);
      setStats(res.data);
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-lg text-muted-foreground">Carregando...</p>
      </div>
    );
  }

  const chartData = stats?.recent_conferences?.map(conf => ({
    name: conf.name.substring(0, 15),
    Matches: conf.matches,
    Divergências: conf.divergences,
    Duplicatas: conf.duplicates,
  })) || [];

  return (
    <div className="p-6 lg:p-8 space-y-8" data-testid="dashboard-page">
      <div>
        <h1 className="text-3xl lg:text-4xl font-heading font-bold text-foreground mb-2">
          Dashboard
        </h1>
        <p className="text-muted-foreground">
          Visão geral das conferências realizadas
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          icon={FileCheck}
          title="Conferências"
          value={stats?.total_conferences || 0}
          subtitle="Total realizadas"
        />
        <KPICard
          icon={BarChart3}
          title="Registros"
          value={(stats?.total_records_processed || 0).toLocaleString()}
          subtitle="Total processados"
        />
        <KPICard
          icon={AlertTriangle}
          title="Divergências"
          value={stats?.total_divergences || 0}
          subtitle={`${stats?.divergence_rate || 0}% do total`}
        />
        <KPICard
          icon={Copy}
          title="Duplicatas"
          value={stats?.total_duplicates || 0}
          subtitle={`${stats?.duplicate_rate || 0}% do total`}
        />
      </div>

      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center gap-2 mb-6">
          <TrendingUp className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-heading font-semibold">Conferências Recentes</h2>
        </div>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #E2E8F0',
                  borderRadius: '0.5rem',
                }}
              />
              <Legend />
              <Bar dataKey="Matches" fill="#10B981" />
              <Bar dataKey="Divergências" fill="#F97316" />
              <Bar dataKey="Duplicatas" fill="#EF4444" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-center text-muted-foreground py-12">
            Nenhuma conferência realizada ainda
          </p>
        )}
      </div>

      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-xl font-heading font-semibold mb-4">Últimas Conferências</h2>
        {stats?.recent_conferences?.length > 0 ? (
          <div className="space-y-3">
            {stats.recent_conferences.map((conf) => (
              <Link
                key={conf.id}
                to={`/conferences/${conf.id}`}
                data-testid={`conference-link-${conf.id}`}
                className="flex items-center justify-between p-4 rounded-lg border border-border hover:border-primary transition bg-white"
              >
                <div className="flex-1">
                  <p className="font-medium text-foreground">{conf.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {new Date(conf.created_at).toLocaleDateString('pt-BR', {
                      day: '2-digit',
                      month: 'short',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right hidden sm:block">
                    <p className="text-sm text-muted-foreground">Registros</p>
                    <p className="font-mono font-medium">{conf.total_records}</p>
                  </div>
                  <StatusBadge status={conf.status} />
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <p className="text-center text-muted-foreground py-8">
            Nenhuma conferência realizada ainda
          </p>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;