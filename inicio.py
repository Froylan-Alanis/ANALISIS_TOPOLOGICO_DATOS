# ================= LIBRERÍAS =================
import os
import sqlite3
import re
import pandas as pd
from io import BytesIO
from flask import (
    Flask,
    render_template,
    jsonify,
    flash,
    send_file,
    redirect,
    url_for
)

# ================= CONFIGURACIÓN =================
app = Flask(__name__)
app.secret_key = 'info'

UPLOAD_FOLDER = './Files'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DB_PATH = "./BD_PROJECT_ULISES.db"

# ================= CONEXIÓN BD =================
def get_db_connection():

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

# ================= RUTA PRINCIPAL =================
@app.route('/')
def index():
    return render_template('index.html')

# ================= TABLA  =================
@app.route('/tabla')
def tabla():

    conn = get_db_connection()

    if not conn:
        flash("Error de conexión con la base de datos", "danger")
        return redirect(url_for('index'))

    try:

        cursor = conn.cursor()
        cursor.execute("""

    SELECT

        NOM_ENT,

        COUNT(*) AS total_localidades,

        SUM(
            CASE
                WHEN POBTOT GLOB '*[0-9]*'
                THEN CAST(POBTOT AS REAL)
                ELSE 0
            END
        ) AS poblacion_total,

        AVG(
            CASE
                WHEN POBTOT GLOB '*[0-9]*'
                THEN CAST(POBTOT AS REAL)
                ELSE NULL
            END
        ) AS promedio_poblacion,

        MAX(
            CASE
                WHEN POBTOT GLOB '*[0-9]*'
                THEN CAST(POBTOT AS REAL)
                ELSE 0
            END
        ) AS max_poblacion,

        MIN(
            CASE
                WHEN POBTOT GLOB '*[0-9]*'
                THEN CAST(POBTOT AS REAL)
                ELSE NULL
            END
        ) AS min_poblacion

    FROM ITER_NALCSV20

    WHERE
        LOC NOT IN ('0000','9998','9999')

    GROUP BY NOM_ENT

    ORDER BY poblacion_total DESC

""")

        datos = [dict(f) for f in cursor.fetchall()]

        return render_template(
            'tabla_simple.html',
            datos=datos
        )

    except Exception as e:

        flash(f"Error en la consulta: {e}", "danger")
        return redirect(url_for('index'))

    finally:
        conn.close()

