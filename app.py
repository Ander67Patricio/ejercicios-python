# ============================================================
# APLICACIÓN STREAMLIT: Ejercicios de Python
#   1) Registro y gráficos de ventas mensuales
#   2) Graficador de curvas 2D (circunferencia, elipse, recta)
#   3) Graficador de curvas 3D (esfera, elipsoide, recta en el espacio)
#
# Instalación : pip install -r requirements.txt
# Ejecución   : streamlit run app.py
# ============================================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Ejercicios de Python", page_icon="📊", layout="wide")

MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
         'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

# Datos de prueba (total esperado: 220,050.00)
DATOS_PRUEBA = [12500, 13800, 15200, 14100, 16750, 18300,
                17200, 19500, 18900, 21000, 24500, 28300]


# ============================================================
# FUNCIONES AUXILIARES (ecuaciones y validaciones)
# ============================================================
def cuadrado(var, c):
    """Devuelve '(x - 2)^2', '(x + 3)^2' o 'x^2' según el valor del centro c."""
    if c == 0:
        return f"{var}^2"
    signo = "-" if c > 0 else "+"
    return f"({var} {signo} {abs(c):g})^2"


def ecuacion_recta(m, b):
    """Ecuación y = mx + b con los signos bien formados."""
    if m == 0:
        return f"y = {b:g}"
    parte_m = "x" if m == 1 else ("-x" if m == -1 else f"{m:g}x")
    if b == 0:
        return f"y = {parte_m}"
    return f"y = {parte_m} {'-' if b < 0 else '+'} {abs(b):g}"


def a_texto(txt):
    """Cambia '^2' por '²' para textos que no admiten LaTeX (leyendas de Plotly)."""
    return txt.replace("^2", "²")


def mostrar_errores(errores):
    """Muestra los errores de validación. Devuelve True si hubo alguno."""
    if errores:
        st.error("⚠️ Corrige lo siguiente para poder graficar:\n\n" +
                 "\n".join(f"- {e}" for e in errores))
        return True
    return False


def numero(col, etiqueta, valor, clave):
    """Campo numérico con valor inicial y clave única (conserva lo escrito)."""
    return col.number_input(etiqueta, value=float(valor), step=0.5, key=clave)


# ============================================================
# EJERCICIO 2: VENTAS MENSUALES
# ============================================================
def nueva_tabla(valores):
    return pd.DataFrame({"Mes": MESES, "Ventas": valores}, dtype="object").astype(
        {"Mes": "string", "Ventas": "float64"})


def cargar_prueba():
    st.session_state.ventas_ini = [float(v) for v in DATOS_PRUEBA]
    st.session_state.ver += 1          # nueva clave => el editor se reinicia


def limpiar_tabla():
    st.session_state.ventas_ini = [np.nan] * 12
    st.session_state.ver += 1


def grafico_barras(df, anio, moneda):
    ventas = df["Ventas"].values
    i_max, i_min = int(ventas.argmax()), int(ventas.argmin())
    colores = ["tab:blue"] * 12                       # verde = máximo, rojo = mínimo
    colores[i_max], colores[i_min] = "tab:green", "tab:red"

    fig, ax = plt.subplots(figsize=(10, 6))
    barras = ax.bar(MESES, ventas, color=colores, edgecolor="black")
    ax.bar_label(barras, labels=[f"{moneda}{v:,.0f}" for v in ventas],
                 padding=3, fontsize=8, rotation=90)  # valores sobre cada barra
    ax.set_ylim(0, max(ventas.max() * 1.22, 1))
    ax.set_title(f"Ventas mensuales {anio} - Gráfico de barras", fontweight="bold")
    ax.set_xlabel("Mes")
    ax.set_ylabel(f"Ventas ({moneda})")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", linestyle=":", alpha=0.7)
    ax.legend(handles=[
        Patch(color="tab:green", label=f"Mayor venta: {MESES[i_max]}"),
        Patch(color="tab:red", label=f"Menor venta: {MESES[i_min]}"),
        Patch(color="tab:blue", label="Otros meses")], loc="upper left")
    fig.tight_layout()
    return fig


