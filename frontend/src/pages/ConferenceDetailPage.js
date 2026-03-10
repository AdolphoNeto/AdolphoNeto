import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { API } from '../App';
import StatusBadge from '../components/StatusBadge';
import KPICard from '../components/KPICard';
import { ArrowLeft, FileCheck, AlertTriangle, Copy, Download, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const ConferenceDetailPage = () => {
  const { id } = useParams();
  const [conference, setConference] = useState(null);
  const [results, setResults] = useState([]);
  const [filteredResults, setFilteredResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    fetchConference();
    fetchResults();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  useEffect(() => {
    if (statusFilter === 'all') {
      setFilteredResults(results);
    } else {
      setFilteredResults(results.filter(r => r.status === statusFilter));
    }
  }, [statusFilter, results]);

  const fetchConference = async () => {
    try {
      const res = await axios.get(`${API}/conferences/${id}`);
      setConference(res.data);
    } catch (error) {
      console.error('Erro ao carregar conferência:', error);
    }
  };

  const fetchResults = async () => {
    try {
      const res = await axios.get(`${API}/conferences/${id}/results`);
      setResults(res.data);
      setFilteredResults(res.data);
    } catch (error) {
      console.error('Erro ao carregar resultados:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !conference) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-lg text-muted-foreground">Carregando...</p>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 space-y-6" data-testid="conference-detail-page">
      <div className="flex items-center gap-4">
        <Link to="/conferences">
          <Button variant="outline" size="icon" data-testid="back-button">
            <ArrowLeft className="w-4 h-4" />
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl lg:text-3xl font-heading font-bold text-foreground">
            {conference.name}
          </h1>
          <p className="text-muted-foreground">
            {new Date(conference.created_at).toLocaleDateString('pt-BR', {
              day: '2-digit',
              month: 'long',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </p>
        </div>
        <StatusBadge status={conference.status} />
      </div>

      {conference.description && (
        <div className="bg-card border border-border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">{conference.description}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          icon={FileCheck}
          title="Total de Registros"
          value={conference.total_records}
        />
        <KPICard
          icon={FileCheck}
          title="Matches"
          value={conference.matches}
          subtitle="Registros conferidos"
        />
        <KPICard
          icon={AlertTriangle}
          title="Divergências"
          value={conference.divergences}
          subtitle={`${((conference.divergences / conference.total_records) * 100 || 0).toFixed(1)}% do total`}
        />
        <KPICard
          icon={Copy}
          title="Duplicatas"
          value={conference.duplicates}
          subtitle={`${((conference.duplicates / conference.total_records) * 100 || 0).toFixed(1)}% do total`}
        />
      </div>

      <div className="bg-card border border-border rounded-lg p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-heading font-semibold">Resultados</h2>
            <span className="text-sm text-muted-foreground">({filteredResults.length})</span>
          </div>
          <div className="flex items-center gap-4">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]" data-testid="status-filter">
                <SelectValue placeholder="Filtrar por status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="match">Matches</SelectItem>
                <SelectItem value="divergence">Divergências</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="sm" data-testid="export-button">
              <Download className="w-4 h-4 mr-2" />
              Exportar
            </Button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full data-table">
            <thead className="bg-muted sticky top-0">
              <tr className="border-b border-border">
                <th className="text-left p-3 text-xs font-medium text-muted-foreground uppercase">ID</th>
                <th className="text-left p-3 text-xs font-medium text-muted-foreground uppercase">Fonte</th>
                <th className="text-left p-3 text-xs font-medium text-muted-foreground uppercase">Status</th>
                <th className="text-left p-3 text-xs font-medium text-muted-foreground uppercase">Issues</th>
                <th className="text-left p-3 text-xs font-medium text-muted-foreground uppercase">Matches</th>
              </tr>
            </thead>
            <tbody>
              {filteredResults.map((result, idx) => (
                <tr
                  key={result.id}
                  data-testid={`result-row-${idx}`}
                  className="border-b border-border hover:bg-muted/50 transition"
                >
                  <td className="p-3 text-sm">{result.record_id}</td>
                  <td className="p-3 text-sm">{result.source_type}</td>
                  <td className="p-3">
                    <StatusBadge status={result.status} />
                  </td>
                  <td className="p-3 text-sm">
                    {result.issues.length > 0 ? (
                      <ul className="list-disc list-inside text-secondary">
                        {result.issues.map((issue, i) => (
                          <li key={i} className="text-xs">{issue}</li>
                        ))}
                      </ul>
                    ) : (
                      <span className="text-muted-foreground text-xs">-</span>
                    )}
                  </td>
                  <td className="p-3 text-sm">
                    {result.matched_records.length > 0 ? (
                      <span className="text-success text-xs">
                        {result.matched_records.length} match(es)
                      </span>
                    ) : (
                      <span className="text-muted-foreground text-xs">-</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredResults.length === 0 && (
          <p className="text-center text-muted-foreground py-8">
            Nenhum resultado encontrado
          </p>
        )}
      </div>
    </div>
  );
};

export default ConferenceDetailPage;