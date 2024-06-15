import requests
import hmac
import hashlib
import time

def binance_request(event):
    try:
        method = event.get('method')
        path = event.get('path')
        keys = event.get('keys')
        params = event.get('params', {})
        base_url = 'https://api.binance.com'
        
        if not keys or not keys.get('api'):
            # Public API
            query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
            url = f"{base_url}{path}?{query_string}" if query_string else f"{base_url}{path}"
            resp = requests.get(url)
            resp.raise_for_status()
            return {'statusCode': 200, 'body': resp.json()}
        
        # Signed API
        params['timestamp'] = int(time.time() * 1000) - 1000
        params['recvWindow'] = 15000
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        api_key = keys['api']
        secret_key = keys['sec']
        signature = hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        url = f"{base_url}{path}?{query_string}&signature={signature}"
        headers = {'X-MBX-APIKEY': api_key}
        
        if method == 'GET':
            resp = requests.get(url, headers=headers)
        else:
            resp = requests.post(url, headers=headers)
        
        resp.raise_for_status()
        return {'statusCode': resp.status_code, 'body': resp.json()}
    except Exception as e:
        raise e

# Example usage