def grafico_lineas(df, anio, moneda):
    ventas = df["Ventas"].values
    promedio = ventas.mean()
    i_max, i_min = int(ventas.argmax()), int(ventas.argmin())

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(MESES, ventas, marker="o", color="tab:purple", linewidth=2,
            label="Ventas mensuales")
    ax.axhline(promedio, color="orange", linestyle="--",
               label=f"Promedio: {moneda}{promedio:,.2f}")
    for mes, v in zip(MESES, ventas):                 # valores sobre cada punto
        ax.annotate(f"{moneda}{v:,.0f}", (mes, v), textcoords="offset points",
                    xytext=(0, 9), ha="center", fontsize=8)
    ax.scatter(MESES[i_max], ventas[i_max], s=140, color="tab:green", zorder=5, label="Máximo")
    ax.scatter(MESES[i_min], ventas[i_min], s=140, color="tab:red", zorder=5, label="Mínimo")
    ax.set_ylim(0, max(ventas.max() * 1.15, 1))
    ax.set_title(f"Ventas mensuales {anio} - Evolución anual", fontweight="bold")
    ax.set_xlabel("Mes")
    ax.set_ylabel(f"Ventas ({moneda})")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, linestyle=":", alpha=0.7)
    ax.legend(loc="upper left")
    fig.tight_layout()
    return fig


def pagina_ventas():
    st.header("📊 Registro y gráficos de ventas mensuales")
    st.write("Escribe las ventas de cada mes en la tabla (solo números ≥ 0). "
             "Los resultados y gráficos se actualizan **automáticamente** al editar cualquier valor.")

    # Estado inicial de la sesión
    if "ver" not in st.session_state:
        st.session_state.ver = 0
        st.session_state.ventas_ini = [np.nan] * 12

    izq, der = st.columns([1, 2], gap="large")

    # ---------- Columna izquierda: entrada de datos ----------
    with izq:
        anio = st.number_input("Año a registrar", min_value=1900, max_value=2100,
                               value=2025, step=1)
        moneda = st.text_input("Símbolo de moneda", value="$", max_chars=4)
        b1, b2 = st.columns(2)
        b1.button("Cargar datos de prueba", on_click=cargar_prueba)
        b2.button("Limpiar tabla", on_click=limpiar_tabla)

        # Tabla editable: el tipo numérico impide escribir texto
        editada = st.data_editor(
            nueva_tabla(st.session_state.ventas_ini),
            key=f"editor_{st.session_state.ver}",
            hide_index=True, disabled=["Mes"], num_rows="fixed",
            column_config={"Ventas": st.column_config.NumberColumn(
                f"Ventas ({moneda})", min_value=0.0, format="%.2f")})

    # ---------- Validación ----------
    errores = []
    for mes, v in zip(MESES, editada["Ventas"]):
        if pd.isna(v):
            errores.append(f"**{mes}**: el campo está vacío.")
        elif not np.isfinite(v):
            errores.append(f"**{mes}**: el valor debe ser un número finito.")
        elif v < 0:
            errores.append(f"**{mes}**: no se permiten valores negativos ({v:g}).")

    with der:
        if mostrar_errores(errores):
            return

        # Estructura de datos: DataFrame de Pandas
        df = pd.DataFrame({"Mes": MESES, "Ventas": editada["Ventas"].astype(float).values})

        # Cálculos automáticos
        total = df["Ventas"].sum()
        promedio = df["Ventas"].mean()
        fila_max = df.loc[df["Ventas"].idxmax()]
        fila_min = df.loc[df["Ventas"].idxmin()]

        m1, m2 = st.columns(2)
        m1.metric("Total de ventas anuales", f"{moneda}{total:,.2f}")
        m2.metric("Promedio mensual", f"{moneda}{promedio:,.2f}")
        m3, m4 = st.columns(2)
        m3.metric(f"Mayor venta: {fila_max['Mes']}", f"{moneda}{fila_max['Ventas']:,.2f}")
        m4.metric(f"Menor venta: {fila_min['Mes']}", f"{moneda}{fila_min['Ventas']:,.2f}")

        tab1, tab2, tab3 = st.tabs(["📊 Gráfico de barras", "📈 Gráfico de líneas", "📋 Tabla"])
        with tab1:
            fig = grafico_barras(df, anio, moneda)
            st.pyplot(fig)
            plt.close(fig)
        with tab2:
            fig = grafico_lineas(df, anio, moneda)
            st.pyplot(fig)
            plt.close(fig)
        with tab3:
            st.dataframe(df, hide_index=True)
            st.download_button("Descargar CSV", df.to_csv(index=False).encode("utf-8"),
                               file_name=f"ventas_{anio}.csv", mime="text/csv")


