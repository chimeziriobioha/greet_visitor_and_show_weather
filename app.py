import os
import requests
import weatherloc
from markupsafe import Markup
from flask import Flask, jsonify, request


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['APP_SECRET_KEY']


@app.route("/")
def home():
    return Markup(
        "<h1>Hello, Welcome!</h1> <br>"
        "<h3>This is HNG11 Stage One Task by Chimeziri Obioha.</h3> <br>"
        f"<h3>Visit <u><em>{request.base_url}api/hello?visitor_name='YOUR NAME'</em></u> for take-away greeting</h3>"
    )


@app.route("/api/hello", methods=['GET'])
def hello_visitor():

    visitor_name = request.args.get('visitor_name')

    # Get Visitor's IP Address
    if os.environ.get('APP_IN_PRODUCTION'):
        visitor_ip = str(request.environ.get(
            'HTTP_X_FORWARDED_FOR')) or str(request.environ.get('REMOTE_ADDR'))
    else:
        visitor_ip = request.remote_addr

    # get gealocation info for IP address
    loc_info = requests.get(f'https://ipapi.co/{visitor_ip}/json/', timeout=1200).json()

    # init weather api client
    wea_client = weatherloc.Client(os.environ['WEATHER_API_KEY'])

    # get city, with a fall-back to "Lagos"
    visitor_city = loc_info.get('city') or "Lagos"

    # get city weather details using weather api client
    city_weather = wea_client.current(visitor_city)
    city_temp = city_weather.feelslike_c

    # reatun json
    return jsonify(
        {
        "client_ip": f"{visitor_ip}", # The IP address of the requester
        "location": f"{visitor_city}", # The city of the requester
        "greeting": f"Hello, {visitor_name}!, the temperature "
                    f"is {city_temp} degrees Celcius in {visitor_city}",
        }
    )


@app.route("/api/test-production/", methods=['GET'])
def test_production():
    """
    Just to quick way to test out the production version when in localhost
    """
    prod_url = "https://chimeziri-obioha-hng11-stage1-task.cleverapps.io/api/hello?visitor_name='Chimeziri Obioha'"

    return jsonify(requests.get(prod_url, timeout=1200).json())


if __name__ == "__main__":
    if os.environ.get('APP_IN_PRODUCTION'):
        app.run(debug=False)
    else:
        app.run(debug=True)