import pika


binding_keys = """
    kern.*
    *.critical
    """
exchange_name = "app_data"
exchange_type = "topic"
params = pika.ConnectionParameters(host="localhost")
