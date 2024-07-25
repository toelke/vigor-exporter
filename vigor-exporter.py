import os
from base64 import b64encode

from bs4 import BeautifulSoup
from prometheus_client import make_wsgi_app
from prometheus_client.core import (REGISTRY, CounterMetricFamily,
                                    GaugeMetricFamily)
from prometheus_client.registry import Collector
from requests import session


class CustomCollector(Collector):
    def __init__(self):
        self.session = None

    def _do_login(self):
        if self.session is not None:
            return
        self.session = session()
        payload = {'aa': b64encode(os.environ['VIGOR_USERNAME'].encode()), 'ab': b64encode(os.environ['VIGOR_PASSWORD'].encode())}
        self.session.post('http://192.168.1.1/cgi-bin/wlogin.cgi', data=payload)

    def collect(self, retry=True):
        if self.session is None:
            self._do_login()

        try:
            response = self.session.get('http://192.168.1.1/doc/dslstatus.sht')
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
                name = name.strip(": ")
                c = GaugeMetricFamily(f"vigor_status_{name.replace(' ', '_').lower()}", f"Vigor status {name}", labels=["value"])
                c.add_metric([value], 1)
                yield c

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
                name = name.strip(": ")
                ds = ds.replace(" ", "")
                us = us.replace(" ", "")
                if name in ("Path Mode", "Trellis"):
                    c = GaugeMetricFamily(
                        f"vigor_line_statistic_{name.replace(' ', '_').lower()}", f"Vigor line statistic {name}", labels=["direction", "value"]
                    )
                    c.add_metric(["downstream", ds], 1)
                    c.add_metric(["upstream", us], 1)
                    yield c
                elif name in ("NFEC", "RFEC", "LYSMB", "Attenuation", "SNR Margin", "Interleave Depth", "Actual PSD"):
                    c = GaugeMetricFamily(
                        f"vigor_line_statistic_{name.replace(' ', '_').lower()}",
                        f"Vigor line statistic {name}",
                        labels=["direction"] + ([] if usu is None and dsu is None else ["unit"]),
                    )
                    c.add_metric(["downstream"] + ([] if dsu is None else [dsu]), float(ds))
                    c.add_metric(["upstream"] + ([] if usu is None else [usu]), float(us))
                    yield c
                else:
                    c = CounterMetricFamily(
                        f"vigor_line_statistic_{name.replace(' ', '_').lower()}",
                        f"Vigor line statistic {name}",
                        labels=["direction"] + ([] if usu is None and dsu is None else ["unit"]),
                    )
                    c.add_metric(["downstream"] + ([] if dsu is None else [dsu]), float(ds))
                    c.add_metric(["upstream"] + ([] if usu is None else [usu]), float(us))
                    yield c
        except:
            self.session = None
            if retry:
                return self.collect(retry=False)
            raise


REGISTRY.register(CustomCollector())
app = make_wsgi_app()
