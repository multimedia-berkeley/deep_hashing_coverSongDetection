# -*- coding: utf-8 -*- 

import sqlite3
import json

DB = "music_indexed.db"
TABLE = "annotation"
conn = sqlite3.connect(DB)
c = conn.cursor()

for term in ["title", "artist"]:
    c.execute("select id, {term} from {tn}".format(term=term, tn=TABLE))
    rows = c.fetchall()
    row_id = [r[0] for r in rows]
    row_term = [r[1] for r in rows]
    terms = set(row_term)

    term_index_dict = dict()
    term_index_dict_reverse = dict()
    index = 0
    for t in terms:
        term_index_dict[index] = t
        term_index_dict_reverse[t] = index
        index += 1

    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".\
            format(tn=TABLE, cn="{}_id".format(term), ct="INTEGER"))

    for i in range(len(rows)):
        index = rows[i][0]
        t = rows[i][1]
        print("Updating index {}, term {} to {}".format(index, t, term_index_dict_reverse[t]))
        c.execute("UPDATE {tn} SET {cn}={cv} WHERE {rn}={rv}".\
            format(tn=TABLE, cn="{}_id".format(term), 
                cv=term_index_dict_reverse[t], rn="id", rv=index))

    with open('{}_index.json'.format(term), 'w') as fp:
        json.dump(term_index_dict, fp, sort_keys=True, indent=4)

conn.commit()
conn.close()



