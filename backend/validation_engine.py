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
        
        seen_cubo_ids = {}
        
        log2_id_counts = {}
        if 'Número de carga' in self.log2_df.columns:
            for _, row in self.log2_df.iterrows():
                log2_id = str(row.get('Número de carga', '')).strip()
                if log2_id:
                    log2_id_counts[log2_id] = log2_id_counts.get(log2_id, 0) + 1
        
        log3_id_counts = {}
        if 'ID Cliente' in self.log3_df.columns:
            for _, row in self.log3_df.iterrows():
                log3_id = str(row.get('ID Cliente', '')).strip()
                if log3_id:
                    log3_id_counts[log3_id] = log3_id_counts.get(log3_id, 0) + 1
        
        for idx, cubo_row in self.cubo_df.iterrows():
            stats['total_records'] += 1
            
            serie = str(cubo_row.get('Serie', '')).strip()
            guia = str(cubo_row.get('Guia CEM', '')).strip()
            cubo_id = f"{serie}-{guia}"
            
            if cubo_id in seen_cubo_ids:
                stats['duplicates'] += 1
            seen_cubo_ids[cubo_id] = True
            
            issues = []
            matched = []
            status = "not_found"
            found_in = []
            has_duplicate = False
            
            cubo_volume = cubo_row.get('Peso Liquido', 0)
            if pd.notna(cubo_volume):
                cubo_volume = float(cubo_volume)
            else:
                cubo_volume = 0
            
            log2_matches = []
            log3_matches = []
            
            if 'Número de carga' in self.log2_df.columns:
                for _, log2_row in self.log2_df.iterrows():
                    log2_id = str(log2_row.get('Número de carga', '')).strip()
                    if log2_id and log2_id == cubo_id:
                        log2_matches.append(log2_row)
                
                if len(log2_matches) > 0:
                    found_in.append("Log 2")
                    if len(log2_matches) > 1:
                        has_duplicate = True
                        issues.append(f"ID Viagem duplicado em Log 2 ({len(log2_matches)} ocorrências)")
                        stats['duplicates'] += 1
            
            if 'ID Cliente' in self.log3_df.columns:
                for _, log3_row in self.log3_df.iterrows():
                    log3_id = str(log3_row.get('ID Cliente', '')).strip()
                    if log3_id and log3_id == cubo_id:
                        log3_matches.append(log3_row)
                
                if len(log3_matches) > 0:
                    found_in.append("Log 3")
                    if len(log3_matches) > 1:
                        has_duplicate = True
                        issues.append(f"ID Viagem duplicado em Log 3 ({len(log3_matches)} ocorrências)")
                        stats['duplicates'] += 1
            
            if len(log2_matches) == 0 and len(log3_matches) == 0:
                status = "not_found"
                issues.append("Valor não encontrado em nenhuma das bases")
                stats['divergences'] += 1
            else:
                has_divergence = False
                
                if len(log2_matches) > 0:
                    for log2_match in log2_matches:
                        log2_volume = self.normalize_volume(log2_match.get('Volume Sólido'))
                        volume_diff = abs(log2_volume - cubo_volume)
                        
                        matched.append({
                            "source": "Log 2",
                            "id": str(log2_match.get('Número de carga', '')),
                            "volume": log2_volume
                        })
                        
                        if volume_diff > 0.01:
                            has_divergence = True
                            issues.append(f"Divergência Log 2: Volume Cubo={cubo_volume:.2f} vs Log2={log2_volume:.2f} (diff={volume_diff:.2f})")
                
                if len(log3_matches) > 0:
                    for log3_match in log3_matches:
                        log3_volume = self.normalize_volume(log3_match.get('Volume Sólido'))
                        volume_diff = abs(log3_volume - cubo_volume)
                        
                        matched.append({
                            "source": "Log 3",
                            "id": str(log3_match.get('ID Cliente', '')),
                            "volume": log3_volume
                        })
                        
                        if volume_diff > 0.01:
                            has_divergence = True
                            issues.append(f"Divergência Log 3: Volume Cubo={cubo_volume:.2f} vs Log3={log3_volume:.2f} (diff={volume_diff:.2f})")
                
                if has_duplicate:
                    if has_divergence:
                        status = "duplicate_divergence"
                    else:
                        status = "duplicate"
                elif len(found_in) == 2:
                    if has_divergence:
                        status = "found_both_divergence"
                        issues.append("Encontrado em ambas as bases com divergência de volume")
                        stats['divergences'] += 1
                    else:
                        status = "found_both_match"
                        issues.append("Encontrado em ambas as bases com volumes corretos")
                        stats['matches'] += 1
                elif has_divergence:
                    status = "divergence"
                    stats['divergences'] += 1
                else:
                    status = "match"
                    stats['matches'] += 1
            
            result = {
                "record_id": cubo_id,
                "source_type": "Cubo 160",
                "status": status,
                "data": {
                    "serie": serie,
                    "guia_cem": guia,
                    "volume": cubo_volume,
                    "found_in": ", ".join(found_in) if found_in else "Nenhuma"
                },
                "issues": issues,
                "matched_records": matched
            }
            results.append(result)
        
        return results, stats