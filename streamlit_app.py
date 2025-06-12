
import streamlit as st

# Datos de bebidas
bebidas = {
    "Cerveza (330 ml, 5%)": (330, 5),
    "Vino (150 ml, 12%)": (150, 12),
    "Cava (150 ml, 11.5%)": (150, 11.5),
    "Licor (50 ml, 30%)": (50, 30),
    "Combinado (250 ml, 20%)": (250, 20)
}

densidad_alcohol = 0.8
eliminacion_por_hora = 0.15

# Funciones
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

def evaluar_sancion(mg_l, tipo):
    if mg_l == 0 and tipo == "Menor":
        return "Multa: 500 €, 4 puntos (si no se supera 0.5 g/L en sangre)"
    elif mg_l <= 0.25:
        return "Multa: 200 €, 2 puntos"
    elif mg_l <= 0.5 and tipo == "General":
        return "Multa: 500 €, 4 puntos"
    elif mg_l <= 0.3 and tipo != "General":
        return "Multa: 500 €, 4 puntos"
    elif mg_l > 0.5 and tipo == "General":
        return "Multa: 1000 €, 6 puntos"
    elif mg_l > 0.3 and tipo != "General":
        return "Multa: 1000 €, 6 puntos"
    else:
        return "Consulta específica requerida para tu caso."

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
        bac_mg_l_aire = bac * 0.5  # conversión
        tiempo_extra = tiempo_hasta_limite(bac, limite_legal)
        sancion = evaluar_sancion(bac_mg_l_aire, tipo_conductor)

        st.subheader("Resultados")
        st.write(f"**BAC estimado (sangre):** {bac:.2f} g/L")
        st.write(f"**Equivalente en aire espirado:** {bac_mg_l_aire:.2f} mg/L")
        st.write(f"**Límite legal para tu caso:** {limite_legal:.2f} g/L sangre ({limite_legal*0.5:.2f} mg/L aire)")
        st.write(f"**Tiempo estimado hasta estar por debajo del límite legal:** {tiempo_extra:.1f} horas")
        st.warning(f"**Sanción estimada según normativa española:** {sancion}")

        # Mensajes personalizados
        if bac > 2:
            st.error("🚨 Nivel muy alto de alcoholemia. Riesgo severo para la salud.")
        elif bac > 1:
            st.warning("⚠️ Nivel elevado. Evita conducir y considera buscar ayuda médica si hay síntomas.")
        elif bac > 0.5:
            st.info("ℹ️ Podrías experimentar efectos moderados: euforia, menor coordinación.")
        elif bac > 0:
            st.info("ℹ️ Efectos leves posibles: relajación, reducción de reflejos.")
