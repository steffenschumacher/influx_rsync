from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet

last_data_qry = 'SELECT * FROM /.*/ ORDER BY DESC LIMIT 1'
tags_qry = 'show tag keys from /.*/'
dbs_qry = 'show databases'
fkey_qry = 'show field keys'


def get_database_measurements(client):
    """
    :param InfluxDBClient client:
    :rtype: dict[str, dict[str, str]]
    :return dict of databases, and their measurement, last_data_timestamp pairs
    """
    dbs = {}
    for db in client.get_list_database():
        if db['name'].startswith('_'):
            continue
        dbs[db['name']] = {'last': None, 'tags': None}
        client.switch_database(db['name'])
        last_data = client.query(last_data_qry)
        if not isinstance(last_data, ResultSet):
            continue
        dbs[db['name']]['last'] = {meas: next(points)['time'] for (meas, ign), points in last_data.items()}
        tags = client.query(tags_qry)
        if not isinstance(tags, ResultSet):
            continue

        dbs[db['name']]['tags'] = {meas: [x['tagKey'] for x in points] for (meas, ign), points in tags.items()}
        fkeys = client.query(fkey_qry)
        if not isinstance(fkeys, ResultSet):
            continue

        dbs[db['name']]['fkey'] = \
            {meas: {x['fieldKey']: x['fieldType'] for x in points} for (meas, ign), points in fkeys.items()}

    return dbs


class InfluxRSync(object):
    def __init__(self, src, dst):
        """

        :param InfluxDBClient src:
        :param InfluxDBClient dst:
        """
        self.src = src
        self.dst = dst
        self._src_dbs = None
        self._dst_dbs = None

    @property
    def src_dbs(self):
        if self._src_dbs is None:
            self._src_dbs = get_database_measurements(self.src)
        return self._src_dbs

    @property
    def dst_dbs(self):
        if self._dst_dbs is None:
            self._dst_dbs = get_database_measurements(self.dst)
        return self._dst_dbs

    def sync(self):
        records=0
        for db, meta in self.src_dbs.items():
            self.src.switch_database(db)
            if db not in self.dst_dbs:
                self.dst.create_database(db)
                dst_meta = {'last': {}}
            else:
                dst_meta = self.dst_dbs[db]
            self.dst.switch_database(db)
            for meas, tags in meta['tags'].items():
                qry = 'select * from ' + meas
                last = None if meas not in dst_meta['last'] else dst_meta['last'][meas]
                if last is not None:
                        qry += ' where time > \'{}\''.format(last)
                json_body = []
                dps = self.src.query(qry)
                if not isinstance(dps, ResultSet):
                    continue
                for dp in dps.get_points(meas):
                    p = {'measurement': meas, 'time': dp['time']}
                    del dp['time']
                    p['tags'] = {t: dp[t] for t in tags if t in dp}
                    p['fields'] = {}
                    for k, v in dp.items():
                        if k in meta['tags'][meas]:
                            continue
                        if v is not None and \
                                meta['fkey'][meas][k] in ['integer', 'float'] and \
                                type(v) != meta['fkey'][meas][k]:
                            v = int(v) if type(v) == 'float' else float(v)
                        p['fields'][k] = v
                    json_body.append(p)
                self.dst.write_points(points=json_body, database=db, batch_size=1000)
                print('wrote {} points to {}@{}'.format(len(json_body), meas, db))
                records += len(json_body)
        return 'Sent {} records in {} databases to destination'.format(records, len(self.src_dbs))


if __name__ == '__main__':
    src = InfluxDBClient(host='192.168.1.10')
    dst = InfluxDBClient(host='sommerhus.schumacheren.dk', verify_ssl=True, username='nordsoevej51', password='detsorteHU8')
    irs = InfluxRSync(src, dst)
    print(irs.sync())
