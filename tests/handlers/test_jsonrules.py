# python and pytest are somewhat complicated with the paths...
# added the 'src/' directory to the path to find the remaining modules
import sys
sys.path.append("./src/")

import handlers.jsonrules

def testJsonRulesGet():
    handlers.jsonrules.setup("./tests/handlers/")
    dummy_rules = "{'msg': \"don't talk to me, I'm an error...\"}"
    test_rules = handlers.jsonrules.get("test_proto")
    assert isinstance(test_rules, dict)
    assert dummy_rules == str(test_rules)