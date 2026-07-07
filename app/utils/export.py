import pandas as pd
from typing import List, Dict, Any
from io import BytesIO

class ExportService:
    @staticmethod
    def export_candidates_to_excel(candidates: List[Dict[str, Any]]) -> bytes:
        """
        Converts a list of candidate dictionaries into an Excel byte stream.
        """
        if not candidates:
            return b""

        # Flatten the data for tabular representation
        flat_data = []
        for cand in candidates:
            flat_data.append({
                "Candidate Name": cand.get("candidate_name", "N/A"),
                "Total Suitability Score (%)": cand.get("score", 0),
                "Skill Match (%)": cand.get("breakdown", {}).get("skill_match", 0),
                "Semantic Match (%)": cand.get("breakdown", {}).get("semantic_match", 0),
                "Experience Match (%)": cand.get("breakdown", {}).get("experience_match", 0),
                "Matched Skills": ", ".join(cand.get("matched_skills", [])),
                "Missing Skills": ", ".join(cand.get("missing_skills", [])),
                "Bonus Skills Found": ", ".join(cand.get("preferred_skills", []))
            })

        df = pd.DataFrame(flat_data)
        
        output = BytesIO()
        # Use openpyxl engine for modern .xlsx support
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='AI Shortlist')
            
            # Auto-adjust column widths for readability
            worksheet = writer.sheets['AI Shortlist']
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column].width = min(adjusted_width, 50) # Cap at 50

        return output.getvalue()