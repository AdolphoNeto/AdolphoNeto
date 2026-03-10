import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { API, setAuthToken } from '../App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { LogIn, UserPlus } from 'lucide-react';

const AuthPage = ({ setUser }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        const res = await axios.post(`${API}/auth/login`, {
          email: formData.email,
          password: formData.password,
        });
        setAuthToken(res.data.access_token);
        setUser(res.data.user);
        toast.success('Login realizado com sucesso!');
        navigate('/dashboard');
      } else {
        await axios.post(`${API}/auth/register`, {
          email: formData.email,
          password: formData.password,
          name: formData.name,
          role: 'user',
        });
        toast.success('Conta criada! Faça login para continuar.');
        setIsLogin(true);
        setFormData({ email: formData.email, password: '', name: '' });
      }
    } catch (error) {
      const message = error.response?.data?.detail || 'Erro ao processar solicitação';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      <div className="flex-1 flex items-center justify-center p-8 bg-background">
        <div className="w-full max-w-md space-y-8">
          <div className="text-center">
            <h1 className="text-4xl font-heading font-bold text-primary mb-2">
              WoodTech
            </h1>
            <p className="text-muted-foreground">
              Sistema de Validação de Logs
            </p>
          </div>

          <div className="bg-card p-8 rounded-lg border border-border">
            <div className="flex gap-2 mb-6">
              <button
                onClick={() => setIsLogin(true)}
                data-testid="tab-login"
                className={`flex-1 py-2 px-4 rounded-lg font-medium transition ${
                  isLogin
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'
                }`}
              >
                Login
              </button>
              <button
                onClick={() => setIsLogin(false)}
                data-testid="tab-register"
                className={`flex-1 py-2 px-4 rounded-lg font-medium transition ${
                  !isLogin
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'
                }`}
              >
                Registrar
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                <div className="space-y-2">
                  <Label htmlFor="name">Nome</Label>
                  <Input
                    id="name"
                    data-testid="input-name"
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required={!isLogin}
                    placeholder="Seu nome completo"
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  data-testid="input-email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  placeholder="seu@email.com"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Senha</Label>
                <Input
                  id="password"
                  data-testid="input-password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                  placeholder="••••••••"
                />
              </div>

              <Button
                type="submit"
                data-testid="submit-button"
                className="w-full bg-primary hover:bg-primary/90"
                disabled={loading}
              >
                {loading ? (
                  'Processando...'
                ) : isLogin ? (
                  <>
                    <LogIn className="w-4 h-4 mr-2" />
                    Entrar
                  </>
                ) : (
                  <>
                    <UserPlus className="w-4 h-4 mr-2" />
                    Criar Conta
                  </>
                )}
              </Button>
            </form>
          </div>
        </div>
      </div>

      <div
        className="hidden lg:block lg:w-1/2 relative"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1762857995681-39f4ddb00e9f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw0fHxmb3Jlc3RyeSUyMGxvZ2dpbmclMjBvcGVyYXRpb25zJTIwdGltYmVyJTIwdHJ1Y2t8ZW58MHx8fHwxNzczMTQ4ODkxfDA&ixlib=rb-4.1.0&q=85')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <div className="absolute inset-0 bg-primary/90" />
        <div className="relative h-full flex items-center justify-center p-12 text-white">
          <div className="max-w-lg space-y-6">
            <h2 className="text-4xl font-heading font-bold">
              Conferência SGF x WoodTech
            </h2>
            <p className="text-lg text-white/80">
              Sistema de validação automática de logs de carregamento de madeira.
              Compare dados entre múltiplas fontes e identifique divergências em segundos.
            </p>
            <div className="flex flex-col gap-4 pt-4">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-secondary mt-2" />
                <div>
                  <p className="font-medium">Upload Simples</p>
                  <p className="text-sm text-white/70">Arraste e solte seus arquivos Excel</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-secondary mt-2" />
                <div>
                  <p className="font-medium">Validação Automática</p>
                  <p className="text-sm text-white/70">Processamento inteligente e rápido</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-secondary mt-2" />
                <div>
                  <p className="font-medium">Relatórios Detalhados</p>
                  <p className="text-sm text-white/70">Exporte resultados em Excel ou PDF</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;