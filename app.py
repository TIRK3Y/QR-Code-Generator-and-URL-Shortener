from flask import Flask, render_template, request, send_from_directory
import qrcode
import os
import requests
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/qr_codes/'

BITLY_ACCESS_TOKEN = '909e1f1f819438f23afeb8870620d09ec944db5b'

def shorten_url(long_url):
    headers = {'Authorization': f'Bearer {BITLY_ACCESS_TOKEN}', 'Content-Type': 'application/json'}
    data = {'long_url': long_url}
    response = requests.post('https://api-ssl.bitly.com/v4/shorten', json=data, headers=headers)
    
    if response.status_code == 200:
        return response.json().get('link')
    else:
        print(f"Error shortening URL: {response.content.decode('utf-8')}")
        return None


def sanitize_filename(url):
    # Remove scheme (http, https) 
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', url)
    return sanitized

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        get_short_url = 'short_url' in request.form
        get_qr_code = 'qr_code' in request.form
        
        short_url = None
        qr_img_path = None

        if get_short_url:
            short_url = shorten_url(url)
        
        if get_qr_code:
            if not short_url:
                short_url = url
            sanitized_filename = sanitize_filename(short_url)
            qr_img = qrcode.make(short_url)
            qr_img_filename = f'{sanitized_filename}.png'
            qr_img_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_img_filename)
            qr_img.save(qr_img_path)

        return render_template('index.html', short_url=short_url, qr_img=qr_img_path)
    
    return render_template('index.html')

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
