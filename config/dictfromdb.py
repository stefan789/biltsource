import cloudant
import json

acct = cloudant.Account(uri="http://localhost:5984")
res = acct.login("stefan", "root")
assert res.status_code == 200

# Grab the correct database
db = acct["nedm%2Finternal_coils_n"]
des = db.design("document_type")
theview = des.view("document_type")

conf = theview.get(params=dict(
                            endkey = ["bilt_currents_settings"],
                            startkey = ["bilt_currents_settings", {}],
                            include_docs=True,
                            descending=True,
                            reduce = False
                            )).json()

# descending=True and [0] -> latest settings document
print json.dumps(conf, indent=4)
