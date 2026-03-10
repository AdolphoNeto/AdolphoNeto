import pandas as pd
from typing import Dict, List, Any, Tuple
from datetime import datetime
import re

class ValidationEngine:
    def __init__(self):
        self.log2_df = None
        self.log3_df = None
        self.cubo_df = None
    
    def load_log2(self, file_path: str):
        df = pd.read_excel(file_path, header=1)
        df.columns = df.columns.str.strip()
        self.log2_df = df
        return len(df)
    
    def load_log3(self, file_path: str):
        df = pd.read_excel(file_path, header=1)
        df.columns = df.columns.str.strip()
        self.log3_df = df
        return len(df)
    
    def load_cubo160(self, file_path: str):
        df = pd.read_excel(file_path, header=1)
        df.columns = df.columns.str.strip()
        self.cubo_df = df
        return len(df)
    
    def normalize_id(self, value: Any) -> str:
        if pd.isna(value):
            return ""
        return str(value).strip().replace("-", "").replace(" ", "")
    
    def normalize_volume(self, value: Any) -> float:
        if pd.isna(value):
            return 0.0
        if isinstance(value, str):
            value = value.replace(",", ".").strip()
        try:
            return float(value)
        except:
            return 0.0
    
    def parse_date(self, value: Any) -> str:
        if pd.isna(value):
            return ""
        try:
            if isinstance(value, datetime):
                return value.strftime("%d/%m/%Y")
            return str(value).strip()
        except:
            return str(value)
    
    def validate_all(self) -> Tuple[List[Dict], Dict]:
        results = []
        stats = {
            "matches": 0,
            "divergences": 0,
            "duplicates": 0,
            "total_records": 0
        }
        
        if self.cubo_df is None or self.log2_df is None or self.log3_df is None:
            return results, stats
        
        log2_ids = set()
        log3_ids = set()
        
        if 'Número de carga' in self.log2_df.columns:
            for idx, row in self.log2_df.iterrows():
                id_val = self.normalize_id(row.get('Número de carga'))
                if id_val:
                    if id_val in log2_ids:
                        stats['duplicates'] += 1
                    log2_ids.add(id_val)
        
        if 'ID Cliente' in self.log3_df.columns:
            for idx, row in self.log3_df.iterrows():
                id_val = self.normalize_id(row.get('ID Cliente'))
                if id_val:
                    if id_val in log3_ids:
                        stats['duplicates'] += 1
                    log3_ids.add(id_val)
        
        for idx, cubo_row in self.cubo_df.iterrows():
            stats['total_records'] += 1
            
            serie = str(cubo_row.get('Serie', '')).strip()
            guia = str(cubo_row.get('Guia CEM', '')).strip()
            cubo_id = f"{serie}-{guia}"
            
            issues = []
            matched = []
            status = "match"
            
            peso_liquido = cubo_row.get('Peso Liquido', 0)
            if pd.notna(peso_liquido) and peso_liquido > 0:
                peso_liquido = float(peso_liquido)
            else:
                peso_liquido = 0
            
            log2_match = None
            log3_match = None
            
            if 'Número de carga' in self.log2_df.columns:
                for _, log2_row in self.log2_df.iterrows():
                    log2_id = self.normalize_id(log2_row.get('Número de carga'))
                    if log2_id and log2_id in cubo_id:
                        log2_match = log2_row.to_dict()
                        break
            
            if 'ID Cliente' in self.log3_df.columns:
                for _, log3_row in self.log3_df.iterrows():
                    log3_id = self.normalize_id(log3_row.get('ID Cliente'))
                    if log3_id and log3_id in cubo_id:
                        log3_match = log3_row.to_dict()
                        break
            
            if log2_match is None and log3_match is None:
                issues.append("Registro não encontrado nos logs")
                status = "divergence"
                stats['divergences'] += 1
            else:
                if log2_match:
                    matched.append({"source": "Log 2", "data": str(log2_match)})
                if log3_match:
                    matched.append({"source": "Log 3", "data": str(log3_match)})
                
                if log2_match and 'Volume Sólido' in log2_match:
                    log2_volume = self.normalize_volume(log2_match.get('Volume Sólido'))
                    tolerance = 5.0
                    if abs(log2_volume - peso_liquido) > tolerance:
                        issues.append(f"Divergência de volume: Cubo={peso_liquido:.2f} vs Log2={log2_volume:.2f}")
                        status = "divergence"
                        stats['divergences'] += 1
                
                if len(matched) > 0 and len(issues) == 0:
                    stats['matches'] += 1
            
            result = {
                "record_id": cubo_id,
                "source_type": "Cubo 160",
                "status": status,
                "data": cubo_row.to_dict(),
                "issues": issues,
                "matched_records": matched
            }
            results.append(result)
        
        return results, stats