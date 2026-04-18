import xmlrpc.client
from woocommerce import API
from config_loader import load_json_secret

# --- CONFIGURACIÓN ODOO ---
odoo_config = load_json_secret("odoo.json")
ODOO_URL = odoo_config["url"]
ODOO_DB = odoo_config["db"]
ODOO_USER = odoo_config["user"]
ODOO_API_KEY = odoo_config["api_key"]

# --- CONFIGURACIÓN WOOCOMMERCE ---
woocommerce_config = load_json_secret("woocommerce.json")
wcapi = API(
    url=woocommerce_config["url"],
    consumer_key=woocommerce_config["consumer_key"],
    consumer_secret=woocommerce_config["consumer_secret"],
    version="wc/v3",
    timeout=30
)

def get_odoo_products():
    print("Conectando a Odoo...")
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_API_KEY, {})
    
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    # Traemos productos de Odoo 17
    # Campos: nombre, precio, descripción y SKU (default_code)
    products = models.execute_kw(ODOO_DB, uid, ODOO_API_KEY, 'product.template', 'search_read',
        [[['sale_ok', '=', True]]],
        {'fields': ['name', 'list_price', 'description_sale', 'default_code']}
    )
    return products

def sync_to_woo():
    try:
        odoo_products = get_odoo_products()
        print(f"Se encontraron {len(odoo_products)} productos en Odoo.\n")

        for product in odoo_products:
            sku = product['default_code'] if product['default_code'] else f"ODOO-{product['id']}"
            
            # --- BLOQUE DE DEPURACIÓN ---
            response_check = wcapi.get("products", params={"sku": sku})
            
            if response_check.status_code != 200:
                print(f"Error de conexión con WooCommerce (Status {response_check.status_code})")
                print(f"Respuesta del servidor: {response_check.text[:]}") # Ver los primeros 200 caracteres
                break # Detenemos para no saturar de errores
            
            check_exists = response_check.json()
            # --- FIN BLOQUE DE DEPURACIÓN ---

            product_data = {
                "name": product['name'],
                "type": "simple",
                "regular_price": str(product['list_price']),
                "description": product['description_sale'] or "",
                "sku": sku
            }

            if check_exists:
                product_id = check_exists[0]['id']
                wcapi.put(f"products/{product_id}", product_data)
                print(f"Actualizado: {product['name']}")
            else:
                wcapi.post("products", product_data)
                print(f"Creado: {product['name']}")

    except Exception as e:
        print(f"Error crítico: {e}")
if __name__ == "__main__":
    sync_to_woo()