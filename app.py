from flask import Flask, render_template, jsonify
import boto3, os, json, pymysql
from datetime import datetime

app = Flask(__name__)

# Credenciales S3
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = 'bucket-lambda-s3-fegf'
FILE_NAME = 'kc_house_datcsv.json'

# Credenciales MySQL (RDS)
DB_HOST = 'flaskdb.cyvqyyk0mosb.us-east-1.rds.amazonaws.com'
DB_USER = 'admin'
DB_PASSWORD = '12345Seguro'
DB_NAME = 'flaskdb'

def insertar_datos_en_mysql(data):
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            port=3306
        )
        cursor = conn.cursor()

        for row in data:
            try:
                fecha_str = row.get("date", "")
                fecha = datetime.strptime(fecha_str, "%Y%m%dT%H%M%S").date()

                cursor.execute("""
                    INSERT IGNORE INTO casas (
                        ID, DATE, PRICE, BEDROOMS, BATHROOMS, SQFT_LIVING, SQFT_LOT,
                        FLOORS, WATERFRONT, VIEW, `CONDITION`, GRADE, SQFT_ABOVE,
                        SQFT_BASEMENT, YR_BUILT, YR_RENOVATED, ZIPCODE, LAT, `LONG`,
                        SQFT_LIVING15, SQFT_LOT15
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    row["id"], fecha, row["price"], row["bedrooms"], row["bathrooms"],
                    row["sqft_living"], row["sqft_lot"], row["floors"], row["waterfront"],
                    row["view"], row["condition"], row["grade"], row["sqft_above"],
                    row["sqft_basement"], row["yr_built"], row["yr_renovated"],
                    row["zipcode"], row["lat"], row["long"],
                    row["sqft_living15"], row["sqft_lot15"]
                ))

            except Exception as fila_error:
                print(f"❌ Fila con error: {fila_error}")
        
        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print("❌ Error conectando a MySQL:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/json')
def obtener_json():
    try:
        s3 = boto3.client(
            's3',
            region_name='us-east-1',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_NAME)
        contenido = obj['Body'].read().decode('utf-8')
        data = json.loads(contenido)

        if isinstance(data, list) and data:
            insertar_datos_en_mysql(data)
            return jsonify({'status': '✅ Datos insertados correctamente o ya existentes'})
        else:
            return jsonify({'warning': '⚠️ El archivo JSON está vacío o mal formateado.'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
