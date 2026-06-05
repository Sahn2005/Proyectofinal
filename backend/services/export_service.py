from fpdf import FPDF
import pandas as pd

def export_metrics_pdf(training_id, metrics):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt=f"Metricas del Entrenamiento #{training_id}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for k, v in metrics.items():
        pdf.cell(200, 10, txt=f"{k.capitalize()}: {round(v*100,2)}%", ln=True)
    path = f"static/plots/metrics_{training_id}.pdf"
    pdf.output(path)
    return path

def export_results_excel(training_id, training_row):
    data = {'Métrica': ['Accuracy','Precision','Recall','F1','AUC'],
            'Valor': [training_row['accuracy'], training_row['precision'], training_row['recall'],
                      training_row['f1_score'], training_row['auc']]}
    df = pd.DataFrame(data)
    path = f"static/plots/results_{training_id}.xlsx"
    df.to_excel(path, index=False)
    return path