# ==================== REPORTE ====================
@app.route('/exportar_excel')
def exportar_excel():

    conn = get_db_connection()

    if not conn:

        return jsonify({
            "error": "No se pudo conectar a la BD"
        }), 500

    try:
        output = BytesIO()

        writer = pd.ExcelWriter(
            output,
            engine='openpyxl'
        )
        query_general = """

            SELECT *
            FROM ITER_NALCSV20
            LIMIT 1000

        """

        df_general = pd.read_sql_query(
            query_general,
            conn
        )

        df_general.to_excel(
            writer,
            sheet_name='General',
            index=False
        )
        query_nube = """

            SELECT

                NOM_ENT,
                NOM_LOC,
                LATITUD,
                LONGITUD,

                CAST(POBTOT AS REAL) AS poblacion,

                (
                    CAST(POB0_14 AS REAL) +
                    CAST(POB15_64 AS REAL) +
                    CAST(POB65_MAS AS REAL)
                ) AS densidad_demografica

            FROM ITER_NALCSV20

            WHERE
                LOC NOT IN ('0000','9998','9999')
                AND POBTOT > 0

            LIMIT 1000

        """

        df_nube = pd.read_sql_query(
            query_nube,
            conn
        )

        df_nube.to_excel(
            writer,
            sheet_name='Nube_Puntos',
            index=False
        )
        query_vector = """

            SELECT

                NOM_LOC,

                CAST(POBTOT AS REAL) AS poblacion_total,

                CAST(POB0_14 AS REAL) AS pob_0_14,

                CAST(POB15_64 AS REAL) AS pob_15_64,

                CAST(POB65_MAS AS REAL) AS pob_65_mas,

                SQRT(

                    (CAST(POBTOT AS REAL) * CAST(POBTOT AS REAL)) +

                    (CAST(POB0_14 AS REAL) * CAST(POB0_14 AS REAL)) +

                    (CAST(POB15_64 AS REAL) * CAST(POB15_64 AS REAL)) +

                    (CAST(POB65_MAS AS REAL) * CAST(POB65_MAS AS REAL))

                ) AS norma_euclidiana

            FROM ITER_NALCSV20

            WHERE
                LOC NOT IN ('0000','9998','9999')
                AND POBTOT > 0

            LIMIT 500

        """

        df_vector = pd.read_sql_query(
            query_vector,
            conn
        )

        df_vector.to_excel(
            writer,
            sheet_name='Vector_TDA',
            index=False
        )

        query_distancias = """

            SELECT

                A.NOM_LOC AS localidad_1,

                B.NOM_LOC AS localidad_2,

                ABS(
                    CAST(A.POBTOT AS REAL) -
                    CAST(B.POBTOT AS REAL)
                )

                +

                ABS(
                    CAST(A.POB0_14 AS REAL) -
                    CAST(B.POB0_14 AS REAL)
                )

                +

                ABS(
                    CAST(A.POB15_64 AS REAL) -
                    CAST(B.POB15_64 AS REAL)
                )

                +

                ABS(
                    CAST(A.POB65_MAS AS REAL) -
                    CAST(B.POB65_MAS AS REAL)
                )

                AS distancia_manhattan

            FROM
            (
                SELECT *
                FROM ITER_NALCSV20
                WHERE
                    POBTOT > 0
                    AND LOC NOT IN ('0000','9998','9999')
                LIMIT 50
            ) A

            JOIN
            (
                SELECT *
                FROM ITER_NALCSV20
                WHERE
                    POBTOT > 0
                    AND LOC NOT IN ('0000','9998','9999')
                LIMIT 50
            ) B

            ON A.LOC < B.LOC

            ORDER BY distancia_manhattan ASC

            LIMIT 200

        """

        df_distancias = pd.read_sql_query(
            query_distancias,
            conn
        )

        df_distancias.to_excel(
            writer,
            sheet_name='Distancias',
            index=False
        )
        query_componentes = """

            SELECT

                NOM_ENT,

                COUNT(*) AS num_localidades,

                AVG(CAST(POBTOT AS REAL)) AS promedio_poblacion,

                MAX(CAST(POBTOT AS REAL)) AS max_poblacion,

                MIN(CAST(POBTOT AS REAL)) AS min_poblacion

            FROM ITER_NALCSV20

            WHERE
                LOC NOT IN ('0000','9998','9999')
                AND POBTOT > 0

            GROUP BY NOM_ENT

            ORDER BY promedio_poblacion DESC

        """

        df_componentes = pd.read_sql_query(
            query_componentes,
            conn
        )

        df_componentes.to_excel(
            writer,
            sheet_name='Componentes',
            index=False
        )

        writer.close()

        output.seek(0)

        return send_file(

            output,

            download_name='Reporte_TDA.xlsx',

            as_attachment=True,

            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        )

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        conn.close()

# ================= APIs TDA ======================
# 1. NUBE DE PUNTOS
import re
def dms_a_decimal(coord):
    try:
        patron = r'(\d+)°(\d+)\'([\d.]+)"\s*([NSEW])'
        match = re.match(patron, coord)
        if not match:
            return None
        grados = float(match.group(1))
        minutos = float(match.group(2))
        segundos = float(match.group(3))
        direccion = match.group(4)
        decimal = grados + minutos / 60 + segundos / 3600
        if direccion in ['S', 'W']:
            decimal *= -1
        return decimal
    except:
        return None
    
@app.route('/api/nube_puntos')

