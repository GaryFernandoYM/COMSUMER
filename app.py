from flask import Flask, render_template, jsonify
import boto3, os, json

app = Flask(__name__)

# Credenciales AWS
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = 'bucket-lambda-s3-fegf'
FILE_NAME = 'kc_house_datcsv.json'

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
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
