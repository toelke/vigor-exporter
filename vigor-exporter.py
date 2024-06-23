from requests import session
from base64 import b64encode
from bs4 import BeautifulSoup

payload = {'aa': b64encode(b'admin'), 'ab': b64encode(b'admin')}

with session() as c:
    c.post('http://192.168.1.1/cgi-bin/wlogin.cgi', data=payload)
    response = c.get('http://192.168.1.1/doc/dslstatus.sht')
    soup = BeautifulSoup(response.text, features="html.parser")

    base_div = soup.find('div', {'class': 'pagetext'})

    # Information
    for line in base_div.find(string="ATU-R Information").parent.parent.parent.parent.find_all('tr'):
        if "Line Statistics" in line.text:
            break
        if 'Type:' in str(line) or 'Hardware' in str(line):
            continue
        try:
            _, name, value = (x.text for x in line.find_all('td'))
        except ValueError:
            continue
        print(name, value)



    # Line statistics
    for line in base_div.find(string="Downstream            ").parent.parent.parent.parent.find_all('tr'):
        if 'Near End' in str(line) or 'Bitswap' in str(line) or 'Downstream' in str(line):
            continue
        try:
            name, ds, dsu, us, usu = (x.text for x in line.find_all('td'))
        except ValueError:
            try:
                name, ds, us = (x.text for x in line.find_all('td'))
                dsu = usu = None
            except ValueError:
                continue
        print(name, ds, dsu, us, usu)

    import code
    code.interact(local=locals())