def api_nube_puntos():

    conexion = sqlite3.connect(
        "BD_PROJECT_ULISES.db"
    )

    conexion.row_factory = sqlite3.Row

    cursor = conexion.cursor()

    cursor.execute("""

        SELECT

            NOM_ENT,

            NOM_LOC,

            LATITUD,

            LONGITUD,

            CAST(POBTOT AS REAL) AS poblacion,

            (

                CAST(POB0_14 AS REAL) +

                CAST(POB15_64 AS REAL) +

                CAST(POB65_MAS AS REAL)

            ) AS densidad_demografica

        FROM ITER_NALCSV20

        WHERE

            LOC NOT IN ('0000','9998','9999')

            AND POBTOT GLOB '*[0-9]*'

            AND CAST(POBTOT AS REAL) > 0

        LIMIT 1000

    """)

    datos = [
        dict(fila)
        for fila in cursor.fetchall()
    ]

    conexion.close()

    return jsonify(datos)
 
# 2. VECTORES MULTIDIMENSIONALES
@app.route('/api/vector')
def api_vector():

    conn = get_db_connection()

    if not conn:

        return jsonify({
            "error": "No se pudo conectar a la BD"
        }), 500

    try:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""

            SELECT

                NOM_LOC,

                CAST(POBTOT AS REAL) AS poblacion_total,

                CAST(POB0_14 AS REAL) AS pob_0_14,

                CAST(POB15_64 AS REAL) AS pob_15_64,

                CAST(POB65_MAS AS REAL) AS pob_65_mas,

                SQRT(

                    (CAST(POBTOT AS REAL) * CAST(POBTOT AS REAL)) +

                    (CAST(POB0_14 AS REAL) * CAST(POB0_14 AS REAL)) +

                    (CAST(POB15_64 AS REAL) * CAST(POB15_64 AS REAL)) +

                    (CAST(POB65_MAS AS REAL) * CAST(POB65_MAS AS REAL))

                ) AS norma_euclidiana

            FROM ITER_NALCSV20

            WHERE

                LOC NOT IN ('0000','9998','9999')

                AND POBTOT GLOB '*[0-9]*'

                AND CAST(POBTOT AS REAL) > 0

            LIMIT 500

        """)

        datos = []

        for row in cursor.fetchall():

            try:

                datos.append({

                    "NOM_LOC": row["NOM_LOC"],

                    "poblacion_total": float(
                        row["poblacion_total"] or 0
                    ),

                    "pob_0_14": float(
                        row["pob_0_14"] or 0
                    ),

                    "pob_15_64": float(
                        row["pob_15_64"] or 0
                    ),

                    "pob_65_mas": float(
                        row["pob_65_mas"] or 0
                    ),

                    "norma_euclidiana": round(

                        float(
                            row["norma_euclidiana"] or 0
                        ),

                        2
                    )

                })

            except Exception as e:

                print("Error fila:", e)

                continue

        return jsonify(datos)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        conn.close()

# 3. DISTANCIAS MANHATTAN
@app.route('/api/distancias')
def api_distancias():

    conn = get_db_connection()

    if not conn:
        return jsonify({
            "error": "No se pudo conectar a la BD"
        }), 500

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT

    A.NOM_LOC AS localidad_1,

    B.NOM_LOC AS localidad_2,

    ABS(
        CAST(A.POBTOT AS REAL) -
        CAST(B.POBTOT AS REAL)
    )

    +

    ABS(
        CAST(A.POB0_14 AS REAL) -
        CAST(B.POB0_14 AS REAL)
    )

    +

    ABS(
        CAST(A.POB15_64 AS REAL) -
        CAST(B.POB15_64 AS REAL)
    )

    +

    ABS(
        CAST(A.POB65_MAS AS REAL) -
        CAST(B.POB65_MAS AS REAL)
    )

    AS distancia_manhattan

FROM
(
    SELECT *
    FROM ITER_NALCSV20
    WHERE
        POBTOT > 0
        AND LOC NOT IN ('0000','9998','9999')
    LIMIT 50
) A

JOIN
(
    SELECT *
    FROM ITER_NALCSV20
    WHERE
        POBTOT > 0
        AND LOC NOT IN ('0000','9998','9999')
    LIMIT 50
) B

ON A.LOC < B.LOC

ORDER BY distancia_manhattan ASC

LIMIT 200
        """)

        datos = [dict(f) for f in cursor.fetchall()]

        return jsonify(datos)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:
        conn.close()

