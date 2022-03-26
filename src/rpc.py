from config import http_provider_url
from web3.middleware import geth_poa_middleware
from web3 import Web3
from web3._utils.request import make_post_request
from web3.providers.rpc import HTTPProvider
import json

web3 = Web3(Web3.HTTPProvider(http_provider_url))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)
pairABI = json.load(open('./abi/IUniswapV2Pair.json'))['abi']

def generate_json_rpc(method, params, request_id=1):
    return {
        'jsonrpc': '2.0',
        'method': method,
        'params': params,
        'id': request_id,
    }


def generate_get_reserves_json_rpc(pairs, blockNumber='latest'):
    c = web3.eth.contract(abi=pairABI)
    for pair in pairs:
        yield generate_json_rpc(
            method='eth_call',
            params=[{
                'to': pair['address'],
                'data': c.encodeABI(fn_name='getReserves', args=[]),
            },
                hex(blockNumber) if blockNumber != 'latest' else 'latest',
            ]
        )

def rpc_response_batch_to_results(response):
    for response_item in response:
        yield rpc_response_to_result(response_item)

def rpc_response_to_result(response):
    result = response.get('result')
    if result is None:
        error_message = 'result is None in response {}.'.format(response)
        raise ValueError(error_message)
    return result

class BatchHTTPProvider(HTTPProvider):

    def make_batch_request(self, text):
        self.logger.debug("Making request HTTP. URI: %s, Request: %s",
                          self.endpoint_uri, text)
        request_data = text.encode('utf-8')
        # 发送post请求
        raw_response = make_post_request(
            self.endpoint_uri,
            request_data,
            **self.get_request_kwargs()
        )
        # 获取结果
        response = self.decode_rpc_response(raw_response)
        self.logger.debug("Getting response HTTP. URI: %s, "
                          "Request: %s, Response: %s",
                          self.endpoint_uri, text, response)
        return response
