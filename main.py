import io
import csv
import requests
import matplotlib.pyplot as plt
from flask import Flask, request, send_file

app = Flask(__name__)


def convert_github_url(url):
    """
    Eğer URL GitHub'ın blob URL'siyse, ham URL'ye çevirir.
    Örnek:
    https://github.com/CagataySavasli/GreenAlphaPredictor/blob/main/outputs/result.csv ->
    https://raw.githubusercontent.com/CagataySavasli/GreenAlphaPredictor/main/outputs/result.csv
    """
    if "github.com" in url and "/blob/" in url:
        url = url.replace("https://github.com/", "https://raw.githubusercontent.com/")
        url = url.replace("/blob", "")
    return url


@app.route('/render')
def render_csv():
    # Sorgu parametresi ile CSV dosyasının URL'sini alıyoruz.
    file_url = request.args.get('file_url')
    if not file_url:
        return "Lütfen file_url parametresini sağlayın.", 400

    # GitHub URL'si geliyorsa, ham URL'ye çeviriyoruz.
    file_url = convert_github_url(file_url)

    # CSV dosyasını indiriyoruz.
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        csv_content = response.text.splitlines()
    except Exception as e:
        return f"CSV dosyası alınırken hata oluştu: {str(e)}", 500

    # CSV verisini ayrıştırıp liste haline getiriyoruz.
    reader = csv.reader(csv_content)
    rows = list(reader)
    if not rows:
        return "CSV dosyası boş.", 400

    # Matplotlib ile tablo oluşturuyoruz.
    num_rows = len(rows)
    num_cols = len(rows[0])
    fig, ax = plt.subplots(figsize=(num_cols * 2, (num_rows + 1) * 0.5))
    ax.axis('tight')
    ax.axis('off')

    # Tüm CSV verisini tablo olarak yerleştiriyoruz.
    table = ax.table(cellText=rows, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)

    # Tablo görselini BytesIO'ya kaydediyoruz.
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    # PNG görselini döndürüyoruz.
    return send_file(buf, mimetype='image/png')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
