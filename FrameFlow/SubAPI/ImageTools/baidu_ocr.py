import time
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API 密钥（请替换为自己的）
__API_KEY = 'API_KEY'
__SECRET_KEY = 'SECRET_KEY'

# Token 缓存
_token_cache = {"token": None, "expires_at": 0}

# 速率控制
_last_api_call_time = 0
_API_CALL_INTERVAL = 0.5   # QPS=2 -> 间隔0.5秒

# 创建带重试和连接池的 Session
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET", "POST"]
)
adapter = HTTPAdapter(pool_connections=20, pool_maxsize=50, max_retries=retry_strategy)
session = requests.Session()
session.mount('https://', adapter)
session.mount('http://', adapter)

def _rate_limit():
    """控制API调用频率，保证不超过QPS=2"""
    global _last_api_call_time
    now = time.time()
    elapsed = now - _last_api_call_time
    if elapsed < _API_CALL_INTERVAL:
        sleep_time = _API_CALL_INTERVAL - elapsed
        logger.debug(f"速率限制，休眠 {sleep_time:.2f} 秒")
        time.sleep(sleep_time)
    _last_api_call_time = time.time()

def _get_access_token(api_key, secret_key):
    """获取百度OCR access_token"""
    url = 'https://aip.baidubce.com/oauth/2.0/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': api_key,
        'client_secret': secret_key
    }
    response = session.post(url, data=data, timeout=(5, 10))
    if response.status_code == 200:
        result = response.json()
        return result.get('access_token')
    else:
        raise Exception(f"获取token失败，状态码：{response.status_code}")
    
def get_cached_access_token():
    """获取缓存的token，若过期则重新获取"""
    now = time.time()
    if _token_cache["token"] and _token_cache["expires_at"] > now + 60:
        return _token_cache["token"]
    token = _get_access_token(__API_KEY, __SECRET_KEY)
    _token_cache["token"] = token
    _token_cache["expires_at"] = now + 2592000  # 30天
    return token

def general_ocr(img_base64,access_token):
    _rate_limit()
    request_url_base = 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic'
    request_url = request_url_base + "?access_token=" + access_token
    params = {
        'image':img_base64,
        'detect_direction':'true'
        # 'probability':'true'
    }
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = session.post(request_url,data=params,headers=headers,timeout=(5,10))
    if response.status_code==200:
        result = response.json()
        if 'error_code' in result:
            # API 返回错误
            error_code = result.get('error_code')
            error_msg = result.get('error_msg')
            logger.error(f'通用OCR识别失败，error_code={error_code}，error_msg={error_msg}')
            return None
        words_list = result.get("words_result", [])
        full_text = ''.join(item['words'] for item in words_list)
        idcard_keywords = ['姓名','性别','民族','出生','公民身份号码']
        if any(kw in full_text for kw in idcard_keywords):
            logger.info("检测到身份证特征，调用身份证OCR")
            id_result = _idcard_ocr(img_base64,access_token)
            if id_result:
                return {'type':'idcard','data':id_result}
        bank_keywords = ['银行卡','卡号','有效期','发卡行','借记卡','信用卡','ABC','ATM','银行']
        if any(kw in full_text for kw in bank_keywords):
            logger.info("检测到银行卡特征，调用银行卡OCR")
            bank_result = _bankcard_ocr(img_base64,access_token)
            if bank_result:
                return {'type':'bankcard','data':bank_result}
        return {'type':'general','data':{'text':full_text[:200]}}
        
    else:
        logger.error(f'请求失败，错误原因status_code = {response.status_code}')
        return None
    
def _idcard_ocr(img_base64,access_token):
    _rate_limit()
    request_url_base = "https://aip.baidubce.com/rest/2.0/ocr/v1/idcard"
    params = {"id_card_side":"front","image":img_base64}
    request_url = request_url_base + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = session.post(request_url, data=params, headers=headers,timeout=(5,10))
    if response.status_code==200:
        result = response.json()
        if 'error_code' in result:
            # API 返回错误
            error_code = result.get('error_code')
            error_msg = result.get('error_msg')
            logger.error(f'身份证OCR识别失败，error_code={error_code}，error_msg={error_msg}')
            return None
        words_result = result.get("words_result", {})
        return(
                words_result.get('住址',{}).get('words'),
                words_result.get('公民身份号码',{}).get('words'),
                words_result.get('出生',{}).get('words'),
                words_result.get('姓名',{}).get('words'),
                words_result.get('性别',{}).get('words'),
                words_result.get('民族',{}).get('words'),
            )
    else:
        logger.error(f'身份证OCR请求失败，错误原因status_code = {response.status_code}')
        return None
    
def _bankcard_ocr(img_base64,access_token):
    _rate_limit()
    request_url_base = "https://aip.baidubce.com/rest/2.0/ocr/v1/bankcard"
    params = {"id_card_side":"front","image":img_base64}
    request_url = request_url_base + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = session.post(request_url, data=params, headers=headers,timeout=(5,10))
    if response.status_code==200:
        result = response.json()
        if 'error_code' in result:
            # API 返回错误
            error_code = result.get('error_code')
            error_msg = result.get('error_msg')
            logger.error(f'银行卡OCR识别失败，error_code={error_code}，error_msg={error_msg}')
            return None
        _result = result.get("result", {})
        return(
                _result.get('bank_card_number'),
                _result.get('valid_date'),
                _result.get('bank_card_type'),
                _result.get('bank_name'),
                _result.get('holder_name'),
            )
    else:
        logger.error(f'银行卡OCR请求失败，错误原因status_code = {response.status_code}')
        return None