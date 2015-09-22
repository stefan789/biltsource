import cloudant
import json

def readconfig(conf):
    """ Reads configurations from file conf and return dictionary."""
    with open(str(conf), "r") as f:
        sources = json.loads(f.read())
    return sources

settings = readconfig("config.dict")

#acct = cloudant.Account(uri="http://raid.nedm1")
#res = acct.login("internal_coils_writer", "clu$terXz")
#assert res.status_code == 200

acct = cloudant.Account(uri="http://localhost:5984")
res = acct.login("stefan", "root")
assert res.status_code == 200

# Grab the correct database
db = acct["nedm%2Finternal_coils"]
des = db.design("nedm_default")

adoc = {
            "_id" : "bilt_config",
            "type": "bilt_currents_settings",
            "value": settings
            }
orig_data_doc = des.post("_update/insert_with_timestamp",params=adoc).json()
print orig_data_doc
