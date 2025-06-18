import streamlit as st

bebidas = {
    "Cerveza (330 ml, 5%)": (330, 5),
    "Vino (150 ml, 12%)": (150, 12),
    "Cava (150 ml, 11.5%)": (150, 11.5),
    "Licor (50 ml, 30%)": (50, 30),
    "Combinado (250 ml, 20%)": (250, 20)
}

densidad_alcohol = 0.8
eliminacion_por_hora = 0.15

def calcular_alcohol_total(ingestas):
    total_alcohol = 0
    for bebida, cantidad in ingestas.items():
        volumen_unitario, graduacion = bebidas[bebida]
        volumen_total = cantidad * volumen_unitario
        alcohol = volumen_total * (graduacion / 100) * densidad_alcohol
        total_alcohol += alcohol
    return total_alcohol

def calcular_bac(alcohol_g, peso, r, horas):
    bac = alcohol_g / (peso * r) - eliminacion_por_hora * horas
    return max(bac, 0)

def tiempo_hasta_limite(bac, limite):
    if bac <= limite:
        return 0
    return (bac - limite) / eliminacion_por_hora

def evaluar_sancion(mg_l, tipo, reincidente=False):
    resultado = ""

    # Vía penal
    if mg_l >= 0.60:
        resultado += "🟥 **DELITO**: Conducción bajo influencia del alcohol (≥ 0,60 mg/L aire o ≥ 1,2 g/L sangre).\n"
        resultado += "- Pena: prisión de 3 a 6 meses, multa de 6 a 12 meses o trabajos comunitarios de 30 a 90 días.\n"
        resultado += "- Retirada de carnet: 1 a 4 años.\n"

    # Vía administrativa
    if tipo == "Menor":
        if mg_l > 0.5:
            resultado += "🟧 Menores: Tasa superior a 0,50 mg/L → 4 puntos + 1.000 € (salvo patinete/bici)."
        else:
            resultado += "🟨 Menores: Tasa hasta 0,50 mg/L → 4 puntos + 500 € (salvo patinete/bici)."
    elif tipo == "Novel/Profesional":
        if mg_l > 0.3:
            resultado += "🟥 Profesionales/Noveles: Tasa > 0,30 mg/L → 6 puntos + 1.000 €"
        elif mg_l >= 0.15:
            resultado += "🟨 Profesionales/Noveles: Tasa 0,15–0,30 mg/L → 4 puntos + 500 €"
    elif tipo == "General":
        if mg_l > 0.5:
            resultado += "🟥 General: Tasa > 0,50 mg/L → 6 puntos + 1.000 €"
        elif mg_l >= 0.25:
            resultado += "🟨 General: Tasa 0,25–0,50 mg/L → 4 puntos + 500 €"
        elif mg_l >= 0.1:
            resultado += "🟦 General: Tasa 0,10–0,25 mg/L → 2 puntos + 200 €"

    if reincidente:
        resultado += "\n⚠️ Reincidente: multa de 1.000 € + 4 a 6 puntos (según tasa)."

    return resultado

# Interfaz
st.title("Calculadora de Alcoholemia (España)")

st.header("Datos personales")
peso = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=70.0)
sexo = st.selectbox("Sexo", ["Hombre", "Mujer"])
r = 0.7 if sexo == "Hombre" else 0.6
horas = st.number_input("Horas desde la última bebida", min_value=0.0, max_value=24.0, value=1.0)

st.header("Tipo de conductor")
tipo_conductor = st.selectbox("Selecciona tu tipo de conductor", ["General", "Novel/Profesional", "Menor"])
limite_legal = 0.5 if tipo_conductor == "General" else 0.3

reincidente = st.checkbox("¿Eres reincidente en alcoholemia?")


st.header("Bebidas ingeridas")
ingestas = {}
for bebida in bebidas:
    cantidad = st.number_input(f"Nº de {bebida}", min_value=0, max_value=20, value=0)
    if cantidad > 0:
        ingestas[bebida] = cantidad

if st.button("Calcular"):
    if not ingestas:
        st.warning("Introduce al menos una bebida.")
    else:
        alcohol_total = calcular_alcohol_total(ingestas)
        bac = calcular_bac(alcohol_total, peso, r, horas)
        bac_mg_l_aire = bac * 0.5
        tiempo_extra = tiempo_hasta_limite(bac, limite_legal)
        sancion = evaluar_sancion(bac_mg_l_aire, tipo_conductor, reincidente=reincidente)

        st.subheader("Resultados")
        st.write(f"**BAC estimado (sangre):** {bac:.2f} g/L")
        st.write(f"**Equivalente en aire espirado:** {bac_mg_l_aire:.2f} mg/L")
        st.write(f"**Límite legal para tu caso:** {limite_legal:.2f} g/L sangre ({limite_legal*0.5:.2f} mg/L aire)")
        st.write(f"**Tiempo estimado hasta estar por debajo del límite legal:** {tiempo_extra:.1f} horas")
        st.warning(f"**Sanción estimada según normativa española:**\n{sancion}")

        if bac > 2:
            st.error("🚨 Nivel muy alto de alcoholemia. Riesgo severo para la salud.")
        elif bac > 1:
            st.warning("⚠️ Nivel elevado. Evita conducir y considera buscar ayuda médica si hay síntomas.")
        elif bac > 0.5:
            st.info("ℹ️ Podrías experimentar efectos moderados: euforia, menor coordinación.")
        elif bac > 0:
            st.info("ℹ️ Efectos leves posibles: relajación, reducción de reflejos.")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-size: 0.9em;'>"
    "Aplicación creada por <strong>Susana Simal</strong><br>"
    "© 2025 Todos los derechos reservados"
    "</div>",
    unsafe_allow_html=True
)