# 4. COMPONENTES POR ESTADO
@app.route('/api/componentes')
def api_componentes():

    conn = get_db_connection()

    if not conn:
        return jsonify({
            "error": "No se pudo conectar a la BD"
        }), 500

    try:

        cursor = conn.cursor()

        cursor.execute("""
SELECT

    NOM_ENT,

    COUNT(*) AS num_localidades,

    AVG(CAST(POBTOT AS REAL)) AS promedio_poblacion,

    MAX(CAST(POBTOT AS REAL)) AS max_poblacion,

    MIN(CAST(POBTOT AS REAL)) AS min_poblacion

FROM ITER_NALCSV20

WHERE
    LOC NOT IN ('0000','9998','9999')
    AND POBTOT > 0

GROUP BY NOM_ENT

ORDER BY promedio_poblacion DESC
        """)

        datos = [dict(f) for f in cursor.fetchall()]

        return jsonify(datos)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:
        conn.close()

# 5. OUTLIERS
@app.route('/api/outliers')
def api_outliers():

    conn = get_db_connection()

    if not conn:

        return jsonify({
            "error": "No se pudo conectar a la BD"
        }), 500

    try:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""

            SELECT

                AVG(
                    CAST(POBTOT AS REAL)
                ) AS promedio,

                AVG(

                    CAST(POBTOT AS REAL) *

                    CAST(POBTOT AS REAL)

                ) AS promedio2

            FROM ITER_NALCSV20

            WHERE

                LOC NOT IN ('0000','9998','9999')

                AND POBTOT GLOB '*[0-9]*'

                AND CAST(POBTOT AS REAL) > 0

        """)

        stats = cursor.fetchone()

        promedio = float(
            stats["promedio"] or 0
        )

        promedio2 = float(
            stats["promedio2"] or 0
        )

        desviacion = (

            promedio2 - promedio**2

        ) ** 0.5

        cursor.execute("""

            SELECT

                NOM_LOC,

                CAST(POBTOT AS REAL) AS poblacion

            FROM ITER_NALCSV20

            WHERE

                LOC NOT IN ('0000','9998','9999')

                AND POBTOT GLOB '*[0-9]*'

                AND CAST(POBTOT AS REAL) > 0

            LIMIT 2000

        """)

        datos = []

        for row in cursor.fetchall():

            try:

                poblacion = float(
                    row["poblacion"] or 0
                )

                z_score = (

                    poblacion - promedio

                ) / desviacion

                if abs(z_score) >= 2:

                    clasificacion = (
                        "Outlier extremo"
                        if abs(z_score) >= 3
                        else "Outlier moderado"
                    )

                    datos.append({

                        "NOM_LOC":
                            row["NOM_LOC"],

                        "POBLACION":
                            int(poblacion),

                        "Z_SCORE":
                            round(z_score, 2),

                        "DESVIACION":
                            round(desviacion, 2),

                        "CLASIFICACION":
                            clasificacion

                    })

            except Exception as e:

                print("Error fila:", e)

                continue

        return jsonify(datos)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        conn.close()


# ================== VISTAS TDA ===================

@app.route('/vista/nube_puntos')
def vista_nube_puntos():
    return render_template('tda_nube_puntos.html')


@app.route('/vista/vector')
def vista_vector():
    return render_template('tda_vector.html')


@app.route('/vista/distancias')
def vista_distancias():
    return render_template('tda_distancias.html')


@app.route('/vista/componentes')
def vista_componentes():
    return render_template('tda_componentes.html')


@app.route('/vista/outliers')
def vista_outliers():
    return render_template('tda_outliers.html')


# ==================== MAIN ========================
if __name__ == '__main__':
    app.run(debug=True)