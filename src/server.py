"""
Server entire point for Text Insight web service
"""
from api import BackendApi

backend_api = BackendApi()
app = backend_api.get_app()
