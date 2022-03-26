from config import http_provider_url
from rpc import BatchHTTPProvider, generate_get_reserves_json_rpc, rpc_response_batch_to_results
from eth_abi import decode_abi
import json

batch_provider = BatchHTTPProvider(http_provider_url)

def get_reserves(pairs, blockNumber='latest'):
    # 生成rpc请求结构体
    r = list(generate_get_reserves_json_rpc(pairs, blockNumber))
    resp = batch_provider.make_batch_request(json.dumps(r))
    results = list(rpc_response_batch_to_results(resp))
    for i in range(len(results)):
        res = decode_abi(['uint256', 'uint256', 'uint256'], bytes.fromhex(results[i][2:]))
        pairs[i]['reserve0'] = res[0]
        pairs[i]['reserve1'] = res[1]
    return pairs