def generate_explanation(accuracy, coefficients):
    sorted_coefs = sorted(coefficients.items(), key=lambda x: abs(x[1]), reverse=True)
    top_positive = [f for f, c in sorted_coefs if c > 0][:3]
    top_negative = [f for f, c in sorted_coefs if c < 0][:3]
    explanation = f"El modelo alcanzo una precision del {round(accuracy*100,1)}%. "
    if top_positive:
        explanation += f"Variables que mas aumentan la probabilidad de la clase positiva: {', '.join(top_positive)}. "
    if top_negative:
        explanation += f"Variables que la reducen: {', '.join(top_negative)}. "
    if not top_positive and not top_negative:
        explanation += "No hay coeficientes determinantes claros."
    if accuracy > 0.99:
        explanation += " Advertencia: Posible sobreajuste o fuga de datos."
    elif accuracy < 0.6:
        explanation += " El rendimiento es bajo, se recomienda revisar caracteristicas."
    else:
        explanation += " Rendimiento aceptable."
    return explanation
