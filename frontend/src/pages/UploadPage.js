import { useState } from 'react';
import axios from 'axios';
import { API } from '../App';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import { Upload, FileUp, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

const UploadPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
  });
  const [files, setFiles] = useState({
    log2: null,
    log3: null,
    cubo: null,
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = (type, file) => {
    if (file && !file.name.match(/\.(xlsx|xls|xlsm)$/i)) {
      toast.error('Por favor, selecione um arquivo Excel válido');
      return;
    }
    setFiles({ ...files, [type]: file });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!files.log2 || !files.log3 || !files.cubo) {
      toast.error('Por favor, faça upload de todos os arquivos');
      return;
    }

    setLoading(true);

    const data = new FormData();
    data.append('name', formData.name);
    data.append('description', formData.description);
    data.append('log2_file', files.log2);
    data.append('log3_file', files.log3);
    data.append('cubo_file', files.cubo);

    try {
      const res = await axios.post(`${API}/conferences`, data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      toast.success('Conferência criada com sucesso!');
      navigate(`/conferences/${res.data.id}`);
    } catch (error) {
      const message = error.response?.data?.detail || 'Erro ao criar conferência';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const FileUploadBox = ({ label, type, file }) => (
    <div className="space-y-2">
      <Label htmlFor={type}>{label}</Label>
      <div
        className="relative border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary transition cursor-pointer"
        onClick={() => document.getElementById(type).click()}
      >
        <input
          id={type}
          data-testid={`input-${type}`}
          type="file"
          accept=".xlsx,.xls,.xlsm"
          onChange={(e) => handleFileChange(type, e.target.files[0])}
          className="hidden"
        />
        {file ? (
          <div className="flex items-center justify-center gap-2 text-success">
            <CheckCircle2 className="w-5 h-5" />
            <span className="font-medium">{file.name}</span>
          </div>
        ) : (
          <div className="space-y-2">
            <FileUp className="w-8 h-8 mx-auto text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              Clique ou arraste o arquivo aqui
            </p>
            <p className="text-xs text-muted-foreground">
              Formatos: .xlsx, .xls, .xlsm
            </p>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="p-6 lg:p-8" data-testid="upload-page">
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl lg:text-4xl font-heading font-bold text-foreground mb-2">
            Nova Conferência
          </h1>
          <p className="text-muted-foreground">
            Faça upload dos arquivos para iniciar a validação
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="bg-card border border-border rounded-lg p-6 space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Nome da Conferência *</Label>
              <Input
                id="name"
                data-testid="input-name"
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                placeholder="Ex: Conferência Fevereiro 2026"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Descrição</Label>
              <Textarea
                id="description"
                data-testid="input-description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Adicione uma descrição opcional..."
                rows={3}
              />
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-6 space-y-6">
            <div className="flex items-center gap-2">
              <Upload className="w-5 h-5 text-primary" />
              <h2 className="text-xl font-heading font-semibold">Arquivos</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <FileUploadBox label="Log 2 *" type="log2" file={files.log2} />
              <FileUploadBox label="Log 3 *" type="log3" file={files.log3} />
              <FileUploadBox label="Cubo 160 *" type="cubo" file={files.cubo} />
            </div>
          </div>

          <div className="flex gap-4">
            <Button
              type="submit"
              data-testid="submit-button"
              className="bg-primary hover:bg-primary/90"
              disabled={loading}
            >
              {loading ? 'Processando...' : 'Iniciar Conferência'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/conferences')}
            >
              Cancelar
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UploadPage;