# ============================================================
# EJERCICIO 3 (2D): CIRCUNFERENCIA, ELIPSE Y RECTA
# ============================================================
def preparar_ejes_2d(titulo):
    """Figura con ejes X e Y diferenciados, cuadrícula, título y etiquetas."""
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.axhline(0, color="black", linewidth=1.4, label="Eje X (y = 0)")
    ax.axvline(0, color="dimgray", linewidth=1.4, linestyle="--", label="Eje Y (x = 0)")
    ax.grid(True, linestyle=":", alpha=0.7)
    ax.set_xlabel("Eje X")
    ax.set_ylabel("Eje Y")
    ax.set_title(titulo, fontsize=14, fontweight="bold")
    return fig, ax


def finalizar_2d(fig, ax, xs, ys, igual=False, incluir_origen=True):
    """Ajusta límites y escala proporcional, agrega la leyenda y muestra la figura."""
    x_min, x_max, y_min, y_max = xs.min(), xs.max(), ys.min(), ys.max()
    if incluir_origen:                               # asegura que los ejes sean visibles
        x_min, x_max = min(x_min, 0), max(x_max, 0)
        y_min, y_max = min(y_min, 0), max(y_max, 0)
    px = 0.1 * (x_max - x_min) or 1.0
    py = 0.1 * (y_max - y_min) or 1.0
    ax.set_xlim(x_min - px, x_max + px)
    ax.set_ylim(y_min - py, y_max + py)
    if igual:                                        # escala 1:1 (no deforma la figura)
        ax.set_aspect("equal", adjustable="box")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, fontsize=9)
    st.pyplot(fig)
    plt.close(fig)


def curva_circunferencia():
    izq, der = st.columns([1, 2], gap="large")
    with izq:
        st.latex(r"(x - h)^2 + (y - k)^2 = r^2")
        h = numero(st, "Centro en X (h)", 2, "c_h")
        k = numero(st, "Centro en Y (k)", -1, "c_k")
        r = numero(st, "Radio (r)", 3, "c_r")
    with der:
        if mostrar_errores(["El radio (r) debe ser mayor que 0."] if r <= 0 else []):
            return
        t = np.linspace(0, 2 * np.pi, 400)
        x, y = h + r * np.cos(t), k + r * np.sin(t)       # forma paramétrica
        ec = f"{cuadrado('x', h)} + {cuadrado('y', k)} = {r**2:g}"
        st.latex(ec)
        fig, ax = preparar_ejes_2d("Circunferencia")
        ax.plot(x, y, color="tab:blue", linewidth=2.5, label=f"${ec}$")
        ax.plot(h, k, "o", color="navy", label=f"Centro ({h:g}, {k:g})")
        ax.plot([h, h + r], [k, k], "--", color="navy", linewidth=1)
        ax.annotate(f"r = {r:g}", (h + r / 2, k), textcoords="offset points",
                    xytext=(0, 6), ha="center", color="navy")
        finalizar_2d(fig, ax, x, y, igual=True)


