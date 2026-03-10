import { useEffect, useState } from 'react';
import axios from 'axios';
import { API } from '../App';
import { Link } from 'react-router-dom';
import { Search, Calendar } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { Input } from '@/components/ui/input';

const ConferencesPage = () => {
  const [conferences, setConferences] = useState([]);
  const [filteredConferences, setFilteredConferences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchConferences();
  }, []);

  useEffect(() => {
    if (searchTerm) {
      const filtered = conferences.filter(conf =>
        conf.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        conf.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredConferences(filtered);
    } else {
      setFilteredConferences(conferences);
    }
  }, [searchTerm, conferences]);

  const fetchConferences = async () => {
    try {
      const res = await axios.get(`${API}/conferences`);
      setConferences(res.data);
      setFilteredConferences(res.data);
    } catch (error) {
      console.error('Erro ao carregar conferências:', error);
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

  return (
    <div className="p-6 lg:p-8 space-y-6" data-testid="conferences-page">
      <div>
        <h1 className="text-3xl lg:text-4xl font-heading font-bold text-foreground mb-2">
          Conferências
        </h1>
        <p className="text-muted-foreground">
          Histórico de todas as conferências realizadas
        </p>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            data-testid="search-input"
            type="text"
            placeholder="Buscar conferências..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {filteredConferences.length > 0 ? (
        <div className="grid grid-cols-1 gap-4">
          {filteredConferences.map((conf) => (
            <Link
              key={conf.id}
              to={`/conferences/${conf.id}`}
              data-testid={`conference-card-${conf.id}`}
              className="bg-card border border-border rounded-lg p-6 hover:border-primary transition"
            >
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                <div className="flex-1 space-y-2">
                  <div className="flex items-start justify-between gap-4">
                    <h3 className="text-lg font-heading font-semibold text-foreground">
                      {conf.name}
                    </h3>
                    <StatusBadge status={conf.status} />
                  </div>
                  {conf.description && (
                    <p className="text-sm text-muted-foreground">{conf.description}</p>
                  )}
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Calendar className="w-4 h-4" />
                    {new Date(conf.created_at).toLocaleDateString('pt-BR', {
                      day: '2-digit',
                      month: 'long',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </div>
                </div>

                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground mb-1">Total</p>
                    <p className="text-lg font-mono font-semibold text-foreground">
                      {conf.total_records}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground mb-1">Matches</p>
                    <p className="text-lg font-mono font-semibold text-success">
                      {conf.matches}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground mb-1">Diverg.</p>
                    <p className="text-lg font-mono font-semibold text-secondary">
                      {conf.divergences}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground mb-1">Duplic.</p>
                    <p className="text-lg font-mono font-semibold text-destructive">
                      {conf.duplicates}
                    </p>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="bg-card border border-border rounded-lg p-12 text-center">
          <p className="text-muted-foreground mb-4">
            {searchTerm ? 'Nenhuma conferência encontrada' : 'Nenhuma conferência realizada ainda'}
          </p>
          {!searchTerm && (
            <Link
              to="/upload"
              className="inline-flex items-center justify-center px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition"
            >
              Criar Primeira Conferência
            </Link>
          )}
        </div>
      )}
    </div>
  );
};

export default ConferencesPage;