from woocommerce import API
from config_loader import load_json_secret

woocommerce_config = load_json_secret("woocommerce.json")

wcapi = API(
    url=woocommerce_config["url"],
    consumer_key=woocommerce_config["consumer_key"],
    consumer_secret=woocommerce_config["consumer_secret"],
    version="wc/v3"
)

# Ejemplo: Crear un producto simple
data = {
    "name": "Producto de Prueba API",
    "type": "simple",
    "regular_price": "150.00",
    "description": "Creado desde Python en localhost",
    "categories": [{"id": 1}] # Asegúrate de que el ID de categoría existe
}

print(wcapi.post("products", data).json())