def curva_elipse():
    izq, der = st.columns([1, 2], gap="large")
    with izq:
        st.latex(r"\text{Horizontal: } \frac{(x-h)^2}{a^2} + \frac{(y-k)^2}{b^2} = 1")
        st.latex(r"\text{Vertical: } \frac{(x-h)^2}{b^2} + \frac{(y-k)^2}{a^2} = 1")
        h = numero(st, "Centro en X (h)", 1, "e_h")
        k = numero(st, "Centro en Y (k)", 2, "e_k")
        a = numero(st, "Semieje mayor (a)", 5, "e_a")
        b = numero(st, "Semieje menor (b)", 3, "e_b")
        ori = st.radio("Orientación del eje mayor", ["Horizontal", "Vertical"],
                       horizontal=True, key="e_ori")
    with der:
        errores = []
        if a <= 0 or b <= 0:
            errores.append("Los semiejes a y b deben ser mayores que 0.")
        elif b > a:
            errores.append("El semieje mayor (a) debe ser mayor o igual que el menor (b).")
        if mostrar_errores(errores):
            return

        sx, sy = (a, b) if ori == "Horizontal" else (b, a)   # semiejes sobre X e Y
        t = np.linspace(0, 2 * np.pi, 400)
        x, y = h + sx * np.cos(t), k + sy * np.sin(t)

        t1, t2 = cuadrado("x", h), cuadrado("y", k)
        ec = r"\frac{" + t1 + "}{" + f"{sx**2:g}" + r"} + \frac{" + t2 + "}{" + f"{sy**2:g}" + "} = 1"
        c = np.sqrt(a**2 - b**2)                             # distancia centro-foco
        st.latex(ec)
        st.caption(f"c = {c:.4g} · excentricidad e = {c / a:.4g}")

        fig, ax = preparar_ejes_2d(f"Elipse ({ori.lower()})")
        ax.plot(x, y, color="tab:red", linewidth=2.5, label=f"${ec}$")
        ax.plot(h, k, "o", color="darkred", label=f"Centro ({h:g}, {k:g})")
        if c > 0:                                            # si a = b los focos coinciden
            fx, fy = ([h - c, h + c], [k, k]) if ori == "Horizontal" else ([h, h], [k - c, k + c])
            ax.plot(fx, fy, "*", color="gold", markeredgecolor="black",
                    markersize=13, label="Focos")
        finalizar_2d(fig, ax, x, y, igual=True)


def curva_recta():
    izq, der = st.columns([1, 2], gap="large")
    with izq:
        st.latex(r"y = mx + b")
        m = numero(st, "Pendiente (m)", 2, "r_m")
        b = numero(st, "Intersección con el eje Y (b)", 1, "r_b")
        x1 = numero(st, "X mínimo a visualizar", -5, "r_x1")
        x2 = numero(st, "X máximo a visualizar", 5, "r_x2")
    with der:
        if mostrar_errores(["X mínimo debe ser menor que X máximo."] if x1 >= x2 else []):
            return
        x = np.linspace(x1, x2, 400)
        y = m * x + b
        ec = ecuacion_recta(m, b)
        st.latex(ec)
        fig, ax = preparar_ejes_2d("Recta")
        ax.plot(x, y, color="tab:green", linewidth=2.5, label=f"${ec}$")
        if x1 <= 0 <= x2:                                    # corte con el eje Y
            ax.plot(0, b, "o", color="darkgreen", label=f"Intersección con Y: (0, {b:g})")
        if m != 0:                                           # corte con el eje X
            x0 = -b / m
            if x1 <= x0 <= x2:
                ax.plot(x0, 0, "s", color="purple", label=f"Intersección con X: ({x0:g}, 0)")
        finalizar_2d(fig, ax, x, y, igual=False, incluir_origen=False)


def pagina_curvas_2d():
    st.header("📐 Graficador de curvas 2D")
    curva = st.selectbox("Selecciona la curva", ["Circunferencia", "Elipse", "Recta"])
    st.caption("Modifica los parámetros y la gráfica se actualiza automáticamente.")
    {"Circunferencia": curva_circunferencia,
     "Elipse": curva_elipse,
     "Recta": curva_recta}[curva]()


# ============================================================
# EJERCICIO 3 (3D): ESFERA, ELIPSOIDE Y RECTA EN EL ESPACIO
# ============================================================
def limites_3d(X, Y, Z):
    """Rango de cada eje (incluye el origen) con un margen del 15 %."""
    lims = []
    for V in (X, Y, Z):
        lo, hi = min(np.min(V), 0), max(np.max(V), 0)
        pad = 0.15 * (hi - lo) or 1.0
        lims.append((lo - pad, hi + pad))
    return lims


def trazas_ejes(lims):
    """Tres líneas de colores distintos que representan los ejes X, Y, Z."""
    (lx, hx), (ly, hy), (lz, hz) = lims
    return [
        go.Scatter3d(x=[lx, hx], y=[0, 0], z=[0, 0], mode="lines",
                     line=dict(color="red", width=5), name="Eje X"),
        go.Scatter3d(x=[0, 0], y=[ly, hy], z=[0, 0], mode="lines",
                     line=dict(color="green", width=5), name="Eje Y"),
        go.Scatter3d(x=[0, 0], y=[0, 0], z=[lz, hz], mode="lines",
                     line=dict(color="blue", width=5), name="Eje Z")]


def mostrar_3d(fig, titulo):
    """Aplica título, etiquetas de ejes y escala proporcional, y muestra la figura."""
    fig.update_layout(
        title=dict(text=titulo, x=0.5),
        scene=dict(xaxis_title="Eje X", yaxis_title="Eje Y", zaxis_title="Eje Z",
                   aspectmode="data"),              # escala 1:1:1
        height=700, showlegend=True,
        legend=dict(x=0, y=1, bgcolor="rgba(255,255,255,0.7)"))
    st.plotly_chart(fig)


def malla_esferica(h, k, l, sx, sy, sz):
    """Superficie paramétrica de una esfera / elipsoide con semiejes sx, sy, sz."""
    u, v = np.meshgrid(np.linspace(0, 2 * np.pi, 60), np.linspace(0, np.pi, 40))
    return (h + sx * np.cos(u) * np.sin(v),
            k + sy * np.sin(u) * np.sin(v),
            l + sz * np.cos(v))


def superficie(X, Y, Z, color, nombre):
    return go.Surface(x=X, y=Y, z=Z, opacity=0.75, showscale=False,
                      colorscale=[[0, color], [1, color]], name=nombre, showlegend=True)


def figura_esfera():
    izq, der = st.columns([1, 2], gap="large")
    with izq:
        st.latex(r"(x-h)^2 + (y-k)^2 + (z-l)^2 = r^2")
        h = numero(st, "Centro en X (h)", 1, "s_h")
        k = numero(st, "Centro en Y (k)", 2, "s_k")
        l = numero(st, "Centro en Z (l)", 3, "s_l")
        r = numero(st, "Radio (r)", 2, "s_r")
    with der:
        if mostrar_errores(["El radio (r) debe ser mayor que 0."] if r <= 0 else []):
            return
        X, Y, Z = malla_esferica(h, k, l, r, r, r)
        ec = f"{cuadrado('x', h)} + {cuadrado('y', k)} + {cuadrado('z', l)} = {r**2:g}"
        st.latex(ec)
        fig = go.Figure()
        fig.add_trace(superficie(X, Y, Z, "#1f77b4", a_texto(ec)))
        fig.add_trace(go.Scatter3d(x=[h], y=[k], z=[l], mode="markers",
                                   marker=dict(size=5, color="navy"),
                                   name=f"Centro ({h:g}, {k:g}, {l:g})"))
        for tr in trazas_ejes(limites_3d(X, Y, Z)):
            fig.add_trace(tr)
        mostrar_3d(fig, "Esfera")


def figura_elipsoide():
    izq, der = st.columns([1, 2], gap="large")
    with izq:
        st.latex(r"\frac{(x-h)^2}{a^2} + \frac{(y-k)^2}{b^2} + \frac{(z-l)^2}{c^2} = 1")
        h = numero(st, "Centro en X (h)", 0, "el_h")
        k = numero(st, "Centro en Y (k)", 0, "el_k")
        l = numero(st, "Centro en Z (l)", 0, "el_l")
        a = numero(st, "Semieje en X (a)", 4, "el_a")
        b = numero(st, "Semieje en Y (b)", 3, "el_b")
        c = numero(st, "Semieje en Z (c)", 2, "el_c")
    with der:
        if mostrar_errores(["Los semiejes a, b y c deben ser mayores que 0."]
                           if min(a, b, c) <= 0 else []):
            return
        X, Y, Z = malla_esferica(h, k, l, a, b, c)
        tx, ty, tz = cuadrado("x", h), cuadrado("y", k), cuadrado("z", l)
        ec = (r"\frac{" + tx + "}{" + f"{a**2:g}" + r"} + \frac{" + ty + "}{" + f"{b**2:g}"
              + r"} + \frac{" + tz + "}{" + f"{c**2:g}" + "} = 1")
        st.latex(ec)
        fig = go.Figure()
        fig.add_trace(superficie(X, Y, Z, "#d62728",
                                 a_texto(f"{tx}/{a**2:g} + {ty}/{b**2:g} + {tz}/{c**2:g} = 1")))
        fig.add_trace(go.Scatter3d(x=[h], y=[k], z=[l], mode="markers",
                                   marker=dict(size=5, color="darkred"),
                                   name=f"Centro ({h:g}, {k:g}, {l:g})"))
        for tr in trazas_ejes(limites_3d(X, Y, Z)):
            fig.add_trace(tr)
        mostrar_3d(fig, "Elipsoide")


def figura_recta_3d():
    izq, der = st.columns([1, 2], gap="large")
    with izq:
        st.latex(r"(x,y,z) = (x_0,y_0,z_0) + t\,(u,v,w)")
        x0 = numero(st, "Punto base x₀", 1, "l_x0")
        y0 = numero(st, "Punto base y₀", 2, "l_y0")
        z0 = numero(st, "Punto base z₀", 0, "l_z0")
        u = numero(st, "Dirección u", 1, "l_u")
        v = numero(st, "Dirección v", 2, "l_v")
        w = numero(st, "Dirección w", 3, "l_w")
        t1 = numero(st, "t mínimo", -3, "l_t1")
        t2 = numero(st, "t máximo", 3, "l_t2")
    with der:
        errores = []
        if u == 0 and v == 0 and w == 0:
            errores.append("El vector dirección (u, v, w) no puede ser (0, 0, 0).")
        if t1 >= t2:
            errores.append("t mínimo debe ser menor que t máximo.")
        if mostrar_errores(errores):
            return
        t = np.linspace(t1, t2, 200)
        X, Y, Z = x0 + u * t, y0 + v * t, z0 + w * t          # ecuación paramétrica
        ec = f"(x, y, z) = ({x0:g}, {y0:g}, {z0:g}) + t·({u:g}, {v:g}, {w:g})"
        st.code(ec, language=None)
        st.caption(f"Extremos: ({X[0]:g}, {Y[0]:g}, {Z[0]:g})  →  ({X[-1]:g}, {Y[-1]:g}, {Z[-1]:g})")
        fig = go.Figure()
        fig.add_trace(go.Scatter3d(x=X, y=Y, z=Z, mode="lines",
                                   line=dict(color="#2ca02c", width=7), name=ec))
        fig.add_trace(go.Scatter3d(x=[x0], y=[y0], z=[z0], mode="markers",
                                   marker=dict(size=6, color="darkgreen"),
                                   name=f"Punto base P₀ ({x0:g}, {y0:g}, {z0:g})"))
        for tr in trazas_ejes(limites_3d(X, Y, Z)):
            fig.add_trace(tr)
        mostrar_3d(fig, "Recta en el espacio")


def pagina_curvas_3d():
    st.header("🧊 Graficador de curvas 3D")
    figura = st.selectbox("Selecciona la figura", ["Esfera", "Elipsoide", "Recta en el espacio"])
    st.caption("Arrastra con el mouse para rotar y usa la rueda para acercar. "
               "Modifica los parámetros y la gráfica se actualiza automáticamente.")
    {"Esfera": figura_esfera,
     "Elipsoide": figura_elipsoide,
     "Recta en el espacio": figura_recta_3d}[figura]()


# ============================================================
# MENÚ PRINCIPAL (barra lateral)
# ============================================================
st.sidebar.title("Ejercicios de Python")
pagina = st.sidebar.radio("Selecciona el programa",
                          ["📊 Ventas mensuales", "📐 Curvas 2D", "🧊 Curvas 3D"])
st.sidebar.caption("Python · NumPy · Pandas · Matplotlib · Plotly · Streamlit")

if pagina.startswith("📊"):
    pagina_ventas()
elif pagina.startswith("📐"):
    pagina_curvas_2d()
else:
    pagina_curvas_3d()
